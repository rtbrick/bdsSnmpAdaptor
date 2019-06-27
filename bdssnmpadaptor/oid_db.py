# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import time
from bisect import bisect
import collections

from pysnmp.proto.rfc1902 import ObjectIdentifier
from pysnmp.smi import builder
from pysnmp.smi import compiler
from pysnmp.smi import rfc1902
from pysnmp.smi import view

from bdssnmpadaptor import error
from bdssnmpadaptor.config import loadConfig
from bdssnmpadaptor.log import set_logging


def lazilySorted(func):
    """Ensure OID DB items are sorted.

    A decorator expecting `self._oids` attribute of the passing object to
    contain a `dict`, which will be ordered if `self._dirty` is `True`.
    """
    def wrapper(self, *args, **kwargs):
        if self._dirty:
            self._oids = collections.OrderedDict(
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

    Args:
        args (object): argparse namespace object holding command-line options

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

        # this dict holds all OID items indexed by MIB symbols
        self._mibObjects = collections.defaultdict(dict)

        # this dict holds only recently updated OIDs (indexed by
        # MIB name and object)
        self._candidateMibObjects = collections.defaultdict(dict)

        # this dict holds all OID items populated from `mibObjects`
        self._oids = {}

        self._expireBy = time.time() + self.EXPIRE_PERIOD

        self._dirty = True  # OIDs need sorting

    def add(self, mibName, mibSymbol, *indices, value=None,
            valueFormat=None, code=None):
        """Add SNMP MIB managed object instance to the OID DB

        Args:
            mibName (str): MIB name e.g. SNMPv2-MIB. This MIB must be in MIB
                search path.
            mibSymbol (str): MIB symbol name
            indices (vararg): one or more objects representing indices.
                Should be `0` for scalars.
            value: put this value into MIB managed object. This is what SNMP
                manager will get in response. The `None` sentinel refreshes
                existing object.
            valueFormat (string): 'hexValue' to indicate hex `value` initializer.
                Optional.
            code (string): compile and use this Python code snippet for getting a
                value at run time. Optional.

        Examples:

          add('SNMPv2-MIB', 'sysDescr', 0, value='hello world')
          add('SNMPv2-MIB', 'sysDescr', 0, value='10101010', valueFormat='binValue')
          add('SNMPv2-MIB', 'sysDescr', 0, code='print("hello world")')

        """
        if value is None:
            objectIdentity = rfc1902.ObjectIdentity(
                mibName, mibSymbol, *indices).resolveWithMib(self._mibViewController)

            try:
                oidDbItem = self._oids[objectIdentity.getOid()]

            except KeyError:
                raise error.BdsError(
                    'Initial value for managed %s::%s object must be '
                    'provided' % (mibName, mibSymbol))

        else:
            obj = rfc1902.ObjectType(
                rfc1902.ObjectIdentity(mibName, mibSymbol, *indices), value)

            objectIdentity, objectSyntax = obj.resolveWithMib(self._mibViewController)

            try:
                representation = {valueFormat if valueFormat else 'value': value}
                objectSyntax = objectSyntax.clone(**representation)

                if code:
                    code = compile(code, '<%s::%s>' % (mibName, mibSymbol), 'exec')

                oidDbItem = OidDbItem(
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

        # put new OID online immediately
        self._oids[oidDbItem.oid] = oidDbItem

        self._dirty = True

        now = time.time()

        mibObject = mibName, mibSymbol

        # We update two DBs for some time while use only one, eventually
        # we drop the older DB and use the newer one. This effectively
        # expires DB entries that do not get updated for some time.
        self._mibObjects[mibObject][oidDbItem.oid] = oidDbItem
        self._candidateMibObjects[mibObject][oidDbItem.oid] = oidDbItem

        if self._expireBy < now:

            # put candidate objects online
            (self._mibObjects[mibObject],
             self._candidateMibObjects[mibObject]) = (
                self._candidateMibObjects[mibObject],
                self._mibObjects[mibObject])

            # prepare new candidate objects dict - drop everything it has,
            # most importantly, entries that have not been updated
            # N.B. this only works for tablular SNMP objects
            self._candidateMibObjects[mibObject].clear()

            # stale entries expire in two runs of `.add`
            self._expireBy = now + self.EXPIRE_PERIOD / 2

            # drop all online OIDs
            self._oids.clear()

            # put recently updated OIDs online
            for oidItems in self._mibObjects.values():
                self._oids.update(oidItems)

    def getObjectsByName(self, mibName, symbolName):
        """Fetch SNMP managed objects instances by MIB object name.

        Args:
            mibName (str): MIB module name to search and load up
            symbolName (str): MIB object name to search in MIB module `mibName`

        Returns:
            dict: A `dict` containing zero or more `OidDbItem` objects keyed by
                OIDs of the managed objects instances.

        Examples:

              >>> self.getObjectByName('IF-MIB', 'ifIndex')
              {'1.3.6.1.2.1.2.2.1.1.1': <OidDbItem instance at 0x10283b6c8>,
               '1.3.6.1.2.1.2.2.1.1.2': <OidDbItem instance at 0x1028345a1>}

        """
        mibObject = mibName, symbolName
        return self._mibObjects.get(mibObject, {})

    def getObjectByOid(self, oid):
        """Fetch SNMP managed object instance by OID.

        Args:
            oid (str): OID of the MIB managed object instance to fetch

        Returns:
            OidDbItem: requested `OidDbItem` if found or `None` otherwise.

        Examples:

              >>> self.getObjectByOid('1.3.6.1.2.1.2.2.1.1.1')
              {'1.3.6.1.2.1.2.2.1.1.1': <OidDbItem instance at 0x10283b6c8>,

        """

        try:
            return self._oids[oid]

        except KeyError:
            self.moduleLogger.warning(
                f'requested OID {oid} is not found in OID DB')

    @lazilySorted
    def getNextOid(self, oid):
        """Fetch lexicographically *next* MIB managed object instance OID.

        Args:
            oid (str): OID of the MIB managed object instance which is
                lexicographically just before the desired managed object
                instance.

        Returns:
            str: OID of the lexicographically *next* MIB managed object
                instance or `None` if no *next* OID was not found

        Examples:

              >>> self.getNextOid('1.3.6.1.2.1.2.2.1.1')
              '1.3.6.1.2.1.2.2.1.1.1'

        """
        self.moduleLogger.debug(
            f'searching for OID next to {oid}')

        sortedItems = tuple(self._oids.values())

        searchItem = (oid if isinstance(oid, OidDbItem)
                      else OidDbItem(oid=oid))

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


class OidDbItem(object):
    """Represents managed object in the database.

    Implements managed objects comparison what is used for ordering
    objects by OID.

    Args:
        oid (string): OID of the MIB managed object at hand
        name (string): MIB managed object name
        value (object): object that holds the static value of the OID.
        code (object): Python code object to run and produce a dynamic value at
            the request time

    Examples:

      OidDbItem(
        oid=oidSegment + "1." + str(index),
        name="ifIndex",
        value=rfc1902.Integer32(index)))

    """
    def __init__(self, oid=None, name=None, value=None, code=None):
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
