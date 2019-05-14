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
import os
import sys
import time

from pysnmp.entity.rfc3413 import cmdrsp
from pysnmp.proto.api import v2c
from pysnmp.smi import instrum

from bdssnmpadaptor import daemon
from bdssnmpadaptor import error
from bdssnmpadaptor import snmp_config
from bdssnmpadaptor.access import BdsAccess
from bdssnmpadaptor.config import loadBdsSnmpAdapterConfigFile
from bdssnmpadaptor.log import set_logging

# class Uptime:
#     birthday = time.time()
#     def __call__(self):
#         return (int(time.time()-self.birthday)*100)

BIRTHDAY = time.time()

OctetString = v2c.OctetString
Integer32 = v2c.Integer32
TimeTicks = v2c.TimeTicks
ObjectIdentifier = v2c.ObjectIdentifier
Counter32 = v2c.Counter32
Counter64 = v2c.Counter64
Gauge32 = v2c.Gauge32
Unsigned32 = v2c.Unsigned32
IpAddress = v2c.IpAddress


class MibInstrumController(instrum.AbstractMibInstrumController):
    # TODO: we probably need explicit SNMP type spec in YAML map
    SNMP_TYPE_MAP = {
        int: v2c.Integer32,
        str: v2c.OctetString,
        "pysnmp.proto.rfc1902.ObjectIdentifier": v2c.ObjectIdentifier
    }

    if sys.version_info[0] < 3:
        SNMP_TYPE_MAP[unicode] = v2c.OctetString

    def createVarbindFromOidDbItem(self, _oidDbItem):
        if _oidDbItem.value is None:
            return _oidDbItem.oid, v2c.NoSuchObject()

        if _oidDbItem.name in ["sysUptime", "hrSystemUptime"]:  # FIXME: add a function for realitime OIDs
            _oidDbItem.value = int((time.time() - BIRTHDAY) * 100)

        if _oidDbItem.name in ["snmpEngineTime"]:  # FIXME: add a function for realitime OIDs
            _oidDbItem.value = int((time.time() - BIRTHDAY))

        representation = (_oidDbItem.pysnmpRepresentation
                          if _oidDbItem.pysnmpRepresentation else 'value')

        returnValue = _oidDbItem.pysnmpBaseType(
            **{representation: _oidDbItem.value})

        self.moduleLogger.debug(
            f'createVarbindFromOidDbItem returning oid '
            f'{_oidDbItem.oid} with value {_oidDbItem.value}')

        return _oidDbItem.oid, returnValue

    def setOidDbAndLogger(self, _oidDb, cliArgsDict):
        self._oidDb = _oidDb

        self.moduleFileNameWithoutPy, _ = os.path.splitext(os.path.basename(__file__))

        configDict = loadBdsSnmpAdapterConfigFile(
            cliArgsDict["config"], self.moduleFileNameWithoutPy)

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.moduleLogger.debug(
            f'MibInstrumController set _oidDB: firstItem '
            f'{self._oidDb.firstItem}')

        return self

    def readVars(self, varBinds, *args, **kwargs):

        self.moduleLogger.info(f'GET request var-binds: {varBinds}')

        returnList = []

        for oid, value in varBinds:
            try:
                oidDbItemObj = self._oidDb.getObjFromOid(str(oid))

            except Exception as exc:
                self.moduleLogger.error(f'oidDb read failed for {oid}: {exc}')
                returnList.append((oid, v2c.NoSuchInstance()))
                continue

            self.moduleLogger.debug(
                f'oidDb GET returned {oidDbItemObj} for oid: {oid}')

            if oidDbItemObj is None:
                returnList.append((oid, v2c.NoSuchObject()))
                continue

            returnList.append(self.createVarbindFromOidDbItem(oidDbItemObj))

        self.moduleLogger.debug(
            f'GET response var-binds: {returnList}')

        return returnList

    def readNextVars(self, varBinds, *args, **kwargs):
        """ process get next request

        """
        self.moduleLogger.info(f'GETNEXT request var-binds: {varBinds}')

        returnList = []

        for oid, value in varBinds:
            nextOidString = self._oidDb.getNextOid(str(oid))

            self.moduleLogger.debug(
                f'request OID is {oid}, next OID is {nextOidString}')

            try:
                oidDbItemObj = self._oidDb.getObjFromOid(nextOidString)

            except Exception as exc:
                self.moduleLogger.error(f'oidDb read failed for {oid}: {exc}')
                returnList.append((oid, v2c.EndOfMibView()))
                continue

            self.moduleLogger.debug(
                f'oidDb GETNEXT returned {oidDbItemObj} for oid: {oid}')

            if oidDbItemObj is None:
                returnList.append((oid, v2c.EndOfMibView()))
                continue

            returnList.append(self.createVarbindFromOidDbItem(oidDbItemObj))

        self.moduleLogger.debug(
            f'GETNEXT response var-binds: {returnList}')

        return returnList


class SnmpCommandResponder(object):
    """SNMP Command Responder (AKA SNMP Agent) implementation.


    """

    def __init__(self, cliArgsDict):
        configDict = loadBdsSnmpAdapterConfigFile(
            cliArgsDict["config"], "responder")

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.moduleLogger.debug("configDict:{}".format(configDict))

        self.snmpEngine = snmp_config.getSnmpEngine(
            engineId=configDict.get('engineId'))

        engineBoots = snmp_config.setSnmpEngineBoots(
            self.snmpEngine, configDict.get('stateDir', '.'))

        self.listeningAddress = configDict["listeningIP"]
        self.listeningPort = configDict["listeningPort"]
        self.birthday = time.time()

        self.moduleLogger.info(
            'Running SNMP engine ID {}, boots {}'.format(
                self.snmpEngine.snmpEngineID.prettyPrint(), engineBoots))

        cliArgsDict["snmpEngineIdValue"] = self.snmpEngine.snmpEngineID.asOctets()

        self.bdsAccess = BdsAccess(cliArgsDict)  # Instantiation of the BDS Access Service

        self.oidDb = self.bdsAccess.getOidDb()

        # UDP over IPv4
        try:
            snmp_config.setSnmpTransport(
                self.snmpEngine, (self.listeningAddress, self.listeningPort))

        except Exception as exc:
            self.moduleLogger.error('SNMP transport error: {}'.format(exc))
            raise

        self.moduleLogger.info(
            'SnmpEngine UDPv4 listening on {} {}'.format(
                self.listeningAddress, self.listeningPort)
        )

        for snmpVersion, snmpConfigEntries in configDict.get(
                "versions", {}).items():

            snmpVersion = str(snmpVersion)

            if snmpVersion in ('1', '2c'):

                for security, snmpConfig in snmpConfigEntries.items():
                    community = snmpConfig["community"]

                    snmp_config.setCommunity(
                        self.snmpEngine, security, community, version=snmpVersion)

                    self.moduleLogger.info(
                        'Configuring SNMPv{} security name {}, community '
                        'name {}'.format(snmpVersion, security, community))

            elif snmpVersion == '3':

                for security, usmCreds in snmpConfigEntries.get('usmUsers', {}).items():
                    snmp_config.setUsmUser(
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

            else:
                raise error.BdsError('Unknown SNMP version {}'.format(snmpVersion))

        snmpContext = snmp_config.setMibController(
            self.snmpEngine,
            MibInstrumController().setOidDbAndLogger(self.oidDb, cliArgsDict))

        self.moduleLogger.info(
            'Configuring SNMP context name "{}"'.format(snmpContext))

        cmdrsp.GetCommandResponder(self.snmpEngine, snmpContext)
        cmdrsp.NextCommandResponder(self.snmpEngine, snmpContext)
        # cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)  ## TODO

        self.snmpEngine.transportDispatcher.jobStarted(1)

    async def run_forever(self):
        await asyncio.gather(
            self.bdsAccess.run_forever()
        )


def main():
    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(
        epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "-f", "--config",
        default="bdsSnmpRetrieveAdaptor.yml", type=str,
        help="Path to config file")
    parser.add_argument(
        '--daemonize', action='store_true',
        help="Fork and run as a background process")
    parser.add_argument(
        '--pidfile', type=str,
        help="Path to a PID file the process would create")

    cliargs = parser.parse_args()

    cliArgsDict = vars(cliargs)

    cliargs.config = os.path.abspath(cliargs.config)

    if cliargs.daemonize:
        daemon.daemonize()

    if cliargs.pidfile:
        daemon.pidfile(cliargs.pidfile)

    mySnmpFrontEnd = SnmpCommandResponder(cliArgsDict)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(mySnmpFrontEnd.run_forever())

    except KeyboardInterrupt:
        pass

    loop.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
