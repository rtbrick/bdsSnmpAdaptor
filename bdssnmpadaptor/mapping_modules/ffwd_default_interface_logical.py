# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
from pysnmp.proto.rfc1902 import Integer32
from pysnmp.proto.rfc1902 import OctetString

from bdssnmpadaptor.mapping_functions import BdsMappingFunctions
from bdssnmpadaptor.oidDb import OidDbItem


class FfwdDefaultInterfaceLogical(object):
    """Logical interface

    curl -X POST -H "Content-Type: application/json" -H "Accept: */*" -H "connection: close"\
        -H "Accept-Encoding: application/json"\
        -d '{"table": {"table_name": "default.interface.logical"}}'\
        "http://10.0.3.50:5002/bds/table/walk?format=raw" | jq '.'

    {
      "objects": [
        {
          "attribute": {
            "link_status": "01",
            "admin_status": "01",
            "ipv4_status": "01000000",
            "ipv4_mtu": "ee05",
            "tagged": "00",
            "container_interface_name": "ifc-0/0/1/1",
            "interface_name": "ifl-0/0/1/1/0"
          },
          "update": true,
          "sequence": 1
        }
      ],
      "table": {
        "table_name": "default.interface.logical"
      }
    }
    """

    @classmethod
    async def setOids(cls, bdsJsonResponseDict, targetOidDb):
        oidSegment = '1.3.6.1.2.1.2.2.1.'
        targetOidDb.setLock()

        # targetOidDb.deleteOidsWithPrefix(oidSegment)  #delete existing TableOids
        for bdsJsonObject in bdsJsonResponseDict['objects']:
            ifName = bdsJsonObject['attribute']['interface_name']
            index = BdsMappingFunctions.ifIndexFromIfName(ifName)

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc=__name__,
                    oid=oidSegment + '1.' + str(index),
                    name='ifIndex',
                    pysnmpBaseType=Integer32,
                    value=int(index)))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc=__name__,
                    oid=oidSegment + '2.' + str(index),
                    name='ifDescr',
                    pysnmpBaseType=OctetString,
                    value=bdsJsonObject['attribute']['interface_name']))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc=__name__,
                    oid=oidSegment + '3.' + str(index),
                    name='ifType',
                    pysnmpBaseType=Integer32,
                    value=6))

        targetOidDb.releaseLock()
