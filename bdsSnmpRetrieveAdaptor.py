#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0

import sys
import os
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
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.smi import instrum
from pysnmp.proto.api import v2c
from pysnmp.proto.rfc1902 import OctetString, ObjectIdentifier, TimeTicks, Integer32
from pysnmp.proto.rfc1902 import Gauge32, Counter32, IpAddress
from bdsSnmpAdapterManager import loadBdsSnmpAdapterConfigFile
from bdsSnmpAdapterManager import set_logging
from bdsAccess import BdsAccess
from oidDb import OidDb
import time

class Uptime:
    birthday = time.time()
    def __call__(self):
        return (int(time.time()-self.birthday)*100)

BIRTHDAY = time.time()

class MibInstrumController(instrum.AbstractMibInstrumController):

    # TODO: we probably need explicit SNMP type spec in YAML map
    SNMP_TYPE_MAP = {
        int: v2c.Integer32,
        str: v2c.OctetString,
        "pysnmp.proto.rfc1902.ObjectIdentifier": v2c.ObjectIdentifier
    }

    if sys.version_info[0] < 3:
        SNMP_TYPE_MAP[unicode] = v2c.OctetString

    def createVarbindFromOidDbItem(self,_oidDbItem):
        baseType = _oidDbItem.pysnmpBaseType      #FIXME catch exception
        if _oidDbItem.value != None:
            if _oidDbItem.name == "sysUptime":
                x = Uptime()
                _oidDbItem.value = int((time.time()-BIRTHDAY)*100)
            if _oidDbItem.pysnmpRepresentation:
                evalString = "{}({}='{}')".format(_oidDbItem.pysnmpBaseType,
                                                  _oidDbItem.pysnmpRepresentation,
                                                  _oidDbItem.value)
            else:
                evalString = "{}('{}')".format(_oidDbItem.pysnmpBaseType,
                                               _oidDbItem.value)
            self.moduleLogger.debug("createVarbindFromOidDbItem evalString {})".format(evalString))
            returnValue = eval(evalString )
            self.moduleLogger.debug("createVarbindFromOidDbItem returning oid {} with value {} ".format(_oidDbItem.oid,returnValue))
            return (_oidDbItem.oid, returnValue)
        else:
            return (_oidDbItem.oid, v2c.NoSuchObject())

    def setOidDbAndLogger(self, _oidDb):
        self._oidDb = _oidDb
        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        configDict = loadBdsSnmpAdapterConfigFile(
            cliArgsDict["configFile"], self.moduleFileNameWithoutPy)
        set_logging(configDict, self.moduleFileNameWithoutPy, self)
        self.moduleLogger.debug(f"MibInstrumController set _oidDB: firstItem {self._oidDb.firstItem}")
        return self

    def readVars(self, varBinds, acInfo=(None, None)):
        collonSeparatedVarbindList = [ ', '.join(str(x[0]) for x in varBinds )]
        self.moduleLogger.debug(f'readVars: {collonSeparatedVarbindList}')
        print (f'readVars: {collonSeparatedVarbindList}')
        returnList = []
        for oid, value in varBinds:
            try:
                oidDbItemObj = self._oidDb.getObjFromOid(str(oid))

            except Exception as exc:
                print('oidDb failure: {}'.format(exc))
                valueDict = None                               # FIXME

            else:
                self.moduleLogger.debug(f'oidDb returned\n{oidDbItemObj}for oid: {oid}')
                if oidDbItemObj is None:
                    self.moduleLogger.warning(f'_oidDb return None for oid: {oid}')
                    #print (f'_oidDb return None for oid: {oid}')
                    returnList.append((oid,v2c.NoSuchObject()))
                else:
                    self.moduleLogger.debug(f'createVarbindFromOidDbItem with {oidDbItemObj.oid}')
                    returnList.append(self.createVarbindFromOidDbItem(oidDbItemObj))
        [ print(x) for x in returnList ]
        return returnList


    def readNextVars(self, varBinds, acInfo=(None, None)):
        """ process get next request

        """
        collonSeparatedVarbindList = [ ', '.join(str(x[0]) for x in varBinds )]
        print(f'readNextVars: {collonSeparatedVarbindList}')

        rspVarBinds = []
        oidStrings = []

        returnList = []
        for oid, value in varBinds:
            self.moduleLogger.debug('entry for-loop {},{} in varBinds'.format(oid, value))
            nextOidString = self._oidDb.getNextOid(str(oid))
            #print(f'nextOidString: {nextOidString}')
            try:
                oidDbItemObj = self._oidDb.getObjFromOid(nextOidString)
            except Exception as e:
                print('oidDb failure: {}'.format(e))
            else:
                #print(f'oidDb returned\n{oidDbItemObj}for oid: {nextOidString}')
                if oidDbItemObj is None:
                    #print('return [ ("0.0", v2c.EndOfMibView()) ]')
                    returnList.append( ("0.0", v2c.EndOfMibView()) )

                else:
                    #print(f'createVarbindFromOidDbItem with {oidDbItemObj.oid}')
                    returnList.append(self.createVarbindFromOidDbItem(oidDbItemObj))
        print (returnList)
        return returnList

class SnmpFrontEnd:
    """

    """

    def __init__(self,cliArgsDict):
        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        configDict = loadBdsSnmpAdapterConfigFile(
            cliArgsDict["configFile"], self.moduleFileNameWithoutPy)
        set_logging(configDict,self.moduleFileNameWithoutPy,self)
        self.moduleLogger.debug("configDict:{}".format(configDict))

        self.listeningAddress = configDict["listeningIP"]
        self.listeningPort = configDict["listeningPort"]
        self.snmpVersion = configDict["version"]
        self.birthday = time.time()
        self.snmpEngine = engine.SnmpEngine()
        self.bdsAccess = BdsAccess(cliArgsDict) # Instantiation of the BDS Access Service
        self.oidDb = self.bdsAccess.getOidDb()
        # UDP over IPv4
        try:
            config.addTransport(
                self.snmpEngine,
                udp.domainName,
                udp.UdpTransport().openServerMode(
                    (self.listeningAddress, self.listeningPort)
                )
            )
            print (
                  'SnmpEngine udp transport in server mode: {} {}'.format(
                     self.listeningAddress, self.listeningPort)
                  )

        except Exception as exc:
            logging.error('SNMP transport error: {}'.format(exc))
            raise

        else:
            snmpTransport = config.getTransport
            print ('SNMP engine transport: {}'.format(snmpTransport))

        if str(self.snmpVersion) == "2c":
            self.community = configDict["community"]
            config.addV1System(self.snmpEngine, 'read-subtree', self.community)
            # Allow full MIB access for this user / securityModels at VACM
            config.addVacmUser(self.snmpEngine, 2, 'read-subtree', 'noAuthNoPriv', (1, 3, 6))
            snmpContext = context.SnmpContext(self.snmpEngine)
            snmpContext.unregisterContextName(v2c.OctetString(''))
            snmpContext.registerContextName(
                v2c.OctetString(''),  # Context Name
                MibInstrumController().setOidDbAndLogger(self.oidDb)
            )
        elif str(self.snmpVersion) == "3":
            if "usmUsers" in configDict.keys():
                for usmUserDict in configDict["usmUsers"]:
                    userName = list(usmUserDict.keys())[0]
                    d = usmUserDict[userName]
                    if "authKey" in d.keys():
                        authKey = d["authKey"]
                        authProtocol = "SHA"
                        authProtocolObj = config.usmHMACSHAAuthProtocol
                        if "authProtocol" in d.keys():
                            authProtocol = d["authProtocol"]
                            if authProtocol == "MD5": authProtocolObj = config.usmHMACMD5AuthProtocol
                        if "privKey" in d.keys():
                            privKey = d["privKey"]
                            privProtocol = "AES"
                            privProtocolObj = config.usmAesCfb128Protocol
                            if "privProtocol" in d.keys():
                                privProtocol = d["privProtocol"]
                                if privProtocol == "DES": privProtocolObj = config.usmDESPrivProtocol
                            authString = "authPriv"
                        else:
                            privProtocol = None
                            privProtocolObj = config.usmNoPrivProtocol
                            privKey = None
                            authString = "authNoPriv"
                    else:
                        authProtocol = None
                        authProtocolObj = config.usmNoAuthProtocol
                        authKey = None
                        privProtocol = None
                        privProtocolObj = config.usmNoPrivProtocol
                        privKey = None
                        authString = "noAuthNoPriv"
                    print(f"addV3User:   self.snmpEngine, {userName} {authProtocolObj}:{authKey} {privProtocolObj}:{privKey}")
                    config.addV3User(
                        self.snmpEngine, userName,
                        authProtocolObj, authKey,
                        privProtocolObj, privKey)
                    config.addVacmUser(self.snmpEngine, 3, userName, authString, (1, 3, 6))
                    print(f"addVacmUser: self.snmpEngine, 3, {userName}, {authString}, (1, 3, 6)")
            else:
                raise Exception('snmp v3: missing usmUsers configuration in configfile!')
            #https://github.com/openstack/virtualpdu/blob/master/virtualpdu/pdu/pysnmp_handler.py
            snmpContext = context.SnmpContext(self.snmpEngine)
            snmpContext.unregisterContextName(v2c.OctetString(''))
            snmpContext.registerContextName(
                v2c.OctetString(''),  # Context Name
                MibInstrumController().setOidDbAndLogger(self.oidDb)
            )
        else:
            raise Exception('incorrect snmp version string, just "2c" and "3" are supported')
        cmdrsp.GetCommandResponder(self.snmpEngine, snmpContext)
        cmdrsp.NextCommandResponder(self.snmpEngine, snmpContext)
        #cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)  ## TODO

        self.snmpEngine.transportDispatcher.jobStarted(1)

    async def run_forever(self):
        await asyncio.gather(
            self.bdsAccess.run_forever()
        )


if __name__ == "__main__":

    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(
        epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-f", "--configFile",
                        default="bdsSnmpRetrieveAdaptor.yml", type=str,
                        help="config file")

    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)

    mySnmpFrontEnd = SnmpFrontEnd(cliArgsDict)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(mySnmpFrontEnd.run_forever())

    except KeyboardInterrupt:
        pass

    loop.close()
