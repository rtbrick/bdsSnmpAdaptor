# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#

from bdssnmpadaptor.mapping_functions import BdsMappingFunctions


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
    def setOids(cls, bdsJsonResponseDict, targetOidDb,
                tableSequenceList, birthday):

        with targetOidDb.module(__name__) as add:
            # targetOidDb.deleteOidsWithPrefix(oidSegment)  #delete existing TableOids

            for bdsJsonObject in bdsJsonResponseDict['objects']:
                ifName = bdsJsonObject['attribute']['interface_name']
                index = BdsMappingFunctions.ifIndexFromIfName(ifName)

                add('IF-MIB', 'ifIndex', index, value=index)

                add('IF-MIB', 'ifDescr', index,
                    value=bdsJsonObject['attribute']['interface_name'])

                add('IF-MIB', 'ifType', index, value=6)
