#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import asyncio
import time
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
from bdsSnmpAdapterManager import loadBdsSnmpAdapterConfigFile
from bdsSnmpAdapterManager import set_logging




class snmpBackEnd:


    def __init__(self,cliArgsDict):
        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],self.moduleFileNameWithoutPy)
        set_logging(configDict,self.moduleFileNameWithoutPy,self)


    def snmpGet(self,oid=""):
        self.moduleLogger.debug('snmpGET {}'.format(oid))
        return {oid:v2c.NoSuchObject()}
        self.moduleLogger.debug('snmpGET {}'.format(oid))
    def snmpGetForNext(self,oid=""):

        return {oid:v2c.NoSuchObject()}

    def getOidsStringsForNextVars(self, oid="" ):
        return []

class MibInstrumController(instrum.AbstractMibInstrumController):

    # TODO: we probably need explicit SNMP type spec in YAML map
    SNMP_TYPE_MAP = {
        int: v2c.Integer32,
        str: v2c.OctetString,
        "pysnmp.proto.rfc1902.ObjectIdentifier": v2c.ObjectIdentifier
    }

    if sys.version_info[0] < 3:
        SNMP_TYPE_MAP[unicode] = v2c.OctetString

    def setSnmpBackEnd(self, _snmpBackEnd):
        logging.debug ("MibInstrumController snmpBackEnd: {}".format(snmpBackEnd)) ###Temp
        self._snmpBackEnd = _snmpBackEnd
        return self

    def readVars(self, varBinds, acInfo=(None, None)):
        logging.debug('SNMP request is GET {}'.format(', '.join(str(x[0]) for x in varBinds)))
        try:
            _snmpBackEnd = self._snmpBackEnd   #FIXME
        except AttributeError:
            logging.error('readVars _snmpBackEnd not initialized')
            return [(varBind[0], v2c.NoSuchObject()) for varBind in varBinds]
        rspVarBinds = []
        for oid, value in varBinds:
            try:
                valueDict = _snmpBackEnd.snmpGet(oid=str(oid))
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
            _snmpBackEnd = self._snmpBackEnd
        except AttributeError:
            logging.error('readNextVars _snmpBackEnd not initialized')
            return [(varBind[0], v2c.NoSuchObject()) for varBind in varBinds]   #CHECK
        rspVarBinds = []
        oidStrings = []
        for oid, value in varBinds:
            logging.debug('for {},{} in varBinds'.format(oid, value))
            oidStrings = _snmpBackEnd.getOidsStringsForNextVars(oid=str(oid))
        if len(oidStrings) > 0:
            nextOid = oidStrings[0]
            try:
                valueDict = _snmpBackEnd.snmpGetForNext(oid=str(nextOid))
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


class snmpFrontEnd:


    def __init__(self,cliArgsDict):

        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],self.moduleFileNameWithoutPy)
        set_logging(configDict,self.moduleFileNameWithoutPy,self)
        self.moduleLogger.debug("configDict:{}".format(configDict))
        #
        self.listeningAddress = configDict["listeningIP"]
        self.listeningPort = configDict["listeningPort"]
        self.snmpVersion = configDict["version"]
        if self.snmpVersion == "2c":
            self.community = configDict["community"]
        self.snmpBackEnd = snmpBackEnd(cliArgsDict)
        self.snmpEngine = engine.SnmpEngine()
        # UDP over IPv4
        try:
            config.addTransport(
                self.snmpEngine,
                udp.domainName,
                udp.UdpTransport().openServerMode(( self.listeningAddress ,
                                                    self.listeningPort ))
            )
        except Exception as exc:
            logging.error('SNMP transport error: {}'.format(exc))
            sys.exit(1)
        config.addV1System(self.snmpEngine, 'read-subtree', self.community)
        # Allow full MIB access for this user / securityModels at VACM
        config.addVacmUser(self.snmpEngine, 2, 'read-subtree', 'noAuthNoPriv', (1, 3, 6))
        snmpContext = context.SnmpContext(self.snmpEngine)
        snmpContext.unregisterContextName(v2c.OctetString(''))
        snmpContext.registerContextName(
            v2c.OctetString(''),  # Context Name
            MibInstrumController().setSnmpBackEnd(self.snmpBackEnd)
        )
        cmdrsp.GetCommandResponder(self.snmpEngine, snmpContext)
        cmdrsp.NextCommandResponder(self.snmpEngine, snmpContext)
        self.snmpEngine.transportDispatcher.jobStarted(1)

    async def runSnmpFrontEnd(self):
        logging.debug('SNMP agent is running at {}:{}'.format(self.listeningAddress,
                                                        self.listeningPort))
        print('SNMP agent is running at {}:{}'.format(self.listeningAddress,
                                                        self.listeningPort))
        try:
            await self.snmpEngine.transportDispatcher.runDispatcher() #FIXME ME, Blocking task
        except:
            self.snmpEngine.transportDispatcher.closeDispatcher()
            raise

    async def backgroundMessages (self):
        while True:
            print ("background message: {}".format(time.time()))
            await asyncio.sleep(1)


    async def run_forever(self):
        await asyncio.gather(
            self.runSnmpFrontEnd(),     #FIXME ME, Blocking task
            self.backgroundMessages(),
            self.backgroundMessages()
            )


if __name__ == "__main__":

    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--configFile",
                            default="./asyncioTestConfig.yml", type=str,
                            help="config file")

    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)

    mySnmpFrontEnd = snmpFrontEnd(cliArgsDict)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(mySnmpFrontEnd.run_forever())
    except KeyboardInterrupt:
        pass
    loop.close()
