# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import sys
import yaml


def loadBdsSnmpAdapterConfigFile(config, moduleName):

    try:
        with open(config, 'r') as stream:
            data = yaml.load(stream)

    except Exception as e:
        print('Failed to open configuration file')
        print(e)
        sys.exit(-1)

    else:
        configDict = {}

        for key in data['bdsSnmpAdapter']:
            if type(data['bdsSnmpAdapter'][key]) != dict:
                configDict[key] = data['bdsSnmpAdapter'][key]

        if moduleName in data['bdsSnmpAdapter']:
            for key in data['bdsSnmpAdapter'][moduleName]:
                configDict[key] = data['bdsSnmpAdapter'][moduleName][key]

        return configDict
