# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
from pysnmp.proto.rfc1902 import Integer32
from pysnmp.proto.rfc1902 import ObjectIdentifier
from pysnmp.proto.rfc1902 import OctetString

from bdssnmpadaptor.oidDb import OidDbItem

# running(1),
# runnable(2),    -- waiting for resource
#                 -- (i.e., CPU, memory, IO)
# notRunnable(3), -- loaded but waiting for event
# invalid(4)      -- not loaded
HRSWRUNSTATUSMAP = {
    2: 1,  # running(1)
}


class ConfdGlobalStartupStatusConfd(object):
    """Startup status

    curl -X POST -H "Content-Type: application/json" -H "Accept: */*" -v -H "connection: close"
         -H "Accept-Encoding: application/json"
         -d '{"table": {"table_name": "global.startup.status.confd"}}' "http://10.0.3.50:2002/bds/table/walk?format=raw"

    { "table": { "table_name": "global.startup.status.confd" },
      "objects": [
         { "sequence": 5, "update": true, "attribute":
           { "module_name": "bd", "startup_status": "02", "up_time": "a03d475c642e696e", "bd_name": "confd" } },
         { "sequence": 6, "update": true, "attribute":
           { "module_name": "bds", "startup_status": "02", "up_time": "a03d475c2e696e63", "bd_name": "confd" } },
         { "sequence": 3, "update": true, "attribute":
           { "module_name": "lwip", "startup_status": "02", "up_time": "a03d475c6c6f672e", "bd_name": "confd" } } ] }

    """

    @classmethod
    async def setOids(cls, bdsJsonResponseDict, targetOidDb,
                      tableSequenceList, birthday):
        oidSegment = '1.3.6.1.2.1.25.4.'

        targetOidDb.insertOid(newOidItem=OidDbItem(
            bdsMappingFunc=__name__,
            oid=oidSegment + '1.0',
            name='hrSWOSIndex',
            pysnmpBaseType=Integer32,
            value=0))

        oidSegment = '1.3.6.1.2.1.25.4.2.1.'

        for index0, bdsJsonObject in enumerate(bdsJsonResponseDict['objects']):
            index = index0 + 1

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc=__name__,
                    oid=oidSegment + '1.' + str(index),
                    name='hrSWRunIndex',
                    pysnmpBaseType=Integer32,
                    value=index))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc=__name__,
                    oid=oidSegment + '2.' + str(index),
                    name='hrSWRunName', pysnmpBaseType=OctetString,
                    value=bdsJsonObject['attribute']['module_name']))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc=__name__,
                    oid=oidSegment + '3.' + str(index),
                    name='hrSWRunID', pysnmpBaseType=ObjectIdentifier,
                    value='0.0'))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc=__name__,
                    oid=oidSegment + '4.' + str(index),
                    name='hrSWRunPath', pysnmpBaseType=OctetString,
                    value=bdsJsonObject['attribute']['bd_name']))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc=__name__,
                    oid=oidSegment + '5.' + str(index),
                    name='hrSWRunParameters', pysnmpBaseType=OctetString,
                    value=''))

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc=__name__,
                    oid=oidSegment + '6.' + str(index),
                    name='hrSWRunType', pysnmpBaseType=Integer32,
                    value=4))  ## fixed value 4 for application

            targetOidDb.insertOid(
                newOidItem=OidDbItem(
                    bdsMappingFunc=__name__,
                    oid=oidSegment + '7.' + str(index),
                    name='hrSWRunStatus', pysnmpBaseType=Integer32,
                    value=HRSWRUNSTATUSMAP[int(bdsJsonObject['attribute']['startup_status'])]))

        # logging.debug(len(targetOidDb.oidDict)
        # logging.debug(targetOidDb)
        # targetOidDb.releaseLock()
