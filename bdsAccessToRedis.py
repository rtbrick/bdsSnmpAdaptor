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
import redis
import time



class bdsAccessToRedis():

    def __init__(self,cliArgsDict):
        self.redisServer = cliArgsDict["redisServer"]
        self.rtbrickHost = cliArgsDict['rtbrickHost']
        self.rtbrickCtrldPort = cliArgsDict['rtbrickCtrldPort']
        self.rtbrickContainerName = cliArgsDict['rtbrickContainerName']
        self.expirytimer = cliArgsDict['expiryTimer']
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
        #logging.info ("POST {}".format(url))
        logging.debug ("POST {} {}".format(url,json.dumps(requestData)))
        try:
            self.response = requests.post(url,
                data=json.dumps(requestData),
                headers= headers,timeout=1)
        except Exception as e:
            return False,e
        else:
            logging.debug (self.response)
            if len(self.response.text) > 0:
                try:
                    responseJSON = json.loads(self.response.text)
                    responseString = json.dumps(responseJSON,indent=4)
                    logging.debug (responseString)
                except Exception as e:
                    return False,e
                else:
                    return True,responseString
            else:
                return False,"json length error"

    def run_forever(self):
        while True:
            redisKeys = self.redisServer.scan_iter("bdsTableRequest-*")
            redisKeysAsList = list(redisKeys)
            redisKeysAsList.sort()
            for key in redisKeysAsList:
                #key format bdsRequests-requesterIP-number
                logging.debug ("working on {}::{}".format(key.decode(),self.redisServer.get(key).decode()))
                bdsRequestAsJsonString = self.redisServer.get(key)
                bdsRequestDict = json.loads(bdsRequestAsJsonString)['bdsRequest']
                bdsProcess = bdsRequestDict['process']
                bdsTable = bdsRequestDict['table']
                self.responseSequence += 1
                redisKeyForResponse = "bdsTableInfo-{}-{}".format(bdsProcess,bdsTable)
                self.redisServer.set(redisKeyForResponse,"requested",ex=3)     #prevents further bdsTableRequests requests on same table
                logging.debug ("bdsRequestDict:{}".format(bdsRequestDict))
                resultFlag,responseJSON = self.getJson(bdsRequestDict)
                self.redisServer.set(redisKeyForResponse,responseJSON,ex=60)
                self.redisServer.delete(key)
            time.sleep(0.001)


if __name__ == "__main__":

    logging.getLogger().setLevel(logging.DEBUG)       # FIXME set level from cliargs
    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--rtbrickHost",
                        default='192.168.56.22', type=str,
                        help="Define IP address of RtBrick Host, please make sure that ctrld on port 19091 runs on this system")
    parser.add_argument("--rtbrickCtrldPort",
                        default=19091, type=int,
                        help="Define the port on which ctrld listens")
    parser.add_argument("--rtbrickContainerName",
                        default='Basesim', type=str,
                        help="Define the name of RtBrick Container")
    # parser.add_argument("--confdPort",
    #                     default=2002, type=int,
    #                     help="Define port number for confd access")
    # parser.add_argument("--bgpIodPort",
    #                     default=3102, type=int,
    #                     help="Define port number for bgp-iod access")
    # parser.add_argument("--fwddPort",
    #                     default=5002, type=int,
    #                     help="Define port number for fwdd access")
    parser.add_argument("--logging", choices=['debug', 'warning', 'info'],
                        default='warning', type=str,
                        help="Define logging level(debug=highest)")
    parser.add_argument('--redisServerIp', default='127.0.0.1',
                        help='redis server IP address, default is 127.0.0.1', type=str)
    parser.add_argument('--redisServerPort', default=6379,
                        help='redis Server port, default is 6379', type=int)
    parser.add_argument('-e', '--expiryTimer', default=60,
                        help='redis key expiry timer setting', type=int)
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    cliArgsDict["redisServer"] = redis.Redis(host=cliArgsDict["redisServerIp"], port=cliArgsDict["redisServerPort"], db=0)
    logging.debug(cliArgsDict)
    myBdsAccess = bdsAccessToRedis(cliArgsDict)
    myBdsAccess.run_forever()
