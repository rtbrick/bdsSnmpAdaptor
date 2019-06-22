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
from bdssnmpadaptor.mapping_modules import fwdd_global_interface_physical_statistics


@mock.patch('tempfile.NamedTemporaryFile', new=mock.MagicMock)
class FwddGlobalInterfacePhysicalStatisticsTestCase(unittest.TestCase):

    with open(os.path.join(os.path.dirname(__file__), '..', 'samples',
                           'fwdd_global_interface_physical_statistics.json')) as fl:
        JSON_RESPONSE = json.load(fl)

    def setUp(self):
        with mock.patch.object(oid_db, 'loadConfig', autospec=True):
            with mock.patch.object(oid_db, 'set_logging', autospec=True):
                self.oidDb = oid_db.OidDb(mock.MagicMock(config={}))

        self.container = fwdd_global_interface_physical_statistics.FwddGlobalInterfacePhysicalStatistics()

        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        super(FwddGlobalInterfacePhysicalStatisticsTestCase, self).setUp()

    def test_setOids(self):
        self.container.setOids(self.oidDb, self.JSON_RESPONSE, [], 0)

        oids_in_db = []
        oid = '1.3.6'
        while oid:
            oid = self.oidDb.getNextOid(oid)
            if oid:
                oids_in_db.append(oid)

        expected = [
            '1.3.6.1.2.1.2.1.0',
            '1.3.6.1.2.1.2.2.1.9.528384',
            '1.3.6.1.2.1.2.2.1.10.528384',
            '1.3.6.1.2.1.2.2.1.11.528384',
            '1.3.6.1.2.1.2.2.1.12.528384',
            '1.3.6.1.2.1.2.2.1.13.528384',
            '1.3.6.1.2.1.2.2.1.14.528384',
            '1.3.6.1.2.1.2.2.1.15.528384',
            '1.3.6.1.2.1.2.2.1.16.528384',
            '1.3.6.1.2.1.2.2.1.17.528384',
            '1.3.6.1.2.1.2.2.1.18.528384',
            '1.3.6.1.2.1.2.2.1.19.528384',
            '1.3.6.1.2.1.2.2.1.20.528384',
            '1.3.6.1.2.1.2.2.1.21.528384',
            '1.3.6.1.2.1.31.1.5.0',
            '1.3.6.1.2.1.31.1.6.0'
        ]

        self.assertEqual(expected, [str(o) for o in oids_in_db])


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
