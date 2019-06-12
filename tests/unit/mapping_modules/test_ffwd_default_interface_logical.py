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
from bdssnmpadaptor.mapping_modules import ffwd_default_interface_logical


@mock.patch('tempfile.NamedTemporaryFile', new=mock.MagicMock)
class FfwdDefaultInterfaceLogicalTestCase(unittest.TestCase):

    with open(os.path.join(os.path.dirname(__file__), '..', 'samples',
                           'ffwd-default-interface-logical.json')) as fl:
        JSON_RESPONSE = json.load(fl)

    def setUp(self):
        with mock.patch.object(oid_db, 'loadConfig', autospec=True):
            with mock.patch.object(oid_db, 'set_logging', autospec=True):
                self.oidDb = oid_db.OidDb({'config': {}})

        self.container = ffwd_default_interface_logical.FfwdDefaultInterfaceLogical()

        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        super(FfwdDefaultInterfaceLogicalTestCase, self).setUp()

    def test_setOids(self):
        self.container.setOids(self.oidDb, self.JSON_RESPONSE, [], 0)

        oids_in_db = []
        oid = '1.3.6'
        while oid:
            oid = self.oidDb.getNextOid(oid)
            if oid:
                oids_in_db.append(oid)

        expected = [
            '1.3.6.1.2.1.2.2.1.1.528385',
            '1.3.6.1.2.1.2.2.1.2.528385',
            '1.3.6.1.2.1.2.2.1.3.528385'
        ]

        self.assertEqual(expected, [str(o) for o in oids_in_db])


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
