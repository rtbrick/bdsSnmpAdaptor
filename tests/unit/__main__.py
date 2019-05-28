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
     'tests.unit.test_oiddb.suite',
     'tests.unit.test_mapping_functions.suite',
     'tests.unit.test_access.suite',
     'tests.unit.test_config.suite',
     'tests.unit.test_mib_controller.suite',
     'tests.unit.test_snmp_responder.suite',
     'tests.unit.test_snmp_notificator.suite',
     'tests.unit.test_rest_responder.suite',
     'mapping_modules',
     'commands']
)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
