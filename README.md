# bdsSnmpAdaptor

Installation:

## Redis:
```shell
sudo apt install redis-server
sudo vim /etc/redis/redis.conf   ### change manually: supervised systemd 
sudo systemctl restart redis.service
redis-cli info
```

## Required apt and pip3 modules
```shell
sudo apt-get install python3-pip
#sudo add-apt-repository ppa:wireshark-dev/stable
#sudo apt-get install wireshark net-tools 
sudo apt-get install git snmp snmp-mibs-downloader
sudo pip3 install redis aiohttp aioredis pysnmp
```

## bdsSnmpAdapter python modules and mibs
```shell
mkdir ~/git
cd git 
git clone https://github.com/slieberth/bdsSnmpAdaptor
cd bdsSnmpAdaptor
sudo cp mibs/RT* /usr/share/snmp/mibs
sudo cp bdsSnmpAdapterConfig.yml /etc/bdsSnmpAdapterConfig.yml  
```

## Modify config parameters in config file

