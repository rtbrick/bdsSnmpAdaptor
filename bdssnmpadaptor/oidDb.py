#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
from bisect import bisect
from collections import OrderedDict

from bdssnmpadaptor.config import loadBdsSnmpAdapterConfigFile
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
        configDict = loadBdsSnmpAdapterConfigFile(
            cliArgsDict['config'], 'oidDb')

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.moduleLogger.debug('configDict:{}'.format(configDict))

        self.firstItem = None  # root of the DB chain
        self.oidDict = OrderedDict()  # this dict holds all OID items in this # DB
        self.dirty = True  # DB needs sorting
        self.lock = False  # not implemented yet, locker for insertOid

    def insertOid(self, newOidItem):
        self.moduleLogger.debug(
            f'{"updating" if newOidItem.oid in self.oidDict else "adding"} '
            f'{newOidItem.oid} {newOidItem.value}')
        self.oidDict[newOidItem.oid] = newOidItem
        self.dirty = True

    def deleteOidsWithPrefix(self, oidPrefix):
        for oid in tuple(self.oidDict):
            if oid.startswith(oidPrefix):
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

    @lazilySorted
    def getFirstItem(self):
        if self.oidDict:
            first = tuple(self.oidDict)[0]
            return self.oidDict[first]

        self.moduleLogger.warning(f'OID DB is empty')

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


class OidDbItem(object):
    """ Database Item, which pysnmp attributes required for get and getnext.

    """

    def __init__(self, bdsMappingFunc=None, oid=None, name=None,
                 pysnmpBaseType=None, pysnmpRepresentation=None, value=None,
                 bdsRequest=None):
        """ Database Item, which pysnmp attributes required for get and getnext.

        Args:
            bdsMappingFunc(string): used to mark, which mapping function owns this oid. (used for delete)
            oid(string): oid as string, separated by dots.
            name(string): name of the oid, should map with MIB identifier name, altough this is not enforced
            pysnmpBaseType(class): used for conversion of value, options are defined in pysnmp.proto.rfc1902
            pysnmpRepresentation(string): used to siganal hexValue representation for stringsself.
            value: object that holds the value of the oid. Type is flexible, subject to oidself
            bdsRequest: obsolete ###FIXME deprecate

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
        self.oid = oid
        self.oidAsList = [int(x) for x in self.oid.split('.')]  # for compare
        self.name = name
        self.pysnmpBaseType = pysnmpBaseType
        self.pysnmpRepresentation = pysnmpRepresentation
        self.value = value
        self.bdsRequest = bdsRequest

    def _encodeValue(self):

        representation = (self.pysnmpRepresentation
                          if self.pysnmpRepresentation else 'value')

        try:
            self.encodedValue = self.pysnmpBaseType(**{representation: self.value})

        except Exception as ex:
            self.encodedValue = None
            raise Exception(f'cannot encode value for {self.name}, representation '
                            f'{representation}: {ex}')

    def _getOidAsList(self, oid2):
        if isinstance(oid2, str):
            return [int(x) for x in oid2.split('.')]

        elif isinstance(oid2, OidDbItem):
            return oid2.oidAsList

        raise ValueError(f'Unsupported type {type(oid2)} in comparison')

    def __lt__(self, oid2):
        return self.oidAsList < self._getOidAsList(oid2)

    def __eq__(self, oid2):
        return self.oidAsList == self._getOidAsList(oid2)

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

        if self.pysnmpRepresentation is not None:
            returnStr += f"""\
SNMP format: {self.pysnmpRepresentation}
"""

        if self.bdsRequest:
            returnStr += f"""\
BDS request: {self.bdsRequest}
"""

        returnStr += f"""\
############################################################
"""

        return returnStr
