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
import redis
import time


PROCESS_LIST = [ "restServer" ,"redisToSnmpTrap" , "getOidFromRedis" , "bdsSnmpTables" , "bdsAccessToRedis" ]
BSA_STATUS_KEY = "BSA_status_"

def set_logging(configDict,moduleFileNameWithoutPy,moduleObj):
    logging.root.handlers = []
    moduleObj.moduleLogger = logging.getLogger(moduleFileNameWithoutPy)
    logFile = configDict['rotatingLogFile'] + moduleFileNameWithoutPy + ".log"
    #
    #logging.basicConfig(filename=logFile, filemode='w', level=logging.DEBUG)
    rotateHandler = RotatingFileHandler(logFile, maxBytes=1000000,backupCount=2)  #1M rotating log
    formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
    rotateHandler.setFormatter(formatter)
    logging.getLogger("").addHandler(rotateHandler)
    #
    moduleObj.loggingLevel = configDict['loggingLevel']
    if moduleObj.loggingLevel in ["debug", "info", "warning"]:
        if moduleObj.loggingLevel == "debug": logging.getLogger().setLevel(logging.DEBUG)
        if moduleObj.loggingLevel == "info": logging.getLogger().setLevel(logging.INFO)
        if moduleObj.loggingLevel == "warning": logging.getLogger().setLevel(logging.WARNING)

def loadBdsSnmpAdapterConfigFile(configFile,moduleName):
    data = {}
    try:
        with open(configFile, "r") as stream:
            data = yaml.load(stream)
    except Exception as e:
        print("Failed to open configuration file")
        print(e)
        sys.exit(-1)
    else:
        configDict = {}
        for key in data["bdsSnmpAdapter"].keys():
            if type(data["bdsSnmpAdapter"][key]) != dict:
                configDict[key] = data["bdsSnmpAdapter"][key]
        if moduleName in data["bdsSnmpAdapter"].keys():
            for key in data["bdsSnmpAdapter"][moduleName].keys():
                configDict[key] = data["bdsSnmpAdapter"][moduleName][key]
        return configDict


class bdsSnmpAdapterManager:


    def __init__(self,cliArgsDict):
        self.moduleFileNameWithoutPy = sys.modules[__name__].__file__.split(".")[0]
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],self.moduleFileNameWithoutPy)
        set_logging(configDict,self.moduleFileNameWithoutPy,self)
        self.moduleLogger.debug("configDict:{}".format(configDict))
        self.redisServer = redis.StrictRedis(host=configDict["redisServerIp"], port=configDict["redisServerPort"], db=0,decode_responses=True)

    def run_forever(self):
        while True:
            print ("#"*60)
            for processString in PROCESS_LIST:
                redisKey = BSA_STATUS_KEY + processString
                modulStatusDict = self.redisServer.hgetall(redisKey)
                print ("{:20s}{}".format(processString,modulStatusDict))
            time.sleep(1)



if __name__ == "__main__":

    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--configFile",
                            default="/etc/bdsSnmpAdapterConfig.yml", type=str,
                            help="config file")
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    bdsSnmpAdapterManager = bdsSnmpAdapterManager(cliArgsDict)
    bdsSnmpAdapterManager.run_forever()
