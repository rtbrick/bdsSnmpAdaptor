# -*- coding: future_fstrings -*-
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
    """Implement SNMP HOST-RESOURCES-MIB for BDS system.

    Populates SNMP managed objects of SNMP `HOST-RESOURCES-MIB` module from
    `global.startup.status.confd` BDS table.

    Notes
    -----

    Expected input:

    .. code-block:: json

    {
      "objects": [
        {
          "sequence": 5,
          "update": true,
          "attribute": {
            "module_name": "bd",
            "startup_status": "02",
            "up_time": "a03d475c642e696e",
            "bd_name": "confd"
          }
        }
      ]
    }
    """

    @classmethod
    def setOids(cls, oidDb, bdsData, bdsIds, birthday):
        """Populates OID DB with BDS information.

        Takes known objects from JSON document, puts them into
        the OID DB as specific MIB managed objects.

        Args:
            oidDb (OidDb): OID DB instance to work on
            bdsData (dict): BDS information to put into OID DB
            bdsIds (list): list of last known BDS record sequence IDs
            birthday (float): timestamp of system initialization

        Raises:
            BdsError: on OID DB population error
        """

        newBdsIds = [obj['sequence'] for obj in bdsData['objects']]

        if newBdsIds == bdsIds:
            return

        add = oidDb.add

        for index0, bdsJsonObject in enumerate(bdsData['objects']):
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

        bdsIds[:] = newBdsIds
