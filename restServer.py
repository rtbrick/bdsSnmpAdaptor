
#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  \author    Stefan Lieberth / Maik Pfeil
#  \version   3.3.01

import asyncio
import logging
from logging.handlers import RotatingFileHandler
import yaml
from copy import deepcopy
import pprint
import re
import datetime
import json
import sys
import argparse

from aiohttp import web
from aiohttp.web import Application, Response, StreamResponse, run_app
import aioredis

from bdsSnmpAdapterManager import loadBdsSnmpAdapterConfigFile
from bdsSnmpAdapterManager import set_logging

class restHttpServer():

    def __init__(self,configDict):
        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],self.moduleFileNameWithoutPy)
        set_logging(configDict,self.moduleFileNameWithoutPy,self)
        self.listeningIP =  configDict["listeningIP"]
        self.listeningPort = configDict["listeningPort"]
        self.redisServerIp = configDict["redisServerIp"]
        self.redisServerPort = configDict["redisServerPort"]
        self.requestCounter = 0


    async def handler(self,request):
        peerIP = request._transport_peername[0]
        self.requestCounter += 1
        self.moduleLogger.info ("handler: peerIP:{} headers:{} counter:{} ".format(peerIP,request.headers,self.requestCounter))
        data = {'headers': dict(request.headers)}
        jsonTxt = await request.text() #
        self.redisServer = await aioredis.create_redis((self.redisServerIp,self.redisServerPort))
        redisKey = "rtbrickLogging-{}-{}".format(peerIP,self.requestCounter )
        self.moduleLogger.info ("redisKey:{},jsonTxt:{}".format(redisKey,jsonTxt))
        await self.redisServer.setex(redisKey, 60,  jsonTxt )
        return web.json_response(data)


    async def run_forever(self):
        server = web.Server(self.handler)
        runner = web.ServerRunner(server)
        await runner.setup()
        site = web.TCPSite(runner, self.listeningIP , self.listeningPort )
        await site.start()
        while True:
            await asyncio.sleep(1)
            self.redisServer = await aioredis.create_redis((self.redisServerIp,self.redisServerPort))
            statusDict = {"running":1,"recv":self.requestCounter} #add uptime
            for key in statusDict.keys():
                await self.redisServer.hmset ("BSA_status_restServer",key,statusDict[key])
            await self.redisServer.expire ("BSA_status_restServer", 4)
            self.redisServer.close()



if __name__ == "__main__":
    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--configFile",
                            default="/etc/bdsSnmpAdapterConfig.yml", type=str,
                            help="config file")
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    myRestHttpServer = restHttpServer(cliArgsDict)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(myRestHttpServer.run_forever())
    except KeyboardInterrupt:
        pass
    loop.close()
