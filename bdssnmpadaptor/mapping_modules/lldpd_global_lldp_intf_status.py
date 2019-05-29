# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import binascii
import struct
import time

from pysnmp.proto.rfc1902 import Integer32

from bdssnmpadaptor.mapping_functions import BdsMappingFunctions
from bdssnmpadaptor.oidDb import OidDbItem

IFTYPEMAP = {
    1: 6  # ethernet-csmacd(6)
}

IFOPERSTATUSMAP = {
    0: 2,  # down(2)
    1: 1,  # up(1),       -- ready to pass packets
    2: 3,  # testing(3)   -- in some test mode
    3: 3  # testing(3)   -- in some test mode
}

bigEndianFloatStruct = struct.Struct('>f')
littleEndianShortStruct = struct.Struct('<h')

IFMTU_LAMBDA = lambda x: int(
    littleEndianShortStruct.unpack(binascii.unhexlify(x))[0])

IFSPEED_LAMBDA = lambda x: int(
    bigEndianFloatStruct.unpack(binascii.unhexlify(x))[0] / 1000 * 8)


# HEX_STRING_LAMBDA = lambda x : int(x,16)
# IFMTU_LAMBDA = lambda x : int(''.join([m[2:4]+m[0:2] for m in [x[i:i+4] for i in range(0,len(x),4)]]),16)

class LldpdGlobalLldpIntfStatus(object):
    """
        curl -X POST -H "Content-Type: application/json" -H "Accept: */*" -H "connection: close"\
                       -H "Accept-Encoding: application/json"\
                       -d '{"table": {"table_name": "global.lldp.intf.status"}}'\
                       "http://10.0.3.10:2002/bds/table/walk?format=raw" | jq '.'

        {
          "objects": [
            {
              "attribute": {
                "supported_breakout_modes": [
                  "4x1G"
                ],
                "configured_layer2_mtu": "dc05",
                "supported_max_layer2_mtu": "f205",
                "supported_min_layer2_mtu": "4000",
                "supported_auto_negotiation": "01",
                "configured_bandwidth": "4e9502f9",
                "default_bandwidth": "4e9502f9",
                "supported_bandwidths": [
                  "10.000 Gbps",
                  "1.000 Gbps"
                ],
                "interface_name": "ifp-0/0/1",
                "interface_description": "Physical interface #1 from node 0, chip 0",
                "interface_type": "01",
                "bandwidth": "4e9502f9",
                "layer2_mtu": "f205",
                "mac_address": "b86a97a59201",
                "admin_status": "01",
                "link_status": "01"
              },
              "update": true,
              "sequence": 200197
            },
            {
              "attribute": {
                "supported_breakout_modes": [
                  "4x1G"
                ],
                "configured_layer2_mtu": "dc05",
                "supported_max_layer2_mtu": "f205",
                "supported_min_layer2_mtu": "4000",
                "supported_auto_negotiation": "01",
                "configured_bandwidth": "4e9502f9",
                "default_bandwidth": "4e9502f9",
                "supported_bandwidths": [
                  "10.000 Gbps",
                  "1.000 Gbps"
                ],
                "interface_name": "ifp-0/0/2",
                "interface_description": "Physical interface #2 from node 0, chip 0",
                "interface_type": "01",
                "bandwidth": "4e9502f9",
                "layer2_mtu": "f205",
                "mac_address": "b86a97a59202",
                "admin_status": "01",
                "link_status": "01"
              },
              "update": true,
              "sequence": 200198
            },


        5
        ifTableLastChange	TICKS	ReadOnly	.1.3.6.1.2.1.31.1.5
        The value of sysUpTime at the time of the last creation or
        deletion of an entry in the ifTable.  If the number of
        entries has been unchanged since the last re-initialization
        of the local network management subsystem, then this object
        contains a zero value.
        6
        ifStackLastChange	TICKS	ReadOnly	.1.3.6.1.2.1.31.1.6
        The value of sysUpTime at the time of the last change of
        the (whole) interface stack.  A change of the interface
        stack is defined to be any creation, deletion, or change in
        value of any instance of ifStackStatus.  If the interface
        stack has been unchanged since the last re-initialization of
        the local network management subsystem, then this object
        contains a zero value.

    """

    @classmethod
    async def setOids(cls, bdsJsonResponseDict, targetOidDb,
                      lastSequenceNumberList, birthday):

        newSequenceNumberList = [
            obj['sequence'] for obj in bdsJsonResponseDict['objects']]

        if str(newSequenceNumberList) == str(lastSequenceNumberList):
            return

        currentSysTime = int((time.time() - birthday) * 100)

        targetOidDb.setLock()

        with targetOidDb.module(__name__) as add:

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc=__name__,
                    oid='1.3.6.1.2.1.2.1.0',
                    name='ifIndex',
                    pysnmpBaseType=Integer32,
                    value=len(bdsJsonResponseDict['objects'])))

            # targetOidDb.deleteOidsWithPrefix(oidSegment)  #delete existing TableOids

            for i, bdsJsonObject in enumerate(bdsJsonResponseDict['objects']):
                thisSequenceNumber = bdsJsonObject['sequence']

                attribute = bdsJsonObject['attribute']

                ifName = attribute['interface_name']
                index = BdsMappingFunctions.ifIndexFromIfName(ifName)

                ifPhysicalLocation = BdsMappingFunctions.stripIfPrefixFromIfName(ifName)

                add('IF-MIB', 'ifIndex', index, value=index)

                add('IF-MIB', 'ifDescr', index, value=ifPhysicalLocation)

                add('IF-MIB', 'ifType', index,
                    value=IFTYPEMAP[int(attribute['interface_type'])])

                add('IF-MIB', 'ifMtu', index,
                    value=IFMTU_LAMBDA(attribute['layer2_mtu']))

                add('IF-MIB', 'ifSpeed', index,
                    value=IFSPEED_LAMBDA(attribute['bandwidth']))

                add('IF-MIB', 'ifPhysAddress', index,
                    value=attribute['mac_address'].replace(':', ''))

                add('IF-MIB', 'ifAdminStatus', index,
                    value=IFOPERSTATUSMAP[int(attribute['admin_status'])])

                add('IF-MIB', 'ifOperStatus', index,
                    value=IFOPERSTATUSMAP[int(attribute['link_status'])])

                if len(lastSequenceNumberList) == 0:  # first run
                    add('IF-MIB', 'ifLastChange', index, value=0)

                elif thisSequenceNumber != lastSequenceNumberList[i]:
                    add('IF-MIB', 'ifLastChange', index, value=currentSysTime)

                if len(lastSequenceNumberList) == 0:  # first run
                    add('IF-MIB', 'ifStackLastChange', index, value=0)

                    # Fixme - do we have to observe logical interfaces?
                    add('IF-MIB', 'ifTableLastChange', index, value=0)

                else:
                    add('IF-MIB', 'ifTableLastChange', index,
                        value=currentSysTime)

            targetOidDb.releaseLock()
