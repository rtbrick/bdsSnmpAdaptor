# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import sys
import unittest

from bdssnmpadaptor import if_tools


class MappingFunctionsTestCase(unittest.TestCase):

    def test_ifIndexFromIfName_ifc(self):
        ifName = "ifc-0/0/1/1"
        ifIndex = if_tools.ifIndexFromIfName(ifName)
        expected = 528384
        self.assertEqual(expected, ifIndex)

    def test_ifIndexFromIfName_ifp(self):
        ifName = "ifp-0/0/1"
        ifIndex = if_tools.ifIndexFromIfName(ifName)
        expected = 4096
        self.assertEqual(expected, ifIndex)

    def test_ifIndexFromIfName_ifl(self):
        ifName = "ifl-0/0/1/1/0"
        ifIndex = if_tools.ifIndexFromIfName(ifName)
        expected = 528385
        self.assertEqual(expected, ifIndex)

    def test_ifIndexFromIfName_lo(self):
        ifName = "lo-0/0/1"
        ifIndex = if_tools.ifIndexFromIfName(ifName)
        expected = 4294971392
        self.assertEqual(expected, ifIndex)

    def test_ifIndexFromIfName_unknown(self):
        ifName = "unk-1/0/1"
        ifIndex = if_tools.ifIndexFromIfName(ifName)
        self.assertIsNone(ifIndex)

    def test_stripIfPrefixFromIfName_ifc(self):
        ifName = "ifc-0/0/1/1"
        stripped = if_tools.stripIfPrefixFromIfName(ifName)
        expected = '0/1/1'
        self.assertEqual(expected, stripped)

    def test_stripIfPrefixFromIfName_ifp(self):
        ifName = "ifp-0/0/1"
        stripped = if_tools.stripIfPrefixFromIfName(ifName)
        expected = '0/0/1'
        self.assertEqual(expected, stripped)

    def test_stripIfPrefixFromIfName_ifl(self):
        ifName = "ifl-0/0/1/1/0"
        stripped = if_tools.stripIfPrefixFromIfName(ifName)
        expected = '0/0/1/1/0'
        self.assertEqual(expected, stripped)

    def test_stripIfPrefixFromIfName_unknown(self):
        ifName = "unk-0/0/1/1/0/0"
        stripped = if_tools.stripIfPrefixFromIfName(ifName)
        self.assertIsNone(stripped)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
