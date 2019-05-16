# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import sys
import unittest
from unittest import mock

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

    def test___eq__(self):
        oid1 = oidDb.OidDbItem(oid='1.3.6.7.8')
        oid2 = oidDb.OidDbItem(oid='1.3.6.8.1')

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

    OIDS = [
        '1.3.6.1.2.3.0',
        '1.3.6.1.20.3.0',
        '1.3.6.11.29.32.3',
        '1.3.6.999.1.33222.4443'
    ]

    def setUp(self):
        with mock.patch.object(oidDb, 'loadConfig', autospec=True):
            with mock.patch.object(oidDb, 'set_logging', autospec=True):
                self.oidDb = oidDb.OidDb({'config': {}})

                oidDbItems = [oidDb.OidDbItem(bdsMappingFunc=self.__class__, oid=oid)
                              for oid in self.OIDS]

                for oidDbItem in reversed(oidDbItems):
                    self.oidDb.insertOid(oidDbItem)

        super(OidDbTestCase, self).setUp()

    def test_getFirstItem(self):
        self.assertEqual(self.OIDS[0], self.oidDb.getFirstItem().oid)

    def test_getNextOid(self):
        for idx, oid in enumerate(self.OIDS[:-1]):
            nextOid = self.oidDb.getNextOid(oid)

            self.assertEqual(self.OIDS[idx + 1], nextOid)

    def test_deleteOidsWithPrefix_all(self):
        self.oidDb.deleteOidsWithPrefix('1.3.6')

        nextOid = self.oidDb.getNextOid(self.OIDS[0])

        self.assertIsNone(nextOid)

    def test_deleteOidsWithPrefix_one(self):
        self.oidDb.deleteOidsWithPrefix(self.OIDS[2])

        nextOid = self.oidDb.getNextOid(self.OIDS[1])

        self.assertEqual(self.OIDS[3], nextOid)

    def test_deleteOidsWithPrefix_none(self):
        self.oidDb.deleteOidsWithPrefix(self.OIDS[0] + '.123')

        nextOid = self.oidDb.getNextOid(self.OIDS[0])

        self.assertEqual(self.OIDS[1], nextOid)

    def test_deleteOidsFromBdsMappingFunc_all(self):
        self.oidDb.deleteOidsFromBdsMappingFunc(self.__class__)

        nextOid = self.oidDb.getNextOid(self.OIDS[1])

        self.assertIsNone(nextOid)

    def test_deleteOidsFromBdsMappingFunc_none(self):
        self.oidDb.deleteOidsFromBdsMappingFunc(None)

        nextOid = self.oidDb.getNextOid(self.OIDS[0])

        self.assertEqual(self.OIDS[1], nextOid)

    def test_getObjFromOid_good(self):
        oidItem = self.oidDb.getObjFromOid(self.OIDS[1])

        self.assertEqual(self.OIDS[1], oidItem.oid)

    def test_getObjFromOid_not_exists(self):
        oidItem = self.oidDb.getObjFromOid(self.OIDS[1] + '.1')

        self.assertIsNone(oidItem)

    def test_locks(self):
        self.assertFalse(self.oidDb.isLocked())
        self.oidDb.setLock()
        self.assertTrue(self.oidDb.isLocked())


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
