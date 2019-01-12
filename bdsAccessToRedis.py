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
from bdsSnmpAdapterManager import set_logging


class bdsAccessToRedis():


    def __init__(self,cliArgsDict):
        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        #self.moduleLogger = logging.getLogger(self.moduleFileNameWithoutPy)
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],self.moduleFileNameWithoutPy)
        set_logging(configDict,self.moduleFileNameWithoutPy,self)
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
            if self.response.status_code != 200:
                self.moduleLogger.error ("received {} for {}".format(self.response.status_code,url))
            else:
                self.moduleLogger.info ("received {} for {}".format(self.response.status_code,url))
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
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    logging.debug(cliArgsDict)
    myBdsAccess = bdsAccessToRedis(cliArgsDict)
    myBdsAccess.run_forever()
