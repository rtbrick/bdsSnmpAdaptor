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
        if self.dirty:
            self.oidDict = OrderedDict(
                sorted(self.oidDict.items(), key=lambda x: x[1]))
            self.dirty = False

            self.moduleLogger.debug(
                f'resorted OIDs in OID DB: {self.oidDict.keys()}')

        return func(self, *args, **kwargs)

    return wrapper


class OidDb(object):
    """ Database for chained oidDbItems
        Use insertOid and deleteOidsWithPrefix to set or del oidItems
        in self.oidDict in order to maintain the chain structure.
    """

    def __init__(self, cliArgsDict):
        configDict = loadConfig(cliArgsDict['config'])

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.moduleLogger.debug('configDict:{}'.format(configDict))

        mibBuilder = builder.MibBuilder()
        self.mibViewController = view.MibViewController(mibBuilder)

        compiler.addMibCompiler(
            mibBuilder, sources=configDict['snmp'].get('mibs', ()))

        self.oidDict = OrderedDict()  # this dict holds all OID items in this # DB

        self.dirty = True  # DB needs sorting
        self.lock = False  # not implemented yet, locker for insertOid

    def add(self, mibName, mibSymbol, *indices, value=None,
            valueFormat=None, bdsMappingFunc=None):
        """ Database Item, which pysnmp attributes required for get and getnext.

        Args:
            mibName (str): MIB name e.g. SNMPv2-MIB. This MIB must be in MIB search path.
            mibSymbol (str): MIB symbol name
            indices (vararg): one or more objects representing indices. Should be `0` for scalars.
            value: put this value into MIB managed object. This is what SNMP manager will get in response.
            valueFormat (string): 'hexValue' to indiciate hex `value` initializer
            bdsMappingFunc(string): used to mark, which mapping function owns this oid. (used for delete)

        Examples:
          add('SNMPv2-MIB', 'sysDescr', 0,
              value='hello world',
              bdsMappingFunc="confd_global_interface_container")

        """
        obj = rfc1902.ObjectType(
            rfc1902.ObjectIdentity(mibName, mibSymbol, *indices), value)

        objectIdentity, objectSyntax = obj.resolveWithMib(self.mibViewController)

        representation = {valueFormat if valueFormat else 'value': value}
        objectSyntax = objectSyntax.clone(**representation)

        try:
            objectSyntax = objectSyntax.clone(**representation)

            oidDbItem = OidDbItem(
                bdsMappingFunc=bdsMappingFunc,
                oid=objectIdentity.getOid(),
                name=objectIdentity.getMibSymbol()[1],
                value=objectSyntax
            )

        except Exception as exc:
            raise error.BdsError(
                'Error setting managed object %s (%s) of type %s to value '
                '"%s"' % ('::'.join(objectIdentity.getMibSymbol()),
                          objectIdentity.getOid(), objectSyntax, value))

        self.insertOid(oidDbItem)

    def insertOid(self, newOidItem):
        self.moduleLogger.debug(
            f'{"updating" if newOidItem.oid in self.oidDict else "adding"} '
            f'{newOidItem.oid} {newOidItem.value}')
        self.oidDict[newOidItem.oid] = newOidItem
        self.dirty = True

    def deleteOidsWithPrefix(self, oidPrefix):
        oidPrefix = ObjectIdentifier(oidPrefix)

        for oid in tuple(self.oidDict):
            if oidPrefix.isPrefixOf(oid):
                self.moduleLogger.debug(
                    f'deleting {oid} by prefix {oidPrefix}')
                del self.oidDict[oid]
                self.dirty = True

    def deleteOidsFromBdsMappingFunc(self, bdsMappingFunc):
        for oid, item in tuple(self.oidDict.items()):
            if item.bdsMappingFunc == bdsMappingFunc:
                self.moduleLogger.debug(
                    f'deleting {oid} by func {bdsMappingFunc}')
                del self.oidDict[oid]
                self.dirty = True

    def getObjFromOid(self, oid):
        try:
            return self.oidDict[oid]

        except KeyError:
            self.moduleLogger.warning(
                f'requested OID {oid} is not found in OID DB')

    @lazilySorted
    def getNextOid(self, searchOid):
        self.moduleLogger.debug(
            f'searching for OID next to {searchOid}')

        sortedItems = tuple(self.oidDict.values())

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

    def setLock(self):
        self.lock = True

    def releaseLock(self):
        self.lock = False

    def isLocked(self):
        return self.lock

    @lazilySorted
    def __str__(self):
        return '\n'.join(self.oidDict)

    @contextlib.contextmanager
    def module(self, bdsMappingFunc):
        yield functools.partial(self.add, bdsMappingFunc=bdsMappingFunc)


class OidDbItem(object):
    """ Database Item, which pysnmp attributes required for get and getnext.

    """

    def __init__(self, bdsMappingFunc=None, oid=None, name=None,
                 pysnmpBaseType=None, value=None, pysnmpRepresentation=None):
        """ Database Item, which pysnmp attributes required for get and getnext.

        Args:
            bdsMappingFunc(string): used to mark, which mapping function owns this oid. (used for delete)
            oid(string): oid as string, separated by dots.
            name(string): name of the oid, should map with MIB identifier name, altough this is not enforced
            pysnmpBaseType(class): used for conversion of value, options are defined in pysnmp.proto.rfc1902
            value: object that holds the value of the oid. Type is flexible, subject to oidself

        Examples:
          OidDbItem(
            bdsMappingFunc = "confd_global_interface_container",
            oid = oidSegment+"1."+str(index),
            name="ifIndex",
            pysnmpBaseType="Integer32",
            value=int(index)))

        raise:

        Todo:
            * Verify value type, by cross-checking with pysnmpBaseType
        """
        self.bdsMappingFunc = bdsMappingFunc
        self.oid = ObjectIdentifier(oid)
        self.name = name

        # For backward compatibility
        if pysnmpBaseType is not None:
            representation = {pysnmpRepresentation if pysnmpRepresentation else 'value': value}
            value = pysnmpBaseType(**representation)

        self.pysnmpBaseType = pysnmpBaseType
        self.value = value

    def __lt__(self, oidItem):
        return self.oid < oidItem.oid

    def __eq__(self, oidItem):
        return self.oid == oidItem.oid

    def __str__(self):
        returnStr = f"""\
############################################################
OID:         {self.oid}            
Name:        {self.name}
SNMP type:   {self.pysnmpBaseType}
"""

        if self.value is not None:
            returnStr += f"""\
Value:       {self.value}
"""

        returnStr += f"""\
############################################################
"""

        return returnStr
