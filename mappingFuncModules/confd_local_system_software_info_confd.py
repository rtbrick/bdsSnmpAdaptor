import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from bdsMappingFunctions import bdsMappingFunctions
import logging
from oidDb import OidDbItem
import asyncio

class confd_local_system_software_info_confd(object):
    """


    """
    @classmethod
    async def setOids(self,bdsJsonResponseDict,targetOidDb):
        oidSegment = "1.3.6.1.4.1.50058.101.1.1."
        targetOidDb.setLock()
        targetOidDb.deleteOidsWithPrefix(oidSegment)  #delete existing TableOids
        for bdsJsonObject in bdsJsonResponseDict["objects"]:
            indexString = bdsJsonObject["attribute"]["library"]
            indexCharList = [str(ord(c)) for c in indexString]
            index = str(len(indexCharList)) + "." + ".".join(indexCharList)  # FIXME add description
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"1."+str(index),
                name="name", pysnmpBaseType="OctetString",
                value=indexString))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"2."+str(index),
                name="commitId", pysnmpBaseType="OctetString",
                value=bdsJsonObject["attribute"]["commit_id"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"3."+str(index),
                name="commitDate", pysnmpBaseType="OctetString",
                value=bdsJsonObject["attribute"]["commit_date"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"4."+str(index),
                name="packageDate", pysnmpBaseType="OctetString",
                value=bdsJsonObject["attribute"]["package_date"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"5."+str(index),
                name="vcCheckout", pysnmpBaseType="OctetString",
                value=bdsJsonObject["attribute"]["vc_checkout"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"6."+str(index),
                name="branch", pysnmpBaseType="OctetString",
                value=bdsJsonObject["attribute"]["branch"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"7."+str(index),
                name="libraryVersion", pysnmpBaseType="OctetString",
                value=bdsJsonObject["attribute"]["version"]))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                oid = oidSegment+"8."+str(index),
                name="sourcePath", pysnmpBaseType="OctetString",
                value=bdsJsonObject["attribute"]["source_path"]))
        # in addition the SW Info Flag is set by
        # creating an abbreviated string over all modules
        swString = bdsMappingFunctions.stringFromSoftwareInfo (bdsJsonResponseDict)
        targetOidDb.insertOid(newOidItem = OidDbItem(
            oid = "1.3.6.1.2.1.1.1.0",
            name="sysDescr", pysnmpBaseType="OctetString",
            value=swString ))
        targetOidDb.releaseLock()
