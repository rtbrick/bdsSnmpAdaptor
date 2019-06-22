# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import binascii
import struct

from bdssnmpadaptor import mapping_functions

HEX_STRING_LAMBDA = lambda x: int(x, 16)

LELL_LAMBDA = lambda x: int(
    struct.Struct('<q').unpack(binascii.unhexlify(x))[0])


class FwddGlobalInterfacePhysicalStatistics(object):
    """Implement SNMP IF-MIB for physical BDS interfaces.

    Populates SNMP managed objects of SNMP `IF-MIB` module from
    `global.interface.physical.statistics` BDS table.

    Notes
    -----

    Expected input:

    .. code-block:: json

    {
      "objects": [
        {
          "attribute": {
            "bcm_stat_tx_double_vlan_tag_frame": "0000000000000000",
            "bcm_stat_rx_double_vlan_tag_frame": "0000000000000000",
            "bcm_stat_tx_vlan_tag_frame": "0000000000000000",
            "bcm_stat_rx_vlan_tag_frame": "0000000000000000",
            "port_stat_ether_stats_pkts_4096_to_9216_octets": "0000000000000000",
            "port_stat_ether_stats_pkts_2048_to_4095_octets": "0000000000000000",
            "port_stat_ether_stats_pkts_1522_to_2047_octets": "0000000000000000",
            "port_stat_ieee_8021_pfc_indications": "0000000000000000",
            "port_stat_ieee_8021_pfc_requests": "0000000000000000",
            "port_stat_if_out_multicast_pkts": "0000000000000000",
            "port_stat_if_out_broadcast_pkts": "0000000000000000",
            "port_stat_if_in_multicast_pkts": "0000000000000000",
            "port_stat_if_in_broadcast_pkts": "0000000000000000",
            "port_stat_ipv6_if_stats_out_mcast_pkts": "0000000000000000",
            "port_stat_ipv6_if_stats_in_mcast_pkts": "0000000000000000",
            "port_stat_ipv6_if_stats_out_discards": "0000000000000000",
            "port_stat_ipv6_if_stats_out_forw_datagrams": "0000000000000000",
            "port_stat_ipv6_if_stats_in_discards": "0000000000000000",
            "port_stat_ipv6_if_stats_in_addr_errors": "0000000000000000",
            "port_stat_ipv6_if_stats_in_hdr_errors": "0000000000000000",
            "port_stat_ipv6_if_stats_in_receives": "0000000000000000",
            "port_stat_if_hc_out_broadcast_pkts": "0000000000000000",
            "port_stat_if_hc_out_multicast_pkts": "0000000000000000",
            "port_stat_if_hc_out_ucast_pkts": "0000000000000000",
            "port_stat_ether_stats_pkts_512_to_1023_octets": "0000000000000000",
            "port_stat_ether_stats_pkts_256_to_511_octets": "0000000000000000",
            "port_stat_ether_stats_pkts_128_to_255_octets": "0000000000000000",
            "port_stat_ether_stats_pkts_65_to_127_octets": "0000000000000000",
            "port_stat_ether_stats_pkts_64_octets": "0000000000000000",
            "port_stat_ether_stats_fragments": "0000000000000000",
            "port_stat_ether_stats_undersize_pkts": "0000000000000000",
            "port_stat_ether_stats_broadcast_pkts": "0000000000000000",
            "port_stat_ether_stats_multicast_pkts": "0000000000000000",
            "port_stat_ether_stats_drop_events": "0000000000000000",
            "port_stat_dot1d_port_in_discards": "0000000000000000",
            "port_stat_dot1d_tp_port_out_frames": "0000000000000000",
            "port_stat_dot1d_tp_port_in_frames": "0000000000000000",
            "port_stat_dot1d_base_port_mtu_exceeded_discards": "0000000000000000",
            "port_stat_dot1d_base_port_delay_exceeded_drops": "0000000000000000",
            "port_stat_ip_in_discards": "0000000000000000",
            "port_stat_if_out_octets": "0000000000000000",
            "port_stat_if_in_unknown_protos": "0000000000000000",
            "port_stat_if_in_errors": "0000000000000000",
            "port_stat_if_in_discards": "0000000000000000",
            "port_stat_if_in_non_ucast_pkts": "0000000000000000",
            "port_stat_if_in_ucast_pkts": "0000000000000000",
            "port_stat_if_in_octets": "0000000000000000",
            "interface_name": "ifp-0/1/1",
            "port_stat_if_out_ucast_pkts": "0000000000000000",
            "port_stat_if_out_non_ucast_pkts": "0000000000000000",
            "port_stat_if_out_discards": "0000000000000000",
            "port_stat_if_out_errors": "0000000000000000",
            "port_stat_if_out_qlen": "0000000000000000",
            "port_stat_ip_in_receives": "0000000000000000",
            "port_stat_ip_in_hdr_errors": "0000000000000000",
            "port_stat_ip_forw_datagrams": "0000000000000000",
            "port_stat_ether_stats_pkts_1024_to_1518_octets": "0000000000000000",
            "port_stat_ether_stats_oversize_pkts": "0000000000000000",
            "port_stat_ether_rx_oversize_pkts": "0000000000000000",
            "port_stat_ether_tx_oversize_pkts": "0000000000000000",
            "port_stat_ether_stats_jabbers": "0000000000000000",
            "port_stat_ether_stats_octets": "0000000000000000",
            "port_stat_ether_stats_pkts": "0000000000000000",
            "port_stat_ether_stats_collisions": "0000000000000000",
            "port_stat_ether_stats_crc_align_errors": "0000000000000000",
            "port_stat_ether_stats_tx_no_errors": "0000000000000000",
            "port_stat_ether_stats_rx_no_errors": "0000000000000000",
            "port_stat_dot3_stats_alignment_errors": "0000000000000000",
            "port_stat_dot3_stats_fcs_errors": "0000000000000000",
            "port_stat_dot3_stats_single_collision_frames": "0000000000000000",
            "port_stat_dot3_stats_multiple_collision_frames": "0000000000000000",
            "port_stat_dot3_stats_sqet_test_errors": "0000000000000000",
            "port_stat_dot3_stats_deferred_transmissions": "0000000000000000",
            "port_stat_dot3_stats_late_collisions": "0000000000000000",
            "port_stat_dot3_stats_excessive_collisions": "0000000000000000",
            "port_stat_dot3_stats_internal_mac_xmit_errors": "0000000000000000",
            "port_stat_dot3_stats_carrier_sense_errors": "0000000000000000",
            "port_stat_dot3_stats_frame_too_longs": "0000000000000000",
            "port_stat_dot3_stats_internal_mac_receive_errors": "0000000000000000",
            "port_stat_dot3_stats_symbol_errors": "0000000000000000",
            "port_stat_dot3_stat_sol_in_unknown_opcodes": "0000000000000000",
            "port_stat_dot3_in_pause_frames": "0000000000000000",
            "port_stat_dot3_out_pause_frames": "0000000000000000",
            "port_stat_if_hc_in_octets": "0000000000000000",
            "port_stat_if_hc_in_ucast_pkts": "0000000000000000",
            "port_stat_if_hc_in_multicast_pkts": "0000000000000000",
            "port_stat_if_hc_in_broadcast_pkts": "0000000000000000",
            "port_stat_if_hc_out_octets": "0000000000000000"
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

        add = oidDb.add

        for i, bdsJsonObject in enumerate(bdsData['objects']):

            attribute = bdsJsonObject['attribute']

            ifName = attribute['interface_name']

            index = mapping_functions.ifIndexFromIfName(ifName)

            add('IF-MIB', 'ifInOctets', index,
                value=LELL_LAMBDA(attribute['port_stat_if_in_octets']))

            add('IF-MIB', 'ifInUcastPkts', index,
                value=LELL_LAMBDA(attribute['port_stat_if_in_ucast_pkts']))

            add('IF-MIB', 'ifInNUcastPkts', index,
                value=LELL_LAMBDA(attribute['port_stat_if_in_non_ucast_pkts']))

            add('IF-MIB', 'ifInDiscards', index,
                value=LELL_LAMBDA(attribute['port_stat_if_in_discards']))

            add('IF-MIB', 'ifInErrors', index,
                value=LELL_LAMBDA(attribute['port_stat_if_in_errors']))

            add('IF-MIB', 'ifInUnknownProtos', index,
                value=LELL_LAMBDA(attribute['port_stat_if_in_unknown_protos']))

            add('IF-MIB', 'ifOutOctets', index,
                value=LELL_LAMBDA(attribute['port_stat_if_out_octets']))

            add('IF-MIB', 'ifOutUcastPkts', index,
                value=LELL_LAMBDA(attribute['port_stat_if_out_ucast_pkts']))

            add('IF-MIB', 'ifOutNUcastPkts', index,
                value=LELL_LAMBDA(attribute['port_stat_if_out_non_ucast_pkts']))

            add('IF-MIB', 'ifOutDiscards', index,
                value=LELL_LAMBDA(attribute['port_stat_if_out_discards']))

            add('IF-MIB', 'ifOutErrors', index,
                value=LELL_LAMBDA(attribute['port_stat_if_out_errors']))

            add('IF-MIB', 'ifOutQLen', index,
                value=LELL_LAMBDA(attribute['port_stat_if_out_qlen']))

        # count *all* IF-MIB interfaces we currently have - some
        # may be contributed by other modules
        ifNumber = len(oidDb.getObjectsByName('IF-MIB', 'ifIndex'))

        add('IF-MIB', 'ifNumber', 0, value=ifNumber)

        bdsIds[:] = newBdsIds
