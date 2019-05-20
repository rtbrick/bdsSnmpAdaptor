# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import asyncio
import json
import os
import sys
import unittest
from unittest import mock

from bdssnmpadaptor import oidDb
from bdssnmpadaptor.mapping_modules import confd_global_startup_status_confd


@mock.patch('tempfile.NamedTemporaryFile', new=mock.MagicMock)
class ConfdGlobalStartupStatusConfdTestCase(unittest.TestCase):

    CONFIG = {
        'config': {
            'snmp': {
                'mibs': [
                    'mibs',
                    '/usr/share/snmp/mibs'
                ]
            }
        }
    }

    with open(os.path.join(os.path.dirname(__file__), '..', 'samples',
                           'confd-global-startup-status.json')) as fl:
        JSON_RESPONSE = json.load(fl)

    def setUp(self):
        with mock.patch.object(oidDb, 'loadConfig', autospec=True) as config_mock:
            config_mock.return_value = self.CONFIG['config']

            with mock.patch.object(oidDb, 'set_logging', autospec=True):
                self.oidDb = oidDb.OidDb(self.CONFIG)

        self.container = confd_global_startup_status_confd.ConfdGlobalStartupStatusConfd()

        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        super(ConfdGlobalStartupStatusConfdTestCase, self).setUp()

    def test_setOids(self):
        self.my_loop.run_until_complete(
            self.container.setOids(self.JSON_RESPONSE, self.oidDb, [], 0))

        oids_in_db = []
        oid = '1.3.6'
        while oid:
            oid = self.oidDb.getNextOid(oid)
            if oid:
                oids_in_db.append(oid)

        expected = [
            '1.3.6.1.2.1.25.4.1.1',
            '1.3.6.1.2.1.25.4.1.2',
            '1.3.6.1.2.1.25.4.1.3',
            '1.3.6.1.2.1.25.4.2.1.2.1',
            '1.3.6.1.2.1.25.4.2.1.2.2',
            '1.3.6.1.2.1.25.4.2.1.2.3',
            '1.3.6.1.2.1.25.4.2.1.3.1',
            '1.3.6.1.2.1.25.4.2.1.3.2',
            '1.3.6.1.2.1.25.4.2.1.3.3',
            '1.3.6.1.2.1.25.4.2.1.4.1',
            '1.3.6.1.2.1.25.4.2.1.4.2',
            '1.3.6.1.2.1.25.4.2.1.4.3',
            '1.3.6.1.2.1.25.4.2.1.5.1',
            '1.3.6.1.2.1.25.4.2.1.5.2',
            '1.3.6.1.2.1.25.4.2.1.5.3',
            '1.3.6.1.2.1.25.4.2.1.6.1',
            '1.3.6.1.2.1.25.4.2.1.6.2',
            '1.3.6.1.2.1.25.4.2.1.6.3',
            '1.3.6.1.2.1.25.4.2.1.7.1',
            '1.3.6.1.2.1.25.4.2.1.7.2',
            '1.3.6.1.2.1.25.4.2.1.7.3'
         ]

        self.assertEqual(expected, [str(o) for o in oids_in_db])


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
