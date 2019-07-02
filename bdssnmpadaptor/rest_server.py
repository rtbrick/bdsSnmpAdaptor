# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import asyncio
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

    Args:
        args (object): argparse namespace object holding command-line options
        queue (Queue): asyncio `Queue` instance used for passing received
            REST API calls on to outer consumers

    """
    def __init__(self, args, queue):

        configDict = loadConfig(args.config)

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.listeningIP = configDict['notificator']['listeningIP']
        self.listeningPort = configDict['notificator']['listeningPort']

        self.requestCounter = 0

        self.queue = queue

    @asyncio.coroutine
    def handler(self, request):
        """Handle REST API call

        Args:
            request (Request): aiohttp `Request` object representing incoming
                REST API call

        Returns:
            Response: aiohttp `Response` object indicating the outcome
                of the request

        Note:
            This coroutine queues the request and responds immediately even
            if further processing fails.
        """
        # depending on aiohttp version, there can be different ways of
        # getting remote address
        try:
            peer = request.remote

        except AttributeError:
            try:
                peer = request._transport_peername

            except AttributeError:
                try:
                    peer = request._transport._extra['peername']

                except (AttributeError, KeyError):
                    peer = 'unknown'

        self.requestCounter += 1

        self.moduleLogger.info(
            f'handler: incoming request peer {peer}, headers '
            f'{request.headers}, count {self.requestCounter}')

        data = {
            'headers': dict(request.headers)
        }

        # TODO: use aiohttp for json parsing, handle JSON errors
        jsonTxt = yield from request.text()

        try:
            bdsLogDict = json.loads(jsonTxt)

        except Exception as exc:
            self.moduleLogger.error(
                f'cannot convert JSON to dict {jsonTxt}: {exc}')

        else:
            self.queue.put_nowait(bdsLogDict)

        return web.json_response(data)

    @asyncio.coroutine
    def initialize(self):
        """Create REST API endpoint

        Returns:
            object: `asyncio` awaitable object
        """
        server = web.Server(self.handler)

        loop = asyncio.get_event_loop()

        yield from loop.create_server(server, self.listeningIP, self.listeningPort)
