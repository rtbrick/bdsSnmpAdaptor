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
from pysnmp.proto.rfc1902 import OctetString, ObjectIdentifier, TimeTicks, Integer32
from pysnmp.proto.rfc1902 import Gauge32, Counter32
from bdsSnmpTables import ifTable
from oidDefintion import oidObj, oidListObj

                    

class bdsSnmpAdapter:
    def __init__(self,configFile=""):
        self.configFile = configFile
        try:
            with open(self.configFile, 'r') as stream:
                self.configDict = yaml.load(stream)
        except Exception as e:
            logging.error("cannot load config file: {}".format(e))
            raise
        else:
            #pprint.pprint(self.configDict)
            self.listeningAddress = self.configDict["config"]["snmp"]["listeningAddress"]
            self.listeningPort = self.configDict["config"]["snmp"]["listeningPort"]
            self.v2Community = self.configDict["config"]["snmp"]["community"]
            self.bdsAccess = self.configDict["config"]["bdsAccess"]
            try:
                oidYamlFile = self.configDict["config"]["snmp"]["oidMappingFile"]
                with open(oidYamlFile, 'r') as stream:
                    self.oidDict = yaml.load(stream)
            except Exception as e:
                logging.error("cannot load config file: {}".format(e))
                raise
            else:
                self.oidDict = ifTable.addTableEntry(self.oidDict,1)
                self.oidDict = ifTable.addTableEntry(self.oidDict,2)
                self.oidList = list(self.oidDict.keys())
                self.oidList = oidListObj.getSortedList(self.oidList)
                pprint.pprint(self.oidList)             ###temp
                #pprint.pprint(self.oidDict)             ###temp

    def snmpGet(self,oid=""):
        print ("snmpGet for oid {}".format(oid))
        if oid in self.oidList:
            logging.info ("snmpGet {} in Dict".format(oid))
            iodIndex = self.oidList.index(oid)
            oidDict = self.oidDict[oid]
            baseType = oidDict["pysnmpBaseType"]        #FIXME catch exception
            if "fixedValue" in oidDict.keys():
                evalString = "{}('{}')".format(oidDict["pysnmpBaseType"],oidDict["fixedValue"])
                logging.info("evalString {}('{}')".format(oidDict["pysnmpBaseType"],oidDict["fixedValue"]))
                returnValue = eval(evalString )             
                logging.info ("snmpGet {} returning {} for fixed value".format(oid,returnValue))
                #print ({oid:returnValue})
                return {oid:returnValue}  
            elif 'BDSrequest' in oidDict.keys():
                print (oidDict['BDSrequest'])
                bdsProcess = oidDict['BDSrequest'].split("::")[0]
                bdsHostIp = self.bdsAccess[bdsProcess]["host"]
                bdsHostPort = self.bdsAccess[bdsProcess]["port"]
                bdsSuffix = oidDict['BDSrequest'].split("::")[1]
                bdsTable = oidDict['BDSrequest'].split("::")[2]
                requestData = {"table":{"table_name":bdsTable}}
                url = "http://{}:{}{}".format(bdsHostIp,bdsHostPort,bdsSuffix)
                headers = {'Content-Type': 'application/json'} 
                logging.info ("POST {}".format(url))
                logging.debug ("POST {} {}".format(url,json.dumps(requestData)))
                self.response = requests.post(url,
                        data=json.dumps(requestData),
                        headers= headers)
                logging.debug (self.response)
                return {oid:v2c.NoSuchObject()} 
        else:
            logging.error ("snmpGet {} not in Dict".format(oid))   
            nextOid = self.oidList[0]
            oidDict = self.oidDict[nextOid]  
        return {oid:v2c.NoSuchObject()}  


    def getNextOid(self,oid=""):
        print ("getNextOid {}".format(oid))
        if oid in self.oidList:
            iodIndex = self.oidList.index(oid) 
            if iodIndex < len(self.oidList) - 1:
                nextOid = self.oidList[self.oidList.index(oid)+1]
                print ("getNextOid returns {}".format(nextOid))
                return nextOid
            else:
                nextOid = "1.3.6.1.3.92.1.1.1.0"
                print ("getNextOid returns {}".format(nextOid))
                return nextOid 
        elif self.oidList[0].startswith(oid):
                nextOid = self.oidList[0]
                print ("getNextOid returns {}".format(nextOid))
                return nextOid
        else:
            nextOid = "1.3.6.1.3.92.1.1.1.0"
            print ("getNextOid returns {}".format(nextOid))
            return nextOid




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
                    rspVarBinds.append((oid, value))
        return rspVarBinds

    def readNextVars(self, varBinds, acInfo=(None, None) ):
        logging.debug('SNMP request is GET-NEXT {}'.format(', '.join(str(x[0]) for x in varBinds)))
        try:
            bdsAdapter = self._bdsAdapter
        except AttributeError:
            logging.error('BDS adapter not initialized')
            return [(varBind[0], v2c.NoSuchObject()) for varBind in varBinds]
        rspVarBinds = []
        for oid, value in varBinds:
            nextOid = bdsAdapter.getNextOid(oid=str(oid))
        if nextOid != "1.3.6.1.3.92.1.1.1.0":
            try:
                valueDict = bdsAdapter.snmpGet(oid=str(nextOid))
            except Exception as exc:
                logging.error('BDS failure: {}'.format(exc))
                valueDict = None
                value = v2c.NoSuchObject()
                rspVarBinds.append((nextOid, value))
                return rspVarBinds
            else:
                if valueDict is None:
                    logging.error('BDS return None: {}')
                    value = v2c.NoSuchObject()
                else:
                    value = valueDict[str(nextOid)]
                rspVarBinds.append((nextOid, value))
                return rspVarBinds
        else:
            rspVarBinds.append((nextOid, v2c.Integer32(2) ))
            return rspVarBinds


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="SNMP Agent serving BDS data")

    parser.add_argument('--config',
                        metavar='<PATH>',
                        type=str,
                        default='bdsAdapterConfig.yml',
                        help='config file [bdsAdapterConfig.yml]')

    args = parser.parse_args()

    logging.getLogger().setLevel(logging.DEBUG)

    pprint.pprint(args.config)

    myBdsSnmpAdapter = bdsSnmpAdapter(configFile=args.config)

    snmpEngine = engine.SnmpEngine()

    # UDP over IPv4
    try:
        config.addTransport(
            snmpEngine,
            udp.domainName,
            udp.UdpTransport().openServerMode(( myBdsSnmpAdapter.listeningAddress ,
                                                myBdsSnmpAdapter.listeningPort ))
        )

    except Exception as exc:
        logging.error('SNMP transport error: {}'.format(exc))
        sys.exit(1)

    config.addV1System(snmpEngine, 'read-subtree', myBdsSnmpAdapter.v2Community)

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

    logging.debug('SNMP agent is running at {}:{}'.format(myBdsSnmpAdapter.listeningAddress, 
                                                             myBdsSnmpAdapter.listeningPort))

    snmpEngine.transportDispatcher.jobStarted(1)

    try:
        snmpEngine.transportDispatcher.runDispatcher()
    except:
        snmpEngine.transportDispatcher.closeDispatcher()
        raise
