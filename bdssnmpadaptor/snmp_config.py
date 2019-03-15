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

        if not engineId.startswith('0x') and not engineId.startswith('0X'):
            engineId = '0x' + engineId

        engineId = OctetString(hexValue=engineId)

    return SnmpEngine(engineId=engineId)
