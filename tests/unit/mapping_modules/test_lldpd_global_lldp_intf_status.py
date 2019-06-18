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
import time
import unittest
from unittest import mock

from bdssnmpadaptor import oid_db
from bdssnmpadaptor.mapping_modules import lldpd_global_lldp_intf_status


@mock.patch('tempfile.NamedTemporaryFile', new=mock.MagicMock)
class LldpdGlobalLldpIntfStatusTestCase(unittest.TestCase):

    with open(os.path.join(os.path.dirname(__file__), '..', 'samples',
                           'lldpd-global-lldp-intf-status.json')) as fl:
        JSON_RESPONSE = json.load(fl)

    def setUp(self):
        with mock.patch.object(oid_db, 'loadConfig', autospec=True):
            with mock.patch.object(oid_db, 'set_logging', autospec=True):
                self.oidDb = oid_db.OidDb(mock.MagicMock(config={}))

        self.container = lldpd_global_lldp_intf_status.LldpdGlobalLldpIntfStatus()

        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        super(LldpdGlobalLldpIntfStatusTestCase, self).setUp()

    def test_setOids(self):
        self.container.setOids(self.oidDb, self.JSON_RESPONSE, [], time.time())

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
            '1.3.6.1.2.1.2.2.1.2.4096',
            '1.3.6.1.2.1.2.2.1.2.8192',
            '1.3.6.1.2.1.2.2.1.3.4096',
            '1.3.6.1.2.1.2.2.1.3.8192',
            '1.3.6.1.2.1.2.2.1.4.4096',
            '1.3.6.1.2.1.2.2.1.4.8192',
            '1.3.6.1.2.1.2.2.1.5.4096',
            '1.3.6.1.2.1.2.2.1.5.8192',
            '1.3.6.1.2.1.2.2.1.6.4096',
            '1.3.6.1.2.1.2.2.1.6.8192',
            '1.3.6.1.2.1.2.2.1.7.4096',
            '1.3.6.1.2.1.2.2.1.7.8192',
            '1.3.6.1.2.1.2.2.1.8.4096',
            '1.3.6.1.2.1.2.2.1.8.8192',
            '1.3.6.1.2.1.2.2.1.9.4096',
            '1.3.6.1.2.1.2.2.1.9.8192',
            '1.3.6.1.2.1.31.1.5.0',
            '1.3.6.1.2.1.31.1.6.0'
        ]

        self.assertEqual(expected, [str(o) for o in oids_in_db])


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
