# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import sys
import unittest

from bdssnmpadaptor import error


class BdsErrorTestCase(unittest.TestCase):

    def test_error(self):

        def willRaise():
            raise error.BdsError()

        self.assertRaises(error.BdsError, willRaise)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
