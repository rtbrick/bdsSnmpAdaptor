#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import logging
import argparse
import yaml
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.smi import instrum
from pysnmp.proto.api import v2c

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


class MibInstrumController(instrum.AbstractMibInstrumController):

    # TODO: we probably need explicit SNMP type spec in YAML map
    SNMP_TYPE_MAP = {
        int: v2c.Integer32,
        str: v2c.OctetString,
    }

    if sys.version_info[0] < 3:
        SNMP_TYPE_MAP[unicode] = v2c.OctetString

    def setBdsAdapter(self, bdsAdapter):
        self._bdsAdapter = bdsAdapter
        return self

    def readVars(self, varBinds, acInfo=(None, None)):
        logging.debug('SNMP request is GET {}'.format(', '.join(str(x[0]) for x in varBinds)))

        try:
            bdsAdapter = self._bdsAdapter

        except AttributeError:
            logging.error('BDS adapter not initialized')
            return [(varBind[0], v2c.NoSuchObject()) for varBind in varBinds]

        rspVarBinds = []

        for oid, value in varBinds:
            try:
                valueDict = bdsAdapter.snmpGet(oid=str(oid))

            except Exception as exc:
                logging.error('BDS failure: {}'.format(exc))
                valueDict = None

            if valueDict is None:
                value = v2c.NoSuchObject()
            else:
                value = valueDict[str(oid)]

                try:
                    value = self.SNMP_TYPE_MAP[value.__class__](value)

                except KeyError:
                    logging.error('unmapped BDS type {}'.format(value.__class__.__name__))
                    value = v2c.NoSuchObject()

            rspVarBinds.append((oid, value))

        logging.debug('SNMP response is {}'.format(', '.join(['{}={}'.format(*x) for x in rspVarBinds])))

        return rspVarBinds


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="SNMP Agent serving BDS data")

    parser.add_argument('--bds-host',
                        metavar='<IPv4>',
                        type=str,
                        required=True,
                        help='hostname/address of the BDS REST API service')

    parser.add_argument('--bds-map',
                        metavar='<PATH>',
                        type=str,
                        default='snmpOidMapping.yml',
                        help='SNMP to BDS objects map file [snmpOidMapping.yml]')

    parser.add_argument('--snmp-agent-ipv4-address',
                        metavar='IPv4',
                        type=str,
                        default='0.0.0.0',
                        help='SNMP agent listens at this address [0.0.0.0]')

    parser.add_argument('--snmp-agent-udp-port',
                        metavar='<INT>',
                        type=int,
                        default=161,
                        help='SNMP agent listens at this UDP port [161]')

    parser.add_argument('--snmp-community-name',
                        metavar='<STRING>',
                        type=str,
                        default='public',
                        help='SNMP agent responds to this community name [public]')

    args = parser.parse_args()

    logging.getLogger().setLevel(logging.DEBUG)

    myBdsSnmpAdapter = bdsSnmpAdapter(host=args.bds_host, #"10.0.3.110",
                                      portDict={"confd":"2002","bgp.iod":"3102"})
    myBdsSnmpAdapter.loadOidMappingFromYamlFile(args.bds_map)

    snmpEngine = engine.SnmpEngine()

    # UDP over IPv4
    try:
        config.addTransport(
            snmpEngine,
            udp.domainName,
            udp.UdpTransport().openServerMode((args.snmp_agent_ipv4_address,
                                               args.snmp_agent_udp_port))
        )

    except Exception as exc:
        logging.error('SNMP transport error: {}'.format(exc))
        sys.exit(1)

    config.addV1System(snmpEngine, 'read-subtree', args.snmp_community_name)

    # Allow full MIB access for this user / securityModels at VACM
    config.addVacmUser(snmpEngine, 2, 'read-subtree', 'noAuthNoPriv', (1, 3, 6))

    snmpContext = context.SnmpContext(snmpEngine)

    snmpContext.unregisterContextName(v2c.OctetString(''))

    snmpContext.registerContextName(
        v2c.OctetString(''),  # Context Name
        MibInstrumController().setBdsAdapter(myBdsSnmpAdapter)
    )

    cmdrsp.GetCommandResponder(snmpEngine, snmpContext)

    logging.debug('SNMP agent is running at {}:{}'.format(args.snmp_agent_ipv4_address, args.snmp_agent_udp_port))

    snmpEngine.transportDispatcher.jobStarted(1)

    try:
        snmpEngine.transportDispatcher.runDispatcher()
    except:
        snmpEngine.transportDispatcher.closeDispatcher()
        raise
