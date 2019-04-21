# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import sys
import unittest

from bdssnmpadaptor import oidDb


class OidDbItemTestCase(unittest.TestCase):

    def test___init__(self):
        oid = oidDb.OidDbItem(
            bdsMappingFunc='interface_container',
            oid='1.3.6.7.8',
            name='ifIndex',
            pysnmpBaseType=object,
            pysnmpRepresentation='hexValue',
            value='0x123456789',
        )

        self.assertEqual('interface_container', oid.bdsMappingFunc)
        self.assertEqual('1.3.6.7.8', oid.oid)
        self.assertEqual('ifIndex', oid.name)
        self.assertEqual(object, oid.pysnmpBaseType)
        self.assertEqual('hexValue', oid.pysnmpRepresentation)
        self.assertEqual('0x123456789', oid.value)

    def test___lt__(self):
        oid1 = oidDb.OidDbItem(oid='1.3.6.7.8')
        oid2 = oidDb.OidDbItem(oid='1.3.6.8.1')

        self.assertLess(oid1, oid2)
        self.assertGreater(oid2, oid1)
        self.assertNotEqual(oid1, oid2)
        self.assertEqual(oid1, oid1)

    def test___str__(self):
        oid = oidDb.OidDbItem(
            bdsMappingFunc='interface_container',
            oid='1.3.6.7.8',
            name='ifIndex',
            pysnmpBaseType=object,
            pysnmpRepresentation='hexValue',
            value='0x123456789',
        )

        self.assertIsInstance(str(oid), str)
        self.assertTrue(str(oid))


class OidDbTestCase(unittest.TestCase):

    def setUp(self):
        super(OidDbTestCase, self).setUp()


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
