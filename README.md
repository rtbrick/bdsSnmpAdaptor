Copyright (C) 2017-2019, RtBrick Inc
License: BSD License 2.0

# bdsSnmpAdaptor

SNMP front end to (Rt)Brick-Data-Store Information.

v0.4 - under development.

Installation:

## Required apt and pip3 modules
```shell
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install git snmp snmp-mibs-downloader
sudo pip3 install aiohttp pysnmp requests
```

## bdsSnmpAdapter python modules and mibs
```shell
mkdir ~/git
cd git
git clone https://github.com/rtbrick/bdsSnmpAdaptor
cd bdsSnmpAdaptor
sudo cp mibs/RT* /usr/share/snmp/mibs
```

## Modify config parameters in config file (dev. status)

The `bdsSnmpRetrieveAdaptor.yml` file holds the config attribute for SNMP
GET/GETNEXT commands. The format will change, when moving to deployment
architecture.

```shell
vim bdsSnmpRetrieveAdaptor.yml
```
```yaml
bdsSnmpAdapter:
  loggingLevel: debug
  rotatingLogFile: /tmp/bdsSnmpAdaptor_   #FIXME store this at permanent location
  bdsAccess:
    rtbrickHost: 10.0.3.10
    rtbrickPorts:
     - confd: 2002  #Define the rest port on which confd listens"
     - fwdd-hald: 5002  #Define the rest port on which fwdd listens"
  bdsSnmpRetrieveAdaptor:
    listeningIP: 0.0.0.0  #SNMP GET/GETNEXT command responder listening IPv4 address
    listeningPort: 161  #SNMP GET/GETNEXT responder listening UDP port
    version: 2c  # specify SNMP version type=str, choices=['2c', '3']
    community: public  # SNMP v2c community name
    #
    # alternatively SNMP v3 config:
    #
#    version: 3 # specify snmp version type=str, choices=['2c', '3']
    # User-based Security Model (USM) for version 3 configurations:
    # http://snmplabs.com/pysnmp/docs/api-reference.html#security-parameters
    usmUsers:
      - testUser1:
          authKey: authKey123
          authProtocol: SHA     #optional (MD5|SHA), default = SHA
          privKey: privkey123
          privProtocol: AES     #optional, (DES|AES) default = AES
      - testUser2:
          authKey: authKey123
```

The `bdsSnmpTrapAdaptor.yml` file holds the config attribute for SNMP notifications.
The format will change, when moving to deployment architecture.

```shell
vim bdsSnmpRetrieveAdaptor.yml
```
```yaml
bdsSnmpAdapter:
  loggingLevel: debug
  rotatingLogFile: /tmp/bdsSnmpAdapter_   #FIXME store this at permanent location
  bdsSnmpTrapAdaptor:
    listeningIP: 0.0.0.0  #REST API listening IP address
    listeningPort: 5000  #REST API listening port
    snmpTrapServer: 127.0.0.1  #SNMP notification receiver listening IPv4 address
    snmpTrapPort: 162  #SNMP notification receiver listening UDP port
    version: 2c # specify SNMP version type=str, choices=['2c', '3']
    community: public # SNMP v2c community name
    usmUsers:
      - testUser1:
          authKey: authKey123
          authProtocol: SHA     #optional (MD5|SHA), default = SHA
          privKey: privkey123
          privProtocol: AES     #optional, (DES|AES) default = AES
```
config statement on rtbrick:
```shell
set snmp server-ip 10.0.3.20 server-port 5000 server-ep / bd-name confd.rtbrick
```
