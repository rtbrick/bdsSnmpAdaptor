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
from bdssnmpadaptor import rest_server


class AsyncioRestServerTestCase(unittest.TestCase):

    CONFIG = """
bdsSnmpAdapter:
  loggingLevel: debug
  # Log to stdout unless log file is set here
#  rotatingLogFile: /tmp   #FIXME store this at permanent location
  stateDir: /var/run/bds-snmp-adaptor
  # SNMP notification originator configuration
  notificator:
    # temp config lines to test incomming graylog message end #
    listeningIP: 0.0.0.0  # our REST API listens on this address
    listeningPort: 5000 # our REST API listens on this port

"""
    def setUp(self):
        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        super(AsyncioRestServerTestCase, self).setUp()

    def test___init__(self):

        with mock.patch(
                'bdssnmpadaptor.config.open',
                side_effect=[io.StringIO(self.CONFIG),
                             io.StringIO(self.CONFIG),
                             io.StringIO(self.CONFIG)]):
            mock_queue = mock.MagicMock()
            rs = rest_server.AsyncioRestServer(
                mock.MagicMock(config={}), mock_queue)

            self.assertEqual('0.0.0.0', rs.listeningIP)
            self.assertEqual(5000, rs.listeningPort)

    @mock.patch('bdssnmpadaptor.rest_server.json', autospec=True)
    @mock.patch('bdssnmpadaptor.rest_server.web', autospec=True)
    def test_handler(self, mock_web, mock_json):
            mock_queue = mock.MagicMock(asyncio.Queue)

            with mock.patch(
                    'bdssnmpadaptor.config.open',
                    side_effect=[io.StringIO(self.CONFIG),
                                 io.StringIO(self.CONFIG),
                                 io.StringIO(self.CONFIG)]):
                rs = rest_server.AsyncioRestServer(
                    mock.MagicMock(config={}), mock_queue)

            mock_web.json_response = asynctest.CoroutineMock()

            mock_request = mock.MagicMock()

            mock_request.text = asynctest.CoroutineMock()

            self.my_loop.run_until_complete(
                rs.handler(mock_request))

            mock_json.loads.assert_called_once_with(mock.ANY)

            mock_queue.put_nowait.assert_called_once_with(mock.ANY)

            mock_web.json_response.assert_called_once_with(mock.ANY)

    @asynctest.patch('bdssnmpadaptor.rest_server.web', autospec=True)
    def test_initialize(self, mock_web):
            mock_queue = mock.MagicMock(asyncio.Queue)

            with mock.patch(
                    'bdssnmpadaptor.config.open',
                    side_effect=[io.StringIO(self.CONFIG),
                                 io.StringIO(self.CONFIG),
                                 io.StringIO(self.CONFIG)]):
                rs = rest_server.AsyncioRestServer(
                    mock.MagicMock(config={}), mock_queue)

            self.my_loop.create_server = asynctest.CoroutineMock()

            self.my_loop.run_until_complete(rs.initialize())

            mock_server = mock_web.Server
            mock_server.assert_called_once()


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
