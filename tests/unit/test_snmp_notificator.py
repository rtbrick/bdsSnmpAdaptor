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

from pysnmp.proto import rfc1902

from bdssnmpadaptor import snmp_notificator


@mock.patch('bdssnmpadaptor.snmp_notificator.snmp_config', autospec=True)
@mock.patch('bdssnmpadaptor.snmp_notificator.ntforg', autospec=True)
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
  notificator:
    # temp config lines to test incomming graylog message end #
    listeningIP: 0.0.0.0  # our REST API listens on this address
    listeningPort: 5000 # our REST API listens on this port
    # A single REST API call will cause SNMP notifications to all the listed targets
    snmpTrapTargets:  # array of SNMP trap targets
      target-I:  # descriptive name of this notification target
        address: 127.0.0.1  # send SNMP trap to this address
        port: 162  # send SNMP trap to this port
        security-name: manager-B  # use this SNMP security name
      target-II:  # descriptive name of this notification target
        address: 127.0.0.2  # send SNMP trap to this address
        port: 162  # send SNMP trap to this port
        security-name: user1  # use this SNMP security name
"""

    def setUp(self):
        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

        super(SnmpNotificationOriginatorTestCase, self).setUp()

    def test___init__(self, mock_ntforg, mock_snmp_config):

        self.mock_queue = mock.MagicMock

        with mock.patch(
                'bdssnmpadaptor.config.open',
                side_effect=[io.StringIO(self.CONFIG),
                             io.StringIO(self.CONFIG),
                             io.StringIO(self.CONFIG)]):
            snmp_notificator.SnmpNotificationOriginator(
                {'config': '/file'}, self.mock_queue)

        mock_snmpEngine = mock_snmp_config.getSnmpEngine.return_value

        mock_snmp_config.getSnmpEngine.assert_called_once_with(
            engineId=mock.ANY)
        mock_snmp_config.setSnmpEngineBoots.assert_called_once_with(
            mock_snmpEngine, '/var/run/bds-snmp-responder')
        mock_snmp_config.setSnmpTransport.assert_called_once_with(
            mock_snmpEngine)
        mock_snmp_config.setTrapTypeForTag.assert_called_once_with(
            mock_snmpEngine, 'mgrs')

        mock_setCommunity_calls = [
            mock.call(mock_snmpEngine, 'manager-A', 'public',
                      tag='mgrs', version='1'),
            mock.call(mock_snmpEngine, 'manager-B', 'public',
                      tag='mgrs', version='2c'),
        ]
        mock_snmp_config.setCommunity.assert_has_calls(
            mock_setCommunity_calls)

        mock_setUsmUser_calls = [
            mock.call(mock_snmpEngine, 'user1', 'testUser1',
                      'authkey123', 'md5', None, None),
            mock.call(mock_snmpEngine, 'user2', 'testUser2',
                      'authkey123', 'md5', 'privkey123', 'des'),

        ]
        mock_snmp_config.setUsmUser.assert_has_calls(
            mock_setUsmUser_calls)

        mock_setTrapTargetAddress_calls = [
            mock.call(mock_snmpEngine, 'manager-B', ('127.0.0.1', 162), 'mgrs'),
            mock.call(mock_snmpEngine, 'user1', ('127.0.0.2', 162), 'mgrs')
        ]
        mock_snmp_config.setTrapTargetAddress.assert_has_calls(
            mock_setTrapTargetAddress_calls)

        mock_setTrapVersion_calls = [
            mock.call(mock_snmpEngine, 'manager-B', mock.ANY, '2c'),
            mock.call(mock_snmpEngine, 'user1', mock.ANY, '3')
        ]
        mock_snmp_config.setTrapVersion.assert_has_calls(
            mock_setTrapVersion_calls)

    def test_sendTrap(self, mock_ntforg, mock_snmp_config):

        self.mock_queue = mock.MagicMock

        with mock.patch(
                'bdssnmpadaptor.config.open',
                side_effect=[io.StringIO(self.CONFIG),
                             io.StringIO(self.CONFIG),
                             io.StringIO(self.CONFIG)]):
            ntf = snmp_notificator.SnmpNotificationOriginator(
                {'config': '/file'}, self.mock_queue)

        self.my_loop.run_until_complete(ntf.sendTrap({}))

        mock_snmpEngine = mock_snmp_config.getSnmpEngine.return_value

        expectedVarBinds = [
            (rfc1902.ObjectIdentifier('1.3.6.1.2.1.1.3.0'), mock.ANY),
            (rfc1902.ObjectIdentifier('1.3.6.1.6.3.1.1.4.1.0'), rfc1902.ObjectIdentifier('1.3.6.1.4.1.50058.103.1.1')),
            (rfc1902.ObjectIdentifier('1.3.6.1.4.1.50058.104.2.1.1.0'), rfc1902.Integer32(1)),
            (rfc1902.ObjectIdentifier('1.3.6.1.4.1.50058.104.2.1.2.0'), rfc1902.OctetString('error')),
            (rfc1902.ObjectIdentifier('1.3.6.1.4.1.50058.104.2.1.3.0'), rfc1902.Integer32(0)),
            (rfc1902.ObjectIdentifier('1.3.6.1.4.1.50058.104.2.1.4.0'), rfc1902.OctetString('error')),
        ]

        ntf.ntfOrg.sendVarBinds.assert_called_once_with(
            mock_snmpEngine, mock.ANY, None, '', expectedVarBinds, mock.ANY)


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
