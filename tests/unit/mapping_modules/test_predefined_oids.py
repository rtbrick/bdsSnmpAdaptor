# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import asyncio
import os
import sys
import types
import unittest
from unittest import mock

from bdssnmpadaptor import oid_db
from bdssnmpadaptor.mapping_modules import predefined_oids as mmod

from pysnmp.proto.rfc1902 import ObjectIdentifier


@mock.patch('tempfile.NamedTemporaryFile', new=mock.MagicMock)
class StaticAndPredefinedOidsTestCase(unittest.TestCase):

    STATIC_CONFIG = {
        'SNMPv2-MIB::sysDescr': {
            'value': 'l2.pod2.nbg2.rtbrick.net'
        },
        'SNMPv2-MIB::sysUpTime': {
            'value': 0,
            'code': """
# no op
pass
"""
        }
    }

    CONFIG = {
        'snmp': {
            'mibs': [
                os.path.join(os.path.dirname(mmod.__file__), '..', '..', 'mibs')
            ]
        }
    }

    def setUp(self):
        with mock.patch.object(oid_db, 'loadConfig', autospec=True) as config_mock:
            with mock.patch.object(oid_db, 'set_logging', autospec=True):
                config_mock.return_value = self.CONFIG
                self.oidDb = oid_db.OidDb(mock.MagicMock(config={}))

        self.container = mmod.StaticAndPredefinedOids()

        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        super(StaticAndPredefinedOidsTestCase, self).setUp()

    def test_setOidsStaticValue(self):
        self.container.setOids(self.oidDb, self.STATIC_CONFIG, [], 0)

        obj = self.oidDb.getObjectByOid(ObjectIdentifier('1.3.6.1.2.1.1.1.0'))

        self.assertEqual('l2.pod2.nbg2.rtbrick.net', str(obj.value))
        self.assertIsNone(obj.code)

    def test_setOidsCodeValue(self):
        self.container.setOids(self.oidDb, self.STATIC_CONFIG, [], 0)

        obj = self.oidDb.getObjectByOid(ObjectIdentifier('1.3.6.1.2.1.1.3.0'))

        self.assertIsInstance(obj.code, types.CodeType)
        self.assertEqual(0, obj.value)

    def test_setFromStaticConfig(self):
        self.container.setOids(self.oidDb, self.STATIC_CONFIG, [], 0)

        oids_in_db = []
        oid = '1.3.6'
        while oid:
            oid = self.oidDb.getNextOid(oid)
            if oid:
                oids_in_db.append(oid)

        expected = [
            '1.3.6.1.2.1.1.1.0',
            '1.3.6.1.2.1.1.3.0',
            '1.3.6.1.2.1.47.1.1.1.1.1.1',
            '1.3.6.1.2.1.47.1.1.1.1.1.2',
            '1.3.6.1.2.1.47.1.1.1.1.1.3',
            '1.3.6.1.2.1.47.1.1.1.1.1.4',
            '1.3.6.1.2.1.47.1.1.1.1.1.5',
            '1.3.6.1.2.1.47.1.1.1.1.1.6',
            '1.3.6.1.2.1.47.1.1.1.1.2.1',
            '1.3.6.1.2.1.47.1.1.1.1.2.2',
            '1.3.6.1.2.1.47.1.1.1.1.2.3',
            '1.3.6.1.2.1.47.1.1.1.1.2.4',
            '1.3.6.1.2.1.47.1.1.1.1.2.5',
            '1.3.6.1.2.1.47.1.1.1.1.2.6',
            '1.3.6.1.2.1.47.1.1.1.1.3.1',
            '1.3.6.1.2.1.47.1.1.1.1.3.2',
            '1.3.6.1.2.1.47.1.1.1.1.3.3',
            '1.3.6.1.2.1.47.1.1.1.1.3.4',
            '1.3.6.1.2.1.47.1.1.1.1.3.5',
            '1.3.6.1.2.1.47.1.1.1.1.3.6',
            '1.3.6.1.2.1.47.1.1.1.1.4.1',
            '1.3.6.1.2.1.47.1.1.1.1.4.2',
            '1.3.6.1.2.1.47.1.1.1.1.4.3',
            '1.3.6.1.2.1.47.1.1.1.1.4.4',
            '1.3.6.1.2.1.47.1.1.1.1.4.5',
            '1.3.6.1.2.1.47.1.1.1.1.4.6',
            '1.3.6.1.2.1.47.1.1.1.1.5.1',
            '1.3.6.1.2.1.47.1.1.1.1.5.2',
            '1.3.6.1.2.1.47.1.1.1.1.5.3',
            '1.3.6.1.2.1.47.1.1.1.1.5.4',
            '1.3.6.1.2.1.47.1.1.1.1.5.5',
            '1.3.6.1.2.1.47.1.1.1.1.5.6',
            '1.3.6.1.2.1.47.1.1.1.1.6.1',
            '1.3.6.1.2.1.47.1.1.1.1.6.2',
            '1.3.6.1.2.1.47.1.1.1.1.6.3',
            '1.3.6.1.2.1.47.1.1.1.1.6.4',
            '1.3.6.1.2.1.47.1.1.1.1.6.5',
            '1.3.6.1.2.1.47.1.1.1.1.6.6',
            '1.3.6.1.2.1.47.1.1.1.1.7.1',
            '1.3.6.1.2.1.47.1.1.1.1.7.2',
            '1.3.6.1.2.1.47.1.1.1.1.7.3',
            '1.3.6.1.2.1.47.1.1.1.1.7.4',
            '1.3.6.1.2.1.47.1.1.1.1.7.5',
            '1.3.6.1.2.1.47.1.1.1.1.7.6',
            '1.3.6.1.2.1.47.1.1.1.1.8.1',
            '1.3.6.1.2.1.47.1.1.1.1.8.2',
            '1.3.6.1.2.1.47.1.1.1.1.8.3',
            '1.3.6.1.2.1.47.1.1.1.1.8.4',
            '1.3.6.1.2.1.47.1.1.1.1.8.5',
            '1.3.6.1.2.1.47.1.1.1.1.8.6',
            '1.3.6.1.2.1.47.1.1.1.1.9.1',
            '1.3.6.1.2.1.47.1.1.1.1.9.2',
            '1.3.6.1.2.1.47.1.1.1.1.9.3',
            '1.3.6.1.2.1.47.1.1.1.1.9.4',
            '1.3.6.1.2.1.47.1.1.1.1.9.5',
            '1.3.6.1.2.1.47.1.1.1.1.9.6',
            '1.3.6.1.2.1.47.1.1.1.1.10.1',
            '1.3.6.1.2.1.47.1.1.1.1.10.2',
            '1.3.6.1.2.1.47.1.1.1.1.10.3',
            '1.3.6.1.2.1.47.1.1.1.1.10.4',
            '1.3.6.1.2.1.47.1.1.1.1.10.5',
            '1.3.6.1.2.1.47.1.1.1.1.10.6',
            '1.3.6.1.2.1.47.1.1.1.1.11.1',
            '1.3.6.1.2.1.47.1.1.1.1.11.2',
            '1.3.6.1.2.1.47.1.1.1.1.11.3',
            '1.3.6.1.2.1.47.1.1.1.1.11.4',
            '1.3.6.1.2.1.47.1.1.1.1.11.5',
            '1.3.6.1.2.1.47.1.1.1.1.11.6',
            '1.3.6.1.2.1.47.1.1.1.1.12.1',
            '1.3.6.1.2.1.47.1.1.1.1.12.2',
            '1.3.6.1.2.1.47.1.1.1.1.12.3',
            '1.3.6.1.2.1.47.1.1.1.1.12.4',
            '1.3.6.1.2.1.47.1.1.1.1.12.5',
            '1.3.6.1.2.1.47.1.1.1.1.12.6',
            '1.3.6.1.2.1.47.1.1.1.1.13.1',
            '1.3.6.1.2.1.47.1.1.1.1.13.2',
            '1.3.6.1.2.1.47.1.1.1.1.13.3',
            '1.3.6.1.2.1.47.1.1.1.1.13.4',
            '1.3.6.1.2.1.47.1.1.1.1.13.5',
            '1.3.6.1.2.1.47.1.1.1.1.13.6',
            '1.3.6.1.2.1.47.1.1.1.1.14.1',
            '1.3.6.1.2.1.47.1.1.1.1.14.2',
            '1.3.6.1.2.1.47.1.1.1.1.14.3',
            '1.3.6.1.2.1.47.1.1.1.1.14.4',
            '1.3.6.1.2.1.47.1.1.1.1.14.5',
            '1.3.6.1.2.1.47.1.1.1.1.14.6',
            '1.3.6.1.2.1.47.1.1.1.1.15.1',
            '1.3.6.1.2.1.47.1.1.1.1.15.2',
            '1.3.6.1.2.1.47.1.1.1.1.15.3',
            '1.3.6.1.2.1.47.1.1.1.1.15.4',
            '1.3.6.1.2.1.47.1.1.1.1.15.5',
            '1.3.6.1.2.1.47.1.1.1.1.15.6',
            '1.3.6.1.2.1.47.1.1.1.1.16.1',
            '1.3.6.1.2.1.47.1.1.1.1.16.2',
            '1.3.6.1.2.1.47.1.1.1.1.16.3',
            '1.3.6.1.2.1.47.1.1.1.1.16.4',
            '1.3.6.1.2.1.47.1.1.1.1.16.5',
            '1.3.6.1.2.1.47.1.1.1.1.16.6',
            '1.3.6.1.2.1.47.1.1.1.1.17.1',
            '1.3.6.1.2.1.47.1.1.1.1.17.2',
            '1.3.6.1.2.1.47.1.1.1.1.17.3',
            '1.3.6.1.2.1.47.1.1.1.1.17.4',
            '1.3.6.1.2.1.47.1.1.1.1.17.5',
            '1.3.6.1.2.1.47.1.1.1.1.17.6',
            '1.3.6.1.2.1.47.1.1.1.1.18.1',
            '1.3.6.1.2.1.47.1.1.1.1.18.2',
            '1.3.6.1.2.1.47.1.1.1.1.18.3',
            '1.3.6.1.2.1.47.1.1.1.1.18.4',
            '1.3.6.1.2.1.47.1.1.1.1.18.5',
            '1.3.6.1.2.1.47.1.1.1.1.18.6'
        ]

        self.assertEqual(expected, [str(o) for o in oids_in_db])


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
