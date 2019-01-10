#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import logging
import argparse
import yaml
import pprint



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
        for key in data["bdsSnmpAdapter"][moduleName].keys():
            configDict[key] = data["bdsSnmpAdapter"][moduleName][key]
        return configDict


class bdsSnmpAdapterManager:

    def __init__(self,cliArgsDict):
        pass
