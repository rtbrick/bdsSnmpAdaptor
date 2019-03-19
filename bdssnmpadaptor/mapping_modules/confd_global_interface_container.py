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

from bdssnmpadaptor.mapping_functions import bdsMappingFunctions
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

IFMTU_LAMBDA = lambda x : int(littleEndianShortStruct.unpack(binascii.unhexlify(x))[0])
IFSPEED_LAMBDA = lambda x : int(bigEndianFloatStruct.unpack(binascii.unhexlify(x))[0]/1000000*8)


# HEX_STRING_LAMBDA = lambda x : int(x,16)
# IFMTU_LAMBDA = lambda x : int("".join([m[2:4]+m[0:2] for m in [x[i:i+4] for i in range(0,len(x),4)]]),16)


class confd_global_interface_container(object):
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
    async def setOids(cls, bdsJsonResponseDict, targetOidDb, lastSequenceNumberList, birthday):
        newSequenceNumberList = []

        for i, bdsJsonObject in enumerate(bdsJsonResponseDict["objects"]):
            newSequenceNumberList.append(bdsJsonObject["sequence"])

        if str(newSequenceNumberList) == str(lastSequenceNumberList):
            pass  # add logger statement

        else:
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "confd_global_interface_container",
                oid = "1.3.6.1.2.1.2.1.0",
                name="ifIndex",
                pysnmpBaseType="Integer32",
                value=len(bdsJsonResponseDict["objects"])))
            targetOidDb.setLock()
            #targetOidDb.deleteOidsWithPrefix(oidSegment)  #delete existing TableOids
            for i,bdsJsonObject in enumerate(bdsJsonResponseDict["objects"]):
                oidSegment = "1.3.6.1.2.1.2.2.1."
                thisSequenceNumber = bdsJsonObject["sequence"]
                ifName = bdsJsonObject["attribute"]["interface_name"]

                index = bdsMappingFunctions.ifIndexFromIfName(ifName)
                # index =  i + 1
                ifPhysicalLocation = bdsMappingFunctions.stripIfPrefixFromIfName(ifName)

                targetOidDb.insertOid(newOidItem=OidDbItem(
                    bdsMappingFunc="confd_global_interface_container",
                    oid=oidSegment + "1." + str(index),
                    name="ifIndex",
                    pysnmpBaseType="Integer32",
                    value=int(index)))

                targetOidDb.insertOid(newOidItem=OidDbItem(
                    bdsMappingFunc="confd_global_interface_container",
                    oid=oidSegment + "2." + str(index),
                    name="ifDescr",
                    pysnmpBaseType="OctetString",
                    value=ifPhysicalLocation))

                targetOidDb.insertOid(newOidItem=OidDbItem(
                    bdsMappingFunc="confd_global_interface_container",
                    oid=oidSegment + "3." + str(index),
                    name="ifType",
                    pysnmpBaseType="Integer32",
                    value=IFTYPEMAP[int(bdsJsonObject["attribute"]["encapsulation_type"])]))

                targetOidDb.insertOid(newOidItem=OidDbItem(
                    bdsMappingFunc="confd_global_interface_container",
                    oid=oidSegment + "4." + str(index),
                    name="ifMtu",
                    pysnmpBaseType="Integer32",
                    value=IFMTU_LAMBDA(bdsJsonObject["attribute"]["layer2_mtu"])))
                targetOidDb.insertOid(newOidItem = OidDbItem(
                    bdsMappingFunc = "confd_global_interface_container",
                    oid = oidSegment+"6."+str(index),
                    name="ifPhysAddress",
                    pysnmpBaseType="OctetString",
                    pysnmpRepresentation="hexValue",
                    value=bdsJsonObject["attribute"]["mac_address"].replace(":", "")))

                targetOidDb.insertOid(newOidItem=OidDbItem(
                    bdsMappingFunc="confd_global_interface_container",
                    oid=oidSegment + "7." + str(index),
                    name="ifAdminStatus",
                    pysnmpBaseType="Integer32",
                    value=bdsJsonObject["attribute"]["admin_status"]))

                targetOidDb.insertOid(newOidItem=OidDbItem(
                    bdsMappingFunc="confd_global_interface_container",
                    oid=oidSegment + "8." + str(index),
                    name="ifOperStatus",
                    pysnmpBaseType="Integer32",
                    value=IFOPERSTATUSMAP[int(bdsJsonObject["attribute"]["link_status"])]))

                if len(lastSequenceNumberList) == 0:  # first run
                    targetOidDb.insertOid(newOidItem=OidDbItem(
                        bdsMappingFunc="confd_global_interface_container",
                        oid=oidSegment + "9." + str(index),
                        name="ifLastChange",
                        pysnmpBaseType="TimeTicks",
                        value=0 ))
                elif thisSequenceNumber != lastSequenceNumberList[i] :    #status has changed
                    targetOidDb.insertOid(newOidItem = OidDbItem(
                        bdsMappingFunc = "confd_global_interface_container",
                        oid = oidSegment+"9."+str(index),
                        name="ifTableLastChange",
                        pysnmpBaseType="TimeTicks",
                        value=int((time.time() - birthday) * 100)))

                if len(lastSequenceNumberList) == 0:  # first run
                    targetOidDb.insertOid(newOidItem=OidDbItem(
                        bdsMappingFunc="confd_global_interface_container",
                        oid="1.3.6.1.2.1.31.1.5",
                        name="ifTableLastChange",
                        pysnmpBaseType="TimeTicks",
                        value=0))
                    targetOidDb.insertOid(newOidItem=OidDbItem(
                        bdsMappingFunc="confd_global_interface_container",
                        oid="1.3.6.1.2.1.31.1.6",
                        name="ifTableLastChange",
                        pysnmpBaseType="TimeTicks",
                        value=0))  # Fixme - do we have to observe logical interfaces?

                else:
                    targetOidDb.insertOid(newOidItem=OidDbItem(
                        bdsMappingFunc="confd_global_interface_container",
                        oid="1.3.6.1.2.1.31.1.5",
                        name="ifTableLastChange",
                        pysnmpBaseType="TimeTicks",
                        value=int((time.time()-birthday)*100) ))
                #
                # Change to ífXTable
                #
                oidSegment = "1.3.6.1.2.1.31.1.1.1."
                targetOidDb.insertOid(newOidItem = OidDbItem(
                    bdsMappingFunc = "confd_global_interface_container",
                    oid = oidSegment+"15."+str(index),
                    name="ifSpeed",
                    pysnmpBaseType="Gauge32",
                    value=IFSPEED_LAMBDA(bdsJsonObject["attribute"]["bandwidth"])))

            targetOidDb.releaseLock()
