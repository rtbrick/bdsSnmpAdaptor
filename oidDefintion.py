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


class oidObj():

    def __init__(self,oid):
        self.oid = oid
        self.oidAsList = [ int(x) for x in self.oid.split(".")]

    def __lt__(self,oid2):
        if isinstance(oid2,str):
            oid2AsList = [ int(x) for x in oid2.split(".")]
        elif isinstance(oid2,oidObj):  
            oid2AsList = oid2.oidAsList
        pos = 0
        while pos < len(self.oidAsList) and pos < len(oid2AsList):
            #print(self.oidAsList[pos],oid2AsList[pos])
            if oid2AsList[pos] < self.oidAsList[pos]:
                #print("return False",self.oidAsList[pos],oid2AsList[pos])
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
            #print(self.oidAsList[pos],oid2AsList[pos])
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
        

class oidListObj():

    def __init__(self,oidList):
        self.oidList = oidList

    @classmethod
    def getSortedList(self,oidList):
        returnList = []
        for oid in oidList:
            if len(returnList) == 0:
                returnList.append(oid)
            else:
                newOidObj = oidObj(oid)
                insertedFlag = False
                for i,existingOid in enumerate(returnList):
                    existingOidObj = oidObj(existingOid)
                    if newOidObj < existingOidObj:
                        returnList.insert(i,oid)
                        insertedFlag = True
                        break
                if not insertedFlag:
                    returnList.append(oid)       
        return(returnList)

if __name__ == '__main__':

    myOidObj1 = oidObj('1.3.6.1.2.1.2.2.1.1.2')
    myOidObj2 = oidObj('1.3.6.1.2.1.2.2.1.2.1')
    result = myOidObj1 < myOidObj2
    assert result == True
    myOidObj1 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    result = myOidObj1 < "1.3.6.1.2.1.2.2.1.10.1"
    assert result == True
    myOidObj1 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    result = myOidObj1 < "1.3.6.1.2.1.2.2.1.4.1"
    assert result == False
    myOidObj1 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    myOidObj2 = oidObj("1.3.6.1.2.1.2.2.1.6.1")
    result = myOidObj1 < myOidObj2
    assert result == True
    myOidObj1 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    myOidObj2 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    result = myOidObj1 < myOidObj2
    assert result == False
    myOidObj1 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    myOidObj2 = oidObj("1.3.6.1.2.1.2.2.1.5")
    result = myOidObj1 < myOidObj2
    assert result == False
    myOidObj1 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    myOidObj2 = oidObj("1.3.6.1.2.1.2.2.1.5.1.1")
    result = myOidObj1 < myOidObj2
    assert result == True
    myOidObj1 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    myOidObj2 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    result = myOidObj1 > myOidObj2
    assert result == False
    myOidObj1 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    myOidObj2 = oidObj("1.3.6.1.2.1.2.2.1.6.1")
    result = myOidObj1 > myOidObj2
    assert result == False
    myOidObj1 = oidObj("1.3.6.1.2.1.2.2.1.6.1")
    myOidObj2 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    result = myOidObj1 > myOidObj2
    assert result == True
    myOidObj1 = oidObj("1.3.6.1.2.1.2.2.1.5.1.1")
    myOidObj2 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    result = myOidObj1 > myOidObj2
    assert result == True
    myOidObj1 = oidObj("1.3.6.1.2.1.2.2.1.5.1")
    myOidObj2 = oidObj("1.3.6.1.2.1.2.2.1.5.1.1")
    result = myOidObj1 > myOidObj2
    assert result == False


