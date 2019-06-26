# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import yaml

from bdssnmpadaptor import error


def loadConfig(filename):
    """Load and parse .yaml configuration file

    Args:
        filename (str): Path to system configuration file

    Returns:
        dict: representing configuration information

    Raises:
        BdsError: if unable to get configuration information
    """
    try:
        with open(filename) as stream:
            config = yaml.load(stream)
            return config['bdsSnmpAdapter']

    except Exception as exc:
        raise error.BdsError(
            'Failed to read configuration file %s: %s' % (filename, exc))
