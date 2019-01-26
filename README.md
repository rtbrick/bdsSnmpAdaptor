# bdsSnmpAdaptor

Installation:

## Required apt and pip3 modules
```shell
sudo apt-get install python3-pip
sudo apt-get install git snmp snmp-mibs-downloader
sudo pip3 install redis aiohttp aioredis pysnmp
```

## bdsSnmpAdapter python modules and mibs
```shell
mkdir ~/git
cd git
git clone https://github.com/rtbrick/bdsSnmpAdaptor
cd bdsSnmpAdaptor
sudo cp mibs/RT* /usr/share/snmp/mibs
```

## Modify config parameters in config file
