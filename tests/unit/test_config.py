# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import io
import sys
import unittest
from unittest import mock

from bdssnmpadaptor import config


class ConfigTestCase(unittest.TestCase):

    CONFIG = """\
bdsSnmpAdapter:
  loggingLevel: debug
  rotatingLogFile: /tmp   #FIXME store this at permanent location
  stateDir: /var/run/bds-snmp-adaptor    
"""
    CONFIG = io.StringIO(CONFIG)

    @mock.patch('bdssnmpadaptor.config.open')
    def test_loadConfig(self, mock_open):
        mock_open.return_value.__enter__.return_value = self.CONFIG

        cfg = config.loadConfig('/configfile')

        self.assertTrue(cfg)

        expected = {
            'loggingLevel': 'debug',
            'rotatingLogFile': '/tmp',
            'stateDir': '/var/run/bds-snmp-adaptor'
        }
        self.assertDictEqual(expected, cfg)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
