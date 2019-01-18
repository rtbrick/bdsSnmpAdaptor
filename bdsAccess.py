#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
#import asyncio
#import aiohttp
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
from oidDb import oidDb
from mappingFuncModules.confd_local_system_software_info_confd import confd_local_system_software_info_confd

REQUEST_MAPPING_DICTS = {
   "confd_local.system.software.info.confd" : {
       "mappingFunc": confd_local_system_software_info_confd,
       "bdsRequestDict": {'process': 'confd',
                          'urlSuffix':'/bds/table/walk?format=raw',
                         'table':'local.system.software.info.confd'}
    }
  }

class bdsAccess():

    def __init__(self,cliArgsDict):
        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],self.moduleFileNameWithoutPy)
        set_logging(configDict,self.moduleFileNameWithoutPy,self)
        self.moduleLogger.debug("configDict:{}".format(configDict))
        self.rtbrickHost = configDict['rtbrickHost']
        self.rtbrickCtrldPort = configDict['rtbrickCtrldPort']
        self.rtbrickContainerName = configDict['rtbrickContainerName']
        self.expirytimer = 50 ### FIXME
        self.responseSequence = 0
        self.requestMappingDict = REQUEST_MAPPING_DICTS
        self.responseJsonDicts = {}
        self.oidDb = oidDb
        #'logging': 'warning'
        # do more stuff here. e.g. connecectivity checks etc


    def getJson(self,bdsRequestDict):  #confd_local.system.software.info.confd
        bdsProcess = bdsRequestDict['process']
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
        url = "http://{}:{}/api/application-rest-proxy/{}/{}/{}".format(self.rtbrickHost,
                                       self.rtbrickCtrldPort,
                                       self.rtbrickContainerName,
                                       bdsProcess,
                                       bdsSuffix)
        headers = {'Content-Type': 'application/json'}
        self.moduleLogger.debug ("POST {} {}".format(url,json.dumps(requestData)))
        try:
            self.response = requests.post(url,
                data=json.dumps(requestData),
                headers= headers,timeout=5)
        except Exception as e:
            return False,e
        else:
            if self.response.status_code != 200:
                self.moduleLogger.error ("received {} for {}".format(self.response.status_code,url))
                return False,"status_code != 200"
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
            for bdsRequestDictKey in self.requestMappingDict.keys():
                bdsRequestDict = self.requestMappingDict[bdsRequestDictKey]["bdsRequestDict"]
                mappingfunc = self.requestMappingDict[bdsRequestDictKey]["mappingFunc"]
                self.moduleLogger.debug ("working on {}".format(bdsRequestDictKey))
                bdsProcess = bdsRequestDict['process']
                bdsTable = bdsRequestDict['table']
                resultFlag,responseJsonString = self.getJson(bdsRequestDict)
                if resultFlag:
                    redisKeyForResponse = "{}_{}".format(bdsProcess,bdsTable)
                    responseAsDict = json.loads(responseJsonString)
                    self.moduleLogger.debug ("received {}".format(responseAsDict))
                    self.responseJsonDicts[redisKeyForResponse] = responseAsDict
                    self.moduleLogger.debug("self.responseJsonDicts[{}] {}"\
                                  .format(redisKeyForResponse,responseAsDict))
                    mappingfunc.setOids(responseAsDict,self.oidDb)
            time.sleep(5)


if __name__ == "__main__":

    logging.getLogger().setLevel(logging.DEBUG)       # FIXME set level from cliargs
    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--configFile",
                            default="./bdsAccessConfig.yml", type=str,
                            help="config file")
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    logging.debug(cliArgsDict)
    myBdsAccess = bdsAccess(cliArgsDict)
    myBdsAccess.run_forever()
