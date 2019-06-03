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
from bdssnmpadaptor.rest_server import AsyncioRestServer
from bdssnmpadaptor.snmp_notificator import SnmpNotificationOriginator


def main():
    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(
        epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-f', '--config', default='bdsSnmpTrapAdaptor.yml', type=str,
        help='config file')
    parser.add_argument(
        '--daemonize', action='store_true',
        help='Fork and run as a background process')
    parser.add_argument(
        '--pidfile', type=str,
        help='Path to a PID file the process would create')

    cliargs = parser.parse_args()

    cliargs.config = os.path.abspath(cliargs.config)

    if cliargs.daemonize:
        daemon.daemonize()

    if cliargs.pidfile:
        daemon.pidfile(cliargs.pidfile)

    cliArgsDict = vars(cliargs)

    queue = asyncio.Queue()

    snmpNtfOrg = SnmpNotificationOriginator(cliArgsDict, queue)

    httpServer = AsyncioRestServer(cliArgsDict, queue)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(
            asyncio.gather(snmpNtfOrg.run_forever(), httpServer.initialize())
        )

    except KeyboardInterrupt:
        pass

    loop.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
