#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from bdsMappingFunctions import bdsMappingFunctions
import logging
from oidDb import OidDbItem
import asyncio

class StaticAndPredefinedOids (object):

    """


    """

    @classmethod
    async def setOids(self,targetOidDb):
        targetOidDb.insertOid(newOidItem = OidDbItem(
            oid = "1.3.6.1.2.1.1.7.0",
            name="SysServices", pysnmpBaseType="Integer32",
            value=6 ))
