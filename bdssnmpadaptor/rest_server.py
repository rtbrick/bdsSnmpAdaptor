# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import json
import os

from aiohttp import web

from bdssnmpadaptor.config import loadConfig
from bdssnmpadaptor.log import set_logging


class AsyncioRestServer(object):
    """REST API server for receiving notifications

    Implements HTTP server running within asyncio loop and receiving
    notification through REST API. Places received notifications
    into a queue for consumers to read from.
    """
    def __init__(self, cliArgsDict, queue):

        self.moduleFileNameWithoutPy, _ = os.path.splitext(os.path.basename(__file__))

        configDict = loadConfig(cliArgsDict['config'])

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.listeningIP = configDict['notificator']['listeningIP']
        self.listeningPort = configDict['notificator']['listeningPort']

        self.requestCounter = 0

        self.queue = queue

    async def handler(self, request):
        """Handle HTTP request

        A coroutine that accepts a Request instance as its only argument.
        Returns 200 with a copy of the incoming header dict.
        """
        peerIP = request._transport_peername[0]

        self.requestCounter += 1

        self.moduleLogger.info(
            f'handler: incoming request peerIP {peerIP}, headers '
            f'{request.headers}, count {self.requestCounter}')

        data = {
            'headers': dict(request.headers)
        }

        jsonTxt = await request.text()

        try:
            bdsLogDict = json.loads(jsonTxt)

        except Exception as exc:
            self.moduleLogger.error(
                f'cannot convert JSON to dict {jsonTxt}: {exc}')

        else:
            self.queue.put_nowait(bdsLogDict)

        return web.json_response(data)

    async def initialize(self):
        server = web.Server(self.handler)
        runner = web.ServerRunner(server)

        await runner.setup()

        site = web.TCPSite(runner, self.listeningIP, self.listeningPort)

        await site.start()

