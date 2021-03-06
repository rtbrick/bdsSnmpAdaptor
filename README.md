
[![Build status](https://travis-ci.org/rtbrick/bdsSnmpAdaptor.svg?branch=master)](https://travis-ci.org/rtbrick/bdsSnmpAdaptor)
[![Coverage Status](https://img.shields.io/codecov/c/github/rtbrick/bdsSnmpAdaptor.svg)](https://codecov.io/github/rtbrick/bdsSnmpAdaptor)
[![GitHub license](https://img.shields.io/badge/license-BSD-blue.svg)](https://raw.githubusercontent.com/rtbrick/bdsSnmpAdaptor/master/LICENSE.rst)

Copyright (C) 2017-2019, RtBrick Inc
License: BSD License 2.0

# SNMP frontend to (Rt)Brick Datastore

*Version 0.0.1*

The BDS SNMP adaptor tool implements SNMP interface to otherwise REST-based
[RtBrick](https://www.rtbrick.com) bare metal switch platform.

# Installation

Required apt and pip3 modules
```shell
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install git snmp snmp-mibs-downloader
```

bdsSnmpAdapter python modules and MIBs
```shell
git clone https://github.com/rtbrick/bdsSnmpAdaptor
cd bdsSnmpAdaptor
sudo pip3 install .
sudo mkdir -p /etc/bds-snmp-adaptor/mibs
sudo mkdir /var/log/bds-snmp-adaptor
sudo mkdir /var/run/bds-snmp-adaptor
sudo cp mibs/* /etc/bds-snmp-adaptor/mibs
sudo cp conf/bds-snmp-adaptor.yml /etc/bds-snmp-adaptor
```

Modify config parameters in config file (dev. status)

The `bds-snmp-adaptor.yml` file contains configuration information for all
conceptual parts of the BDS adaptor - SNMP command responder, SNMP notification
originator, BDS REST API client and REST API server.

.. note::

    The format will change, when moving to deployment architecture.

```shell
vim bds-snmp-adaptor.yml
```
```yaml
bdsSnmpAdapter:
  loggingLevel: debug
  # Log to stdout unless log file is set here
  stateDir: /var/run/bds-snmp-adaptor
  # BDS REST API endpoints
  access:
    rtbrickHost: 10.0.3.10
    rtbrickPorts:
     - confd: 2002  # confd REST API listens on this port"
     - fwdd-hald: 5002  # fwwd REST API listens on this port"
  # Common SNMP engine configuration, used by both command responder and
  # notification originator
  snmp:
    # Paths to ASN.1 MIB files in form of directories or URI, in
    # desired search order
    mibs:
      - /etc/bds-snmp-adaptor/mibs
      - /usr/share/snmp/mibs
    # SNMP engine ID uniquely identifies SNMP engine within an administrative
    # domain. For SNMPv3 crypto feature to work, the same SNMP engine ID value
    # should be configured at the TRAP receiver.
    engineId: 80:00:C3:8A:04:73:79:73:4e:61:6d:65:31:32:33
    # User-based Security Model (USM) configuration:
    # http://snmplabs.com/pysnmp/docs/api-reference.html#security-parameters
    versions:  # SNMP versions map, choices=['1', '2c', '3']
      1:  # map of configuration maps
        manager-A:  # SNMP security name
          community: public
      2c:  # map of configuration maps
        manager-B:  # SNMP security name
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
  # SNMP command responder configuration
  responder:
    listeningIP: 0.0.0.0  # SNMP command responder listens on this address
    listeningPort: 161  # SNMP command responder listens on this port
    staticOidContent:
      sysDescr: l2.pod2.nbg2.rtbrick.net
      sysContact: stefan@rtbrick.com
      sysName: l2.pod2.nbg2.rtbrick.net
      sysLocation: nbg2.rtbrick.net
      # FIXME get from BDS entity table
      sysObjectID: '1.3.6.1.4.1.50058.102.1'
      sysUpTime: 0
      sysServices: 72
  # SNMP notification originator configuration
  notificator:
    # temp config lines to test incomming graylog message end #
    listeningIP: 0.0.0.0  # our REST API listens on this address
    listeningPort: 5000 # our REST API listens on this port
    # A single REST API call will cause SNMP notifications to all the listed targets
    snmpTrapTargets:  # array of SNMP trap targets
      target-I:  # descriptive name of this notification target
        bind-address: 0.0.0.0  # send SNMP trap messages from this address
        address: 127.0.0.1  # send SNMP trap to this address
        port: 162  # send SNMP trap to this port
        security-name: manager-B  # use this SNMP security name
      target-II:  # descriptive name of this notification target
        bind-address: 0.0.0.0  # send SNMP trap messages from this address
        address: 127.0.0.2  # send SNMP trap to this address
        port: 162  # send SNMP trap to this port
        security-name: user1  # use this SNMP security name
```
config statement on rtbrick:
```shell
set snmp server-ip 10.0.3.20 server-port 5000 server-ep / bd-name confd.rtbrick
```
