#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  \author    Stefan Lieberth / Maik Pfeil
#  \version   3.3.01

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
import aioredis
from bdsSnmpAdapterManager import loadBdsSnmpAdapterConfigFile
from bdsSnmpAdapterManager import set_logging
from pysnmp.proto.rfc1902 import OctetString, ObjectIdentifier, TimeTicks, Integer32
from pysnmp.proto.rfc1902 import Gauge32, Counter32, IpAddress
import asyncio
from pysnmp.hlapi.asyncio import *

RTBRICKSYSLOGTRAP = "1.3.6.1.4.1.50058.103.1.1"
SYSLOGMSGNUMBER   = "1.3.6.1.4.1.50058.102.1.1.0"
SYSLOGMSGFACILITY = "1.3.6.1.4.1.50058.102.1.1.2.0"
SYSLOGMSGSEVERITY = "1.3.6.1.4.1.50058.102.1.1.3.0"
SYSLOGMSGTEXT     = "1.3.6.1.4.1.50058.102.1.1.4.0"

class asyncioTrapGenerator():

    def __init__(self,cliArgsDict):
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
        self.snmpTrapServer = configDict["snmpTrapServer"]
        self.snmpTrapPort = configDict["snmpTrapPort"]
        self.trapCounter = 0
        self.snmpEngine = SnmpEngine()

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
            CommunityData(self.community, mpModel=0),
            UdpTransportTarget((self.snmpTrapServer, self.snmpTrapPort)),
            ContextData(),
            'trap',
            NotificationType(
                ObjectIdentity(RTBRICKSYSLOGTRAP)
            ).addVarBinds(
                ('1.3.6.1.6.3.1.1.4.3.0',RTBRICKSYSLOGTRAP),
                (SYSLOGMSGNUMBER, Integer32(self.trapCounter)),
                (SYSLOGMSGFACILITY, OctetString(syslogMsgFacility)),
                (SYSLOGMSGSEVERITY, Integer32(syslogMsgSeverity)),
                (SYSLOGMSGTEXT, OctetString(syslogMsgText))
            )
        )
        if errorIndication:
            print(errorIndication)

    async def closeSnmpEngine(self):            
        self.snmpEngine.transportDispatcher.closeDispatcher()


class restHttpServer():


    def __init__(self,cliArgsDict):


        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],self.moduleFileNameWithoutPy)
        set_logging(configDict,self.moduleFileNameWithoutPy,self)
        self.listeningIP =  configDict["listeningIP"]
        self.listeningPort = configDict["listeningPort"]
        self.requestCounter = 0
        self.snmpTrapGenerator = asyncioTrapGenerator(cliArgsDict)


    async def handler(self,request):

        """| Coroutine that accepts a Request instance as its only argument.
           | Returnes 200 with a copy of the incoming header dict.

        """
        peerIP = request._transport_peername[0]
        self.requestCounter += 1
        self.moduleLogger.info ("handler: peerIP:{} headers:{} counter:{} ".format(peerIP,request.headers,self.requestCounter))
        data = {'headers': dict(request.headers)}
        jsonTxt = await request.text() #
        try:
            bdsLogDict = json.loads(jsonTxt)
        except Exception as e:
            self.moduleLogger.error ("connot convert json to dict:{} {}".format(jsonTxt,e))
        else:
            await self.snmpTrapGenerator.sendTrap(bdsLogDict)
        return web.json_response(data)


    async def run_forever(self):

        """| starts the aiohttp Web Server
           | runs then in an infinite loop which stores every second a status K/V dataset in redis

        """
        server = web.Server(self.handler)
        runner = web.ServerRunner(server)
        await runner.setup()
        site = web.TCPSite(runner, self.listeningIP , self.listeningPort )
        await site.start()
        while True:
            await asyncio.sleep(1)
            print ("restServer Running - sent traps: {}".format(self.requestCounter))


if __name__ == "__main__":
    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--configFile",
                            default="./bdsLoggingToSnmpNotification.yml", type=str,
                            help="config file")
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    myRestHttpServer = restHttpServer(cliArgsDict)
    #mySnmpTrapGenerator = asyncioTrapGenerator(cliArgsDict)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(myRestHttpServer.run_forever())
    except KeyboardInterrupt:
        pass
    loop.close()
