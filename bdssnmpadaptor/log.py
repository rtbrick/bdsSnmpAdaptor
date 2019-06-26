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


def set_logging(cfg, name):
    """Create isolated Python logger.

    Creates Python logger according to given configuration. The new
    logger object logs solely through its own handler, log message
    propagation towards upper logging object is inhibited.

    Args:
        cfg (dict): BDS system configuration
        name (str): log under this name

    Returns:
        Logger: Python logger object
    """

    logger = logging.getLogger(name)

    logger.propagate = False  # log only via this logger

    logFile = cfg.get('rotatingLogFile')
    if logFile:
        logFile = os.path.join(logFile, name.split('.')[-1]) + '.log'

        handler = RotatingFileHandler(
            logFile, maxBytes=1000000, backupCount=2)  # 1M rotating log

    else:
        handler = StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '%(asctime)s: %(name)s: %(levelname)s: %(message)s')

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    loggingLevel = cfg['loggingLevel']

    logger.setLevel(
        getattr(logging, loggingLevel.upper(), 'ERROR'))

    return logger
