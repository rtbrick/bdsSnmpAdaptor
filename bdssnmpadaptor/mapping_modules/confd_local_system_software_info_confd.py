# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
from pysnmp.proto.rfc1902 import OctetString

from bdssnmpadaptor.mapping_functions import BdsMappingFunctions
from bdssnmpadaptor.oidDb import OidDbItem


class ConfdLocalSystemSoftwareInfoConfd(object):
    """Local system software information
    """

    @classmethod
    async def setOids(cls, bdsJsonResponseDict, targetOidDb,
                      tableSequenceList, birthday):
        swString = BdsMappingFunctions.stringFromSoftwareInfo(bdsJsonResponseDict)

        targetOidDb.insertOid(
            newOidItem=OidDbItem(
                bdsMappingFunc=__name__,
                oid="1.3.6.1.2.1.1.1.0",
                name="sysDescr", pysnmpBaseType=OctetString,
                value=swString))

        # oidSegment = "1.3.6.1.2.1.1.1.0"
        # targetOidDb.setLock()
        # targetOidDb.deleteOidsWithPrefix(oidSegment)  #delete existing TableOids
        # for index,bdsJsonObject in enumerate(bdsJsonResponseDict["objects"]):
        #     #indexString = bdsJsonObject["attribute"]["library"]
        #     #indexCharList = [str(ord(c)) for c in indexString]
        #     #index = str(len(indexCharList)) + "." + ".".join(indexCharList)  # FIXME add description
        #     targetOidDb.insertOid(newOidItem = OidDbItem(
        #         oid = oidSegment+"1."+str(index),
        #         name="hrSWRunIndex", pysnmpBaseType=Integer32,
        #         value=index))
        #     targetOidDb.insertOid(newOidItem = OidDbItem(
        #         oid = oidSegment+"2."+str(index),
        #         name="hrSWRunName", pysnmpBaseType=OctetString,
        #         value=bdsJsonObject["attribute"]["commit_id"]))
        #     targetOidDb.insertOid(newOidItem = OidDbItem(
        #         oid = oidSegment+"3."+str(index),
        #         name="commitDate", pysnmpBaseType=OctetString,
        #         value=bdsJsonObject["attribute"]["commit_date"]))
        #     targetOidDb.insertOid(newOidItem = OidDbItem(
        #         oid = oidSegment+"4."+str(index),
        #         name="packageDate", pysnmpBaseType=OctetString,
        #         value=bdsJsonObject["attribute"]["package_date"]))
        #     targetOidDb.insertOid(newOidItem = OidDbItem(
        #         oid = oidSegment+"5."+str(index),
        #         name="vcCheckout", pysnmpBaseType=OctetString,
        #         value=bdsJsonObject["attribute"]["vc_checkout"]))
        #     targetOidDb.insertOid(newOidItem = OidDbItem(
        #         oid = oidSegment+"6."+str(index),
        #         name="branch", pysnmpBaseType=OctetString,
        #         value=bdsJsonObject["attribute"]["branch"]))
        #     targetOidDb.insertOid(newOidItem = OidDbItem(
        #         oid = oidSegment+"7."+str(index),
        #         name="libraryVersion", pysnmpBaseType=OctetString,
        #         value=bdsJsonObject["attribute"]["version"]))
        #     targetOidDb.insertOid(newOidItem = OidDbItem(
        #         oid = oidSegment+"8."+str(index),
        #         name="sourcePath", pysnmpBaseType=OctetString,
        #         value=bdsJsonObject["attribute"]["source_path"]))
        # # in addition the SW Info Flag is set by
        # # creating an abbreviated string over all modules
        # targetOidDb.releaseLock()
