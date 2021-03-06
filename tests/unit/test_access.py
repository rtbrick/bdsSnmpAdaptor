# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import asyncio
import io
import sys
import unittest
from unittest import mock

import asynctest

from bdssnmpadaptor import access
from bdssnmpadaptor import oid_db


@mock.patch('tempfile.NamedTemporaryFile', new=mock.MagicMock)
class BdsAccessTestCase(unittest.TestCase):

    CONFIG = """
bdsSnmpAdapter:
  loggingLevel: debug
  stateDir: /var/run/bds-snmp-responder
  snmp:
    mibs:
        - /usr/share/snmp/mibs
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

    JSON_RESPONSE = {
        'objects': {}
    }

    def setUp(self):
        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        with mock.patch(
                'bdssnmpadaptor.config.open',
                side_effect=[io.StringIO(self.CONFIG),
                             io.StringIO(self.CONFIG),
                             io.StringIO(self.CONFIG)]):
            self.access = access.BdsAccess(mock.MagicMock(config={}))

        super(BdsAccessTestCase, self).setUp()

    def test_getOidDb(self):
        self.assertIsInstance(self.access.oidDb, oid_db.OidDb)

    @asynctest.patch(
        'bdssnmpadaptor.access.aiohttp.ClientSession', autospec=True)
    @asynctest.patch(
        'bdssnmpadaptor.access.StaticAndPredefinedOids', autospec=True)
    @asynctest.patch.dict(
        access.REQUEST_MAPPING_DICTS[
            'confd_global_interface_physical'],
        {'mappingFunc': asynctest.Mock(setOids=asynctest.CoroutineMock())})
    @asynctest.patch.dict(
        access.REQUEST_MAPPING_DICTS[
            'confd_global_startup_status_confd'],
        {'mappingFunc': asynctest.Mock(setOids=asynctest.CoroutineMock())})
    @asynctest.patch.dict(
        access.REQUEST_MAPPING_DICTS[
            'confd_local.system.software.info.confd'],
        {'mappingFunc': asynctest.Mock(setOids=asynctest.CoroutineMock())})
    def test_run_forever(self, mock_predefined_oids, mock_http):
        mock_session = mock_http.return_value

        mock_json = asynctest.CoroutineMock(
            return_value=self.JSON_RESPONSE)
        mock_response = mock.MagicMock(
            json=mock_json, status=200)
        mock_session.post = asynctest.CoroutineMock(
            return_value=mock_response)

        with asynctest.patch('asyncio.sleep') as sleep:
            sleep.side_effect = [lambda: 1, asyncio.CancelledError]
            try:
                self.my_loop.run_until_complete(self.access.periodicRetriever())

            except asyncio.CancelledError:
                pass

        mock_predefined_oids.setOids.assert_called_once_with(
            mock.ANY, mock.ANY, [], 0)

        mock_phy = access.REQUEST_MAPPING_DICTS[
            'confd_global_interface_physical']['mappingFunc']
        mock_phy.setOids.assert_called_once_with(
            mock.ANY, self.JSON_RESPONSE, mock.ANY, mock.ANY)

        mock_startup = access.REQUEST_MAPPING_DICTS[
            'confd_global_startup_status_confd']['mappingFunc']
        mock_startup.setOids.assert_called_once_with(
            mock.ANY, self.JSON_RESPONSE, mock.ANY, mock.ANY)

        mock_sw = access.REQUEST_MAPPING_DICTS[
            'confd_local.system.software.info.confd']['mappingFunc']
        mock_sw.setOids.assert_called_once_with(
            mock.ANY, self.JSON_RESPONSE, mock.ANY, mock.ANY)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
