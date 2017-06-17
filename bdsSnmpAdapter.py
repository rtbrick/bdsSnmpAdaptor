#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pprint
import csv
import requests
import json
import logging
import yaml

class oidTree:
    def __init__(self):
        self.root = snmpObject()

    def addOid(self,oid,oidDict):
        oidPathList = oid.split(".")
        position = self.root
        for i,oidPathElement in enumerate(oidPathList):
            if oidPathElement not in [ x.id for x in position.childs]:
                if i == len(oidPathList)-1:
                    newSnmpObject = snmpObject(id=oidPathElement,oidDict=oidDict,parent=position,childs=[])
                    position.childs.append(newSnmpObject)
                    pathList = newSnmpObject.rootPath([])
                    thisPath = ".".join(pathList)
                    logging.info ("addOid leaf {} path {}".format(newSnmpObject.oidDict["name"],thisPath))
                else: 
                    newSnmpObject = snmpObject(id=oidPathElement,parent=position,childs=[])
                    position.childs.append(newSnmpObject)
                newPosition = newSnmpObject
            else:
                newPosition = [ x for x in position.childs if x.id == oidPathElement][0]
            position = newPosition

    def getOidDictParentDictAndIndex(self,oid):
        oidPathList = oid.split(".")
        position = self.root
        for i,oidPathElement in enumerate(oidPathList):
            if oidPathElement in [ x.id for x in position.childs]:
                newPosition = [ x for x in position.childs if x.id == oidPathElement][0]
                position = newPosition
            else:
                snmpIndex = ".".join(oidPathList[i:])
                return position.oidDict,position.parent.oidDict,snmpIndex
        #print(position)
        if position.parent.oidDict == {}:
            return position.oidDict,None,None
        else:
            return position.oidDict,position.parent.oidDict,None                         

                       
class snmpObject:
    def __init__(self,id=None,oidDict = None,parent = None,childs=[]):
        self.id = id
        self.parent = parent
        self.childs = childs
        self.oidDict = oidDict

    def rootPath(self,pathList):
        #print("rootPath",pathList)
        if self.parent:
            pathList.append(self.id)
            return self.parent.rootPath(pathList)
        else:
            pathList.reverse()
            return pathList

    def __str__(self):
        returnList = []
        if self.oidDict != None: 
            returnList.append("oid path: {}".format(".".join(self.rootPath([]))))
            returnList.append("name: {}".format(self.oidDict["name"]))
            returnList.append("type: {}".format(self.oidDict["type"]))
        if self.parent != None:
            returnList.append("parent path: {}".format(".".join(self.parent.rootPath([]))))
            if self.parent.oidDict != None:
                returnList.append("parent name: {}".format(self.parent.oidDict["name"]))
                returnList.append("parent type: {}".format(self.parent.oidDict["type"]))
        for child in self.childs:
            if child.oidDict != {}:
                returnList.append("child name: {}".format(child.oidDict["name"]))
        return "\n".join(returnList)

class bdsSnmpAdapter:
    def __init__(self,host="127.0.0.1",portDict={"confd":"2102","bgp.iod":"3102"}):
        self.host = host
        self.oidTree = oidTree()
        self.portDict = portDict


    def loadOidMappingFromYamlFile(self,yamlFile):
        with open(yamlFile, 'r') as stream:
            self.oidDict = yaml.load(stream)
        self.oidList = list(self.oidDict.keys())
        self.oidList.sort()
        for oid in self.oidList:
            oidDict = self.oidDict[oid]
            self.oidTree.addOid(oid,oidDict)


    def snmpGet(self,oid="",urlSuffix="/bds/object/get",indexWalk=False):
        logging.debug ("enter snmpGet {} ".format(oid))
        self.urlSuffix=urlSuffix
        oidDict,parentOidDict,snmpTableIndex = self.oidTree.getOidDictParentDictAndIndex(oid) ###FIXME ErrorCodes
        if oidDict:
            if "value" in oidDict.keys():
                returnValue = oidDict["value"]
                logging.info ("snmpGet {} returning {} for fixed value".format(oid,returnValue))
                print ({oid:returnValue})
                return {oid:returnValue}
            if oidDict["type"] == "snmpObject":
                bdsIndex = oidDict["key"]
                keyAttrName = oidDict["keyAttribute"]
                tableName = oidDict["table"]
                processName = oidDict["process"]
            if oidDict["type"] == "snmpTableObject":
                bdsIndex = eval(parentOidDict["snmpIndexToBdsIndex"])
                keyAttrName = parentOidDict["keyAttribute"]
                tableName = parentOidDict["table"]
                processName = parentOidDict["process"]
            requestData = {"table":{"table_name":tableName},"objects":[{"attribute":{ keyAttrName:bdsIndex}}]}
            url = 'http://'+self.host+":"+self.portDict[processName]+self.urlSuffix
            headers = {'Content-Type': 'application/json'} 
            logging.debug ("POST {} {}".format(url,json.dumps(requestData)))
            self.response = requests.post(url,
                    data=json.dumps(requestData),
                    headers= headers)
            logging.debug (self.response)
            if len(self.response.text) > 0:
                try:
                    responseJSON = json.loads(self.response.text)
                    responseString = json.dumps(responseJSON,indent=4)
                    logging.debug ("JSON response {}".format(responseJSON))
                    if 'object-not-found' in responseJSON[0].keys():
                        logging.warning ("negative REST API response {}!!!!".format(responseJSON))
                        return None
                    if oidDict["attribute"] in responseJSON[0]["attribute"].keys():
                        attributeValue = responseJSON[0]["attribute"][oidDict["attribute"]]
                        logging.debug ("value for attribute {} found in REST API response: {}".format(oidDict["attribute"],attributeValue ))
                        returnValue = attributeValue
                        if "valueMappingDict" in oidDict.keys():
                            if attributeValue in oidDict["valueMappingDict"].keys():
                                returnValue = oidDict["valueMappingDict"][attributeValue] 
                                logging.debug ("bdsValueToSnmpValue new value {}".format(returnValue))
                            else:
                                logging.warning ("{} {} mapping value missing for {}".format(oidDict["name"],
                                                                oid,
                                                                attributeValue))   
                        if snmpTableIndex:
                            logging.info ("snmpGet returning {} via REST API for oid {} index {}".format(returnValue,oid,snmpTableIndex))
                        else:
                            logging.info ("snmpGet returning {} via REST API for oid {}".format(returnValue,oid))
                        print ({oid:returnValue})
                        return {oid:returnValue}
                    else:
                        logging.warning ("oid {} value for attribute {} _NOT_ found in REST API response!!!!".format(oid,oidDict["attribute"]))
                        return None
                except ValueError:
                    responseString = self.response.text
                    logging.warning ("JSON parser error {}".format(responseString))
                    return None
            logging.warning ("JSON body missing in REST API response {} for oid{}".format(self.response,oid))
            return None


    def snmpWalk(self,baseOid="",urlSuffix="/bds/table/walk" ):
        logging.debug ("enter snmpWalk {} ".format(baseOid))
        oidWalkList = []
        for candiateOid in self.oidDict.keys():
            if candiateOid.startswith(baseOid) and self.oidDict[candiateOid]["type"] != "snmpTable":
                oidWalkList.append(candiateOid)
        def oidToInt(item):   
            return int("".join(item.split(".")))
        oidWalkList.sort(key=oidToInt)
        #print ( oidWalkList )
        for oid in oidWalkList:
            if self.oidDict[oid ]["type"] == "snmpObject":
                self.snmpGet(oid=oid)
#             elif self.oidDict[oid ]["type"] == "fixed":
#                 self.snmpGet(oid=oid)
            elif self.oidDict[oid ]["type"] == "snmpTableObject":
                #print (oid)
                oidDict,parentOidDict,snmpTableIndex = self.oidTree.getOidDictParentDictAndIndex(oid) ###FIXME ErrorCodes
                #snmpTableOid = oid.getParentTable(oid)
                #print (snmpTableOid)
                self.urlSuffix="/bds/table/walk"
                oidList = []
                tableName = parentOidDict["table"]
                requestData = {"table":{"table_name":tableName}}
                processName = parentOidDict["process"]
                url = 'http://'+self.host+":"+self.portDict[processName]+self.urlSuffix
                headers = {'Content-Type': 'application/json'} 
                logging.debug ("POST {} {}".format(url,json.dumps(requestData)))
                self.response = requests.post(url,
                        data=json.dumps(requestData),
                        headers= headers)
                logging.debug (self.response)
                if len(self.response.text) > 0:
                    try:
                        responseJSON = json.loads(self.response.text)
                        responseString = json.dumps(responseJSON,indent=4)
                        keyAttribute = parentOidDict["keyAttribute"]
                        for bdsObject in responseJSON['objects']:
                            #print (keyAttribute,bdsObject['attribute'].keys())
                            if keyAttribute in bdsObject['attribute'].keys():
                                keyValue =  bdsObject['attribute'][keyAttribute]
                                logging.debug ("suppressKeys {} keyValue {}".format(oid,keyValue))
                                if "suppressKeys" in parentOidDict.keys():
                                    if  keyValue in parentOidDict["suppressKeys"][keyAttribute]:              
                                        logging.debug("suppress {} keyValue {}".format(oid,keyValue))
                                    else:
                                        bdsIndex = bdsObject["attribute"][parentOidDict["keyAttribute"]]
                                        snmpTableIndex  = eval(parentOidDict["bdsIndexToSnmpIndex"])
                                        oidList.append(".".join([oid,snmpTableIndex]))
                        for thisOid in oidList:
                            self.snmpGet(oid=thisOid)                                 
                    except ValueError:
                        responseString = self.response.text
                        logging.warning ("JSON parser error {}".format(responseString))
                        return None

#logging.getLogger().setLevel(logging.DEBUG)
#logging.getLogger().setLevel(logging.INFO)
logging.getLogger().setLevel(logging.WARNING)
myBdsSnmpAdapter = bdsSnmpAdapter(host="10.0.3.110",portDict={"confd":"2002","bgp.iod":"3102","bgp.appd":"4102"})
myBdsSnmpAdapter.loadOidMappingFromYamlFile("snmpOidMapping.yml")
myBdsSnmpAdapter.oidTree.getOidDictParentDictAndIndex("1.3.6.1.15.3.1.1")
myBdsSnmpAdapter.oidTree.getOidDictParentDictAndIndex("1.3.6.1.15.3.1")
print("#"*60)
print("postive test cases for snmpGet")
print("#"*60)
myBdsSnmpAdapter.snmpGet(oid="1.3.6.1.15.1.0")
myBdsSnmpAdapter.snmpGet(oid="1.3.6.1.15.4.0")
myBdsSnmpAdapter.snmpGet(oid="1.3.6.1.15.3.1.1.20.10.10.1")
myBdsSnmpAdapter.snmpGet(oid="1.3.6.1.15.3.1.2.20.10.10.1")
myBdsSnmpAdapter.snmpGet(oid="1.3.6.1.15.3.1.7.20.10.10.1")
print("#"*60)
print("negative test cases for snmpGet")
print("#"*60)
myBdsSnmpAdapter.snmpGet(oid="1.3.6.1.16")
myBdsSnmpAdapter.snmpGet(oid="1.3.6.1.15.3.1.2.30.10.10.3")
print("#"*60)
print("postive test cases for snmpWalk")
print("#"*60)
myBdsSnmpAdapter.snmpWalk(baseOid="1.3.6.1.15")

