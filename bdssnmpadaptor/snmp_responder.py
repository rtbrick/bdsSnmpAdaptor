# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import time

from pysnmp.entity.rfc3413 import cmdrsp

from bdssnmpadaptor import error
from bdssnmpadaptor import snmp_config
from bdssnmpadaptor.config import loadConfig
from bdssnmpadaptor.log import set_logging


class SnmpCommandResponder(object):
    """SNMP Command Responder.

    Listens for incoming SNMP commands within asyncio loop,
    calls MIB instrumentation controller to retrieve requested
    management information and responds back to SNMP manager.

    Args:
        args (object): argparse namespace object holding command-line options
        mibController (object): MIB controller object to fetch requested
            managed objects from
    """

    def __init__(self, args, mibController):
        self.mibController = mibController

        configDict = loadConfig(args.config)

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.moduleLogger.debug(f'configDict:{configDict}')

        self.snmpEngine = snmp_config.getSnmpEngine(
            engineId=configDict['snmp'].get('engineId'))

        engineBoots = snmp_config.setSnmpEngineBoots(
            self.snmpEngine, configDict.get('stateDir', '.'))

        self.listeningAddress = configDict['responder']['listeningIP']
        self.listeningPort = configDict['responder']['listeningPort']
        self.birthday = time.time()

        self.moduleLogger.info(
            f'Running SNMP engine ID {self.snmpEngine.snmpEngineID.prettyPrint()}, '
            f'boots {engineBoots}')

        # UDP over IPv4
        try:
            snmp_config.setSnmpTransport(
                self.snmpEngine, (self.listeningAddress, self.listeningPort))

        except Exception as exc:
            self.moduleLogger.error(f'SNMP transport error: {exc}')
            raise

        self.moduleLogger.info(
            f'SnmpEngine UDPv4 listening on {self.listeningAddress} '
            f'{self.listeningPort}')

        for snmpVersion, snmpConfigEntries in configDict['snmp'].get(
                'versions', {}).items():

            snmpVersion = str(snmpVersion)

            if snmpVersion in ('1', '2c'):

                for security, snmpConfig in snmpConfigEntries.items():
                    community = snmpConfig['community']

                    snmp_config.setCommunity(
                        self.snmpEngine, security, community, version=snmpVersion)

                    self.moduleLogger.info(
                        f'Configuring SNMPv{snmpVersion} security name '
                        f'{security}, community name {community}')

            elif snmpVersion == '3':

                for security, usmCreds in snmpConfigEntries.get('usmUsers', {}).items():
                    snmp_config.setUsmUser(
                        self.snmpEngine, security,
                        usmCreds.get('user'),
                        usmCreds.get('authKey'), usmCreds.get('authProtocol'),
                        usmCreds.get('privKey'), usmCreds.get('privProtocol'))

                    self.moduleLogger.info(
                        f'Configuring SNMPv3 USM security {security}, user '
                        f'{usmCreds.get("user")}, '
                        f'auth {usmCreds.get("authKey")}/{usmCreds.get("authProtocol")}, '
                        f'priv {usmCreds.get("privKey")}/{usmCreds.get("privProtocol")}')

            else:
                raise error.BdsError('Unknown SNMP version {snmpVersion}')

        snmpContext = snmp_config.setMibController(
            self.snmpEngine, mibController)

        self.moduleLogger.info(
            f'Configuring SNMP context name "{snmpContext}"')

        cmdrsp.GetCommandResponder(self.snmpEngine, snmpContext)
        cmdrsp.NextCommandResponder(self.snmpEngine, snmpContext)
        cmdrsp.BulkCommandResponder(self.snmpEngine, snmpContext)

        self.snmpEngine.transportDispatcher.jobStarted(1)
