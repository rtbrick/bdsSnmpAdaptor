# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0

import sys
import requests
import json
import argparse
import yaml
import pprint
import time

import redis

from bdssnmpadaptor.log import set_logging
from bdssnmpadaptor.config import loadBdsSnmpAdapterConfigFile

PROCESS_LIST = [ "restServer" ,"redisToSnmpTrap" , "getOidFromRedis" , "bdsSnmpTables" , "bdsAccessToRedis" ]
BSA_STATUS_KEY = "BSA_status_"


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


def main():

    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--configFile",
                            default="/etc/bdsSnmpAdapterConfig.yml", type=str,
                            help="config file")
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    _bdsSnmpAdapterManager = bdsSnmpAdapterManager(cliArgsDict)
    _bdsSnmpAdapterManager.run_forever()

    return 0


if __name__ == "__main__":
    sys.exit(main())
