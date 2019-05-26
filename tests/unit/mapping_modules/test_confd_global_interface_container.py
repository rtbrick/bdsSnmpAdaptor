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
from bdssnmpadaptor.mapping_modules import confd_global_interface_container


@mock.patch('tempfile.NamedTemporaryFile', new=mock.MagicMock)
class ConfdGlobalInterfaceContainerTestCase(unittest.TestCase):

    with open(os.path.join(os.path.dirname(__file__), '..', 'samples',
                           'confd-global-interface-container.json')) as fl:
        JSON_RESPONSE = json.load(fl)

    def setUp(self):
        with mock.patch.object(oidDb, 'loadConfig', autospec=True):
            with mock.patch.object(oidDb, 'set_logging', autospec=True):
                self.oidDb = oidDb.OidDb({'config': {}})

        self.container = confd_global_interface_container.ConfdGlobalInterfaceContainer()

        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        super(ConfdGlobalInterfaceContainerTestCase, self).setUp()

    def test_setOids(self):
        self.container.setOids(self.JSON_RESPONSE, self.oidDb, [], 0)

        oids_in_db = []
        oid = '1.3.6'
        while oid:
            oid = self.oidDb.getNextOid(oid)
            if oid:
                oids_in_db.append(oid)

        expected = [
            '1.3.6.1.2.1.2.1.0',
            '1.3.6.1.2.1.2.2.1.1.4096',
            '1.3.6.1.2.1.2.2.1.1.8192',
            '1.3.6.1.2.1.2.2.1.1.12288',
            '1.3.6.1.2.1.2.2.1.2.4096',
            '1.3.6.1.2.1.2.2.1.2.8192',
            '1.3.6.1.2.1.2.2.1.2.12288',
            '1.3.6.1.2.1.2.2.1.3.4096',
            '1.3.6.1.2.1.2.2.1.3.8192',
            '1.3.6.1.2.1.2.2.1.3.12288',
            '1.3.6.1.2.1.2.2.1.4.4096',
            '1.3.6.1.2.1.2.2.1.4.8192',
            '1.3.6.1.2.1.2.2.1.4.12288',
            '1.3.6.1.2.1.2.2.1.5.4096',
            '1.3.6.1.2.1.2.2.1.5.8192',
            '1.3.6.1.2.1.2.2.1.5.12288',
            '1.3.6.1.2.1.2.2.1.6.4096',
            '1.3.6.1.2.1.2.2.1.6.8192',
            '1.3.6.1.2.1.2.2.1.6.12288',
            '1.3.6.1.2.1.2.2.1.7.4096',
            '1.3.6.1.2.1.2.2.1.7.8192',
            '1.3.6.1.2.1.2.2.1.7.12288',
            '1.3.6.1.2.1.2.2.1.8.4096',
            '1.3.6.1.2.1.2.2.1.8.8192',
            '1.3.6.1.2.1.2.2.1.8.12288',
            '1.3.6.1.2.1.2.2.1.9.4096',
            '1.3.6.1.2.1.2.2.1.9.8192',
            '1.3.6.1.2.1.2.2.1.9.12288',
            '1.3.6.1.2.1.31.1.5.4096',
            '1.3.6.1.2.1.31.1.5.8192',
            '1.3.6.1.2.1.31.1.5.12288',
            '1.3.6.1.2.1.31.1.6.4096',
            '1.3.6.1.2.1.31.1.6.8192',
            '1.3.6.1.2.1.31.1.6.12288'
        ]

        self.assertEqual(expected, [str(o) for o in oids_in_db])


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
