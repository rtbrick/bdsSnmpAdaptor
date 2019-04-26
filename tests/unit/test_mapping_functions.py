# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import json
import os
import sys
import unittest

from bdssnmpadaptor.mapping_functions import BdsMappingFunctions


class MappingFunctionsTestCase(unittest.TestCase):

    with open(os.path.join(os.path.dirname(__file__), 'samples',
                           'bds-version-response.json')) as fl:
        JSON_RESPONSE = json.load(fl)

    def test_stringFromSoftwareInfo(self):
        version = BdsMappingFunctions.stringFromSoftwareInfo(self.JSON_RESPONSE)
        expected = ('RtBrick Fullstack: bd:18.06-0 libbgp:18.06-2 libfwdd:18.06-0 '
                    'lwip:18.06-0 libbds:18.06-0 libisis:18.06-3 libconfd:18.06-0')
        self.assertEqual(expected, version)

    def test_ifIndexFromIfName_ifc(self):
        ifName = "ifc-0/0/1/1"
        ifIndex = BdsMappingFunctions.ifIndexFromIfName(ifName)
        expected = 528384
        self.assertEqual(expected, ifIndex)

    def test_ifIndexFromIfName_ifp(self):
        ifName = "ifp-0/0/1"
        ifIndex = BdsMappingFunctions.ifIndexFromIfName(ifName)
        expected = 4096
        self.assertEqual(expected, ifIndex)

    def test_ifIndexFromIfName_ifl(self):
        ifName = "ifl-0/0/1/1/0"
        ifIndex = BdsMappingFunctions.ifIndexFromIfName(ifName)
        expected = 528385
        self.assertEqual(expected, ifIndex)

    def test_stripIfPrefixFromIfName_ifc(self):
        ifName = "ifc-0/0/1/1"
        stripped = BdsMappingFunctions.stripIfPrefixFromIfName(ifName)
        expected = '0/1/1'
        self.assertEqual(expected, stripped)

    def test_stripIfPrefixFromIfName_ifp(self):
        ifName = "ifp-0/0/1"
        stripped = BdsMappingFunctions.stripIfPrefixFromIfName(ifName)
        expected = '0/0/1'
        self.assertEqual(expected, stripped)

    def test_stripIfPrefixFromIfName_ifl(self):
        ifName = "ifl-0/0/1/1/0"
        stripped = BdsMappingFunctions.stripIfPrefixFromIfName(ifName)
        expected = '0/0/1/1/0'
        self.assertEqual(expected, stripped)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
