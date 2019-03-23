# -*- coding: utf-8 -*-
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


def set_logging(configDict, moduleFileNameWithoutPy, moduleObj):

    logging.root.handlers = []

    moduleLogger = logging.getLogger(moduleFileNameWithoutPy)

    logFile = configDict.get('rotatingLogFile')
    if logFile:
        logFile = os.path.join(logFile, moduleFileNameWithoutPy)
        logFile += ".log"

        handler = RotatingFileHandler(
            logFile, maxBytes=1000000, backupCount=2)  # 1M rotating log

    else:
        handler = StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '%(asctime)s : %(name)s : %(levelname)s : %(message)s')

    handler.setFormatter(formatter)

    logging.getLogger("").addHandler(handler)

    moduleObj.loggingLevel = configDict['loggingLevel']

    if moduleObj.loggingLevel == "debug":
        logging.getLogger().setLevel(logging.DEBUG)

    elif moduleObj.loggingLevel == "info":
        logging.getLogger().setLevel(logging.INFO)

    elif moduleObj.loggingLevel == "warning":
        logging.getLogger().setLevel(logging.WARNING)

    else:
        logging.getLogger().setLevel(logging.ERROR)

    return moduleLogger
