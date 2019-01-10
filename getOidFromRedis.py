#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import logging
from logging.handlers import RotatingFileHandler
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
#from bdsSnmpTables import bdsSnmpTables
#from oidDb import oidDb
#from bdsAccess import bdsAccess
import redis
from bdsSnmpAdapterManager import loadBdsSnmpAdapterConfigFile

class oidDbItem():

    def __init__(self,oid=None):
        self.oid = oid
        self.oidAsList = [ int(x) for x in self.oid.split(".")]   #for compare


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
        elif isinstance(oid2,oidDbItem):
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
        return self.oid


class getOidFromRedis:

    def set_logging(self,configDict):
        logging.root.handlers = []
        self.moduleLogger = logging.getLogger('getOidFromRedis')
        logFile = configDict['rotatingLogFile'] + "getOidFromRedis.log"
        #
        #logging.basicConfig(filename=logFile, filemode='w', level=logging.DEBUG)
        rotateHandler = RotatingFileHandler(logFile, maxBytes=1000000,backupCount=2)  #1M rotating log
        formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
        rotateHandler.setFormatter(formatter)
        logging.getLogger("").addHandler(rotateHandler)
        #
        self.loggingLevel = configDict['loggingLevel']
        if self.loggingLevel in ["debug", "info", "warning"]:
            if self.loggingLevel == "debug": logging.getLogger().setLevel(logging.DEBUG)
            if self.loggingLevel == "info": logging.getLogger().setLevel(logging.INFO)
            if self.loggingLevel == "warning": logging.getLogger().setLevel(logging.WARNING)
        self.moduleLogger.info("self.loggingLevel: {}".format(self.loggingLevel))

    def __init__(self,cliArgsDict):
        self.moduleLogger = logging.getLogger('bdsAccessToRedis')
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],"getOidFromRedis")
        self.set_logging(configDict)
        self.moduleLogger.debug("configDict:{}".format(configDict))
        self.redisServer = redis.StrictRedis(host=configDict["redisServerIp"], port=configDict["redisServerPort"], db=0,decode_responses=True)
        #self.redisServer = configDict["redisServer"]
        self.listeningAddress = configDict["listeningIP"]
        self.listeningPort = configDict["listeningPort"]
        self.snmpVersion = configDict["version"]
        if self.snmpVersion == "2c":
            self.community = configDict["community"]


    def snmpGet(self,oid=""):
        self.moduleLogger.debug('snmpGET {}'.format(oid))
        oidDict = self.redisServer.hgetall("oidHash-{}".format(oid))
        self.moduleLogger.debug('snmpGET found dict {}'.format(oidDict))
        if oidDict != {}:
            self.moduleLogger.info ("snmpGet {} found in oidDb with {}".format(oid,oidDict))
            baseType = oidDict["pysnmpBaseType"]      #FIXME catch exception
            if "value" in oidDict.keys():
                if "pysnmpRepresentation" in oidDict.keys():
                    evalString = "{}({}='{}')".format(baseType,
                                                      oidDict["pysnmpRepresentation"],
                                                      oidDict["value"])
                else:
                    evalString = "{}('{}')".format(baseType,
                                                      oidDict["value"])
                self.moduleLogger.debug("evalString {})".format(evalString))
                returnValue = eval(evalString )
                self.moduleLogger.info ("snmpGet {} returning {}".format(oid,returnValue))
                return {oid:returnValue}
            else:
                return {oid:v2c.NoSuchObject()}
        else:
            self.moduleLogger.error ("snmpGet {} not in redis DB".format(oid))
        return {oid:v2c.NoSuchObject()}

    def snmpGetForNext(self,oid=""):
        self.moduleLogger.debug('snmpGetForNext {}'.format(oid))
        oidDict = self.redisServer.hgetall("oidHash-{}".format(oid))
        #self.moduleLogger.debug('snmpGetForNext found oidDict {}'.format(oidDict))
        if oidDict != {}:
            self.moduleLogger.info ("snmpGetForNext {} found in oidDb with {}".format(oid,oidDict))
            baseType = oidDict["pysnmpBaseType"]      #FIXME catch exception
            if "value" in oidDict.keys():
                if "pysnmpRepresentation" in oidDict.keys():
                    evalString = "{}({}='{}')".format(baseType,
                                                      oidDict["pysnmpRepresentation"],
                                                      oidDict["value"])
                else:
                    evalString = "{}('{}')".format(baseType,
                                                      oidDict["value"])
                self.moduleLogger.debug("evalString {})".format(evalString))
                returnValue = eval(evalString )
                self.moduleLogger.info ("snmpGetForNext {} returning {}".format(oid,returnValue))
                return {oid:returnValue}
            else:
                return {oid:v2c.NoSuchObject()}
        else:
            self.moduleLogger.error ("snmpGetForNext {} not in redis DB".format(oid))
        return {oid:v2c.NoSuchObject()}

    def getOidsStringsForNextVars(self, oid="" ):
        self.moduleLogger.debug('getOidsStringsForNextVars for: {}'.format(oid))
        oidStartItem = oidDbItem(oid=oid)
        oidsItems = [ oidDbItem(oid=x[8:]) for x in list(self.redisServer.scan_iter("oidHash-*")) if oidDbItem(oid=x[8:]) > oidStartItem ]
        oidsItems.sort()
        oidsStrings = [ str(x) for x in oidsItems ]
        #self.moduleLogger.debug('oidsStrings: {}'.format(oidsStrings))
        return oidsStrings

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
        logging.debug ("MibInstrumController setBdsAdapter: {}".format(bdsAdapter)) ###Temp
        self._bdsAdapter = bdsAdapter
        return self

    def readVars(self, varBinds, acInfo=(None, None)):
        logging.debug('SNMP request is GET {}'.format(', '.join(str(x[0]) for x in varBinds)))
        try:
            bdsAdapter = self._bdsAdapter
        except AttributeError:
            logging.error('readVars BDS adapter not initialized')
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
            logging.error('readNextVars BDS adapter not initialized')
            return [(varBind[0], v2c.NoSuchObject()) for varBind in varBinds]   #CHECK
        rspVarBinds = []
        oidStrings = []
        for oid, value in varBinds:
            logging.debug('for {},{} in varBinds'.format(oid, value))
            oidStrings = bdsAdapter.getOidsStringsForNextVars(oid=str(oid))
        if len(oidStrings) > 0:
            nextOid = oidStrings[0]
            try:
                valueDict = bdsAdapter.snmpGetForNext(oid=str(nextOid))
            except Exception as exc:
                logging.error('BDS failure: {}'.format(exc))
                valueDict = None
            else:
                if valueDict is None:
                    logging.error('BDS return None: {}')
                    value = v2c.NoSuchObject()
                else:
                    value = valueDict[str(nextOid)]
                    rspVarBinds.append((nextOid, value))
                    logging.debug('rspVarBinds.append {} {}'.format(nextOid, value))
                    return rspVarBinds
        else:
            value = v2c.EndOfMibView()
            rspVarBinds.append(("0.0", value))     #FIXME use endOfMib Constant
            return rspVarBinds




if __name__ == '__main__':

    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--configFile",
                            default="/etc/bdsSnmpAdapterConfig.yml", type=str,
                            help="config file")

    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)

    myBdsSnmpAdapter = getOidFromRedis(cliArgsDict)

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

    config.addV1System(snmpEngine, 'read-subtree', myBdsSnmpAdapter.community)

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
