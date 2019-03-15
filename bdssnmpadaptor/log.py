# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#

import logging
from logging.handlers import RotatingFileHandler

def set_logging(configDict,moduleFileNameWithoutPy,moduleObj):
    logging.root.handlers = []
    moduleObj.moduleLogger = logging.getLogger(moduleFileNameWithoutPy)
    logFile = configDict['rotatingLogFile'] + moduleFileNameWithoutPy + ".log"
    #
    #logging.basicConfig(filename=logFile, filemode='w', level=logging.DEBUG)
    rotateHandler = RotatingFileHandler(logFile, maxBytes=1000000,backupCount=2)  #1M rotating log
    formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
    rotateHandler.setFormatter(formatter)
    logging.getLogger("").addHandler(rotateHandler)
    #
    moduleObj.loggingLevel = configDict['loggingLevel']
    if moduleObj.loggingLevel in ["debug", "info", "warning"]:
        if moduleObj.loggingLevel == "debug": logging.getLogger().setLevel(logging.DEBUG)
        if moduleObj.loggingLevel == "info": logging.getLogger().setLevel(logging.INFO)
        if moduleObj.loggingLevel == "warning": logging.getLogger().setLevel(logging.WARNING)

