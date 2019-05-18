#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
from bdssnmpadaptor.oidDb import OidDbItem

from pysnmp.proto.api import v2c
OctetString = v2c.OctetString
Integer32 = v2c.Integer32
TimeTicks = v2c.TimeTicks
ObjectIdentifier = v2c.ObjectIdentifier
Counter32 = v2c.Counter32
Counter64 = v2c.Counter64
Gauge32 = v2c.Gauge32
Unsigned32 = v2c.Unsigned32
IpAddress = v2c.IpAddress


class StaticAndPredefinedOids(object):
    """


    """

    @classmethod
    async def setOids(cls, targetOidDb, staticOidDict):
        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.2.1.1.1.0',
                name='sysContact', pysnmpBaseType=OctetString,
                value=staticOidDict['sysDesc']))

        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.2.1.1.2.0',
                name='sysObjectID', pysnmpBaseType=ObjectIdentifier,
                value='1.3.6.1.4.1.50058.102.1'))  # FIXME get from BDS entity table

        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.2.1.1.3.0',
                name='sysUptime', pysnmpBaseType=TimeTicks,
                value=0))

        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.2.1.1.4.0',
                name='sysContact', pysnmpBaseType=OctetString,
                value=staticOidDict['sysContact']))

        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.2.1.1.5.0',
                name='sysName', pysnmpBaseType=OctetString,
                value=staticOidDict['sysName']))

        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.2.1.1.6.0',
                name='sysLocation', pysnmpBaseType=OctetString,
                value=staticOidDict['sysLocation']))

        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.2.1.1.7.0',
                name='SysServices', pysnmpBaseType=Integer32,
                value=6))

        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.6.3.10.2.1.1.0',
                name='snmpEngineID',
                pysnmpBaseType=OctetString,
                pysnmpRepresentation='hexValue',
            # value=staticOidDict['snmpEngineID']))
            # FIXME : how to convert b'\x80\x00\xc3\x8a\x04sysName123' ?
            value='80:00:C3:8A:04:73:79:73:4e:61:6d:65:31:32:33'.replace(':', '')))
        # FIXME end.

        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.6.3.10.2.1.2.0',
                name='snmpEngineBoots',
                pysnmpBaseType=Integer32,
                value=1))

        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.6.3.10.2.1.3.0',
                name='snmpEngineTime',
                pysnmpBaseType=Integer32,
                value=0))  # will be set in realtime

        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.6.3.10.2.1.4.0',
                name='snmpEngineMaxMessageSize',
                pysnmpBaseType=Integer32,
                value=2048))
        #
        #  hostResource Mib
        #
        targetOidDb.insertOid(
            newOidItem=OidDbItem(  ##FIXME get from bds
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.2.1.25.1.1.0',
                name='hrSystemUptime', pysnmpBaseType=TimeTicks,
                value=0))

        #
        #  Entity definitions test
        #
        valueMatrix = [['Rtbrick Fullstack on AS5912-54',
                        '1.3.6.1.4.1.50058.102.1',
                        0,  # entPhysicalContainedIn
                        3,  # entPhysicalContainedIn
                        0,  # entPhysicalParentRelPos
                        'chassis',
                        '',
                        '',
                        '',
                        '591654XK1848008',
                        'Accton',
                        'Edgecore Networks AS5912-54 port 10GB SFP+ plus 6 port QSFP28',
                        '5916-54XK-O-AC-F',
                        '',
                        2,
                        '',
                        ''],
                       ['AS5912 Compute Board',
                        '1.3.6.1.4.1.50058.102.1',
                        1,  # entPhysicalContainedIn
                        9,  # entPhysicalContainedIn
                        0,  # entPhysicalParentRelPos
                        'AS5916-54XK',
                        'R02A',
                        'AS5916 V36 20180815',
                        '',
                        '591654XK1848017',
                        'Accton',
                        'Intel(R) Xeon(R) CPU D-1518 @ 2.20GHz',
                        'AS5916-54XK',
                        '',
                        1,
                        '',
                        ''],
                       ['PSU-1',  # entPhysicalDescr
                        '1.3.6.1.4.1.50058.102.1',  # entPhysicalVendorTyp
                        1,  # entPhysicalContainedIn
                        6,  # entPhysicalClass
                        0,  # entPhysicalParentRelPos
                        '',  # entPhysicalName
                        '',
                        '',
                        '',
                        'NULL',
                        'Accton',
                        '',
                        '',
                        '',
                        1,
                        '',
                        ''],
                       ['PSU-2',  # entPhysicalDescr
                        '1.3.6.1.4.1.50058.102.1',  # entPhysicalVendorTyp
                        1,  # entPhysicalContainedIn
                        6,  # entPhysicalClass
                        0,  # entPhysicalParentRelPos
                        '',  # entPhysicalName
                        '',
                        '',
                        '',
                        'NULL',
                        'Accton',
                        '',
                        '',
                        '',
                        1,
                        '',
                        ''],
                       ['Chassis Fan - 1',  # entPhysicalDescr
                        '1.3.6.1.4.1.50058.102.1',  # entPhysicalVendorTyp
                        1,  # entPhysicalContainedIn
                        7,  # entPhysicalClass
                        0,  # entPhysicalParentRelPos
                        '',  # entPhysicalName
                        '',
                        '',
                        '',
                        'NULL',
                        'Accton',
                        '',
                        '',
                        '',
                        1,
                        '',
                        ''],
                       ['Chassis Fan - 2',  # entPhysicalDescr
                        '1.3.6.1.4.1.50058.102.1',  # entPhysicalVendorTyp
                        1,  # entPhysicalContainedIn
                        7,  # entPhysicalClass
                        0,  # entPhysicalParentRelPos
                        '',  # entPhysicalName
                        '',
                        '',
                        '',
                        'NULL',
                        'Accton',
                        '',
                        '',
                        '',
                        1,
                        '',
                        '']]

        for i, phyValueList in enumerate(valueMatrix):
            index = i + 1

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.1.' + str(index),
                    name='entPhysicalIndex', pysnmpBaseType=Integer32,
                    value=index))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.2.' + str(index),
                    name='entPhysicalDescr', pysnmpBaseType=OctetString,
                    value=valueMatrix[i][0]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.3.' + str(index),
                    name='entPhysicalVendorType', pysnmpBaseType=ObjectIdentifier,
                    value=valueMatrix[i][1]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.4.' + str(index),
                    name='entPhysicalContainedIn', pysnmpBaseType=Integer32,
                    value=valueMatrix[i][2]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.5.' + str(index),
                    name='entPhysicalClass', pysnmpBaseType=Integer32,
                    value=valueMatrix[i][3]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.6.' + str(index),
                    name='entPhysicalParentRelPos', pysnmpBaseType=Integer32,
                    value=valueMatrix[i][4]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.7.' + str(index),
                    name='entPhysicalName', pysnmpBaseType=OctetString,
                    value=valueMatrix[i][5]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.8.' + str(index),
                    name='entPhysicalHardwareRev', pysnmpBaseType=OctetString,
                    value=valueMatrix[i][6]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.9.' + str(index),
                    name='entPhysicalFirmwareRev', pysnmpBaseType=OctetString,
                    value=valueMatrix[i][7]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                bdsMappingFunc='StaticAndPredefinedOids',
                oid='1.3.6.1.2.1.47.1.1.1.1.10.' + str(index),
                name='entPhysicalSoftwareRev', pysnmpBaseType=OctetString,
                value=valueMatrix[i][8]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.11.' + str(index),
                    name='entPhysicalSerialNum', pysnmpBaseType=OctetString,
                    value=valueMatrix[i][9]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.12.' + str(index),
                    name='entPhysicalMfgName', pysnmpBaseType=OctetString,
                    value=valueMatrix[i][10]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.13.' + str(index),
                    name='entPhysicalModelName', pysnmpBaseType=OctetString,
                    value=valueMatrix[i][11]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.14.' + str(index),
                    name='entPhysicalAlias', pysnmpBaseType=OctetString,
                    value=valueMatrix[i][12]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.15.' + str(index),
                    name='entPhysicalAlias', pysnmpBaseType=OctetString,
                    value=valueMatrix[i][13]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.16.' + str(index),
                    name='entPhysicalIsFRUs', pysnmpBaseType=Integer32,
                    value=valueMatrix[i][14]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.17.' + str(index),
                    name='entPhysicalMfgDate', pysnmpBaseType=OctetString,
                    value=valueMatrix[i][15]))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc='StaticAndPredefinedOids',
                    oid='1.3.6.1.2.1.47.1.1.1.1.18.' + str(index),
                    name='entPhysicalUris', pysnmpBaseType=OctetString,
                    value=valueMatrix[i][16]))
