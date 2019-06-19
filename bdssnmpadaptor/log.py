# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import logging
import os
import sys
from logging import StreamHandler
from logging.handlers import RotatingFileHandler


def set_logging(configDict, name):

    moduleLogger = logging.getLogger(name)

    moduleLogger.propagate = False  # log only via this logger

    logFile = configDict.get('rotatingLogFile')
    if logFile:
        logFile = os.path.join(logFile, name.split('.')[-1]) + '.log'

        handler = RotatingFileHandler(
            logFile, maxBytes=1000000, backupCount=2)  # 1M rotating log

    else:
        handler = StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '%(asctime)s: %(name)s: %(levelname)s: %(message)s')

    handler.setFormatter(formatter)

    moduleLogger.addHandler(handler)

    loggingLevel = configDict['loggingLevel']

    moduleLogger.setLevel(
        getattr(logging, loggingLevel.upper(), 'ERROR'))

    return moduleLogger
