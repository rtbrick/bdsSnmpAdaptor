#!/usr/bin/env python

import logging
import argparse
import yaml
from pysnmp.hlapi import *


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="SNMP Agent serving BDS data")

    parser.add_argument('--bds-map',
                        metavar='<PATH>',
                        type=str,
                        default='snmpOidMapping.yml',
                        help='SNMP to BDS objects map file [snmpOidMapping.yml]')

    parser.add_argument('--snmp-agent-ipv4-address',
                        metavar='IPv4',
                        type=str,
                        default='127.0.0.1',
                        help='SNMP agent listens at this address [127.0.0.1]')

    parser.add_argument('--snmp-agent-udp-port',
                        metavar='<INT>',
                        type=int,
                        default=161,
                        help='SNMP agent listens at this UDP port [161]')

    parser.add_argument('--snmp-community-name',
                        metavar='<STRING>',
                        type=str,
                        default='public',
                        help='SNMP agent responds to this community name [public]')

    args = parser.parse_args()

    logging.getLogger().setLevel(logging.DEBUG)

    with open(args.bds_map, 'r') as stream:
        oidDict = yaml.load(stream)

    oids = sorted(list(oidDict))

    snmpEngine = SnmpEngine()

    udpTransportTarget = UdpTransportTarget((args.snmp_agent_ipv4_address, args.snmp_agent_udp_port), retries=0, timeout=3)
    snmpCommunity = CommunityData('public')

    logging.debug('querying SNMP SNMP agent at {}'.format(udpTransportTarget))
    logging.debug('using SNMP community name {}'.format(snmpCommunity))

    for oid in oids:
        logging.debug('trying OID {}'.format(oid))

        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(snmpEngine,
                   snmpCommunity,
                   udpTransportTarget,
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )

        if errorIndication:
            logging.debug('OID {} not fetched: {}'.format(oid, errorIndication))

        elif errorStatus:
            logging.debug('OID {} not fetched: {}'.format(oid, errorStatus.prettyPrint()))

        else:
            for varBind in varBinds:
                logging.debug('fetched {}'.format(' = '.join([x.prettyPrint() for x in varBind])))
