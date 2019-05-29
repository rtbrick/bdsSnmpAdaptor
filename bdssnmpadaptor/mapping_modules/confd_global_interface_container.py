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

from bdssnmpadaptor.mapping_functions import BdsMappingFunctions

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
    bigEndianFloatStruct.unpack(binascii.unhexlify(x))[0] / 1000000 * 8)


# HEX_STRING_LAMBDA = lambda x : int(x,16)
# IFMTU_LAMBDA = lambda x : int(''.join([m[2:4]+m[0:2] for m in [x[i:i+4] for i in range(0,len(x),4)]]),16)


class ConfdGlobalInterfaceContainer(object):
    """Interface container

    Notes
    -----

    root@l2-pod2:~#     curl -X POST -H "Content-Type: application/json" -H "Accept: */*" -H "connection: close"\
    >         -H "Accept-Encoding: application/json"\
    >         -d '{"table": {"table_name": "global.interface.container"}}'\
    >         "http://10.0.3.10:2002/bds/table/walk?format=raw" | jq '.'
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100 18629    0 18574  100    55  2826k   8570 --:--:-- --:--:-- --:--:-- 3023k
    {
      "table": {
        "table_name": "global.interface.container"
      },
      "objects": [
        {
          "sequence": 200197,
          "update": true,
          "attribute": {
            "interface_name": "ifc-0/0/0/1",
            "interface_description": "Container interface for ifp-0/0/1",
            "encapsulation_type": "01",
            "bandwidth": "4e9502f9",
            "layer2_mtu": "f205",
            "admin_status": "01",
            "link_status": "01",
            "mac_address": "b86a97a59201",
            "physical_interfaces": [
              "ifp-0/0/1"
            ]
          }
        },
        {
          "sequence": 200198,
          "update": true,
          "attribute": {
            "interface_name": "ifc-0/0/0/2",
            "interface_description": "Container interface for ifp-0/0/2",
            "encapsulation_type": "01",
            "bandwidth": "4e9502f9",
            "layer2_mtu": "f205",
            "admin_status": "01",
            "link_status": "01",
            "mac_address": "b86a97a59202",
            "physical_interfaces": [
              "ifp-0/0/2"
            ]
          }
        },
        {
          "sequence": 200061,
          "update": true,
          "attribute": {
            "interface_name": "ifc-0/0/0/3",
            "interface_description": "Container interface for ifp-0/0/3",
            "encapsulation_type": "01",
            "bandwidth": "4e9502f9",
            "layer2_mtu": "f205",
            "admin_status": "01",
            "link_status": "01",
            "mac_address": "b86a97a59203",
            "physical_interfaces": [
              "ifp-0/0/3"
            ]
          }
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

        targetOidDb.setLock()

        with targetOidDb.module(__name__) as add:

            if str(newSequenceNumberList) != str(lastSequenceNumberList):
                add('IF-MIB', 'ifNumber', 0,
                    value=len(bdsJsonResponseDict['objects']))

                # targetOidDb.deleteOidsWithPrefix(oidSegment)  #delete existing TableOids

                for i, bdsJsonObject in enumerate(bdsJsonResponseDict['objects']):
                    thisSequenceNumber = bdsJsonObject['sequence']

                    ifName = bdsJsonObject['attribute']['interface_name']

                    index = BdsMappingFunctions.ifIndexFromIfName(ifName)

                    ifSpeed = IFSPEED_LAMBDA(bdsJsonObject['attribute']['bandwidth'])

                    if ifSpeed == 100000000:
                        ifGigEtherName = 'hundredGe-' + BdsMappingFunctions.stripIfPrefixFromIfName(ifName)

                    elif ifSpeed == 10000000:
                        ifGigEtherName = 'tenGe-' + BdsMappingFunctions.stripIfPrefixFromIfName(ifName)

                    else:
                        ifGigEtherName = 'ge-' + BdsMappingFunctions.stripIfPrefixFromIfName(ifName)

                    add('IF-MIB', 'ifIndex', index, value=index)

                    add('IF-MIB', 'ifDescr', index, value=ifGigEtherName)

                    add('IF-MIB', 'ifType', index,
                        value=IFTYPEMAP[int(bdsJsonObject['attribute']['encapsulation_type'])])

                    add('IF-MIB', 'ifMtu', index,
                        value=IFMTU_LAMBDA(bdsJsonObject['attribute']['layer2_mtu']))

                    add('IF-MIB', 'ifPhysAddress', index,
                        value=bdsJsonObject['attribute']['mac_address'].replace(':', ''),
                        valueFormat='hexValue')

                    add('IF-MIB', 'ifAdminStatus', index,
                        value=bdsJsonObject['attribute']['admin_status'])

                    add('IF-MIB', 'ifOperStatus', index,
                        value=IFOPERSTATUSMAP[int(bdsJsonObject['attribute']['link_status'])])

                    if len(lastSequenceNumberList) == 0:  # first run
                        add('IF-MIB', 'ifLastChange', index, value=0)

                    elif thisSequenceNumber != lastSequenceNumberList[i]:  # status has changed
                        add('IF-MIB', 'ifLastChange', index,
                            value=int((time.time() - birthday) * 100))

                    if len(lastSequenceNumberList) == 0:  # first run
                        add('IF-MIB', 'ifStackLastChange', index, value=0)

                        # Fixme - do we have to observe logical interfaces?
                        add('IF-MIB', 'ifTableLastChange', index, value=0)

                    else:
                        add('IF-MIB', 'ifTableLastChange', index,
                            value=int((time.time() - birthday) * 100))

                    add('IF-MIB', 'ifSpeed', index,
                        value=IFSPEED_LAMBDA(bdsJsonObject['attribute']['bandwidth']))

            targetOidDb.releaseLock()
