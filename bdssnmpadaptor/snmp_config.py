# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
from pysnmp.hlapi.asyncio import SnmpEngine
from pysnmp.proto.rfc1902 import OctetString


def getSnmpEngine(engineId=None):
    if engineId:
        engineId = engineId.replace(':', '')

        if engineId.startswith('0x') or engineId.startswith('0X'):
            engineId = engineId[2:]

        engineId = OctetString(hexValue=engineId)

    return SnmpEngine(snmpEngineID=engineId)
