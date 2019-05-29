# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import unittest

suite = unittest.TestLoader().loadTestsFromNames(
    ['test_confd_global_interface_physical',
     'test_confd_global_interface_container',
     'test_confd_global_startup_status_confd',
     'test_confd_local_system_software_info_confd',
     'test_ffwd_default_interface_logical']
)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
