# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import os
import tempfile

from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity import config
from pysnmp.entity.engine import SnmpEngine
from pysnmp.entity.rfc3413 import context
from pysnmp.proto.api import v2c
from pysnmp.proto.rfc1902 import OctetString

from bdssnmpadaptor import error

AUTH_PROTOCOLS = {
  'MD5': config.usmHMACMD5AuthProtocol,
  'SHA': config.usmHMACSHAAuthProtocol,
  'SHA224': config.usmHMAC128SHA224AuthProtocol,
  'SHA256': config.usmHMAC192SHA256AuthProtocol,
  'SHA384': config.usmHMAC256SHA384AuthProtocol,
  'SHA512': config.usmHMAC384SHA512AuthProtocol,
  'NONE': config.usmNoAuthProtocol
}

PRIV_PROTOCOLS = {
  'DES': config.usmDESPrivProtocol,
  '3DES': config.usm3DESEDEPrivProtocol,
  'AES': config.usmAesCfb128Protocol,
  'AES128': config.usmAesCfb128Protocol,
  'AES192': config.usmAesCfb192Protocol,
  'AES192BLMT': config.usmAesBlumenthalCfb192Protocol,
  'AES256': config.usmAesCfb256Protocol,
  'AES256BLMT': config.usmAesBlumenthalCfb256Protocol,
  'NONE': config.usmNoPrivProtocol
}

MP_MODELS = {
    '1': 1,
    '2c': 2,
    '3': 3
}


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


def setCommunity(snmpEngine, security, community, version='2c', tag=''):
    """Configure SNMP community name and VACM access
    """
    mpModel = MP_MODELS[version]
    authLevel = 'noAuthNoPriv'

    config.addV1System(
        snmpEngine, security, communityName=community, transportTag=tag)

    config.addVacmUser(
        snmpEngine, mpModel, security, authLevel,
        (1, 3, 6), (1, 3, 6), (1, 3, 6))

    return authLevel


def setUsmUser(snmpEngine, security, user, authKey=None, authProtocol=None,
               privKey=None, privProtocol=None):
    """Configure SNMP USM user credentials and VACM access
    """
    if not authKey:
        authProtocol = 'NONE'

    elif not authProtocol:
        authProtocol = 'MD5'

    if not privKey:
        privProtocol = 'NONE'

    elif not privProtocol:
        privProtocol = 'DES'

    authProtocol = AUTH_PROTOCOLS[authProtocol.upper()]
    privProtocol = PRIV_PROTOCOLS[privProtocol.upper()]

    if (authProtocol == config.usmNoAuthProtocol and
            privProtocol != config.usmNoPrivProtocol):
        raise error.BdsError('SNMP privacy implies enabled authentication')

    elif (authProtocol == config.usmNoAuthProtocol and
            privProtocol == config.usmNoPrivProtocol):
        authLevel = 'noAuthNoPriv'

    elif privProtocol != config.usmNoPrivProtocol:
        authLevel = 'authPriv'

    else:
        authLevel = 'authNoPriv'

    config.addV3User(
        snmpEngine,
        user,
        authProtocol,
        authKey,
        privProtocol,
        privKey,
        securityName=security)

    config.addVacmUser(
        snmpEngine, 3, security, authLevel,
        (1, 3, 6), (1, 3, 6), (1, 3, 6))

    return authLevel


def _getTrapCreds(security):
    return security + '-creds'


def _getTrapTargetName(security):
    return security + '-target'


def setTrapTargetAddress(snmpEngine, security, dst, tag=''):
    """Configure SNMP TRAP target
    """
    config.addTargetAddr(
        snmpEngine, _getTrapTargetName(security), udp.domainName, dst,
        _getTrapCreds(security), tagList=tag)


def setTrapVersion(snmpEngine, security, authLevel, version='2c'):
    """Configure SNMP TRAP target
    """
    mpModel = MP_MODELS[version]

    if mpModel < 3:
        mpModel -= 1

    config.addTargetParams(
        snmpEngine, _getTrapCreds(security), security, authLevel, mpModel)


def setTrapTypeForTag(snmpEngine, tag, kind='trap'):
    targets = 'all-targets'

    config.addNotificationTarget(
        snmpEngine, targets, 'filter', tag, kind)

    config.addContext(snmpEngine, '')

    return targets


def setMibController(snmpEngine, controller):
    snmpContextName = v2c.OctetString('')

    # https://github.com/openstack/virtualpdu/blob/master/virtualpdu/pdu/pysnmp_handler.py
    snmpContext = context.SnmpContext(snmpEngine)
    snmpContext.unregisterContextName(snmpContextName)
    snmpContext.registerContextName(snmpContextName, controller)

    return snmpContext


def setSnmpTransport(snmpEngine, listen=None):
    transport = udp.UdpAsyncioTransport()

    if listen:
        transport = transport.openServerMode(listen)
    else:
        transport = transport.openClientMode()

    config.addTransport(
        snmpEngine,
        udp.domainName,
        transport
    )
