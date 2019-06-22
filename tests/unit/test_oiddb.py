# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import sys
import types
import unittest
from unittest import mock

from pysnmp.proto import rfc1902

from bdssnmpadaptor import oid_db


class OidDbItemTestCase(unittest.TestCase):

    def test___init__(self):
        oid = oid_db.OidDbItem(
            oid='1.3.6.7.8',
            name='ifIndex',
            value=rfc1902.OctetString(hexValue='123456789'),
        )

        self.assertEqual(rfc1902.ObjectIdentifier('1.3.6.7.8'), oid.oid)
        self.assertEqual('ifIndex', oid.name)
        self.assertEqual(b'\x124Vx\x90', oid.value)

    def test___lt__(self):
        oid1 = oid_db.OidDbItem(oid='1.3.6.7.8')
        oid2 = oid_db.OidDbItem(oid='1.3.6.8.1')

        self.assertLess(oid1, oid2)
        self.assertGreater(oid2, oid1)

    def test___eq__(self):
        oid1 = oid_db.OidDbItem(oid='1.3.6.7.8')
        oid2 = oid_db.OidDbItem(oid='1.3.6.8.1')

        self.assertNotEqual(oid1, oid2)
        self.assertEqual(oid1, oid1)

    def test___str__(self):
        oid = oid_db.OidDbItem(
            oid='1.3.6.7.8',
            name='ifIndex',
            value=rfc1902.OctetString(hexValue='123456789'),
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
        with mock.patch.object(oid_db, 'loadConfig', autospec=True):
            with mock.patch.object(oid_db, 'set_logging', autospec=True):
                self.oidDb = oid_db.OidDb(mock.MagicMock(config={}))

                for ident, value in reversed(self.MIB_OBJECTS):
                    self.oidDb.add(*ident, value=value)

        super(OidDbTestCase, self).setUp()

    @mock.patch.object(oid_db, 'loadConfig', autospec=True)
    @mock.patch.object(oid_db, 'set_logging', autospec=True)
    def test_add_value(self, mock_set_logging, mock_loadConfig):
        oidDb = oid_db.OidDb(mock.MagicMock(config={}))

        oidDb.add('SNMPv2-MIB', 'sysDescr', 0, value='my system')

        expectedOid = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.1.0')

        oidItem = oidDb.getObjectByOid(expectedOid)

        self.assertEqual(expectedOid, oidItem.oid)

        expectedValue = rfc1902.OctetString('my system')
        self.assertEqual(expectedValue, oidItem.value)

        self.assertIsNone(oidItem.code)

    @mock.patch.object(oid_db, 'loadConfig', autospec=True)
    @mock.patch.object(oid_db, 'set_logging', autospec=True)
    def test_add_code(self, mock_set_logging, mock_loadConfig):
        oidDb = oid_db.OidDb(mock.MagicMock(config={}))

        code = """
# no op
pass
"""
        oidDb.add('SNMPv2-MIB', 'sysDescr', 0, value='', code=code)

        expectedOid = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.1.0')

        oidItem = oidDb.getObjectByOid(expectedOid)

        self.assertEqual(expectedOid, oidItem.oid)
        self.assertEqual('', str(oidItem.value))
        self.assertIsInstance(oidItem.code, types.CodeType)

    @mock.patch('time.time', autospec=True)
    @mock.patch.object(oid_db, 'loadConfig', autospec=True)
    @mock.patch.object(oid_db, 'set_logging', autospec=True)
    def test_add_expire(self, mock_set_logging, mock_loadConfig, mock_time):
        mock_time.return_value = 0

        oidDb = oid_db.OidDb(mock.MagicMock(config={}))

        # add sysDescr.0 and expect it to be in the OID DB

        oidDb.add('SNMPv2-MIB', 'sysDescr', 0, value='my system')

        expected = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.1.0')

        oidItem = oidDb.getObjectByOid(expected)

        self.assertEqual(expected, oidItem.oid)

        mock_time.return_value = 61

        # add sysORDescr.1 and expect sysDescr.0 & sysORDescr.1
        # to be in the OID DB

        oidDb.add('SNMPv2-MIB', 'sysORDescr', 1, value='descr')

        expected = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.1.0')

        oidItem = oidDb.getObjectByOid(expected)

        self.assertEqual(expected, oidItem.oid)

        expected = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.9.1.3.1')

        oidItem = oidDb.getObjectByOid(expected)

        self.assertEqual(expected, oidItem.oid)

        mock_time.return_value = 122

        # add sysORDescr.2 and expect sysORDescr.1 to expire

        oidDb.add('SNMPv2-MIB', 'sysORDescr', 2, value='descr')

        expected = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.1.0')

        oidItem = oidDb.getObjectByOid(expected)

        self.assertEqual(expected, oidItem.oid)

        not_expected = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.9.1.3.1')

        oidItem = oidDb.getObjectByOid(not_expected)

        self.assertIsNone(oidItem)

        expected = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.9.1.3.2')

        oidItem = oidDb.getObjectByOid(expected)

        self.assertEqual(expected, oidItem.oid)

    @mock.patch('time.time', autospec=True)
    @mock.patch.object(oid_db, 'loadConfig', autospec=True)
    @mock.patch.object(oid_db, 'set_logging', autospec=True)
    def test_add_permanent(self, mock_set_logging, mock_loadConfig, mock_time):
        mock_time.return_value = 0

        oidDb = oid_db.OidDb(mock.MagicMock(config={}))

        # add sysDescr and expect it to be in the OID DB

        oidDb.add('SNMPv2-MIB', 'sysDescr', 0, value='my system')

        expected = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.1.0')

        oidItem = oidDb.getObjectByOid(expected)

        self.assertEqual(expected, oidItem.oid)

        mock_time.return_value = 61

        # add snmpOutNoSuchNames and expect sysDescr & snmpOutNoSuchNames
        # to be in the OID DB

        oidDb.add('SNMPv2-MIB', 'snmpOutNoSuchNames', 0, value=123)

        expected = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.1.0')

        oidItem = oidDb.getObjectByOid(expected)

        self.assertEqual(expected, oidItem.oid)

        expected = rfc1902.ObjectIdentifier('1.3.6.1.2.1.11.21.0')

        oidItem = oidDb.getObjectByOid(expected)

        self.assertEqual(expected, oidItem.oid)

        mock_time.return_value = 122

        # update snmpOutNoSuchNames, but expect sysDescr to still be there

        oidDb.add('SNMPv2-MIB', 'snmpOutNoSuchNames', 0, value=123)

        expected = rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.1.0')

        oidItem = oidDb.getObjectByOid(expected)

        self.assertEqual(expected, oidItem.oid)

        expected = rfc1902.ObjectIdentifier('1.3.6.1.2.1.11.21.0')

        oidItem = oidDb.getObjectByOid(expected)

        self.assertEqual(expected, oidItem.oid)

    def test_getNextOid(self):
        for idx, oid in enumerate(self.OIDS[:-1]):
            nextOid = self.oidDb.getNextOid(oid)

            self.assertEqual(self.OIDS[idx + 1], nextOid)

    def test_getObjFromOid_good(self):
        oidItem = self.oidDb.getObjectByOid(self.OIDS[1])

        self.assertEqual(self.OIDS[1], oidItem.oid)

    def test_getObjFromOid_not_exists(self):
        oidItem = self.oidDb.getObjectByOid(self.OIDS[1] + (1,))

        self.assertIsNone(oidItem)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
