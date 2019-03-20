# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import os
import tempfile

from pysnmp.hlapi.asyncio import SnmpEngine
from pysnmp.proto.rfc1902 import OctetString


def getSnmpEngine(engineId=None):
    if engineId:
        engineId = engineId.replace(':', '')

        if engineId.startswith('0x') or engineId.startswith('0X'):
            engineId = engineId[2:]

        engineId = OctetString(hexValue=engineId)

    return SnmpEngine(snmpEngineID=engineId)


def setSnmpEngineBoots(snmpEngine, stateDir):
    """Read, update and set SnmpEngineBoots counter to SNMP Engine

    Note
    ----
    Make sure to call this function after SNMP engine ID is configured
    to the application.
    """
    mibBuilder = snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

    snmpEngineID, snmpEngineBoots = mibBuilder.importSymbols(
        '__SNMP-FRAMEWORK-MIB', 'snmpEngineID', 'snmpEngineBoots')

    hexValue = ''.join('%x' % x for x in snmpEngineID.syntax.asNumbers())

    stateDir = os.path.join(stateDir, hexValue)

    if not os.path.exists(stateDir):
        os.makedirs(stateDir)

    bootsFile = os.path.join(stateDir, 'boots.txt')

    try:
        with open(bootsFile) as fl:
            boots = int(fl.read())

    except (IOError, ValueError):
        boots = 0

    if boots > 0xffffffff:
        boots = 0

    boots += 1

    with tempfile.NamedTemporaryFile(dir=stateDir, delete=False) as fl:
        fl.write(str(boots).encode())

    snmpEngineBoots.syntax = snmpEngineBoots.syntax.clone(boots)

    os.rename(fl.name, bootsFile)

    return boots
