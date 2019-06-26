# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import time

from bdssnmpadaptor import mapping_functions


class FfwdDefaultInterfaceLogical(object):
    """Implement SNMP IF-MIB for logical BDS interfaces.

    Populates SNMP managed objects of SNMP `IF-MIB` module from
    `default.interface.logical` BDS table.

    Notes
    -----

    Expected input:

    .. code-block:: json

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

        currentSysTime = int((time.time() - birthday) * 100)

        add = oidDb.add

        for i, bdsJsonObject in enumerate(bdsData['objects']):

            ifName = bdsJsonObject['attribute']['interface_name']

            index = mapping_functions.ifIndexFromIfName(ifName)

            add('IF-MIB', 'ifIndex', index, value=index)

            add('IF-MIB', 'ifDescr', index,
                value=bdsJsonObject['attribute']['interface_name'])

            add('IF-MIB', 'ifType', index, value=6)

            if i < len(bdsIds):
                # possible table entry change
                ifLastChange = None if newBdsIds[i] == bdsIds[i] else currentSysTime

            else:
                # initial run or table size change
                ifLastChange = currentSysTime if bdsIds else 0

        # count *all* IF-MIB interfaces we currently have - some
        # may be contributed by other modules
        ifNumber = len(oidDb.getObjectsByName('IF-MIB', 'ifIndex'))

        add('IF-MIB', 'ifNumber', 0, value=ifNumber)

        add('IF-MIB', 'ifStackLastChange', 0,
            value=currentSysTime if bdsIds else 0)
        add('IF-MIB', 'ifTableLastChange', 0,
            value=currentSysTime if bdsIds else 0)

        bdsIds[:] = newBdsIds
