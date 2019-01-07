#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  \author    Stefan Lieberth / Maik Pfeil
#  \version   3.3.01

import asyncio
import logging
import yaml
from copy import deepcopy
import pprint
import re
import datetime
import json
import sys
import argparse


from aiohttp import web
from aiohttp import web
from aiohttp.web import Application, Response, StreamResponse, run_app

import aioredis



class restHttpServer():

    def __init__(self,**kwargs):
        aiohttp_logger = logging.getLogger('restBrickLogToRedis')
        aiohttp_logger.setLevel(logging.WARNING)
        self.requestCounter = 0 


    def init(self,loop):
        app = Application()

        app.router.add_route('*','/{tail:.*}', self.index)
        return app


    async def index(self,request):
        #print (request.__dict__)
        peerIP = request._transport_peername[0]
        self.requestCounter += 1                ##Fixme overrun
        #print (request.headers)
        data = {'headers': dict(request.headers)}
        jsonTxt = await request.text() #
        self.redisServer = await aioredis.create_redis_pool(
            'redis://localhost')
        redisKey = "rtbrickLogging-{}-{}".format(peerIP,self.requestCounter )
        print(redisKey,jsonTxt)
        await self.redisServer.setex(redisKey, 60,  jsonTxt )
        return web.json_response(data)


if __name__ == "__main__":

    logLevel = logging.ERROR
    #logLevel = logging.DEBUG
    logging.basicConfig(filename="myRestHttpServer.log", filemode='w', level=logLevel)
    logging.getLogger().setLevel(logLevel)
    console = logging.StreamHandler()
    console.setLevel(logLevel)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    #redisServer = aioredis.create_redis('redis://localhost')
    myHttpServer = restHttpServer()
    loop = asyncio.get_event_loop()
    app = myHttpServer.init(loop)
    if app != None:
        loop.run_until_complete(run_app(app,port=5000))
    else:
        logging.error("cannot load app")
