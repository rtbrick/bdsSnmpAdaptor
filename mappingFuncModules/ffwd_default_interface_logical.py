import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from bdsMappingFunctions import bdsMappingFunctions
import logging
from oidDb import OidDbItem
import asyncio

class ffwd_default_interface_logical(object):

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
                value= 6 ))
        targetOidDb.releaseLock()
