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
from pysnmp.proto.rfc1902 import Gauge32, Counter32, IpAddress
from bdsSnmpTables import bdsSnmpTables
from oidDb import oidDb
from bdsAccess import bdsAccess

                    

class bdsSnmpAdapter:
    def __init__(self,configFile=""):
        self.oidDb = oidDb()
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
                self.bdsSnmpTablesObj = bdsSnmpTables()
                self.bdsSnmpTablesObj.globalInterfaceContainer(self.oidDb,self.bdsAccess)    #FIXME make this dynamic/recurring
                self.bdsSnmpTablesObj.defaultInterfaceLogical(self.oidDb,self.bdsAccess)    #FIXME make this dynamic/recurring
                self.bdsSnmpTablesObj.globalInterfaceAddressConfig(self.oidDb,self.bdsAccess)    #FIXME make this dynamic/recurring
                self.bdsSnmpTablesObj.defaultFwdNeighborIpv4(self.oidDb,self.bdsAccess)    #FIXME make this dynamic/recurring
                self.bdsSnmpTablesObj.localSystemSoftwareInfoConfd(self.oidDb,self.bdsAccess)    #FIXME make this dynamic/recurring
            print ( self.oidDb )


    def snmpGet(self,oid=""):
        
        oidObj = self.oidDb.getObjFromOid(oid)
        
        if oidObj:
            logging.info ("snmpGet {} in oidDb".format(oid))
            logging.debug ("oidDb: {}".format(oidObj))
            #iodIndex = self.oidList.index(oid)
            #oidDict = self.oidDict[oid]
            baseType = oidObj.pysnmpBaseType      #FIXME catch exception
            if oidObj.fixedValue != None:
                if oidObj.pysnmpRepresentation:
                    evalString = "{}({}='{}')".format(oidObj.pysnmpBaseType,
                                                      oidObj.pysnmpRepresentation,
                                                      oidObj.fixedValue)
                else:
                    evalString = "{}('{}')".format(oidObj.pysnmpBaseType,oidObj.fixedValue)  
                logging.debug("evalString {})".format(evalString))
                returnValue = eval(evalString )             
                logging.info ("snmpGet {} returning {} for fixed value".format(oid,returnValue))
                return {oid:returnValue}  
            else:
                return {oid:v2c.NoSuchObject()} 
        else:
            logging.error ("snmpGet {} not in Dict".format(oid))   
            nextOid = self.oidList[0]
            oidDict = self.oidDict[nextOid]  
        return {oid:v2c.NoSuchObject()}  


    def getNextOid(self,oid=""):
        logging.debug("getNextOid {})".format(self.oidDb.getNextOid(oid)))
        return self.oidDb.getNextOid(oid)

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

    #pprint.pprint(args.config)

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
