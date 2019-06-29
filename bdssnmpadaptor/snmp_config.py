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
    """Create SNMP engine instance.

    Args:
        engineId (str): SNMP engine ID as a ASCII or hex string

    Returns:
        object: SNMP engine object
    """
    if engineId:
        engineId = engineId.replace(':', '')

        if engineId.startswith('0x') or engineId.startswith('0X'):
            engineId = engineId[2:]

        engineId = OctetString(hexValue=engineId)

    return SnmpEngine(snmpEngineID=engineId)


def setSnmpEngineBoots(snmpEngine, stateDir):
    """Manage SNMP engine boots counter.

    Increments stateful SNMP engine boots counter maintained on the local
    file system, applies most current boots counter to the given SNMP
    engine instance.

    Args:
        snmpEngine (object): pysnmp `SnmpEngine` class instance
        stateDir (str): path to application's own writable directory
            for storing boots counter.

    Returns:
        int: updated boots counter

    Notes:
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
    """Configure SNMP v1/v2c community name and VACM access.

    Args:
        snmpEngine (object): pysnmp `SnmpEngine` class instance
        security (str): SNMP security name. Used in SNMP engine configuration
            primarily as an ID for the given SNMP v1/v2c authentication
            information
        community (str): SNMP v1/v2c community name
        version (str): SNMP version to use for this configuration entry. Either
            'v1' or 'v2c'.
        tag (str): Tags this SNMP configuration entry. Tags can be used internally
            by SNMP engine for looking up desired SNMP authentication information.

    Returns:
        str: effective SNMP authentication and privacy level ('noAuthNoPriv')
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
    """Configure SNMP v3 USM user credentials and VACM access.

    Args:
        snmpEngine (object): pysnmp `SnmpEngine` class instance
        security (str): SNMP security name. Used in SNMP engine configuration
            primarily as an ID for the given SNMP v3 authentication information.
        user (str): SNMP v3 USM user name
        authKey (str): SNMP v3 USM authentication key. Must be 8+ characters long,
            unless no SNMP message authentication is in use. Defaults to `None`.
        authProtocol (str): Authentication protocol to use. Known values are:
            'MD5', 'SHA', 'SHA224', 'SHA256', 'SHA384', 'SHA512', 'NONE'. Defaults
            to 'NONE'.
        privKey (str): SNMP v3 USM privacy key. Must be 8+ characters long,
            unless no SNMP payload encryption is in use. Defaults to `None`.
        privProtocol (str): SNMP message encryption protocol to use. Known values are:
            'DES', '3DES', 'AES', 'AES128', 'AES192', 'AES192BLMT', 'AES256',
            'AES256BLMT', 'NONE'. Defaults to 'NONE'.

    Returns:
        str: effective SNMP authentication and privacy level. Known values are:
            'noAuthNoPriv', 'authNoPriv', 'authPriv'.
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
    """Configure SNMP notification target for SNMP security name.

    Args:
        snmpEngine (object): pysnmp `SnmpEngine` class instance
        security (str): SNMP security name to associate SNMP notification target
            address with.
        dst (tuple): notification destination network address in `socket` format
            (i.e. ('XXX.XXX.XXX.XXX', NNN)).
        tag (str): Tags this target address. Tags can be used internally
            by SNMP engine for looking up desired notification destination or SNMP
            authentication information by transport address.
    """
    config.addTargetAddr(
        snmpEngine, _getTrapTargetName(security), udp.domainName, dst,
        _getTrapCreds(security), tagList=tag)


def setTrapVersion(snmpEngine, security, authLevel, version='2c'):
    """Configure SNMP version for SNMP security name.

    Args:
        snmpEngine (object): pysnmp `SnmpEngine` class instance
        security (str): SNMP security name to associate SNMP notification version
            requirement with.
        authLevel (str): SNMP authentication and privacy level to associate
            with this SNMP security name. Known values are: 'noAuthNoPriv',
            'authNoPriv', 'authPriv'.
        version (str): SNMP version to associate with this SNMP security
            name in the context of sending SNMP notifications.
    """
    mpModel = MP_MODELS[version]

    if mpModel < 3:
        mpModel -= 1

    config.addTargetParams(
        snmpEngine, _getTrapCreds(security), security, authLevel, mpModel)


def setTrapTypeForTag(snmpEngine, tag, kind='trap'):
    """Configure SNMP notification type per tag.

    Args:
        snmpEngine (object): pysnmp `SnmpEngine` class instance
        tag (str): SNMP tag to add to the list of tags used for issuing SNMP
            notifications.
        kind (str): SNMP notification type to use. Known values are
            'trap' and 'inform'.

    Returns:
        str: Group name to refer to all tagged configuration entries at
            once for selecting suitable ones for sending SNMP notifications.
    """
    targets = 'all-targets'

    config.addNotificationTarget(
        snmpEngine, targets, 'filter', tag, kind)

    config.addContext(snmpEngine, '')

    return targets


def setMibController(snmpEngine, controller):
    """Register SNMP MIB instrumentation controller with SNMP engine.

    Args:
        snmpEngine (object): pysnmp `SnmpEngine` class instance
        controller (object): SNMP MIB instrumentation controller compliant to pysnmp
            MIB instrumentation API.

    Returns:
        object: pysnmp `SnmpContext` object representing SNMP context for which
            SNMP MIB instrumentation controller is registered.
    """
    snmpContextName = v2c.OctetString('')

    # https://github.com/openstack/virtualpdu/blob/master/virtualpdu/pdu/pysnmp_handler.py
    snmpContext = context.SnmpContext(snmpEngine)
    snmpContext.unregisterContextName(snmpContextName)
    snmpContext.registerContextName(snmpContextName, controller)

    return snmpContext


def setSnmpTransport(snmpEngine, listen=None):
    """Create network endpoint for SNMP communication.

    Args:
        snmpEngine (object): pysnmp `SnmpEngine` class instance
        listen (tuple): if given, should refer to a local network address
            for SNMP engine to listen for SNMP notifications. If not given,
            client-side operation is assumed. When `listen` is given, must be
            in `socket` format (i.e. ('XXX.XXX.XXX.XXX', NNN)).
    """
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
