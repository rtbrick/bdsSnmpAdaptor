#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
#import requests
import asyncio
import aiohttp
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
from oidDb import OidDb
from staticAndPredefinedOids import StaticAndPredefinedOids
from mappingFuncModules.confd_local_system_software_info_confd import confd_local_system_software_info_confd
from mappingFuncModules.confd_global_startup_status_confd import confd_global_startup_status_confd

REQUEST_MAPPING_DICTS = {
   "confd_local.system.software.info.confd" : {
       "mappingFunc": confd_local_system_software_info_confd,
       "bdsRequestDict": {'process': 'confd',
                          'urlSuffix':'bds/table/walk?format=raw',
                         'table':'local.system.software.info.confd'}
    },
   "confd_global_startup_status_confd" : {
       "mappingFunc": confd_global_startup_status_confd,
       "bdsRequestDict": {'process': 'confd',
                          'urlSuffix':'bds/table/walk?format=raw',
                         'table':'global.startup.status.confd'}
    }
  }

class BdsAccess():

    def __init__(self,cliArgsDict):
        self.moduleFileNameWithoutPy, _ = os.path.splitext(
            os.path.basename(sys.modules[__name__].__file__)
        )
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
        self.oidDb = OidDb()
        #'logging': 'warning'
        # do more stuff here. e.g. connecectivity checks etc

    def getOidDb(self):
        return self.oidDb

    async def getJson(self,bdsRequestDict):
        bdsProcess = bdsRequestDict['process']
        bdsSuffix = bdsRequestDict['urlSuffix']
        bdsTable = bdsRequestDict['table']
        if "attributes" in bdsRequestDict.keys():
            attributeDict={}
            for attribute in bdsRequestDict['attributes']:
                attributeDict[attribute]=bdsRequestDict['attributes'][attribute]
            requestData = {'table':{'table_name':bdsTable},
                           'objects':[{'attribute':attributeDict}]}
        else:
            requestData = {'table':{'table_name':bdsTable}}
        url = "http://{}:{}/api/application-rest-proxy/{}/{}/{}".format(self.rtbrickHost,
                                       self.rtbrickCtrldPort,
                                       self.rtbrickContainerName,
                                       bdsProcess,
                                       bdsSuffix)
        try:
            headers = {'Content-Type': 'application/json'}
            async with aiohttp.ClientSession() as session:
                async with session.post(url,timeout=5,
                                       headers = headers,
                                       json = requestData) as response:
                    responseJsonDict = await response.json(content_type='application/json')
        except Exception as e:
            print("Exception: #{}#".format(e))
            return False,e
        else:
            if response.status != 200:
                self.moduleLogger.error ("received {} for {}".format(response.status,url))
                return False,"status != 200"
            else:
                self.moduleLogger.info ("received {} for {}".format(response.status,url))
                self.moduleLogger.debug (response)
                return True,responseJsonDict


    async def run_forever(self):
        while True:
            await StaticAndPredefinedOids.setOids(self.oidDb)
            for bdsRequestDictKey in self.requestMappingDict.keys():
                print(bdsRequestDictKey)
                bdsRequestDict = self.requestMappingDict[bdsRequestDictKey]["bdsRequestDict"]
                mappingfunc = self.requestMappingDict[bdsRequestDictKey]["mappingFunc"]
                self.moduleLogger.debug ("working on {}".format(bdsRequestDictKey))
                bdsProcess = bdsRequestDict['process']
                bdsTable = bdsRequestDict['table']
                resultFlag,responseJsonDict = await self.getJson(bdsRequestDict)
                if resultFlag:
                    responseTableKey = "{}_{}".format(bdsProcess,bdsTable)
                    self.responseJsonDicts[responseTableKey] = responseJsonDict
                    self.moduleLogger.debug("self.responseJsonDicts[{}] {}"\
                                  .format(responseTableKey,responseJsonDict))
                    await mappingfunc.setOids(responseJsonDict,self.oidDb)
            #print(self.oidDb)
            await asyncio.sleep(60)

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
    myBdsAccess = BdsAccess(cliArgsDict)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(myBdsAccess.run_forever())
    except KeyboardInterrupt:
        pass
    loop.close()
