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
import ipaddress
from bdsMappingFunctions import bdsMappingFunctions
import time
import redis
from bdsSnmpAdapterManager import loadBdsSnmpAdapterConfigFile
from bdsSnmpAdapterManager import set_logging
from bdsSnmpAdapterManager import BSA_STATUS_KEY
from bdsSnmpTableModules.confd_global_interface_container import confd_global_interface_container
from bdsSnmpTableModules.ffwd_default_interface_logical import ffwd_default_interface_logical
from bdsSnmpTableModules.confd_local_system_software_info_confd import confd_local_system_software_info_confd
from bdsSnmpTableModules.confd_global_startup_status_confd import confd_global_startup_status_confd

class bdsSnmpTables():


    def __init__(self,cliArgsDict):
        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],self.moduleFileNameWithoutPy)
        set_logging(configDict,self.moduleFileNameWithoutPy,self)
        self.moduleLogger.debug("configDict:{}".format(configDict))
        self.redisServer = redis.Redis(host=configDict["redisServerIp"], port=configDict["redisServerPort"], db=0)

        self.requestCounter = 0
        self.bdsSnmpTableModules = [\
            confd_global_interface_container,
            ffwd_default_interface_logical,
            confd_local_system_software_info_confd,
            confd_global_startup_status_confd
            ]


    def getTableFunctionFromOid(self,oid):
        for btc in self.bdsTableChain:
            if btc[0].startswith(oid):
                return btc[1]
        return None

    def getNextTableOidFromOid(self,oid):
        self.moduleLogger.debug('getNextTableOidFromOid for {}'.format(oid))
        for i,btc in enumerate(self.bdsTableChain):
            if oid.startswith(btc[0]):
                if i + 1 <  len(self.bdsTableChain):
                    nextTableOid = self.bdsTableChain[i+1][0]
                    self.moduleLogger.debug('getNextTableOidFromOid for {} is {}'.format(oid,nextTableOid))
                    return nextTableOid,True  # NextTableFlag = True
                else:
                    return "0.0",False # NextTableFlag = False
        return "0.0",False  # NextTableFlag = False

    def setBdsTableRequest (self,bdsTableDict):
        self.requestCounter += 1    #FIXME overrun prevention
        process = bdsTableDict["bdsRequest"]["process"]
        table = bdsTableDict["bdsRequest"]["table"]
        self.redisServer.set("bdsTableRequest-{}-{}".format(process,table),json.dumps(bdsTableDict),ex=60)
        self.moduleLogger.debug('set bdsTableRequest {}-{}'.format(process,table))

    def checkBdsTableInfo (self,redisKeysAsList):
        bdsTableRedisKey = redisKeysAsList[0]
        try:
            responseString = self.redisServer.get(bdsTableRedisKey).decode()
        except Exception as e:
            self.moduleLogger.error('something went wrong in fetching the responseString: {}'.format(e))
            self.redisServer.set(bdsTableRedisKey,"error",ex=30)
            self.moduleLogger.debug('set {} to error with timeout 30'.format(bdsTableRedisKey))
            return False,"error",bdsTableRedisKey
        else:
            if responseString not in [ "processed", "requested", "error" ]:
                #print(responseString)
                try:
                    responseJSON = json.loads(responseString)
                    self.moduleLogger.debug('loaded JSON from bdsTableRedisKey {} responseString {}'.format(bdsTableRedisKey,responseString))
                except Exception as e:
                    self.moduleLogger.error('cannot decode JSON string: {}'.format(responseString))
                    self.redisServer.set(bdsTableRedisKey,"error",ex=30)
                    self.moduleLogger.debug('set {} to error with timeout 30'.format(bdsTableRedisKey))
                    return False,"error",bdsTableRedisKey
                else:
                    return True,responseJSON,bdsTableRedisKey
            else:
                return False,responseString,bdsTableRedisKey

    def setOidHash (self,fullOid,fullOidDict,expiryTimer):
        self.redisServer.hmset("oidHash-{}".format(fullOid),fullOidDict)
        self.redisServer.expire("oidHash-{}".format(fullOid),expiryTimer)
        self.moduleLogger.debug("set oidHash-{} with {}".format(fullOid,fullOidDict))



    def run_forever(self):
        while True:
            statusDict = {"running":1,"sent":self.requestCounter} #add uptime
            self.redisServer.hmset(BSA_STATUS_KEY+self.moduleFileNameWithoutPy,statusDict)
            self.redisServer.expire(BSA_STATUS_KEY+self.moduleFileNameWithoutPy,4)
            #self.redisServer.hmset("BSA_status_bdsSnmpTables",statusDict)
            #self.redisServer.expire("BSA_status_bdsSnmpTables",4)
            for bdsSnmpTableModule in self.bdsSnmpTableModules:
                bdsSnmpTableModule.setOids(self)
            time.sleep(0.1)


if __name__ == "__main__":

    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--configFile",
                            default="/etc/bdsSnmpAdapterConfig.yml", type=str,
                            help="config file")
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    myBdsSnmpTables = bdsSnmpTables(cliArgsDict)
    myBdsSnmpTables.run_forever()
