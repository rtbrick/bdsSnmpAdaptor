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
from bdssnmpadaptor.mapping_modules import confd_local_system_software_info_confd


@mock.patch('tempfile.NamedTemporaryFile', new=mock.MagicMock)
class ConfdLocalSystemSoftwareInfoConfdTestCase(unittest.TestCase):

    with open(os.path.join(os.path.dirname(__file__), '..', 'samples',
                           'confd-local-system-software-info.json')) as fl:
        JSON_RESPONSE = json.load(fl)

    def setUp(self):
        with mock.patch.object(oidDb, 'loadBdsSnmpAdapterConfigFile', autospec=True):
            with mock.patch.object(oidDb, 'set_logging', autospec=True):
                self.oidDb = oidDb.OidDb({'config': {}})

        self.container = confd_local_system_software_info_confd.ConfdLocalSystemSoftwareInfoConfd()

        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        super(ConfdLocalSystemSoftwareInfoConfdTestCase, self).setUp()

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
            '1.3.6.1.2.1.1.1.0'
        ]

        self.assertEqual(expected, oids_in_db)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
