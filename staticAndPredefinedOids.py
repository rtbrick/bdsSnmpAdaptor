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
    async def setOids(self,targetOidDb,staticOidDict):
        targetOidDb.insertOid(newOidItem = OidDbItem(
            bdsMappingFunc = "StaticAndPredefinedOids",
            oid = "1.3.6.1.2.1.1.1.0",
            name="sysContact", pysnmpBaseType="OctetString",
            value= staticOidDict["sysDesc"]))
        targetOidDb.insertOid(newOidItem = OidDbItem(
            bdsMappingFunc = "StaticAndPredefinedOids",
            oid = "1.3.6.1.2.1.1.2.0",
            name="sysObjectID", pysnmpBaseType="ObjectIdentifier",
            value="1.3.6.1.4.1.50058.102.1.0" ))     #FIXME get from BDS entity table
        targetOidDb.insertOid(newOidItem = OidDbItem(
            bdsMappingFunc = "StaticAndPredefinedOids",
            oid = "1.3.6.1.2.1.1.3.0",
            name="sysUptime", pysnmpBaseType="TimeTicks",
            value=""))
        targetOidDb.insertOid(newOidItem = OidDbItem(
            bdsMappingFunc = "StaticAndPredefinedOids",
            oid = "1.3.6.1.2.1.1.4.0",
            name="sysContact", pysnmpBaseType="OctetString",
            value= staticOidDict["sysContact"]))
        targetOidDb.insertOid(newOidItem = OidDbItem(
            bdsMappingFunc = "StaticAndPredefinedOids",
            oid = "1.3.6.1.2.1.1.5.0",
            name="sysName", pysnmpBaseType="OctetString",
            value= staticOidDict["sysName"]))
        targetOidDb.insertOid(newOidItem = OidDbItem(
            bdsMappingFunc = "StaticAndPredefinedOids",
            oid = "1.3.6.1.2.1.1.6.0",
            name="sysLocation", pysnmpBaseType="OctetString",
            value= staticOidDict["sysLocation"]))
        targetOidDb.insertOid(newOidItem = OidDbItem(
            bdsMappingFunc = "StaticAndPredefinedOids",
            oid = "1.3.6.1.2.1.1.7.0",
            name="SysServices", pysnmpBaseType="Integer32",
            value=6 ))

        #
        print(f'temp print for engineId: {staticOidDict["engineId"]}')
        #
        #  Entity definitions test
        #
        valueMatrix = [["Edgecore Networks AS5912-54 port 10GB SFP+ + 6 port QSFP28",
                        "1.3.6.1.4.1.50058.102.1.0",
                        0,
                        3,
                        0,
                        "chassis",
                        "R02A",
                        "AS5916 V36 20180815",
                        "",
                        "591654XK1848017"]]
        for i,phyValueList in enumerate(valueMatrix):
            index = i+1
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "StaticAndPredefinedOids",
                oid = "1.3.6.1.2.1.47.1.1.1.1.1."+str(index),
                name="entPhysicalIndex", pysnmpBaseType="Integer32",
                value=index ))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "StaticAndPredefinedOids",
                oid = "1.3.6.1.2.1.47.1.1.1.1.2."+str(index),
                name="entPhysicalDescr", pysnmpBaseType="OctetString",
                value=valueMatrix[i][0] ))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "StaticAndPredefinedOids",
                oid = "1.3.6.1.2.1.47.1.1.1.1.3."+str(index),
                name="entPhysicalVendorType", pysnmpBaseType="ObjectIdentifier",
                value=valueMatrix[i][1] ))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "StaticAndPredefinedOids",
                oid = "1.3.6.1.2.1.47.1.1.1.1.4."+str(index),
                name="entPhysicalContainedIn", pysnmpBaseType="Integer32",
                value=valueMatrix[i][2] ))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "StaticAndPredefinedOids",
                oid = "1.3.6.1.2.1.47.1.1.1.1.5."+str(index),
                name="entPhysicalClass", pysnmpBaseType="Integer32",
                value=valueMatrix[i][3] ))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "StaticAndPredefinedOids",
                oid = "1.3.6.1.2.1.47.1.1.1.1.6."+str(index),
                name="entPhysicalParentRelPos", pysnmpBaseType="Integer32",
                value=valueMatrix[i][4] ))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "StaticAndPredefinedOids",
                oid = "1.3.6.1.2.1.47.1.1.1.1.7."+str(index),
                name="entPhysicalName", pysnmpBaseType="OctetString",
                value=valueMatrix[i][5] ))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "StaticAndPredefinedOids",
                oid = "1.3.6.1.2.1.47.1.1.1.1.8."+str(index),
                name="entPhysicalHardwareRev", pysnmpBaseType="OctetString",
                value=valueMatrix[i][6] ))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "StaticAndPredefinedOids",
                oid = "1.3.6.1.2.1.47.1.1.1.1.9."+str(index),
                name="entPhysicalFirmwareRev", pysnmpBaseType="OctetString",
                value=valueMatrix[i][7] ))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "StaticAndPredefinedOids",
                oid = "1.3.6.1.2.1.47.1.1.1.1.10."+str(index),
                name="entPhysicalSoftwareRev", pysnmpBaseType="OctetString",
                value=valueMatrix[i][8] ))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "StaticAndPredefinedOids",
                oid = "1.3.6.1.2.1.47.1.1.1.1.11."+str(index),
                name="entPhysicalSerialNum", pysnmpBaseType="OctetString",
                value=valueMatrix[i][9] ))
