# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import sys
import unittest
from unittest import mock

from bdssnmpadaptor.commands import adaptor


class BdsSnmpAdaptorTestCase(unittest.TestCase):

    @mock.patch('bdssnmpadaptor.commands.adaptor.asyncio', autospec=True)
    @mock.patch('bdssnmpadaptor.commands.adaptor.BdsAccess', autospec=True)
    @mock.patch('bdssnmpadaptor.commands.adaptor.MibInstrumController', autospec=True)
    @mock.patch('bdssnmpadaptor.commands.adaptor.SnmpCommandResponder', autospec=True)
    @mock.patch('bdssnmpadaptor.commands.adaptor.AsyncioRestServer', autospec=True)
    @mock.patch('bdssnmpadaptor.commands.adaptor.SnmpNotificationOriginator', autospec=True)
    def test_main(self, mock_ntforg, mock_restapi, mock_cmdrsp, mock_mibctrl,
                  mock_access, mock_asyncio):

        adaptor.main()

        mock_access.assert_called_once_with(mock.ANY)

        mock_access_instance = mock_access.return_value

        mock_access_instance.periodicRetriever.assert_called_once_with()

        mock_mibctrl.assert_called_once_with()

        mock_cmdrsp.assert_called_once_with(
            mock.ANY, mock_mibctrl.return_value)

        mock_asyncio.Queue.assert_called_once_with()
        mock_queue = mock_asyncio.Queue.return_value

        mock_ntforg.assert_called_once_with(mock.ANY, mock_queue)

        mock_restapi.assert_called_once_with(mock.ANY, mock_queue)

        mock_asyncio.get_event_loop.assert_called_once_with()
        mock_asyncio_loop = mock_asyncio.get_event_loop.return_value

        mock_asyncio_loop.run_until_complete.assert_called_once_with(mock.ANY)
        mock_asyncio_loop.close.assert_called_once_with()


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
