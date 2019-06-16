#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import contextlib
import functools
import time
from bisect import bisect
from collections import OrderedDict

from pysnmp.proto.rfc1902 import ObjectIdentifier
from pysnmp.smi import builder
from pysnmp.smi import compiler
from pysnmp.smi import rfc1902
from pysnmp.smi import view

from bdssnmpadaptor import error
from bdssnmpadaptor.config import loadConfig
from bdssnmpadaptor.log import set_logging


def lazilySorted(func):
    def wrapper(self, *args, **kwargs):
        if self._dirty:
            self._oids = OrderedDict(
                sorted(self._oids.items(), key=lambda x: x[1]))
            self._dirty = False

            self.moduleLogger.debug(
                f'resorted OIDs in OID DB: {tuple(self._oids)}')

        return func(self, *args, **kwargs)

    return wrapper


class OidDb(object):
    """SNMP managed objects database

     Implements in-memory store for MIB managed objects keyed by
     object identifier (OID).

     Managed objects population is based on SNMP MIB information,
     retrieval is based on OID look up.
     """
    EXPIRE_PERIOD = 60

    def __init__(self, args):
        configDict = loadConfig(args.config)

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.moduleLogger.debug('configDict:{}'.format(configDict))

        mibBuilder = builder.MibBuilder()
        self._mibViewController = view.MibViewController(mibBuilder)

        compiler.addMibCompiler(
            mibBuilder, sources=configDict['snmp'].get('mibs', ()))

        # this dict holds all OID items in this # DB
        self._oids = {}

        # this dict maintains non-expiring OID items
        self._permanentOids = {}

        # this dict holds the newer version of the above
        self._candidateOids = {}

        self._expireBy = time.time() + self.EXPIRE_PERIOD

        self._dirty = True  # DB needs sorting

    def add(self, mibName, mibSymbol, *indices, value=None,
            valueFormat=None, code=None, bdsMappingFunc=None, permanent=False):
        """Add SNMP MIB managed object instance to the OID DB

        Args:
            mibName (str): MIB name e.g. SNMPv2-MIB. This MIB must be in MIB
                search path.
            mibSymbol (str): MIB symbol name
            indices (vararg): one or more objects representing indices.
                Should be `0` for scalars.
            value: put this value into MIB managed object. This is what SNMP
                manager will get in response.
            valueFormat (string): 'hexValue' to indicate hex `value` initializer.
                Optional.
            code (string): compile and use this Python code snippet for getting a
                value at run time. Optional.
            bdsMappingFunc(string): used to mark, which mapping function owns
                this oid (used for delete). Optional
            permanent (bool): never expire this object

        Examples:
          add('SNMPv2-MIB', 'sysDescr', 0,
              value='hello world',
              bdsMappingFunc="confd_global_interface_container")

        """
        if value is None:
            raise error.BdsError(
                'Initial value for the managed object must be provided')

        obj = rfc1902.ObjectType(
            rfc1902.ObjectIdentity(mibName, mibSymbol, *indices), value)

        objectIdentity, objectSyntax = obj.resolveWithMib(self._mibViewController)

        try:
            representation = {valueFormat if valueFormat else 'value': value}
            objectSyntax = objectSyntax.clone(**representation)

            if code:
                code = compile(code, '<%s::%s>' % (mibName, mibSymbol), 'exec')

            oidDbItem = OidDbItem(
                bdsMappingFunc=bdsMappingFunc,
                oid=objectIdentity.getOid(),
                name=objectIdentity.getMibSymbol()[1],
                value=objectSyntax,
                code=code
            )

        except Exception as exc:
            raise error.BdsError(
                'Error setting managed object %s (%s) of type %s to value '
                '"%s"' % ('::'.join(objectIdentity.getMibSymbol()),
                          objectIdentity.getOid(), objectSyntax, value))

        self.moduleLogger.debug(
            f'{"updating" if oidDbItem.oid in self._oids else "adding"} '
            f'{oidDbItem.oid} {"<code>" if code else oidDbItem.value.prettyPrint()}')

        self._oids[oidDbItem.oid] = oidDbItem

        if permanent:
            self._permanentOids[oidDbItem.oid] = oidDbItem

        self._dirty = True

        now = time.time()

        # We update two DBs for some time while use only one, eventually
        # we drop the older DB and use the newer one. This effectively
        # expires DB entries that do not get updated for some time.
        self._candidateOids[oidDbItem.oid] = oidDbItem

        if self._expireBy < now:
            self._oids.clear()
            self._oids.update(self._permanentOids)
            self._oids.update(self._candidateOids)
            self._candidateOids.clear()

            # stale entries expire in two runs of `.add`
            self._expireBy = now + self.EXPIRE_PERIOD / 2

    def deleteOidsWithPrefix(self, oidPrefix):
        oidPrefix = ObjectIdentifier(oidPrefix)

        for oid in tuple(self._oids):
            if oidPrefix.isPrefixOf(oid):
                self.moduleLogger.debug(
                    f'deleting {oid} by prefix {oidPrefix}')
                self._oids.pop(oid)
                self._candidateOids.pop(oid)
                self._dirty = True

    def deleteOidsFromBdsMappingFunc(self, bdsMappingFunc):
        for oid, item in tuple(self._oids.items()):
            if item.bdsMappingFunc == bdsMappingFunc:
                self.moduleLogger.debug(
                    f'deleting {oid} by func {bdsMappingFunc}')
                self._oids.pop(oid)
                self._candidateOids.pop(oid)
                self._dirty = True

    def getObjFromOid(self, oid):
        try:
            return self._oids[oid]

        except KeyError:
            self.moduleLogger.warning(
                f'requested OID {oid} is not found in OID DB')

    @lazilySorted
    def getNextOid(self, searchOid):
        self.moduleLogger.debug(
            f'searching for OID next to {searchOid}')

        sortedItems = tuple(self._oids.values())

        searchItem = (searchOid if isinstance(searchOid, OidDbItem)
                      else OidDbItem(oid=searchOid))

        nextIdx = bisect(sortedItems, searchItem)

        try:
            nextItem = sortedItems[nextIdx]

        except IndexError:
            self.moduleLogger.warning(f'no next OID found past {searchItem.oid}')
            return

        self.moduleLogger.debug(f'next OID to {searchItem.oid} is {nextItem.oid}')

        return nextItem.oid

    @lazilySorted
    def __str__(self):
        return '\n'.join(self._oids)

    @contextlib.contextmanager
    def module(self, bdsMappingFunc, permanent=False):
        yield functools.partial(self.add, bdsMappingFunc=bdsMappingFunc, permanent=permanent)


class OidDbItem(object):
    """Represents managed object in the database.

    Implements managed objects comparison what is used for ordering
    objects by OID.
    """
    def __init__(self, bdsMappingFunc=None, oid=None, name=None, value=None, code=None):
        """Database Item, which pysnmp attributes required for get and getnext.

        Args:
            bdsMappingFunc(string): used to mark, which mapping function owns this oid. (used for delete)
            oid(string): oid as string, separated by dots.
            name(string): name of the oid, should map with MIB identifier name, although this is not enforced
            value: object that holds the value of the OID. Type is flexible, subject to OID type
            code (object): use this Python code object for getting a value at run time

        Examples:
          OidDbItem(
            bdsMappingFunc="confd_global_interface_container",
            oid=oidSegment + "1." + str(index),
            name="ifIndex",
            value=rfc1902.Integer32(index)))
        """
        self.bdsMappingFunc = bdsMappingFunc
        self.oid = ObjectIdentifier(oid)
        self.name = name
        self.value = value
        self.code = code

    def __lt__(self, oidItem):
        return self.oid < oidItem.oid

    def __eq__(self, oidItem):
        return self.oid == oidItem.oid

    def __str__(self):
        return "{self.name}({self.value}):{self.value}{self.code}"
