
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


class restHttpServer():

    def set_logging(self,configDict):
        logging.root.handlers = []
        self.moduleLogger = logging.getLogger('restServer.py')
        logFile = configDict['rotatingLogFile'] + "restServer.log"
        #
        #logging.basicConfig(filename=logFile, filemode='w', level=logging.DEBUG)
        rotateHandler = RotatingFileHandler(logFile, maxBytes=1000000,backupCount=2)  #1M rotating log
        formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
        rotateHandler.setFormatter(formatter)
        logging.getLogger("").addHandler(rotateHandler)
        #
        self.loggingLevel = configDict['loggingLevel']
        if self.loggingLevel in ["debug", "info", "warning"]:
            if self.loggingLevel == "debug": logging.getLogger().setLevel(logging.DEBUG)
            if self.loggingLevel == "info": logging.getLogger().setLevel(logging.INFO)
            if self.loggingLevel == "warning": logging.getLogger().setLevel(logging.WARNING)
        self.moduleLogger.info("self.loggingLevel: {}".format(self.loggingLevel))

    def __init__(self,configDict):
        self.moduleLogger = logging.getLogger('redisToSnmpTrap')
        self.set_logging(configDict)
        print(configDict)
        self.listeningIP =  configDict["listeningIP"]
        self.listeningPort = configDict["listeningPort"]
        #self.redisServer = await aioredis.create_redis_pool('redis://localhost')
        #self.redisServer = aioredis.create_redis_pool((configDict["redisServerIp"],configDict["redisServerPort"]))
        self.requestCounter = 0


    async def handler(self,request):
        peerIP = request._transport_peername[0]
        self.requestCounter += 1
        self.moduleLogger.info ("handler: peerIP:{} headers:{} counter:{} ".format(peerIP,request.headers,self.requestCounter))
        data = {'headers': dict(request.headers)}
        #print(data)
        jsonTxt = await request.text() #
        #self.moduleLogger.info (jsonTxt)
        #self.redisServer = await aioredis.create_redis_pool('redis://localhost')
        self.redisServer = await aioredis.create_redis((configDict["redisServerIp"],configDict["redisServerPort"]))
        #print(self.redisServer)
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
            self.redisServer = await aioredis.create_redis((configDict["redisServerIp"],configDict["redisServerPort"]))
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
    #print(cliArgsDict)
    configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],"restServerForRtBrickSnmpTrapsToRedis")
    myRestHttpServer = restHttpServer(configDict)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(myRestHttpServer.run_forever())
    except KeyboardInterrupt:
        pass
    loop.close()
