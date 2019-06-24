# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import binascii
import struct

from bdssnmpadaptor import if_tools

IFTYPEMAP = {
    1: 6  # ethernet-csmacd(6)
}

IFOPERSTATUSMAP = {
    0: 2,  # down(2)
    1: 1,  # up(1),       -- ready to pass packets
    2: 3,  # testing(3)   -- in some test mode
    3: 3  # testing(3)   -- in some test mode
}

IFMTU_LAMBDA = lambda x: int(
    struct.Struct('<h').unpack(binascii.unhexlify(x))[0])

IFSPEED_LAMBDA = lambda x: int(
    struct.Struct('>f').unpack(binascii.unhexlify(x))[0] / 1000000 * 8)


# HEX_STRING_LAMBDA = lambda x : int(x,16)
# IFMTU_LAMBDA = lambda x : int(''.join([m[2:4]+m[0:2] for m in [x[i:i+4] for i in range(0,len(x),4)]]),16)


class ConfdGlobalInterfaceContainer(object):
    """Implement SNMP IF-MIB for container BDS interfaces.

    Populates SNMP managed objects of SNMP `IF-MIB` module from
    `global.interface.container` BDS table.

    Notes
    -----

    Expected input:

    .. code-block:: json

    {
      "objects": [
        {
          "sequence": 200197,
          "update": true,
          "attribute": {
            "interface_name": "ifc-0/0/0/1",
            "interface_description": "Container interface for ifp-0/0/1",
            "encapsulation_type": "01",
            "bandwidth": "4e9502f9",
            "layer2_mtu": "f205",
            "admin_status": "01",
            "link_status": "01",
            "mac_address": "b86a97a59201",
            "physical_interfaces": [
              "ifp-0/0/1"
            ]
          }
        }
      ]
    }
    """

    @classmethod
    def setOids(cls, oidDb, bdsData, bdsIds, uptime):
        """Populates OID DB with BDS information.

        Takes known objects from JSON document, puts them into
        the OID DB as specific MIB managed objects.

        Args:
            oidDb (OidDb): OID DB instance to work on
            bdsData (dict): BDS information to put into OID DB
            bdsIds (list): list of last known BDS record sequence IDs
            uptime (int): system uptime in hundreds of seconds

        Raises:
            BdsError: on OID DB population error
        """

        newBdsIds = [obj['sequence'] for obj in bdsData['objects']]

        if newBdsIds == bdsIds:
            return

        add = oidDb.add

        for i, bdsObject in enumerate(bdsData['objects']):

            ifName = bdsObject['attribute']['interface_name']

            index = if_tools.ifIndexFromIfName(ifName)

            ifSpeed = IFSPEED_LAMBDA(bdsObject['attribute']['bandwidth'])

            if ifSpeed == 100000000:
                ifGigEtherName = 'hundredGe-' + if_tools.stripIfPrefixFromIfName(ifName)

            elif ifSpeed == 10000000:
                ifGigEtherName = 'tenGe-' + if_tools.stripIfPrefixFromIfName(ifName)

            else:
                ifGigEtherName = 'ge-' + if_tools.stripIfPrefixFromIfName(ifName)

            add('IF-MIB', 'ifIndex', index, value=index)

            add('IF-MIB', 'ifDescr', index, value=ifGigEtherName)

            add('IF-MIB', 'ifType', index,
                value=IFTYPEMAP[int(bdsObject['attribute']['encapsulation_type'])])

            add('IF-MIB', 'ifMtu', index,
                value=IFMTU_LAMBDA(bdsObject['attribute']['layer2_mtu']))

            add('IF-MIB', 'ifPhysAddress', index,
                value=bdsObject['attribute']['mac_address'].replace(':', ''),
                valueFormat='hexValue')

            add('IF-MIB', 'ifAdminStatus', index,
                value=bdsObject['attribute']['admin_status'])

            add('IF-MIB', 'ifOperStatus', index,
                value=IFOPERSTATUSMAP[int(bdsObject['attribute']['link_status'])])

            add('IF-MIB', 'ifSpeed', index,
                value=IFSPEED_LAMBDA(bdsObject['attribute']['bandwidth']))

            if i < len(bdsIds):
                # possible table entry change
                ifLastChange = None if newBdsIds[i] == bdsIds[i] else uptime

            else:
                # initial run or table size change
                ifLastChange = uptime if bdsIds else 0

            add('IF-MIB', 'ifLastChange', index, value=ifLastChange)

        # count *all* IF-MIB interfaces we currently have - some
        # may be contributed by other modules
        ifNumber = len(oidDb.getObjectsByName('IF-MIB', 'ifIndex'))

        add('IF-MIB', 'ifNumber', 0, value=ifNumber)

        add('IF-MIB', 'ifStackLastChange', 0, value=uptime if bdsIds else 0)
        add('IF-MIB', 'ifTableLastChange', 0, value=uptime if bdsIds else 0)

        bdsIds[:] = newBdsIds
