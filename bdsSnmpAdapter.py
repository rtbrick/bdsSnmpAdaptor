#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import logging
import argparse
import yaml
import pprint
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.smi import instrum
from pysnmp.proto.api import v2c
from pysnmp.proto.rfc1902 import OctetString, ObjectIdentifier, TimeTicks

                    
                       
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
        self.portDict = portDict


    def loadOidMappingFromYamlFile(self,yamlFile):
        with open(yamlFile, 'r') as stream:
            self.oidDict = yaml.load(stream)
        self.oidList = list(self.oidDict.keys())
        self.oidList.sort()
        pprint.pprint(self.oidList)             ###temp
        pprint.pprint(self.oidDict)             ###temp

    def snmpGet(self,oid=""):
        print ("snmpGet for oid {}".format(oid))
        if oid in self.oidList:
            logging.info ("snmpGet {} in Dict".format(oid))
            iodIndex = self.oidList.index(oid)
            oidDict = self.oidDict[oid]
        else:
            logging.error ("snmpGet {} not in Dict".format(oid))   
            nextOid = self.oidList[0]
            oidDict = self.oidDict[nextOid]
        if "fixedValue" in oidDict.keys():
            baseType = oidDict["pysnmpBaseType"]
            evalString = "{}('{}')".format(oidDict["pysnmpBaseType"],oidDict["fixedValue"])
            logging.info("evalString {}('{}')".format(oidDict["pysnmpBaseType"],oidDict["fixedValue"]))
            returnValue = eval(evalString )             
            logging.info ("snmpGet {} returning {} for fixed value".format(oid,returnValue))
            #print ({oid:returnValue})
            return {oid:returnValue}    
        return None

    def snmpNext(self,oid=""):
        print ("snmpGetNext {}".format(oid))
        if oid in self.oidList:
            iodIndex = self.oidList.index(oid) 
            if iodIndex < len(self.oidList) - 1:
                nextOid = self.oidList[self.oidList.index(oid)+1]
                returnDict = self.snmpGet(nextOid)
                print (returnDict)
                return self.snmpGet(nextOid)
            else:
                nextOid = None
                return None
        return None



class MibInstrumController(instrum.AbstractMibInstrumController):

    # TODO: we probably need explicit SNMP type spec in YAML map
    SNMP_TYPE_MAP = {
        int: v2c.Integer32,
        str: v2c.OctetString,
        "pysnmp.proto.rfc1902.ObjectIdentifier": v2c.ObjectIdentifier
    }

    if sys.version_info[0] < 3:
        SNMP_TYPE_MAP[unicode] = v2c.OctetString

    def setBdsAdapter(self, bdsAdapter):
        logging.debug ("setBdsAdapter: {}".format(bdsAdapter)) ###Temp
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
        print ("MibInstrumController varBinds {}".format(varBinds))
        for oid, value in varBinds:
            try:
                valueDict = bdsAdapter.snmpGet(oid=str(oid))
            except Exception as exc:
                logging.error('BDS failure: {}'.format(exc))
                valueDict = None
            else:
                if valueDict is None:
                    logging.error('BDS return None: {}')
                    value = v2c.NoSuchObject()
                else:
                    value = valueDict[str(oid)]
                    #logging.debug ("value: {} class {} type: {}".format(value,value.__class__,type(value))) ###Temp
                    rspVarBinds.append((oid, value))
                    #logging.debug('SNMP response is {}'.format(', '.join(['{}={}'.format(*x) for x in rspVarBinds])))
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
    cmdrsp.NextCommandResponder(snmpEngine, snmpContext)

    logging.debug('SNMP agent is running at {}:{}'.format(args.snmp_agent_ipv4_address, args.snmp_agent_udp_port))

    snmpEngine.transportDispatcher.jobStarted(1)

    try:
        snmpEngine.transportDispatcher.runDispatcher()
    except:
        snmpEngine.transportDispatcher.closeDispatcher()
        raise
