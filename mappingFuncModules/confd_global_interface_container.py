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


class confd_global_interface_container(object):

    """


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
                oid = oidSegment+"1."+str(index),
                name="ifIndex",
                pysnmpBaseType="Integer32",
                value=int(index)))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"2."+str(index),
                name="ifDescr",
                pysnmpBaseType="OctetString",
                value=bdsJsonObject["attribute"]["interface_name"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"3."+str(index),
                name="ifType",
                pysnmpBaseType="Integer32",
                value=IFTYPEMAP[int(bdsJsonObject["attribute"]["encapsulation_type"])]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"4."+str(index),
                name="ifMtu",
                pysnmpBaseType="Integer32",
                value=bdsJsonObject["attribute"]["layer2_mtu"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"5."+str(index),
                name="ifSpeed",
                pysnmpBaseType="Gauge32",
                value=bdsJsonObject["attribute"]["bandwidth"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"6."+str(index),
                name="ifPhysAddress",
                pysnmpBaseType="OctetString",
                pysnmpRepresentation="hexValue",
                value=bdsJsonObject["attribute"]["mac_address"].replace(":","")))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"7."+str(index),
                name="ifAdminStatus",
                pysnmpBaseType="Integer32",
                value=bdsJsonObject["attribute"]["admin_status"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"8."+str(index),
                name="ifOperStatus",
                pysnmpBaseType="Integer32",
                value=IFOPERSTATUSMAP[int(bdsJsonObject["attribute"]["link_status"])]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"9."+str(index),
                name="ifLastChange",
                pysnmpBaseType="TimeTicks",
                value=0 ))   # Fixme
        targetOidDb.releaseLock()
