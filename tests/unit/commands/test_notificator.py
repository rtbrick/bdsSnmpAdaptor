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

from bdssnmpadaptor.commands import notificator


class SnmpNotificationOriginatorTestCase(unittest.TestCase):

    CONFIG = """
bdsSnmpAdapter:
  loggingLevel: debug
  stateDir: /var/run/bds-snmp-responder
  snmp:
    # SNMP engine ID uniquely identifies SNMP engine within an administrative
    # domain. For SNMPv3 crypto feature to work, the same SNMP engine ID value
    # should be configured at the TRAP receiver.
    engineId: 80:00:C3:8A:04:73:79:73:4e:61:6d:65:31:32:33
    # User-based Security Model (USM) for version 3 configurations:
    # http://snmplabs.com/pysnmp/docs/api-reference.html#security-parameters
    versions:  # SNMP versions map, choices=['1', '2c', '3']
      1:  # map of configuration maps
        manager-A:  # descriptive SNMP security name
          community: public
      2c:  # map of configuration maps
        manager-B:  # descriptive SNMP security name
          community: public
      3:
        usmUsers:  # map of USM users and their configuration
          user1:  # descriptive SNMP security name
            user: testUser1  # USM user name
            authKey: authkey123
            authProtocol: md5  # md5, sha224, sha256, sha384, sha512, none
          user2:  # descriptive SNMP security name
            user: testUser2  # USM user name
            authKey: authkey123
            authProtocol: md5  # md5, sha224, sha256, sha384, sha512, none
            privKey: privkey123
            privProtocol: des  # des, 3des, aes128, aes192, aes192blmt, aes256, aes256blmt, none  
  responder:
    listeningIP: 0.0.0.0  # SNMP command responder listens on this address
    listeningPort: 11161  # SNMP command responder listens on this port
"""

    @mock.patch('bdssnmpadaptor.commands.notificator.asyncio', autospec=True)
    @mock.patch('bdssnmpadaptor.commands.notificator.AsyncioRestServer', autospec=True)
    @mock.patch('bdssnmpadaptor.commands.notificator.SnmpNotificationOriginator', autospec=True)
    def test_main(self, mock_ntforg, mock_restapi, mock_asyncio):

        notificator.main()

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
