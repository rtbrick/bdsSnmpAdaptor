import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from bdssnmpadaptor.bdsMappingFunctions import bdsMappingFunctions
#import pytablewriter
#import yaml
from bdssnmpadaptor.oidDb import OidDbItem
import struct
import binascii


HEX_STRING_LAMBDA = lambda x : int(x,16)

littleEndianLongLongStruct = struct.Struct('<q')
LELL_LAMBDA = lambda x : int(littleEndianLongLongStruct.unpack(binascii.unhexlify(x))[0])


class fwdd_global_interface_physical_statistics(object):

    """

    curl -X POST -H "Content-Type: application/json" -H "Accept: */*" -H "connection: close"\
        -H "Accept-Encoding: application/json"\
        -d '{"table": {"table_name": "global.interface.physical.statistics"}}'\
        "http://10.0.3.10:5002/bds/table/walk?format=raw" | jq '.'

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
      ],
      "table": {
        "table_name": "global.interface.physical.statistics"
      }
    }

    """

    @classmethod
    async def setOids(self,bdsJsonResponseDict,targetOidDb):
        oidSegment = "1.3.6.1.2.1.2.2.1."
        targetOidDb.setLock()
        #targetOidDb.deleteOidsWithPrefix(oidSegment)  #delete existing TableOids
        for i,bdsJsonObject in enumerate(bdsJsonResponseDict["objects"]):
            ifName = bdsJsonObject["attribute"]["interface_name"]
            index =  bdsMappingFunctions.ifIndexFromIfName(ifName)
            #index =  i + 1
            ifPhysicalLocation = bdsMappingFunctions.stripIfPrefixFromIfName(ifName)
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"10."+str(index),
                name="ifInOctets",
                pysnmpBaseType="Counter32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_in_octets"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"11."+str(index),
                name="ifInUcastPkts",
                pysnmpBaseType="Counter32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_in_ucast_pkts"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"12."+str(index),
                name="ifInNUcastPkts",
                pysnmpBaseType="Counter32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_in_non_ucast_pkts"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"13."+str(index),
                name="ifInDiscards",
                pysnmpBaseType="Counter32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_in_discards"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"14."+str(index),
                name="ifInErrors",
                pysnmpBaseType="Counter32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_in_errors"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"15."+str(index),
                name="ifInUnknownProtos",
                pysnmpBaseType="Counter32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_in_unknown_protos"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"16."+str(index),
                name="ifOutOctets",
                pysnmpBaseType="Counter32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_out_octets"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"17."+str(index),
                name="ifOutUcastPkts",
                pysnmpBaseType="Counter32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_out_ucast_pkts"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"18."+str(index),
                name="ifOutNUcastPkts",
                pysnmpBaseType="Counter32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_out_non_ucast_pkts"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"19."+str(index),
                name="ifOutDiscards",
                pysnmpBaseType="Counter32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_out_discards"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"20."+str(index),
                name="ifOutErrors",
                pysnmpBaseType="Counter32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_out_errors"])))
            targetOidDb.insertOid(newOidItem = OidDbItem(
                bdsMappingFunc = "fwdd_global_interface_physical_statistics",
                oid = oidSegment+"21."+str(index),
                name="ifOutQLen",
                pysnmpBaseType="Gauge32",
                value=LELL_LAMBDA(bdsJsonObject["attribute"]["port_stat_if_out_qlen"])))
