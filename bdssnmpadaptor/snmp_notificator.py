# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import time

from pysnmp.entity.rfc3413 import ntforg
from pysnmp.proto.rfc1902 import Integer32
from pysnmp.proto.rfc1902 import ObjectIdentifier
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.proto.rfc1902 import TimeTicks
from pysnmp.proto.rfc1902 import Unsigned32

from bdssnmpadaptor import error
from bdssnmpadaptor import snmp_config
from bdssnmpadaptor.config import loadConfig
from bdssnmpadaptor.log import set_logging

RTBRICKSYSLOGTRAP = '1.3.6.1.4.1.50058.103.1.1'
SYSLOGMSG = '1.3.6.1.4.1.50058.104.2.1.0'
SYSLOGMSGNUMBER = '1.3.6.1.4.1.50058.104.2.1.1.0'
SYSLOGMSGFACILITY = '1.3.6.1.4.1.50058.104.2.1.2.0'
SYSLOGMSGSEVERITY = '1.3.6.1.4.1.50058.104.2.1.3.0'
SYSLOGMSGTEXT = '1.3.6.1.4.1.50058.104.2.1.4.0'


class SnmpNotificationOriginator(object):

    TARGETS_TAG = 'mgrs'

    def __init__(self, cliArgsDict, queue):
        configDict = loadConfig(cliArgsDict['config'])

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.moduleLogger.info(f'original configDict: {configDict}')

        self.queue = queue

        # temp lines for graylog client end #
        # configDict['usmUserDataMatrix'] = [ usmUserTuple.strip().split(',')
        # for usmUserTuple in configDict['usmUserTuples'].split(';') if len(usmUserTuple) > 0 ]
        # self.moduleLogger.debug('configDict['usmUserDataMatrix']: {}'.format(configDict['usmUserDataMatrix']))
        # configDict['usmUsers'] = []
        self.moduleLogger.info(f'modified configDict: {configDict}')

        self.snmpEngine = snmp_config.getSnmpEngine(
            engineId=configDict['snmp'].get('engineId'))

        engineBoots = snmp_config.setSnmpEngineBoots(
            self.snmpEngine, configDict.get('stateDir', '.'))

        snmp_config.setSnmpTransport(self.snmpEngine)

        self.targets = snmp_config.setTrapTypeForTag(self.snmpEngine, self.TARGETS_TAG)

        authEntries = {}

        for snmpVersion, snmpConfigEntries in configDict['snmp'].get(
                'versions', {}).items():

            snmpVersion = str(snmpVersion)

            if snmpVersion in ('1', '2c'):

                for security, snmpConfig in snmpConfigEntries.items():

                    community = snmpConfig['community']

                    authLevel = snmp_config.setCommunity(
                        self.snmpEngine, security, community, version=snmpVersion, tag=self.TARGETS_TAG)

                    self.moduleLogger.info(
                        f'Configuring SNMPv{snmpVersion} security name '
                        f'{security}, community name {community}')

                    authEntries[security] = snmpVersion, authLevel

            elif snmpVersion == '3':

                for security, usmCreds in snmpConfigEntries.get('usmUsers', {}).items():

                    authLevel = snmp_config.setUsmUser(
                        self.snmpEngine, security,
                        usmCreds.get('user'),
                        usmCreds.get('authKey'), usmCreds.get('authProtocol'),
                        usmCreds.get('privKey'), usmCreds.get('privProtocol'))

                    self.moduleLogger.info(
                        f'Configuring SNMPv3 USM security {security}, user '
                        f'{usmCreds.get("user")}, '
                        f'auth {usmCreds.get("authKey")}/{usmCreds.get("authProtocol")}, '
                        f'priv {usmCreds.get("privKey")}/{usmCreds.get("privProtocol")}')

                    authEntries[security] = snmpVersion, authLevel

            else:
                raise error.BdsError(f'Unknown SNMP version {snmpVersion}')

            self.birthday = time.time()

        for targetName, targetConfig in configDict['notificator'].get(
                'snmpTrapTargets', {}).items():

            address, port = targetConfig['address'], int(targetConfig.get('port', 162))
            security = targetConfig['security-name']

            snmp_config.setTrapTargetAddress(
                self.snmpEngine, security, (address, port), self.TARGETS_TAG)

            snmpVersion, authLevel = authEntries[security]

            snmp_config.setTrapVersion(
                self.snmpEngine, security, authLevel, snmpVersion)

            self.moduleLogger.info(
                f'Configuring target {address}:{port} using security '
                f'name {security}')

        self.ntfOrg = ntforg.NotificationOriginator()

        self.trapCounter = 0

        self.moduleLogger.info(
            f'Running SNMP engine ID {self.snmpEngine}, boots {engineBoots}')

    async def sendTrap(self, bdsLogDict):
        self.moduleLogger.info(f'sendTrap bdsLogDict: {bdsLogDict}')

        self.trapCounter += 1

        try:
            syslogMsgFacility = bdsLogDict['host']

        except KeyError:
            self.moduleLogger.error(
                f'cannot get syslog facility from {bdsLogDict}')
            syslogMsgFacility = 'error'

        try:
            syslogMsgSeverity = bdsLogDict['level']

        except KeyError:
            self.moduleLogger.error(
                f'cannot get syslog severity from {bdsLogDict}')
            syslogMsgSeverity = 0

        try:
            syslogMsgText = bdsLogDict['short_message']

        except KeyError:
            self.moduleLogger.error(
                f'cannot get syslog message text from bdsLogDict '
                f'{bdsLogDict}')

            syslogMsgText = 'error'

        self.moduleLogger.info(
            f'data sendTrap {self.trapCounter} {syslogMsgFacility} '
            f'{syslogMsgSeverity} {syslogMsgText}')

        def cbFun(snmpEngine, sendRequestHandle, errorIndication,
                  errorStatus, errorIndex, varBinds, cbCtx):
            if errorIndication:
                self.moduleLogger.error(
                    f'notification {sendRequestHandle} failed: '
                    f'{errorIndication}')

            else:
                self.moduleLogger.error(
                    f'notification {sendRequestHandle} succeeded')

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

        self.moduleLogger.info(
            f'notification {sendRequestHandle or ""} submitted')

    async def run_forever(self):

        while True:
            bdsLogToBeProcessed = await self.queue.get()

            self.moduleLogger.info(f'new log record: {bdsLogToBeProcessed}')

            try:
                await self.sendTrap(bdsLogToBeProcessed)

            except Exception as exc:
                self.moduleLogger.error(f'TRAP not sent: {exc}')

