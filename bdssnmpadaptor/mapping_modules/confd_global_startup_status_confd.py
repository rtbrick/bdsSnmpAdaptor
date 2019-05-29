# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#

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
    def setOids(cls, bdsJsonResponseDict, targetOidDb,
                tableSequenceList, birthday):

        with targetOidDb.module(__name__) as add:

            for index0, bdsJsonObject in enumerate(bdsJsonResponseDict['objects']):
                index = index0 + 1

                add('HOST-RESOURCES-MIB', 'hrSWOSIndex', index, value=index)

                add('HOST-RESOURCES-MIB', 'hrSWRunName', index,
                    value=bdsJsonObject['attribute']['module_name'])

                add('HOST-RESOURCES-MIB', 'hrSWRunID', index, value='0.0')

                add('HOST-RESOURCES-MIB', 'hrSWRunPath', index,
                    value=bdsJsonObject['attribute']['bd_name'])

                add('HOST-RESOURCES-MIB', 'hrSWRunParameters', index, value='')

                add('HOST-RESOURCES-MIB', 'hrSWRunType', index, value=4)  # 4 - application

                add('HOST-RESOURCES-MIB', 'hrSWRunStatus', index,
                    value=HRSWRUNSTATUSMAP[int(bdsJsonObject['attribute']['startup_status'])])
