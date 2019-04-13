# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import sys
import unittest
from unittest import mock

from bdssnmpadaptor import snmp_config

from pysnmp.entity import engine


@mock.patch('os.makedirs', new=mock.MagicMock)
@mock.patch('os.rename', new=mock.MagicMock)
@mock.patch('tempfile.NamedTemporaryFile', new=mock.MagicMock)
@mock.patch('bdssnmpadaptor.snmp_config.config.addVacmUser', new=mock.MagicMock)
class SnmpConfigTestCase(unittest.TestCase):

    def test_getSnmpEngine(self):
        snmpEngine = snmp_config.getSnmpEngine('00:01:02:03:04:05')

        self.assertIsInstance(snmpEngine, engine.SnmpEngine)
        self.assertEqual(snmpEngine.snmpEngineID, b'\x00\x01\x02\x03\x04\x05')

    @mock.patch('bdssnmpadaptor.snmp_config.open')
    def test_getSnmpEngineBoots(self, mock_open):
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.return_value = '1234'

        boots = snmp_config.setSnmpEngineBoots(engine.SnmpEngine(), '/state')

        self.assertEqual(1235, boots)

    def test_setUsmUser(self):

        with mock.patch('bdssnmpadaptor.snmp_config.config.addV3User',
                        autospec=True):

            authLevel = snmp_config.setUsmUser(
                engine.SnmpEngine(), 'security', 'user')

            self.assertEqual('noAuthNoPriv', authLevel)

            authLevel = snmp_config.setUsmUser(
                engine.SnmpEngine(), 'security', 'user', 'authkey1',
                'md5', 'privkey1', 'des')

            self.assertEqual('authPriv', authLevel)

            authLevel = snmp_config.setUsmUser(
                engine.SnmpEngine(), 'security', 'user', 'authkey1',
                'md5')

            self.assertEqual('authNoPriv', authLevel)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
