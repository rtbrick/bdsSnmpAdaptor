#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0

import asyncio
import logging
from logging.handlers import RotatingFileHandler
import yaml
from copy import deepcopy
import pprint
import re
import datetime
import json
import sys
import argparse
from aiohttp import web
from aiohttp.web import Application, Response, StreamResponse, run_app
from bdsSnmpAdapterManager import loadBdsSnmpAdapterConfigFile
from bdsSnmpAdapterManager import set_logging

from pysnmp.proto.rfc1902 import OctetString, ObjectIdentifier, TimeTicks, Integer32
from pysnmp.proto.rfc1902 import Gauge32, Counter32, IpAddress, Unsigned32

#from pysnmp.entity.rfc3413.oneliner.ntforg import NotificationOriginator
#pprint.pprint(NotificationOriginator.__dict__)

from pysnmp.smi import builder, view, compiler, rfc1902

import asyncio
from pysnmp.hlapi.asyncio import SnmpEngine,CommunityData
from pysnmp.hlapi.asyncio import UdpTransportTarget,ContextData
from pysnmp.hlapi.asyncio import NotificationType,ObjectIdentity
from pysnmp.hlapi.asyncio import sendNotification


RTBRICKSYSLOGTRAP = "1.3.6.1.4.1.50058.103.1.1"
SYSLOGMSG         = "1.3.6.1.4.1.50058.102.1.1.0"
SYSLOGMSGNUMBER   = "1.3.6.1.4.1.50058.102.1.1.1.0"
SYSLOGMSGFACILITY = "1.3.6.1.4.1.50058.102.1.1.2.0"
SYSLOGMSGSEVERITY = "1.3.6.1.4.1.50058.102.1.1.3.0"
SYSLOGMSGTEXT     = "1.3.6.1.4.1.50058.102.1.1.4.0"

class asyncioTrapGenerator():

    def __init__(self,cliArgsDict,restHttpServerObj):
        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],self.moduleFileNameWithoutPy)
        set_logging(configDict,self.moduleFileNameWithoutPy,self)
        self.moduleLogger.info("original configDict: {}".format(configDict))
        #configDict["usmUserDataMatrix"] = [ usmUserTuple.strip().split(",") for usmUserTuple in configDict["usmUserTuples"].split(';') if len(usmUserTuple) > 0 ]
        #self.moduleLogger.debug("configDict['usmUserDataMatrix']: {}".format(configDict["usmUserDataMatrix"]))
        #configDict["usmUsers"] = []
        self.moduleLogger.info("modified configDict: {}".format(configDict))
        self.snmpVersion = configDict["version"]
        if self.snmpVersion == "2c":
            self.community = configDict["community"]
            self.moduleLogger.info("SNMP version {} community {}".format(self.snmpVersion,self.community))
            #config.addV1System(self.snmpEngine, 'my-area', self.community )
        elif self.snmpVersion == "3":
            usmUserDataMatrix = [ usmUserTuple.strip().split(",") for usmUserTuple in configDict["usmUserTuples"].split(';') if len(usmUserTuple) > 0 ]
        self.snmpTrapTargets = configDict["snmpTrapTargets"]
        self.snmpTrapPort = configDict["snmpTrapPort"]
        self.trapCounter = 0
        self.snmpEngine = SnmpEngine()
        self.restHttpServerObj = restHttpServerObj

    async def sendTrap(self,bdsLogDict):
        self.moduleLogger.debug ("sendTrap bdsLogDict: {}".format(bdsLogDict))
        self.trapCounter += 1
        try:
            syslogMsgFacility = bdsLogDict["host"]
        except Exception as e:
            self.moduleLogger.error ("connot set syslogMsgFacility from bdsLogDict: {}".format(bdsLogDict,e))
            syslogMsgFacility = "error"
        try:
            syslogMsgSeverity = bdsLogDict["level"]
        except Exception as e:
            self.moduleLogger.error ("connot set syslogMsgSeverity from bdsLogDict: {}".format(bdsLogDict,e))
            syslogMsgSeverity = 0
        try:
            syslogMsgText = bdsLogDict["full_message"]
        except Exception as e:
            self.moduleLogger.error ("connot set syslogMsgText from bdsLogDict: {}".format(bdsLogDict,e))
            syslogMsgText = "error"
        self.moduleLogger.debug ("data sendTrap {} {} {} {}".format(self.trapCounter,
                    syslogMsgFacility,
                    syslogMsgSeverity,
                    syslogMsgText))


        errorIndication, errorStatus, errorIndex, varBinds = await sendNotification(
            self.snmpEngine,
            CommunityData(self.community, mpModel=1),    # mpModel defines version
            UdpTransportTarget((self.snmpTrapServer, self.snmpTrapPort)),
            ContextData(),
            'trap',
            NotificationType(
                ObjectIdentity(RTBRICKSYSLOGTRAP)
            ).addVarBinds(
                #('1.3.6.1.6.3.1.1.4.3.0',RTBRICKSYSLOGTRAP),
                (SYSLOGMSGNUMBER, Unsigned32(self.trapCounter)),
                (SYSLOGMSGFACILITY, OctetString(syslogMsgFacility)),
                (SYSLOGMSGSEVERITY, Integer32(syslogMsgSeverity)),
                (SYSLOGMSGTEXT, OctetString(syslogMsgText))
            )
        )
        if errorIndication:
            self.moduleLogger.error (errorIndication)

    async def run_forever(self):

        while True:
            await asyncio.sleep(0.001)
            if len (self.restHttpServerObj.bdsLogsToBeProcessedList) > 0:
                bdsLogToBeProcessed = self.restHttpServerObj.bdsLogsToBeProcessedList.pop(0)
                self.moduleLogger.debug ("bdsLogToBeProcessed: {}".format(bdsLogToBeProcessed))
                await self.sendTrap(bdsLogToBeProcessed)


    async def closeSnmpEngine(self):
        self.snmpEngine.transportDispatcher.closeDispatcher()


class asyncioRestServer():


    def __init__(self,cliArgsDict):


        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],self.moduleFileNameWithoutPy)
        set_logging(configDict,self.moduleFileNameWithoutPy,self)
        self.listeningIP =  configDict["listeningIP"]
        self.listeningPort = configDict["listeningPort"]
        self.requestCounter = 0
        self.bdsLogsToBeProcessedList = []
        self.snmpTrapGenerator = asyncioTrapGenerator(cliArgsDict,self)


    async def handler(self,request):

        """| Coroutine that accepts a Request instance as its only argument.
           | Returnes 200 with a copy of the incoming header dict.

        """
        peerIP = request._transport_peername[0]
        self.requestCounter += 1
        self.moduleLogger.info ("handler: incoming request peerIP:{}".format(peerIP,request.headers,self.requestCounter))
        print ("handler: incoming request peerIP:{}".format(peerIP,request.headers,self.requestCounter))
        #self.moduleLogger.debug ("handler: peerIP:{} headers:{} counter:{} ".format(peerIP,request.headers,self.requestCounter))
        data = {'headers': dict(request.headers)}
        jsonTxt = await request.text() #
        try:
            bdsLogDict = json.loads(jsonTxt)
            print(f"bdsLogDict {bdsLogDict}")
        except Exception as e:
            self.moduleLogger.error ("connot convert json to dict:{} {}".format(jsonTxt,e))
        else:
            self.bdsLogsToBeProcessedList.append(bdsLogDict)
            #await self.snmpTrapGenerator.sendTrap(bdsLogDict)
        return web.json_response(data)


    async def backgroundLogging (self):
        while True:
            self.moduleLogger.debug ("restServer Running - process list length: {}".format(len(self.bdsLogsToBeProcessedList)))
            await asyncio.sleep(1)

    async def run_forever(self):
        server = web.Server(self.handler)
        runner = web.ServerRunner(server)
        await runner.setup()
        site = web.TCPSite(runner, self.listeningIP , self.listeningPort )
        await site.start()
        await asyncio.gather(
            self.snmpTrapGenerator.run_forever(),
            self.backgroundLogging()
            )

if __name__ == "__main__":
    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--configFile",
                            default="./bdsSnmpTrapAdaptor.yml", type=str,
                            help="config file")
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    myRestHttpServer = asyncioRestServer(cliArgsDict)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(myRestHttpServer.run_forever())
    except KeyboardInterrupt:
        pass
    loop.close()
