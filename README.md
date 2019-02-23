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

bdsSnmpRetrieveAdaptor.yml holds the config attribute for get/get-next
operations. The format will change, when moving to deployment architecture.

```shell
vim bdsSnmpRetrieveAdaptor.yml
```
```yaml
bdsSnmpAdapter:
  loggingLevel: debug
  rotatingLogFile: /tmp/bdsSnmpAdaptor_   #FIXME store this at permament location
  bdsAccess:
    rtbrickHost: 10.0.3.10
    rtbrickPorts:
     - confd: 2002  #Define the rest port on which confd listens"
     - fwdd-hald: 5002  #Define the rest port on which fwwd listens"
  bdsSnmpRetrieveAdaptor:
    listeningIP: 0.0.0.0  #SNMP get/getNext listening IP address
    listeningPort: 161 #SNMP get/getNext listening port
    version: 2c # specify snmp version type=str, choices=['2c', '3']
    community: public # v2c community
    usmUserTuples: "engine,user,authkey,privkey"
                  # "80000a4c010a090150,usr-sha-aes128,authkey1,privkey1
                  # one entry per SNMP v§ server
```

bdsSnmpTrapAdaptor.yml holds the config attribute for notification
operations. The format will change, when moving to deployment architecture.

```shell
vim bdsSnmpRetrieveAdaptor.yml
```
```yaml
bdsSnmpAdapter:
  loggingLevel: debug
  rotatingLogFile: /tmp/bdsSnmpAdapter_   #FIXME store this at permament location
  bdsSnmpTrapAdaptor:
    listeningIP: 0.0.0.0  #REST listening IP address
    listeningPort: 5000 #REST listening port
    snmpTrapServer: 127.0.0.1 #defines the SNMP server, which receives the traps
    snmpTrapPort: 162 # defines the SNMP trap destination port
    version: 2c # specify snmp version type=str, choices=['2c', '3']
    community: public # v2c community
    usmUserTuples: "engine,user,authkey,privkey" # usmUserTuples engine,user,authkey,privkey list as comma separated strings
                                                 # '"80000a4c010a090150,usr-sha-aes128,authkey1,privkey1
                                                 # only one entry is rquired
```
