#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import argparse
import asyncio
import json
import os
import sys
import time

from aiohttp import web
from pysnmp.entity.rfc3413 import ntforg
from pysnmp.proto.rfc1902 import Integer32
from pysnmp.proto.rfc1902 import ObjectIdentifier
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.proto.rfc1902 import TimeTicks
from pysnmp.proto.rfc1902 import Unsigned32

from bdssnmpadaptor import daemon
from bdssnmpadaptor import error
from bdssnmpadaptor import snmp_config
from bdssnmpadaptor.config import loadBdsSnmpAdapterConfigFile
from bdssnmpadaptor.log import set_logging

RTBRICKSYSLOGTRAP = "1.3.6.1.4.1.50058.103.1.1"
SYSLOGMSG = "1.3.6.1.4.1.50058.104.2.1.0"
SYSLOGMSGNUMBER = "1.3.6.1.4.1.50058.104.2.1.1.0"
SYSLOGMSGFACILITY = "1.3.6.1.4.1.50058.104.2.1.2.0"
SYSLOGMSGSEVERITY = "1.3.6.1.4.1.50058.104.2.1.3.0"
SYSLOGMSGTEXT = "1.3.6.1.4.1.50058.104.2.1.4.0"


class AsyncioTrapGenerator(object):

    TARGETS_TAG = 'mgrs'

    def __init__(self, cliArgsDict, restHttpServerObj):
        configDict = loadBdsSnmpAdapterConfigFile(
            cliArgsDict["config"], "notificator")

        self.moduleLogger = set_logging(configDict, "notificator", self)

        self.moduleLogger.info("original configDict: {}".format(configDict))

        # temp lines for graylog client end #
        # configDict["usmUserDataMatrix"] = [ usmUserTuple.strip().split(",")
        # for usmUserTuple in configDict["usmUserTuples"].split(';') if len(usmUserTuple) > 0 ]
        # self.moduleLogger.debug("configDict['usmUserDataMatrix']: {}".format(configDict["usmUserDataMatrix"]))
        # configDict["usmUsers"] = []
        self.moduleLogger.info("modified configDict: {}".format(configDict))

        self.snmpEngine = snmp_config.getSnmpEngine(
            engineId=configDict.get('engineId'))

        engineBoots = snmp_config.setSnmpEngineBoots(
            self.snmpEngine, configDict.get('stateDir', '.'))

        snmp_config.setSnmpTransport(self.snmpEngine)

        self.targets = snmp_config.setTrapTargets(self.snmpEngine, self.TARGETS_TAG)

        authEntries = {}

        for snmpVersion, snmpConfigEntries in configDict.get(
                "versions", {}).items():

            snmpVersion = str(snmpVersion)

            if snmpVersion in ('1', '2c'):

                for security, snmpConfig in snmpConfigEntries.items():

                    community = snmpConfig["community"]

                    authLevel = snmp_config.setCommunity(
                        self.snmpEngine, security, community, version=snmpVersion, tag=self.TARGETS_TAG)

                    self.moduleLogger.info(
                        'Configuring SNMPv{} security name {}, community '
                        'name {}'.format(snmpVersion, security, community))

                    authEntries[security] = snmpVersion, authLevel

            elif snmpVersion == '3':

                for security, usmCreds in snmpConfigEntries.get('usmUsers', {}).items():

                    authLevel = snmp_config.setUsmUser(
                        self.snmpEngine, security,
                        usmCreds.get('user'),
                        usmCreds.get('authKey'), usmCreds.get('authProtocol'),
                        usmCreds.get('privKey'), usmCreds.get('privProtocol'))

                    self.moduleLogger.info(
                        'Configuring SNMPv3 USM security {}, user {}, auth {}/{},'
                        ' priv {}/{}'.format(
                            security,
                            usmCreds.get('user'),
                            usmCreds.get('authKey'), usmCreds.get('authProtocol'),
                            usmCreds.get('privKey'), usmCreds.get('privProtocol')))

                    authEntries[security] = snmpVersion, authLevel

            else:
                raise error.BdsError('Unknown SNMP version {}'.format(snmpVersion))

            self.birthday = time.time()

        for targetName, targetConfig in configDict.get('snmpTrapTargets', {}).items():

            address, port = targetConfig['address'], int(targetConfig.get('port', 162))
            security = targetConfig['security-name']

            snmp_config.setTrapTarget(
                self.snmpEngine, security, (address, port), self.TARGETS_TAG)

            snmpVersion, authLevel = authEntries[security]

            snmp_config.setTrapVersion(
                self.snmpEngine, security, authLevel, snmpVersion)

            self.moduleLogger.info(
                'Configuring target {}:{} using security '
                'name {}'.format(address, port, security))

        self.ntfOrg = ntforg.NotificationOriginator()

        self.trapCounter = 0

        self.restHttpServerObj = restHttpServerObj

        self.moduleLogger.info('Running SNMP engine ID {}, boots {}'.format(
            self.snmpEngine, engineBoots))

    async def sendTrap(self, bdsLogDict):
        self.moduleLogger.debug(
            "sendTrap bdsLogDict: {}".format(bdsLogDict))

        self.trapCounter += 1

        try:
            syslogMsgFacility = bdsLogDict["host"]

        except Exception as e:
            self.moduleLogger.error(
                "cannot set syslogMsgFacility from bdsLogDict: "
                "{}".format(bdsLogDict, e))
            syslogMsgFacility = "error"

        try:
            syslogMsgSeverity = bdsLogDict["level"]

        except Exception as e:
            self.moduleLogger.error(
                "cannot set syslogMsgSeverity from bdsLogDict: "
                "{}".format(bdsLogDict, e))
            syslogMsgSeverity = 0

        try:
            syslogMsgText = bdsLogDict["short_message"]

        except Exception as e:
            self.moduleLogger.error(
                "connot set syslogMsgText from bdsLogDict: "
                "{}".format(bdsLogDict, e))

            syslogMsgText = "error"

        self.moduleLogger.debug(
            "data sendTrap {} {} {} {}".format(
                self.trapCounter, syslogMsgFacility,
                syslogMsgSeverity, syslogMsgText))

        def cbFun(snmpEngine, sendRequestHandle, errorIndication,
                  errorStatus, errorIndex, varBinds, cbCtx):
            if errorIndication:
                self.moduleLogger.error(
                    'notification {} failed: {}'.format(sendRequestHandle, errorIndication))

            else:
                self.moduleLogger.error(
                    'notification {} succeeded'.format(sendRequestHandle))

        uptime = int((time.time() - self.birthday) * 100)

        varBinds = [
            (ObjectIdentifier('1.3.6.1.2.1.1.3.0'), TimeTicks(uptime)),
            (ObjectIdentifier('1.3.6.1.6.3.1.1.4.1.0'), ObjectIdentifier(RTBRICKSYSLOGTRAP)),
            (ObjectIdentifier(SYSLOGMSGNUMBER), Unsigned32(self.trapCounter)),
            (ObjectIdentifier(SYSLOGMSGFACILITY), OctetString(syslogMsgFacility)),
            (ObjectIdentifier(SYSLOGMSGSEVERITY), Integer32(syslogMsgSeverity)),
            (ObjectIdentifier(SYSLOGMSGTEXT), OctetString(syslogMsgText))
        ]

        sendRequestHandle = self.ntfOrg.sendVarBinds(
            self.snmpEngine,
            # Notification targets
            self.targets,
            None, '',  # contextEngineId, contextName
            varBinds,
            cbFun
        )

        self.moduleLogger.debug(
            'notification {} submitted'.format(sendRequestHandle or ''))

    async def run_forever(self):

        while True:
            await asyncio.sleep(0.001)

            if self.restHttpServerObj.bdsLogsToBeProcessedList:

                bdsLogToBeProcessed = self.restHttpServerObj.bdsLogsToBeProcessedList.pop(0)

                self.moduleLogger.debug("bdsLogToBeProcessed: {}".format(bdsLogToBeProcessed))

                await self.sendTrap(bdsLogToBeProcessed)

    async def closeSnmpEngine(self):
        self.snmpEngine.transportDispatcher.closeDispatcher()


class AsyncioRestServer(object):

    def __init__(self, cliArgsDict):

        self.moduleFileNameWithoutPy, _ = os.path.splitext(os.path.basename(__file__))

        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["config"], "notificator")

        self.moduleLogger = set_logging(configDict, "notificator", self)

        self.listeningIP = configDict["listeningIP"]
        self.listeningPort = configDict["listeningPort"]

        self.requestCounter = 0

        self.bdsLogsToBeProcessedList = []
        self.snmpTrapGenerator = AsyncioTrapGenerator(cliArgsDict, self)

    async def handler(self, request):

        """| Coroutine that accepts a Request instance as its only argument.
           | Returnes 200 with a copy of the incoming header dict.

        """
        peerIP = request._transport_peername[0]

        self.requestCounter += 1

        self.moduleLogger.info(
            "handler: incoming request peerIP:{}".format(
                peerIP, request.headers, self.requestCounter))
        # self.moduleLogger.debug ("handler: peerIP:{} headers:{} counter:{}
        # ".format(peerIP,request.headers,self.requestCounter))

        data = {
            'headers': dict(request.headers)
        }

        jsonTxt = await request.text()  #

        try:
            bdsLogDict = json.loads(jsonTxt)

        except Exception as e:
            self.moduleLogger.error(
                "connot convert json to dict:{} {}".format(jsonTxt, e))

        else:
            self.bdsLogsToBeProcessedList.append(bdsLogDict)
            # await self.snmpTrapGenerator.sendTrap(bdsLogDict)

        return web.json_response(data)

    async def backgroundLogging(self):
        while True:
            self.moduleLogger.debug(
                "restServer Running - process list length: {}".format(
                    len(self.bdsLogsToBeProcessedList)))
            await asyncio.sleep(1)

    async def run_forever(self):
        server = web.Server(self.handler)
        runner = web.ServerRunner(server)

        await runner.setup()

        site = web.TCPSite(runner, self.listeningIP, self.listeningPort)

        await site.start()

        await asyncio.gather(
            self.snmpTrapGenerator.run_forever(),
            self.backgroundLogging()
        )


def main():
    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(
        epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "-f", "--config", default="bdsSnmpTrapAdaptor.yml", type=str,
        help="config file")
    parser.add_argument(
        '--daemonize', action='store_true',
        help="Fork and run as a background process")
    parser.add_argument(
        '--pidfile', type=str,
        help="Path to a PID file the process would create")

    cliargs = parser.parse_args()

    cliargs.config = os.path.abspath(cliargs.config)

    if cliargs.daemonize:
        daemon.daemonize()

    if cliargs.pidfile:
        daemon.pidfile(cliargs.pidfile)

    cliArgsDict = vars(cliargs)

    myRestHttpServer = AsyncioRestServer(cliArgsDict)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(myRestHttpServer.run_forever())

    except KeyboardInterrupt:
        pass

    loop.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
