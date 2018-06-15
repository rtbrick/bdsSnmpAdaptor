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




class bdsAccess():

    def __init__():
        pass

    @classmethod
    def getJson(self,oidDict,bdsAccessDict):
        print (oidDict['bdsRequest'])
        bdsProcess = oidDict['bdsRequest']['process']
        bdsHostIp = bdsAccessDict[bdsProcess]["host"]
        bdsHostPort = bdsAccessDict[bdsProcess]["port"]
        bdsSuffix = oidDict['bdsRequest']['urlSuffix']
        bdsTable = oidDict['bdsRequest']['table']
        if "attributes" in oidDict['bdsRequest'].keys():
            attributeDict={}
            for attribute in oidDict['bdsRequest']['attributes']:
                attributeDict[attribute]=oidDict['bdsRequest']['attributes'][attribute]
            requestData = {"table":{"table_name":bdsTable},
                           "objects":[{"attribute":attributeDict}]}
        else:
            requestData = {"table":{"table_name":bdsTable}}
        url = "http://{}:{}{}".format(bdsHostIp,bdsHostPort,bdsSuffix)
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
                    return True,responseJSON
            else:
                return False,"json length error"

            





