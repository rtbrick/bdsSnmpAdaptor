# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import sys
import yaml


def loadConfig(filename):

    try:
        with open(filename) as stream:
            config = yaml.load(stream)
            return config['bdsSnmpAdapter']

    except Exception as e:
        print('Failed to open configuration file')
        print(e)
        sys.exit(-1)
