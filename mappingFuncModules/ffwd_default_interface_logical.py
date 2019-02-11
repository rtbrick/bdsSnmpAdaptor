import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from bdsMappingFunctions import bdsMappingFunctions
import logging
from oidDb import OidDbItem
import asyncio

class ffwd_default_interface_logical(object):

    """

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
    async def setOids(self,bdsJsonResponseDict,targetOidDb):
        oidSegment = "1.3.6.1.2.1.2.2.1."
        targetOidDb.setLock()
        #targetOidDb.deleteOidsWithPrefix(oidSegment)  #delete existing TableOids
        for bdsJsonObject in bdsJsonResponseDict["objects"]:
            ifName = bdsJsonObject["attribute"]["interface_name"]
            index =  bdsMappingFunctions.ifIndexFromIfName(ifName)
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "ffwd_default_interface_logical",
                oid = oidSegment+"1."+str(index),
                name="ifIndex",
                pysnmpBaseType="Integer32",
                value=int(index)))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "ffwd_default_interface_logical",
                oid = oidSegment+"2."+str(index),
                name="ifDescr",
                pysnmpBaseType="OctetString",
                value=bdsJsonObject["attribute"]["interface_name"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "ffwd_default_interface_logical",
                oid = oidSegment+"3."+str(index),
                name="ifType",
                pysnmpBaseType="Integer32",
                value= 6 ))
        targetOidDb.releaseLock()
