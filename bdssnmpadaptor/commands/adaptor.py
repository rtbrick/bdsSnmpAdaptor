#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import argparse
import asyncio
import os
import sys

from bdssnmpadaptor import daemon
from bdssnmpadaptor.access import BdsAccess
from bdssnmpadaptor.snmp_responder import SnmpCommandResponder
from bdssnmpadaptor.mib_controller import MibInstrumController
from bdssnmpadaptor.rest_server import AsyncioRestServer
from bdssnmpadaptor.snmp_notificator import SnmpNotificationOriginator


def main():
    epilogTXT = """
BDS SNMP adaptor tool implements SNMP interface to RtBrick bare metal
switch platform.

Conceptually, this tool contains four parts working together to implement
SNMP<->REST adaptation layer. These parts are:

* BDS REST API client pulling data from RtBrick system and populating SNMP
  managed objects (MIBs) it serves
* SNMP command responder supporting SNMP GET/GETNEXT/GETBULK commands
* REST API server listening for events coming from RtBrick system
* SNMP notification originator emitting SNMP TRAP messages in response
  to RtBrick system events
  
All these parts are driven by .yaml configuration file. Conceptually,
each of the above mentioned components have its own branch in the
configuration.
 
See https://www.rtbrick.com for RtBrick product information.
"""

    parser = argparse.ArgumentParser(
        epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-f', '--config',
        default='/etc/bds-snmp-adaptor/bds-snmp-adaptor.yml', type=str,
        help='Path to config file')
    parser.add_argument(
        '--daemonize', action='store_true',
        help='Fork and run as a background process')
    parser.add_argument(
        '--pidfile', type=str,
        help='Path to a PID file the process would create')

    args = parser.parse_args()

    args.config = os.path.abspath(args.config)

    if args.daemonize:
        daemon.daemonize()

    if args.pidfile:
        daemon.pidfile(args.pidfile)

    bdsAccess = BdsAccess(args)

    mibController = MibInstrumController()
    mibController.setOidDbAndLogger(bdsAccess.oidDb, args)

    SnmpCommandResponder(args, mibController)

    queue = asyncio.Queue()

    snmpNtfOrg = SnmpNotificationOriginator(args, queue)

    httpServer = AsyncioRestServer(args, queue)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(
            asyncio.gather(bdsAccess.run_forever(),
                           snmpNtfOrg.run_forever(), httpServer.initialize())
        )

    except KeyboardInterrupt:
        pass

    loop.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
