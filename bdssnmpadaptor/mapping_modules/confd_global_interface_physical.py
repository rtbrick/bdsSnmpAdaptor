# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import binascii
import struct
import time

from bdssnmpadaptor import mapping_functions

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
    round(struct.Struct('>f').unpack(binascii.unhexlify(x))[0] / 1000) / 1000000 * 8) * 1000


class ConfdGlobalInterfacePhysical(object):
    """Implement SNMP IF-MIB for physical BDS interfaces.

    Populates SNMP managed objects of SNMP `IF-MIB` module from
    `global.interface.physical` BDS table.

    Notes
    -----

    Expected input:

    .. code-block:: json

    {
      "objects": [
        {
          "attribute": {
            "supported_breakout_modes": [
              "4x1G"
            ],
            "configured_layer2_mtu": "dc05",
            "supported_max_layer2_mtu": "f205",
            "supported_min_layer2_mtu": "4000",
            "supported_auto_negotiation": "01",
            "configured_bandwidth": "4e9502f9",
            "default_bandwidth": "4e9502f9",
            "supported_bandwidths": [
              "10.000 Gbps",
              "1.000 Gbps"
            ],
            "interface_name": "ifp-0/0/1",
            "interface_description": "Physical interface #1 from node 0, chip 0",
            "interface_type": "01",
            "bandwidth": "4e9502f9",
            "layer2_mtu": "f205",
            "mac_address": "b86a97a59201",
            "admin_status": "01",
            "link_status": "01"
          },
          "update": true,
          "sequence": 200197
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

        with oidDb.module(__name__) as add:

            add('IF-MIB', 'ifNumber', 0,
                value=len(bdsData['objects']))

            for i, bdsJsonObject in enumerate(bdsData['objects']):

                currentId = bdsJsonObject['sequence']

                ifName = bdsJsonObject['attribute']['interface_name']

                index = mapping_functions.ifIndexFromIfName(ifName)

                #ifPhysicalLocation = mapping_functions.stripIfPrefixFromIfName(ifName)

                if ifName.startswith('if'):     #fix for lo0 in table

                    add('IF-MIB', 'ifIndex', index, value=index)

                    add('IF-MIB', 'ifDescr', index, value=ifName)

                    if 'interface_type' in bdsJsonObject['attribute']:
                        add('IF-MIB', 'ifType', index,
                            value=IFTYPEMAP[int(bdsJsonObject['attribute']['interface_type'])])

                    if 'layer2_mtu' in bdsJsonObject['attribute']:
                        add('IF-MIB', 'ifMtu', index,
                            value=IFMTU_LAMBDA(bdsJsonObject['attribute']['layer2_mtu']))

                    if 'mac_address' in bdsJsonObject['attribute']:
                        add('IF-MIB', 'ifPhysAddress', index,
                            valueFormat='hexValue',
                            value=bdsJsonObject['attribute']['mac_address'].replace(':', ''))

                    if 'admin_status' in bdsJsonObject['attribute']:
                        add('IF-MIB', 'ifAdminStatus', index,
                            value=IFOPERSTATUSMAP[int(bdsJsonObject['attribute']['admin_status'])])

                    if 'link_status' in bdsJsonObject['attribute']:
                        add('IF-MIB', 'ifOperStatus', index,
                            value=IFOPERSTATUSMAP[int(bdsJsonObject['attribute']['link_status'])])

                    if len(bdsIds) == 0:  # first run
                        add('IF-MIB', 'ifLastChange', index, value=0)

                    elif currentId != bdsIds[i]:
                        add('IF-MIB', 'ifLastChange', index, value=currentSysTime)

                    if len(bdsIds) == 0:  # first run
                        add('IF-MIB', 'ifStackLastChange', index, value=0)

                        # Fixme - do we have to observe logical interfaces?
                        add('IF-MIB', 'ifTableLastChange', index, value=0)

                    else:
                        add('IF-MIB', 'ifTableLastChange', index,
                            value=currentSysTime)

                    if 'bandwidth' in bdsJsonObject['attribute']:
                        add('IF-MIB', 'ifSpeed', index,
                            value=IFSPEED_LAMBDA(bdsJsonObject['attribute']['bandwidth']))

        bdsIds[:] = newBdsIds
