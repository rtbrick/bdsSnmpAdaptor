# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import unittest

suite = unittest.TestLoader().loadTestsFromNames(
    ['tests.unit.test_error.suite',
     'tests.unit.test_snmp_config.suite',
     'tests.unit.test_oiddb.suite']
     'tests.unit.test_config.suite']
)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
