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

from bdssnmpadaptor import oid_db
from bdssnmpadaptor.mapping_modules import confd_local_system_software_info_confd as mmod


@mock.patch('tempfile.NamedTemporaryFile', new=mock.MagicMock)
class ConfdLocalSystemSoftwareInfoConfdTestCase(unittest.TestCase):

    with open(os.path.join(os.path.dirname(__file__), '..', 'samples',
                           'confd-local-system-software-info.json')) as fl:
        JSON_RESPONSE = json.load(fl)

    def setUp(self):
        with mock.patch.object(oid_db, 'loadConfig', autospec=True):
            with mock.patch.object(oid_db, 'set_logging', autospec=True):
                self.oidDb = oid_db.OidDb(mock.MagicMock(config={}))

        self.container = mmod.ConfdLocalSystemSoftwareInfoConfd()

        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        super(ConfdLocalSystemSoftwareInfoConfdTestCase, self).setUp()

    def test_getSoftwareInfo(self):
        version = mmod.ConfdLocalSystemSoftwareInfoConfd.getSoftwareInfo(self.JSON_RESPONSE)
        expected = 'RtBrick Fullstack: bd:19.04-29'
        self.assertEqual(expected, version)

    def test_setOids(self):
        self.container.setOids(self.oidDb, self.JSON_RESPONSE, [], 0)

        oids_in_db = []
        oid = '1.3.6'
        while oid:
            oid = self.oidDb.getNextOid(oid)
            if oid:
                oids_in_db.append(oid)

        expected = [
            '1.3.6.1.2.1.1.1.0'
        ]

        self.assertEqual(expected, [str(o) for o in oids_in_db])


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
