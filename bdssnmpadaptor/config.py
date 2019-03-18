# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import sys
import yaml


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