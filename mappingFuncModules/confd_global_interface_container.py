import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from bdsMappingFunctions import bdsMappingFunctions
import logging
#import pytablewriter
#import yaml
from oidDb import OidDbItem
import asyncio


IFTYPEMAP = {
            1 : 6 # ethernet-csmacd(6)
            }
IFOPERSTATUSMAP = {
            0:2,  # down(2)
            1:1,  # up(1),       -- ready to pass packets
            2:3,  # testing(3)   -- in some test mode
            3:3   # testing(3)   -- in some test mode
            }

IFMTU_LAMBDA = lambda a : int(a,16)
IFSPEED_LAMBDA = lambda a : int(a,16)


class confd_global_interface_container(object):

    """

    curl -X POST -H "Content-Type: application/json" -H "Accept: */*" -H "connection: close"\
        -H "Accept-Encoding: application/json"\
        -d '{"table": {"table_name": "global.interface.container"}}'\
        "http://10.0.3.50:2002/bds/table/walk?format=raw" | jq '.'

    {
      "objects": [
        {
          "attribute": {
            "physical_interfaces": [
              "ifp-0/1/1"
            ],
            "interface_name": "ifc-0/0/1/1",
            "interface_description": "Container interface for ifp-0/1/1",
            "encapsulation_type": "01",
            "bandwidth": "00000000",
            "layer2_mtu": "0024",
            "admin_status": "01",
            "link_status": "01",
            "mac_address": "02fe2f60b077"
          },
          "update": true,
          "sequence": 1
        }
      ],
      "table": {
        "table_name": "global.interface.container"
      }
    }

    """

    @classmethod
    async def setOids(self,bdsJsonResponseDict,targetOidDb):
        targetOidDb.insertOid(newOidItem = OidDbItem(
            bdsMappingFunc = "ffwd_default_interface_logical",
            oid = "1.3.6.1.2.1.2.1.0",
            name="ifIndex",
            pysnmpBaseType="Integer32",
            value=len(bdsJsonResponseDict["objects"])))
        oidSegment = "1.3.6.1.2.1.2.2.1."
        targetOidDb.setLock()
        #targetOidDb.deleteOidsWithPrefix(oidSegment)  #delete existing TableOids
        for bdsJsonObject in bdsJsonResponseDict["objects"]:
            ifName = bdsJsonObject["attribute"]["interface_name"]
            index =  bdsMappingFunctions.ifIndexFromIfName(ifName)
            ifPhysicalLocation = bdsMappingFunctions.stripIfPrefixFromIfName(ifName)
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "confd_global_interface_container",
                oid = oidSegment+"1."+str(index),
                name="ifIndex",
                pysnmpBaseType="Integer32",
                value=int(index)))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "confd_global_interface_container",
                oid = oidSegment+"2."+str(index),
                name="ifDescr",
                pysnmpBaseType="OctetString",
                value=ifPhysicalLocation))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "confd_global_interface_container",
                oid = oidSegment+"3."+str(index),
                name="ifType",
                pysnmpBaseType="Integer32",
                value=IFTYPEMAP[int(bdsJsonObject["attribute"]["encapsulation_type"])]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "confd_global_interface_container",
                oid = oidSegment+"4."+str(index),
                name="ifMtu",
                pysnmpBaseType="Integer32",
                value=IFMTU_LAMBDA(bdsJsonObject["attribute"]["layer2_mtu"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "confd_global_interface_container",
                oid = oidSegment+"5."+str(index),
                name="ifSpeed",
                pysnmpBaseType="Gauge32",
                value=IFSPEED_LAMBDA(bdsJsonObject["attribute"]["bandwidth"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "confd_global_interface_container",
                oid = oidSegment+"6."+str(index),
                name="ifPhysAddress",
                pysnmpBaseType="OctetString",
                pysnmpRepresentation="hexValue",
                value=bdsJsonObject["attribute"]["mac_address"].replace(":","")))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "confd_global_interface_container",
                oid = oidSegment+"7."+str(index),
                name="ifAdminStatus",
                pysnmpBaseType="Integer32",
                value=bdsJsonObject["attribute"]["admin_status"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "confd_global_interface_container",
                oid = oidSegment+"8."+str(index),
                name="ifOperStatus",
                pysnmpBaseType="Integer32",
                value=IFOPERSTATUSMAP[int(bdsJsonObject["attribute"]["link_status"])]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "confd_global_interface_container",
                oid = oidSegment+"9."+str(index),
                name="ifLastChange",
                pysnmpBaseType="TimeTicks",
                value=0 ))   # Fixme
        targetOidDb.releaseLock()
