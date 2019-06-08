# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import io
import sys
import unittest
from unittest import mock

from bdssnmpadaptor import mib_controller


class MibControllerTestCase(unittest.TestCase):

    CONFIG = """
    bdsSnmpAdapter:
      loggingLevel: debug
      stateDir: /var/run/bds-snmp-responder
      access:
        rtbrickHost: 10.0.3.10
        rtbrickPorts:
         - confd: 2002  # confd REST API listens on this port"
         - fwdd-hald: 5002  # fwwd REST API listens on this port"
      responder:
        staticOidContent:
          sysDescr: l2.pod2.nbg2.rtbrick.net
          sysContact: stefan@rtbrick.com
          sysName: l2.pod2.nbg2.rtbrick.net
          sysLocation: nbg2.rtbrick.net
    """

    def setUp(self):
        self.mock_oidDb = mock.MagicMock()

        with mock.patch(
                'bdssnmpadaptor.config.open',
                side_effect=[io.StringIO(self.CONFIG),
                             io.StringIO(self.CONFIG),
                             io.StringIO(self.CONFIG)]):
            self.mc = mib_controller.MibInstrumController().setOidDbAndLogger(
                self.mock_oidDb, mock.MagicMock(config={}))

        super(MibControllerTestCase, self).setUp()

    def test_readVars(self):
        varBinds = [('1.3.6.1.2.1.1.0', 123)]

        mock_oidItem = self.mock_oidDb.getObjFromOid.return_value
        mock_oidItem.pysnmpBaseType = lambda **kw: kw['key']
        mock_oidItem.pysnmpRepresentation = 'key'

        rspVarBinds = self.mc.readVars(varBinds)

        self.mock_oidDb.getObjFromOid.assert_called_once_with(
            '1.3.6.1.2.1.1.0')

        expected = [
            (mock_oidItem.oid, mock_oidItem.value)
        ]
        self.assertEqual(expected, rspVarBinds)

    def test_readNextVars(self):
        varBinds = [('1.3.6.1.2.1.1.0', 123)]

        mock_getNextOid = self.mock_oidDb.getNextOid.return_value
        mock_oidItem = self.mock_oidDb.getObjFromOid.return_value
        mock_oidItem.pysnmpBaseType = lambda **kw: kw['key']
        mock_oidItem.pysnmpRepresentation = 'key'

        rspVarBinds = self.mc.readNextVars(varBinds)

        self.mock_oidDb.getObjFromOid.assert_called_once_with(
            mock_getNextOid)

        expected = [
            (mock_oidItem.oid, mock_oidItem.value)
        ]
        self.assertEqual(expected, rspVarBinds)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
