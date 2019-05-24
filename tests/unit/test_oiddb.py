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

from pysnmp.proto import rfc1902

from bdssnmpadaptor import oidDb


class OidDbItemTestCase(unittest.TestCase):

    def test___init__(self):
        oid = oidDb.OidDbItem(
            bdsMappingFunc='interface_container',
            oid='1.3.6.7.8',
            name='ifIndex',
            pysnmpBaseType=rfc1902.OctetString,
            pysnmpRepresentation='hexValue',
            value='123456789',
        )

        self.assertEqual('interface_container', oid.bdsMappingFunc)
        self.assertEqual(rfc1902.ObjectIdentifier('1.3.6.7.8'), oid.oid)
        self.assertEqual('ifIndex', oid.name)
        self.assertEqual(rfc1902.OctetString, oid.pysnmpBaseType)
        self.assertEqual(b'\x124Vx\x90', oid.value)

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
            pysnmpBaseType=rfc1902.OctetString,
            value='0x123456789',
        )

        self.assertIsInstance(str(oid), str)
        self.assertTrue(str(oid))


class OidDbTestCase(unittest.TestCase):

    MIB_OBJECTS = [
        (('SNMPv2-MIB', 'sysDescr', 0), 'my system'),
        (('SNMPv2-MIB', 'snmpOutNoSuchNames', 0), 123),
        (('SNMPv2-MIB', 'snmpEnableAuthenTraps', 0), 1)
    ]

    OIDS = [
        rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.1.0'),
        rfc1902.ObjectIdentifier('1.3.6.1.2.1.11.21.0'),
        rfc1902.ObjectIdentifier('1.3.6.1.2.1.11.30.0'),
    ]

    def setUp(self):
        with mock.patch.object(oidDb, 'loadConfig', autospec=True):
            with mock.patch.object(oidDb, 'set_logging', autospec=True):
                self.oidDb = oidDb.OidDb({'config': {}})

                for ident, value in reversed(self.MIB_OBJECTS):
                    self.oidDb.add(*ident, value=value, bdsMappingFunc=__class__)

        super(OidDbTestCase, self).setUp()

    def test_getNextOid(self):
        for idx, oid in enumerate(self.OIDS[:-1]):
            nextOid = self.oidDb.getNextOid(oid)

            self.assertEqual(self.OIDS[idx + 1], nextOid)

    def test_deleteOidsWithPrefix_all(self):
        self.oidDb.deleteOidsWithPrefix('1.3.6')

        nextOid = self.oidDb.getNextOid(self.OIDS[0])

        self.assertIsNone(nextOid)

    def test_deleteOidsWithPrefix_one(self):
        self.oidDb.deleteOidsWithPrefix(self.OIDS[1])

        nextOid = self.oidDb.getNextOid(self.OIDS[0])

        self.assertEqual(self.OIDS[2], nextOid)

    def test_deleteOidsWithPrefix_none(self):
        self.oidDb.deleteOidsWithPrefix(self.OIDS[0] + (123,))

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
        oidItem = self.oidDb.getObjFromOid(self.OIDS[1] + (1,))

        self.assertIsNone(oidItem)

    def test_contextManager(self):
        with self.oidDb.module('interfaces') as add:
            add('SNMPv2-MIB', 'sysLocation', 0, value='DC')

        oid = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.6.0')

        self.assertIn(oid, self.oidDb.oidDict)
        self.assertEqual(b'DC', self.oidDb.oidDict[oid].value)
        self.assertEqual('interfaces', self.oidDb.oidDict[oid].bdsMappingFunc)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
