#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import logging
from logging.handlers import RotatingFileHandler
import argparse
import yaml
import pprint
from copy import deepcopy
import redis
import time
from bdsSnmpAdapterManager import loadBdsSnmpAdapterConfigFile


class bdsAccessToRedis():


    def set_logging(self,configDict):
        logging.root.handlers = []
        self.moduleLogger = logging.getLogger('bdsAccessToRedis')
        logFile = configDict['rotatingLogFile']
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


    def __init__(self,cliArgsDict):
        self.moduleLogger = logging.getLogger('bdsAccessToRedis')
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],"bdsAccessToRedis")
        self.set_logging(configDict)
        self.moduleLogger.debug("configDict:{}".format(configDict))
        self.redisServer = redis.Redis(host=configDict["redisServerIp"], port=configDict["redisServerPort"], db=0)
        self.rtbrickHost = configDict['rtbrickHost']
        self.rtbrickCtrldPort = configDict['rtbrickCtrldPort']
        self.rtbrickContainerName = configDict['rtbrickContainerName']
        self.expirytimer = 50 ### FIXME
        self.responseSequence = 0
        #'logging': 'warning'
        # do more stuff here. e.g. connecectivity checks etc



    def getJson(self,bdsRequestDict):
        bdsProcess = bdsRequestDict['process']
        #self.rtbrickHost = bdsAccessDict[bdsProcess]["host"]
        #self.rtbrickCtrldPort = bdsAccessDict[bdsProcess]["port"]
        bdsSuffix = bdsRequestDict['urlSuffix']
        bdsTable = bdsRequestDict['table']
        if "attributes" in bdsRequestDict.keys():
            attributeDict={}
            for attribute in bdsRequestDict['attributes']:
                attributeDict[attribute]=bdsRequestDict['attributes'][attribute]
            requestData = {"table":{"table_name":bdsTable},
                           "objects":[{"attribute":attributeDict}]}
        else:
            requestData = {"table":{"table_name":bdsTable}}
        #"http://192.168.56.22:19091/api/application-rest-proxy/Basesim/confd/bds/object/walk"
        url = "http://{}:{}/api/application-rest-proxy/{}/{}/{}".format(self.rtbrickHost,
                                       self.rtbrickCtrldPort,
                                       self.rtbrickContainerName,
                                       bdsProcess,
                                       bdsSuffix)
        headers = {'Content-Type': 'application/json'}
        #self.moduleLogger.info ("POST {}".format(url))
        self.moduleLogger.debug ("POST {} {}".format(url,json.dumps(requestData)))
        try:
            self.response = requests.post(url,
                data=json.dumps(requestData),
                headers= headers,timeout=1)
        except Exception as e:
            return False,e
        else:
            self.moduleLogger.debug (self.response)
            if len(self.response.text) > 0:
                try:
                    responseJSON = json.loads(self.response.text)
                    responseString = json.dumps(responseJSON,indent=4)
                    self.moduleLogger.debug (responseString)
                except Exception as e:
                    return False,e
                else:
                    return True,responseString
            else:
                return False,"json length error"

    def run_forever(self):
        while True:
            statusDict = {"running":1,"recv":self.responseSequence} #add uptime
            self.redisServer.hmset("BSA_status_bdsAccessToRedis",statusDict)
            self.redisServer.expire("BSA_status_bdsAccessToRedis",4)
            redisKeys = self.redisServer.scan_iter("bdsTableRequest-*")
            redisKeysAsList = list(redisKeys)
            redisKeysAsList.sort()
            for key in redisKeysAsList:
                #key format bdsRequests-requesterIP-number
                self.moduleLogger.debug ("working on {}::{}".format(key.decode(),self.redisServer.get(key).decode()))
                bdsRequestAsJsonString = self.redisServer.get(key)
                bdsRequestDict = json.loads(bdsRequestAsJsonString)['bdsRequest']
                bdsProcess = bdsRequestDict['process']
                bdsTable = bdsRequestDict['table']
                self.responseSequence += 1
                redisKeyForResponse = "bdsTableInfo-{}-{}".format(bdsProcess,bdsTable)
                self.redisServer.set(redisKeyForResponse,"requested",ex=3)     #prevents further bdsTableRequests requests on same table
                self.moduleLogger.debug ("bdsRequestDict:{}".format(bdsRequestDict))
                resultFlag,responseJSON = self.getJson(bdsRequestDict)
                self.redisServer.set(redisKeyForResponse,responseJSON,ex=60)
                self.redisServer.delete(key)
            time.sleep(0.001)


if __name__ == "__main__":

    logging.getLogger().setLevel(logging.DEBUG)       # FIXME set level from cliargs
    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--configFile",
                            default="/etc/bdsSnmpAdapterConfig.yml", type=str,
                            help="config file")
    # parser.add_argument("--rtbrickHost",
    #                     default='192.168.56.22', type=str,
    #                     help="Define IP address of RtBrick Host, please make sure that ctrld on port 19091 runs on this system")
    # parser.add_argument("--rtbrickCtrldPort",
    #                     default=19091, type=int,
    #                     help="Define the port on which ctrld listens")
    # parser.add_argument("--rtbrickContainerName",
    #                     default='Basesim', type=str,
    #                     help="Define the name of RtBrick Container")
    # parser.add_argument("--confdPort",
    #                     default=2002, type=int,
    #                     help="Define port number for confd access")
    # parser.add_argument("--bgpIodPort",
    #                     default=3102, type=int,
    #                     help="Define port number for bgp-iod access")
    # parser.add_argument("--fwddPort",
    #                     default=5002, type=int,
    #                     help="Define port number for fwdd access")
    # parser.add_argument("--logging", choices=['debug', 'warning', 'info'],
    #                     default='warning', type=str,
    #                     help="Define logging level(debug=highest)")
    # parser.add_argument('--redisServerIp', default='127.0.0.1',
    #                     help='redis server IP address, default is 127.0.0.1', type=str)
    # parser.add_argument('--redisServerPort', default=6379,
    #                     help='redis Server port, default is 6379', type=int)
    # parser.add_argument('-e', '--expiryTimer', default=60,
    #                     help='redis key expiry timer setting', type=int)
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    logging.debug(cliArgsDict)
    myBdsAccess = bdsAccessToRedis(cliArgsDict)
    myBdsAccess.run_forever()
