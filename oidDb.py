#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import logging
import argparse
import yaml
import pprint
from copy import deepcopy



class oidDb():

    def __init__(self):
        self.firstItem = None
        self.oidDict = {}

    def insertOid(self,newOidItem):
        self.oidDict[newOidItem.oid] = newOidItem
        if self.firstItem == None:
            self.firstItem = newOidItem
        else:
            if newOidItem < self.firstItem:
                tempItem = self.firstItem
                self.firstItem = newOidItem
                self.firstItem.nextOidObj = tempItem
            else:
                iterItem = self.firstItem
                endFlag = False
                while iterItem < newOidItem:
                    lastIterItem = iterItem
                    if iterItem.nextOidObj == None:
                        endFlag = True
                        break
                    else:
                        iterItem = iterItem.nextOidObj
                if endFlag:
                    lastIterItem.nextOidObj = newOidItem
                else:
                    lastIterItem.nextOidObj = newOidItem
                    newOidItem.nextOidObj = iterItem

    def getFirstItem(self,oid):
        return self.firstItem

    def getObjFromOid(self,oid):
        if oid in self.oidDict.keys():
            return self.oidDict[oid]
        else:
            return None

    def getNextOid(self,searchOid):
        logging.debug('getNextOid entry {}'.format(searchOid))
        if self.firstItem:
            if searchOid in self.oidDict.keys():
                logging.debug('getNextOid found {}'.format(self.oidDict[searchOid].oid))
                if self.oidDict[searchOid].nextOidObj:
                    logging.debug('getNextOid returns {}'.format(self.oidDict[searchOid].nextOidObj.oid))
                    return self.oidDict[searchOid].nextOidObj.oid
                else:
                    logging.debug('getNextOid returns 0.0 as no nextOidObj')
                    return "0.0"
            elif self.firstItem.oid.startswith(searchOid):
                logging.debug('getNextOid returns start oid {}'.format(self.firstItem.oid))
                return self.firstItem.oid
            else:
                logging.debug('getNextOid returns 0.0 as no start')
                return "0.0"
        else:
            logging.debug('getNextOid returns 0.0 as no firstItem')
            return "0.0"

    def __str__(self):
        returnStr = ""
        iterItem = self.firstItem
        while iterItem != None:
            returnStr +=  iterItem.oid + "\n"
            iterItem = iterItem.nextOidObj
        return returnStr

class oidDbItem():

    def __init__(self,oid=None,name=None,pysnmpBaseType=None,pysnmpRepresentation=None,
                      value=None,bdsRequest=None,bdsEvalString=None):
        self.oid = oid
        self.oidAsList = [ int(x) for x in self.oid.split(".")]   #for compare
        self.name = name
        self.pysnmpBaseType = pysnmpBaseType
        self.pysnmpRepresentation = pysnmpRepresentation
        self.value = value
        self.bdsRequest = bdsRequest
        self.bdsEvalString = bdsEvalString
        self.nextOidObj = None

    def getNextOid(self):
        if self.nextOidObj:
            return self.nextOidObj.oid
        else:
            return None

    def __lt__(self,oid2):
        if isinstance(oid2,str):
            oid2AsList = [ int(x) for x in oid2.split(".")]
        elif isinstance(oid2,oidDbItem):
            oid2AsList = oid2.oidAsList
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

    def __gt__(self,oid2):
        if isinstance(oid2,str):
            oid2AsList = [ int(x) for x in oid2.split(".")]
        elif isinstance(oid2,oidObj):
            oid2AsList = oid2.oidAsList
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
        returnStr =      "#"*60 + "\n"
        returnStr +=     "oid           :{}\n".format(self.oid)
        returnStr +=     "name          :{}\n".format(self.name)
        returnStr +=     "pysnmp type   :{}\n".format(self.pysnmpBaseType)
        if self.Value != None:
            returnStr += "value         :{}\n".format(self.Value)
        if self.pysnmpRepresentation:
            returnStr += "pysnmp fmt    :{}\n".format(self.pysnmpRepresentation)
        if self.bdsRequest:
            returnStr += "bdsRequest    :{}\n".format(self.bdsRequest)
        if self.bdsEvalString:
            returnStr += "bdsEvalString :{}\n".format(self.bdsEvalString)
        if self.nextOidObj:
            returnStr += "nextOid       :{}\n".format(self.nextOidObj.oid)
        returnStr += "#"*60 + "\n"
        return returnStr

if __name__ == '__main__':

    myOidDb = oidDb()
    oidDefDict1 = {"oid":"1.3.6.1.2.1.1.2.0","name":"sysObjectID","pysnmpBaseType":"ObjectIdentifier",
                  "value": "0.0"}
    oidDefDict2 = {"oid":"1.3.6.1.2.1.1.4.0","name":"sysUpTime","pysnmpBaseType":"OctetString",
                  "value": "this value is configurable in snmpOidMapping.yml e.g. tbd@test.de"}
    myOid1 = oidDbItem(**oidDefDict1)
    #print(myOid1)
    myOid2 = oidDbItem(**oidDefDict2)
    result = myOid1 < myOid2
    assert result == True
    myOidDb.insertOid(myOid1)
    myOidDb.insertOid(myOid2)

    oidDefDict = {"oid":"1.3.6.1.2.1.1.3.0","name":"sysContact","pysnmpBaseType":"OctetString",
                  "bdsRequest": {"process":"confd",
                                 "urlSuffix":"/bds/table/walk",
                                  "table":"global.confd.startup.status"},
                  "bdsEvalString" :'responseJSON["objects"][0]["attribute"]["up_time"]' }
    myOidDb.insertOid(oidDbItem(**oidDefDict))
    print(myOidDb.getObjFromOid("1.3.6.1.2.1.1.2.0"))
    print(myOidDb.getObjFromOid("1.3.6.1.2.1.1.3.0"))
    print(myOidDb.getObjFromOid("1.3.6.1.2.1.1.4.0"))
