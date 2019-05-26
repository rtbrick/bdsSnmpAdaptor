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
from bdssnmpadaptor.mapping_modules import fwdd_global_interface_physical_statistics


@mock.patch('tempfile.NamedTemporaryFile', new=mock.MagicMock)
class FwddGlobalInterfacePhysicalStatisticsTestCase(unittest.TestCase):

    with open(os.path.join(os.path.dirname(__file__), '..', 'samples',
                           'fwdd_global_interface_physical_statistics.json')) as fl:
        JSON_RESPONSE = json.load(fl)

    def setUp(self):
        with mock.patch.object(oidDb, 'loadConfig', autospec=True):
            with mock.patch.object(oidDb, 'set_logging', autospec=True):
                self.oidDb = oidDb.OidDb({'config': {}})

        self.container = fwdd_global_interface_physical_statistics.FwddGlobalInterfacePhysicalStatistics()

        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        super(FwddGlobalInterfacePhysicalStatisticsTestCase, self).setUp()

    def test_setOids(self):
        self.container.setOids(self.JSON_RESPONSE, self.oidDb, [], 0)

        oids_in_db = []
        oid = '1.3.6'
        while oid:
            oid = self.oidDb.getNextOid(oid)
            if oid:
                oids_in_db.append(oid)

        expected = [
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
            '1.3.6.1.2.1.2.2.1.21.528384'
        ]

        self.assertEqual(expected, [str(o) for o in oids_in_db])


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
