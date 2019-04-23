#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
from bdssnmpadaptor.config import loadBdsSnmpAdapterConfigFile
from bdssnmpadaptor.log import set_logging


class OidDb(object):
    """ Database for chained oidDbItems
        Use insertOid and deleteOidsWithPrefix to set or del oidItems
        in self.oidDict in order to maintain the chain structure.
    """

    def __init__(self, cliArgsDict):
        configDict = loadBdsSnmpAdapterConfigFile(
            cliArgsDict["config"], "oidDb")

        self.moduleLogger = set_logging(configDict, "oidDb", self)

        self.moduleLogger.debug("configDict:{}".format(configDict))

        self.firstItem = None  # root of the DB chain
        self.oidDict = {}  # this dict holds all OID items in this # DB
        self.lock = False  # not implemented yet, locker for insertOid

    def insertOid(self, newOidItem):
        if newOidItem.oid in self.oidDict:
            self.moduleLogger.debug(f"updating {newOidItem.oid} {newOidItem.value}")
            self.oidDict[newOidItem.oid].value = newOidItem.value

        else:  # new oid to sorted data structure will be added
            self.moduleLogger.debug(f"creating {newOidItem.oid} {newOidItem.value}")
            self.oidDict[newOidItem.oid] = newOidItem

            if self.firstItem is None:
                self.firstItem = newOidItem

            else:
                if newOidItem < self.firstItem:
                    tempItem = self.firstItem
                    self.firstItem = newOidItem
                    self.firstItem.nextOidObj = tempItem

                else:
                    iterItem = self.firstItem
                    cacheIterItem = iterItem
                    endFlag = False
                    i = 0
                    while iterItem < newOidItem:
                        i += 1

                        cacheIterItem = iterItem

                        if iterItem.nextOidObj is None:
                            endFlag = True
                            break

                        else:
                            iterItem = iterItem.nextOidObj

                    if endFlag:
                        cacheIterItem.nextOidObj = newOidItem

                    else:
                        cacheIterItem.nextOidObj = newOidItem
                        newOidItem.nextOidObj = iterItem

    def deleteOidsWithPrefix(self, oidPrefix):
        iterItem = self.firstItem

        while iterItem is not None:

            if iterItem == self.firstItem:

                if iterItem.oid.startswith(oidPrefix):
                    self.firstItem = iterItem.nextOidObj
                    nextItem = iterItem.nextOidObj
                    self.moduleLogger.debug(f"deleting {iterItem.oid}")
                    self.oidDict.pop(iterItem.oid, None)

                    del iterItem

                    iterItem = nextItem

                else:
                    iterItem = iterItem.nextOidObj

            else:
                if iterItem.nextOidObj is not None:

                    if iterItem.nextOidObj.oid.startswith(oidPrefix):

                        deleteItem = iterItem.nextOidObj
                        iterItem.nextOidObj = iterItem.nextOidObj.nextOidObj
                        self.moduleLogger.debug(f"deleting {deleteItem.oid}")
                        self.oidDict.pop(deleteItem.oid, None)
                        del deleteItem

                    else:
                        iterItem = iterItem.nextOidObj

                else:
                    iterItem = iterItem.nextOidObj

    def deleteOidsFromBdsMappingFunc(self, bdsMappingFunc):
        iterItem = self.firstItem

        while iterItem is not None:
            if iterItem == self.firstItem:
                if iterItem.bdsMappingFunc == bdsMappingFunc:
                    self.firstItem = iterItem.nextOidObj
                    nextItem = iterItem.nextOidObj
                    self.moduleLogger.debug(f"deleting {iterItem.oid}")
                    self.oidDict.pop(iterItem.oid, None)
                    del iterItem
                    iterItem = nextItem

                else:
                    iterItem = iterItem.nextOidObj

            else:
                if iterItem.nextOidObj is not None:

                    if iterItem.bdsMappingFunc == bdsMappingFunc:
                        deleteItem = iterItem.nextOidObj
                        iterItem.nextOidObj = iterItem.nextOidObj.nextOidObj

                        self.moduleLogger.debug(f"deleting {deleteItem.oid}")
                        self.oidDict.pop(deleteItem.oid, None)

                        del deleteItem

                    else:
                        iterItem = iterItem.nextOidObj

                else:
                    iterItem = iterItem.nextOidObj

    def getFirstItem(self):
        return self.firstItem

    def getObjFromOid(self, oid):
        if oid in self.oidDict:
            self.moduleLogger.debug(
                f"getObjFromOid found in oidDict")
            return self.oidDict[oid]

        else:
            self.moduleLogger.warning(
                f"getObjFromOid did NOT found in oidDict")
            return

    def getNextOid(self, searchOid):
        # print(f'getNextOid searchOid:{searchOid}')
        self.moduleLogger.debug(f'getNextOid searchOid:{searchOid}')

        if self.firstItem:

            if searchOid in self.oidDict:  # directMatches
                self.moduleLogger.debug(
                    'getNextOid found {}'.format(self.oidDict[searchOid].oid))

                if self.oidDict[searchOid].nextOidObj:
                    self.moduleLogger.debug(
                        'getNextOid returns {}'.format(self.oidDict[searchOid].nextOidObj.oid))
                    return self.oidDict[searchOid].nextOidObj.oid

                else:
                    self.moduleLogger.warning('getNextOid returns None as not nextOidObj')
                    return

            else:  # find first oid which is greater than searchOid
                # elif self.firstItem.oid.startswith(searchOid):   # Fixme
                #     self.moduleLogger.debug('getNextOid returns start oid {}'.format(self.firstItem.oid))
                #     return self.firstItem.oid
                if self.firstItem > OidDbItem(oid=searchOid):
                    return self.firstItem.oid

                else:
                    # print(f'iterItem = self.firstItem')
                    iterItem = self.firstItem

                    while (iterItem < OidDbItem(oid=searchOid)
                           and iterItem.nextOidObj is not None):
                        # print (iterItem.oid,searchOid)
                        if iterItem.nextOidObj > OidDbItem(oid=searchOid):
                            return iterItem.nextOidObj.oid

                        else:
                            iterItem = iterItem.nextOidObj

                    self.moduleLogger.warning(
                        'getNextOid None as none oid is greater')

                    return
        else:
            self.moduleLogger.warning(
                'getNextOid returns None as no firstItem')
            return

    def setLock(self):
        self.lock = True

    def releaseLock(self):
        self.lock = False

    def isLocked(self):
        return self.lock

    def __str__(self):
        returnStr = ""
        iterItem = self.firstItem

        while iterItem is not None:
            returnStr += iterItem.oid + "\n"
            iterItem = iterItem.nextOidObj

        return returnStr


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
        self.oidAsList = [int(x) for x in self.oid.split(".")]  # for compare
        self.name = name
        self.pysnmpBaseType = pysnmpBaseType
        self.pysnmpRepresentation = pysnmpRepresentation
        self.value = value
        # if self.pysnmpRepresentation:
        #     evalString = "{}({}='{}')".format(self.pysnmpBaseType,
        #                                       self.pysnmpRepresentation,
        #                                       self.value)
        # else:
        #     evalString = "{}('{}')".format(self.pysnmpBaseType,
        #                                    self.value)
        # try:
        #     self.encodedValue = eval(evalString )
        # except Exception as e:
        #     self.encodedValue = None
        #     raise Exception(f'cannot encode value for {self.name} - evalString {evalString}')
        self.bdsRequest = bdsRequest
        self.nextOidObj = None

    def _encodeValue(self):

        if self.pysnmpRepresentation:
            evalString = "{}({}='{}')".format(
                self.pysnmpBaseType, self.pysnmpRepresentation, self.value)

        else:
            evalString = "{}('{}')".format(
                self.pysnmpBaseType, self.value)
        try:
            self.encodedValue = eval(evalString)

        except Exception as e:
            self.encodedValue = None
            raise Exception(f'cannot encode value for {self.name} - evalString'
                            f' {evalString}')

    def getNextOid(self):
        if self.nextOidObj:
            return self.nextOidObj.oid

        else:
            return

    def __lt__(self, oid2):
        if isinstance(oid2, str):
            oid2AsList = [int(x) for x in oid2.split(".")]

        elif isinstance(oid2, OidDbItem):
            oid2AsList = oid2.oidAsList

        else:
            raise ValueError('Unsupported type %s in comparison' % type(oid2))

        pos = 0

        while pos < len(self.oidAsList) and pos < len(oid2AsList):
            if oid2AsList[pos] < self.oidAsList[pos]:
                return False

            if oid2AsList[pos] > self.oidAsList[pos]:
                return True

            pos += 1

        if len(self.oidAsList) < len(oid2AsList):
            return True

        if len(self.oidAsList) > len(oid2AsList):
            return False

        if self.oidAsList == oid2AsList:
            return False

        return True

    def __gt__(self, oid2):
        if isinstance(oid2, str):
            oid2AsList = [int(x) for x in oid2.split(".")]

        elif isinstance(oid2, OidDbItem):
            oid2AsList = oid2.oidAsList

        else:
            raise ValueError('Unsupported type %s in comparison' % type(oid2))

        pos = 0

        while pos < len(self.oidAsList) and pos < len(oid2AsList):
            if oid2AsList[pos] > self.oidAsList[pos]:
                return False

            if oid2AsList[pos] < self.oidAsList[pos]:
                return True

            pos += 1

        if len(self.oidAsList) < len(oid2AsList):
            return False

        if len(self.oidAsList) > len(oid2AsList):
            return True

        if self.oidAsList == oid2AsList:
            return False

        return True

    def __str__(self):
        returnStr = "#" * 60 + "\n"
        returnStr += "oid           :{}\n".format(self.oid)
        returnStr += "name          :{}\n".format(self.name)
        returnStr += "pysnmp type   :{}\n".format(self.pysnmpBaseType)

        if self.value is not None:
            returnStr += "value         :{}\n".format(self.value)

        if self.pysnmpRepresentation:
            returnStr += "pysnmp fmt    :{}\n".format(self.pysnmpRepresentation)

        if self.bdsRequest:
            returnStr += "bdsRequest    :{}\n".format(self.bdsRequest)

        if self.nextOidObj:
            returnStr += "nextOid       :{}\n".format(self.nextOidObj.oid)

        returnStr += "#" * 60 + "\n"

        return returnStr
