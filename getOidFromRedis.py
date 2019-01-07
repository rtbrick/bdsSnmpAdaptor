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
#from bdsSnmpTables import bdsSnmpTables
#from oidDb import oidDb
#from bdsAccess import bdsAccess
import redis


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


class bdsSnmpAdapter:

    def __init__(self,cliArgsDict):
        self.redisServer = cliArgsDict["redisServer"]
        self.listeningAddress = cliArgsDict["listeningIP"]
        self.listeningPort = cliArgsDict["listeningPort"]
        self.snmpVersion = cliArgsDict["version"]
        if self.snmpVersion == "2c":
            self.community = cliArgsDict["community"]


    def snmpGet(self,oid=""):
        logging.debug('snmpGET {}'.format(oid))
        oidDict = self.redisServer.hgetall("oidHash-{}".format(oid))
        logging.debug('snmpGET found dict {}'.format(oidDict))
        if oidDict != {}:
            logging.info ("snmpGet {} found in oidDb with {}".format(oid,oidDict))
            baseType = oidDict["pysnmpBaseType"]      #FIXME catch exception
            if "value" in oidDict.keys():
                if "pysnmpRepresentation" in oidDict.keys():
                    evalString = "{}({}='{}')".format(baseType,
                                                      oidDict["pysnmpRepresentation"],
                                                      oidDict["value"])
                else:
                    evalString = "{}('{}')".format(baseType,
                                                      oidDict["value"])
                logging.debug("evalString {})".format(evalString))
                returnValue = eval(evalString )
                logging.info ("snmpGet {} returning {}".format(oid,returnValue))
                return {oid:returnValue}
            else:
                return {oid:v2c.NoSuchObject()}
        else:
            logging.error ("snmpGet {} not in redis DB".format(oid))
        return {oid:v2c.NoSuchObject()}

    def snmpGetForNext(self,oid=""):
        logging.debug('snmpGetForNext {}'.format(oid))
        oidDict = self.redisServer.hgetall("oidHash-{}".format(oid))
        #logging.debug('snmpGetForNext found oidDict {}'.format(oidDict))
        if oidDict != {}:
            logging.info ("snmpGetForNext {} found in oidDb with {}".format(oid,oidDict))
            baseType = oidDict["pysnmpBaseType"]      #FIXME catch exception
            if "value" in oidDict.keys():
                if "pysnmpRepresentation" in oidDict.keys():
                    evalString = "{}({}='{}')".format(baseType,
                                                      oidDict["pysnmpRepresentation"],
                                                      oidDict["value"])
                else:
                    evalString = "{}('{}')".format(baseType,
                                                      oidDict["value"])
                logging.debug("evalString {})".format(evalString))
                returnValue = eval(evalString )
                logging.info ("snmpGetForNext {} returning {}".format(oid,returnValue))
                return {oid:returnValue}
            else:
                return {oid:v2c.NoSuchObject()}
        else:
            logging.error ("snmpGetForNext {} not in redis DB".format(oid))
        return {oid:v2c.NoSuchObject()}

    def getOidsStringsForNextVars(self, oid="" ):
        logging.debug('getOidsStringsForNextVars for: {}'.format(oid))
        oidStartItem = oidDbItem(oid=oid)
        oidsItems = [ oidDbItem(oid=x[8:]) for x in list(self.redisServer.scan_iter("oidHash-*")) if oidDbItem(oid=x[8:]) > oidStartItem ]
        oidsItems.sort()
        oidsStrings = [ str(x) for x in oidsItems ]
        #logging.debug('oidsStrings: {}'.format(oidsStrings))
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

    parser = argparse.ArgumentParser(description="SNMP Agent serving BDS data")
    parser.add_argument('-s', '--listeningIP', default='0.0.0.0',
                        help='syslog listening IP address, default is 0.0.0.0', type=str)
    parser.add_argument('-p', '--listeningPort', default=161,
                        help='snmp get/getNext listening port, default is 161', type=int)
    parser.add_argument("-v","--version",  default='2c', type=str, choices=['2c', '3'],
                        help='specify snmp version')
    parser.add_argument("-c","--community",  default='public', type=str,
                        help='v2c community')
    parser.add_argument("-u","--usmUserTuples",  default='', type=str,
                        help='usmUserTuples engine,user,authkey,privkey list as comma separated string')
    parser.add_argument("--logging", choices=['debug', 'warning', 'info'],
                        default='warning', type=str,
                        help="Define logging level(debug=highest)")
    parser.add_argument('-m', '--mibs', default='',
                        help='mib list as comma separated string', type=str)
    parser.add_argument('--mibSources', default='',
                        help='mibSource list as comma separated string', type=str)
    parser.add_argument('--decode',action='store_true')
    parser.add_argument('--redisServerIp', default='127.0.0.1',
                        help='redis server IP address, default is 127.0.0.1', type=str)
    parser.add_argument('--redisServerPort', default=6379,
                        help='redis Server port, default is 6379', type=int)
    parser.add_argument('-e', '--expiryTimer', default=3,
                        help='redis key expiry timer setting', type=int)

    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    cliArgsDict["redisServer"] = redis.StrictRedis(host=cliArgsDict["redisServerIp"], port=cliArgsDict["redisServerPort"], db=0,decode_responses=True)
    print(cliArgsDict)
    logging.getLogger().setLevel(logging.DEBUG)       # FIXME set level from cliargs

    myBdsSnmpAdapter = bdsSnmpAdapter(cliArgsDict)

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
