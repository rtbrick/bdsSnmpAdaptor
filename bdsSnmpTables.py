#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import logging
import argparse
import yaml
import pprint
from copy import deepcopy
import ipaddress
#from bdsAccess import bdsAccess
#from redisOidDb import redisOidDb, redisOidSegment
from bdsMappingFunctions import bdsMappingFunctions
import time
import redis
from bdsSnmpTableModules.confd_global_interface_container import confd_global_interface_container
from bdsSnmpTableModules.ffwd_default_interface_logical import ffwd_default_interface_logical
from bdsSnmpTableModules.confd_local_system_software_info_confd import confd_local_system_software_info_confd
from bdsSnmpTableModules.confd_global_startup_status_confd import confd_global_startup_status_confd

class bdsSnmpTables():

    def __init__(self,redisServer):
        self.requestCounter = 0
        self.bdsSnmpTableModules = [\
            confd_global_interface_container,
            ffwd_default_interface_logical,
            confd_local_system_software_info_confd,
            confd_global_startup_status_confd
            ]
        self.redisServer = cliArgsDict["redisServer"]

    def getTableFunctionFromOid(self,oid):
        for btc in self.bdsTableChain:
            if btc[0].startswith(oid):
                return btc[1]
        return None

    def getNextTableOidFromOid(self,oid):
        logging.debug('getNextTableOidFromOid for {}'.format(oid))
        for i,btc in enumerate(self.bdsTableChain):
            if oid.startswith(btc[0]):
                if i + 1 <  len(self.bdsTableChain):
                    nextTableOid = self.bdsTableChain[i+1][0]
                    logging.debug('getNextTableOidFromOid for {} is {}'.format(oid,nextTableOid))
                    return nextTableOid,True  # NextTableFlag = True
                else:
                    return "0.0",False # NextTableFlag = False
        return "0.0",False  # NextTableFlag = False

    def setBdsTableRequest (self,bdsTableDict):
        self.requestCounter += 1    #FIXME overrun prevention
        process = bdsTableDict["bdsRequest"]["process"]
        table = bdsTableDict["bdsRequest"]["table"]
        self.redisServer.set("bdsTableRequest-{}-{}".format(process,table),json.dumps(bdsTableDict),ex=60)
        logging.debug('set bdsTableRequest {}-{}'.format(process,table))

    def checkBdsTableInfo (self,redisKeysAsList):
        bdsTableRedisKey = redisKeysAsList[0]
        try:
            responseString = self.redisServer.get(bdsTableRedisKey).decode()
        except Exception as e:
            logging.error('something went wrong in fetching the responseString: {}'.format(e))
            self.redisServer.set(bdsTableRedisKey,"error",ex=30)
            logging.debug('set {} to error with timeout 30'.format(bdsTableRedisKey))
            return False,"error",bdsTableRedisKey
        else:
            if responseString not in [ "processed", "requested", "error" ]:
                #print(responseString)
                try:
                    responseJSON = json.loads(responseString)
                    logging.debug('loaded JSON from bdsTableRedisKey {} responseString {}'.format(bdsTableRedisKey,responseString))
                except Exception as e:
                    logging.error('cannot decode JSON string: {}'.format(responseString))
                    self.redisServer.set(bdsTableRedisKey,"error",ex=30)
                    logging.debug('set {} to error with timeout 30'.format(bdsTableRedisKey))
                    return False,"error",bdsTableRedisKey
                else:
                    return True,responseJSON,bdsTableRedisKey
            else:
                return False,responseString,bdsTableRedisKey

    def setOidHash (self,fullOid,fullOidDict,expiryTimer):
        self.redisServer.hmset("oidHash-{}".format(fullOid),fullOidDict)
        self.redisServer.expire("oidHash-{}".format(fullOid),expiryTimer)
        logging.debug("set oidHash-{} with {}".format(fullOid,fullOidDict))



    def run_forever(self):
        while True:
            #for oidSegmentFunction in self.oidSegmentFunctions:
                #logging.debug("working on self.oidSegmentFunctions element:  {}".format(oidSegmentFunction))
                #oidSegmentFunction()
            for bdsSnmpTableModule in self.bdsSnmpTableModules:
                #logging.debug("working on self.oidSegmentFunctions element:  {}".format(oidSegmentFunction))
                bdsSnmpTableModule.setOids(self)
            time.sleep(0.1)
            #sys.exit(0)  ###TEMP


if __name__ == "__main__":

    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--logging", choices=['debug', 'warning', 'info'],
                        default='info', type=str,
                        help="Define logging level(debug=highest)")
    parser.add_argument('--redisServerIp', default='127.0.0.1',
                        help='redis server IP address, default is 127.0.0.1', type=str)
    parser.add_argument('--redisServerPort', default=6379,
                        help='redis Server port, default is 6379', type=int)
    parser.add_argument('-e', '--expiryTimer', default=60,
                        help='redis key expiry timer setting', type=int)
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    if cliArgsDict["logging"] == "debug":
        logging.getLogger().setLevel(logging.DEBUG)       # FIXME set level from cliargs
    elif cliArgsDict["logging"] == "warning":
        logging.getLogger().setLevel(logging.WARNING)       # FIXME set level from cliargs
    else:
        logging.getLogger().setLevel(logging.INFO)       # FIXME set level from cliargs
    logging.debug(cliArgsDict)
    cliArgsDict["redisServer"] = redis.Redis(host=cliArgsDict["redisServerIp"], port=cliArgsDict["redisServerPort"], db=0)
    myBdsSnmpTables = bdsSnmpTables(cliArgsDict)
    myBdsSnmpTables.run_forever()
