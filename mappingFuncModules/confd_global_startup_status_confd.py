import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from bdsMappingFunctions import bdsMappingFunctions
import logging
from oidDb import OidDbItem
import asyncio

class confd_global_startup_status_confd(object):

    """


    """


    @classmethod
    async def setOids(self,bdsJsonResponseDict,targetOidDb):
        oidSegment = "1.3.6.1.4.1.50058.101.3.1."
        targetOidDb.setLock()
        targetOidDb.deleteOidsWithPrefix(oidSegment)  #delete existing TableOids
        for bdsJsonObject in bdsJsonResponseDict["objects"]:
            indexString = bdsJsonObject["attribute"]["module_name"]
            indexCharList = [str(ord(c)) for c in indexString]
            index = str(len(indexCharList)) + "." + ".".join(indexCharList)
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"1."+str(index),
                name="moduleName",
                pysnmpBaseType="OctetString",
                value=indexString))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"2."+str(index),
                name="bdName", pysnmpBaseType="OctetString",
                value=bdsJsonObject["attribute"]["bd_name"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"3."+str(index),
                name="upTime", pysnmpBaseType="OctetString",  # FIXME change type
                value=bdsJsonObject["attribute"]["up_time"])) # FIXME calc time
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"4."+str(index),
                name="upTime", pysnmpBaseType="OctetString",
                value=bdsJsonObject["attribute"]["startup_status"]))
        #logging.debug(len(targetOidDb.oidDict.keys()))
        #logging.debug(targetOidDb)
        targetOidDb.releaseLock()
