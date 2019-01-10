# bdsSnmpAdaptor

Installation:

1) Redis:
sudo apt install redis-server
sudo vim /etc/redis/redis.conf   ### change manually the value for supervised:  supervised systemd   (advanced add sed onliner?) ###
sudo systemctl restart redis.service
redis-cli info


2) Required apt and pip3 modules
sudo apt-get install python3-pip
#sudo add-apt-repository ppa:wireshark-dev/stable
#sudo apt-get install wireshark net-tools 
sudo apt-get install git snmp snmp-mibs-downloader
sudo pip3 install redis aiohttp aioredis pysnmp


3) bdsSnmpAdapter python modules and mibs
mkdir ~/git
cd git 
git clone https://github.com/slieberth/bdsSnmpAdaptor
cd bdsSnmpAdaptor
sudo cp mibs/RT* /usr/share/snmp/mibs
Sudo cp bdsSnmpAdapterConfig.yml /etc/bdsSnmpAdapterConfig.yml  


sudo cp bdsSnmpAdapterConfig.yml /etc/bdsSnmpAdapterConfig.yml  
4) Modify config parameters in config file

