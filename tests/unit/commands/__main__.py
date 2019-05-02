# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import unittest

suite = unittest.TestLoader().loadTestsFromNames(
    ['test_responder',
     'test_notificator']
)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
