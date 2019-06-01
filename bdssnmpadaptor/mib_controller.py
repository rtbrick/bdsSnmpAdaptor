# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import os
import time

from pysnmp.proto.api import v2c
from pysnmp.smi import instrum

from bdssnmpadaptor.config import loadConfig
from bdssnmpadaptor.log import set_logging

BIRTHDAY = time.time()


class MibInstrumController(instrum.AbstractMibInstrumController):
    """MIB instrumentation controller.

    Implements SNMP agent interface to OID DB in form of MIB
    instrumentation controller complying to pysnmp API.
    """
    # TODO: we probably need explicit SNMP type spec in YAML map
    SNMP_TYPE_MAP = {
        int: v2c.Integer32,
        str: v2c.OctetString,
        'pysnmp.proto.rfc1902.ObjectIdentifier': v2c.ObjectIdentifier
    }

    def createVarbindFromOidDbItem(self, _oidDbItem):
        if _oidDbItem.value is None:
            return _oidDbItem.oid, v2c.NoSuchObject()

        if _oidDbItem.name in ['sysUpTime', 'hrSystemUptime']:  # FIXME: add a function for realitime OIDs
            _oidDbItem.value = _oidDbItem.value.clone(int((time.time() - BIRTHDAY) * 100))

        if _oidDbItem.name in ['snmpEngineTime']:  # FIXME: add a function for realitime OIDs
            _oidDbItem.value = _oidDbItem.value.clone(int((time.time() - BIRTHDAY)))

        self.moduleLogger.debug(
            f'createVarbindFromOidDbItem returning oid '
            f'{_oidDbItem.oid} with value {_oidDbItem.value}')

        return _oidDbItem.oid, _oidDbItem.value

    def setOidDbAndLogger(self, _oidDb, cliArgsDict):
        self._oidDb = _oidDb

        self.moduleFileNameWithoutPy, _ = os.path.splitext(os.path.basename(__file__))

        configDict = loadConfig(cliArgsDict['config'])

        self.moduleLogger = set_logging(configDict, __class__.__name__)

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
