#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import logging
import argparse
import yaml
import pprint
from copy import deepcopy
import ipaddress
from bdsAccess import bdsAccess
from oidDb import oidDbItem
from bdsMappingFunctions import bdsMappingFunctions




class bdsSnmpTables():

    def __init__(self):
        pass
        

    def globalInterfaceContainer(self,myOidDb,bdsAccessDict):
        self.bdsTable = {'bdsRequest': {'process': 'confd', 'urlSuffix': '/bds/table/walk', 'table': 'global.interface.container'}}
        bdsSuccess,responseJSON = bdsAccess.getJson(self.bdsTable,bdsAccessDict)
        for ifObject in responseJSON["objects"]:
            ifName = ifObject["attribute"]["interface_name"]
            ifIndex =  bdsMappingFunctions.ifIndexFromIfName(ifName)
            myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.1."+str(ifIndex),
                                       name = "ifIndex",
                             pysnmpBaseType = "Integer32",
                                 fixedValue = int(ifIndex) ) )
            myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.2."+str(ifIndex),
                                       name = "ifDescr",
                             pysnmpBaseType = "OctetString",
                                 fixedValue = ifObject["attribute"]["interface_name"] ) )
            myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.3."+str(ifIndex),
                                       name = "ifType",
                             pysnmpBaseType = "Integer32",
                                 fixedValue = 6 ) )   #FIXME - bds mapping
            myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.4."+str(ifIndex),
                                       name = "ifMtu",
                             pysnmpBaseType = "Integer32",
                                 fixedValue = ifObject["attribute"]["layer2_mtu"] ) )
            myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.5."+str(ifIndex),
                                       name = "ifMtu",
                             pysnmpBaseType = "Gauge32",
                                 fixedValue = 10000000 ) )   #FIXME - bds mapping
            myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.6."+str(ifIndex),
                                       name = "ifPhysAddress",
                             pysnmpBaseType = "OctetString",
                       pysnmpRepresentation = "hexValue",
                                 fixedValue = ifObject["attribute"]["mac_address"].replace(":","") ) )  
            myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.7."+str(ifIndex),
                                       name = "ifAdminStatus",
                             pysnmpBaseType = "OctetString",    #FIXME - integer
                                 fixedValue = ifObject["attribute"]["admin_status"] ) )   #FIXME - raw value
            myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.8."+str(ifIndex),
                                       name = "ifOperStatus",
                             pysnmpBaseType = "OctetString",    #FIXME - integer
                                 fixedValue = ifObject["attribute"]["link_status"] ) )   #FIXME - raw value
            myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.9."+str(ifIndex),
                                       name = "ifLastChange",
                             pysnmpBaseType = "TimeTicks",    #FIXME - integer
                                 fixedValue = 0 ) )   #FIXME - bds mapping not available



    def defaultInterfaceLogical(self,myOidDb,bdsAccessDict):
        self.bdsTable = {'bdsRequest': {'process': 'fwdd', 'urlSuffix': '/bds/table/walk', 'table': 'default.interface.logical'}}
        bdsSuccess,responseJSON = bdsAccess.getJson(self.bdsTable,bdsAccessDict)
        print(bdsSuccess,responseJSON)
        if bdsSuccess:
            for ifObject in responseJSON["objects"]:
                ifName = ifObject["attribute"]["interface_name"]
                ifIndex =  bdsMappingFunctions.ifIndexFromIfName(ifName)
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.1."+str(ifIndex),
                                           name = "ifIndex",
                                 pysnmpBaseType = "Integer32",
                                     fixedValue = int(ifIndex) ) )
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.2."+str(ifIndex),
                                           name = "ifDescr",
                                 pysnmpBaseType = "OctetString",
                                     fixedValue = ifObject["attribute"]["interface_name"] ) )
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.2.2.1.3."+str(ifIndex),
                                           name = "ifType",
                                 pysnmpBaseType = "Integer32",
                                     fixedValue = 6 ) )   #FIXME - bds mapping

    def globalInterfaceAddressConfig(self,myOidDb,bdsAccessDict):
        self.bdsTable = {'bdsRequest': {'process': 'confd', 'urlSuffix': '/bds/table/walk', 'table': 'global.interface.address.config'}}
        bdsSuccess,responseJSON = bdsAccess.getJson(self.bdsTable,bdsAccessDict)
        print(bdsSuccess,responseJSON)
        if bdsSuccess:
            for ifObject in responseJSON["objects"]:
                ifName = ifObject["attribute"]["ifl_name"]
                ifIndex =  bdsMappingFunctions.ifIndexFromIfName(ifName)
                if "ipv4_address" in ifObject["attribute"].keys():
                    myIfObj = ipaddress.IPv4Interface(ifObject["attribute"]["ipv4_address"])
                    myAddrObj = ipaddress.IPv4Address(myIfObj.ip)
                    ipIndex = myIfObj.ip
                    myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.4.20.1.1.{}".format(ipIndex),
                                               name = "ipAdEntAddr",
                                     pysnmpBaseType = "IpAddress",
                               pysnmpRepresentation = "hexValue",
                                         fixedValue = myAddrObj.packed.hex() ) )  
                    myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.4.20.1.2.{}".format(ipIndex),
                                               name = "ipAdEntIfIndex",
                                     pysnmpBaseType = "Integer32",
                                         fixedValue = int(ifIndex) ) )
                    myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.4.20.1.3.{}".format(ipIndex),
                                               name = "ipAdEntNetMask",
                                     pysnmpBaseType = "IpAddress",
                               pysnmpRepresentation = "hexValue",
                                         fixedValue = myIfObj.network.netmask.packed.hex() ) )  
                    myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.4.20.1.4.{}".format(ipIndex),
                                               name = "ipAdEntBcastAddr",
                                     pysnmpBaseType = "Integer32",
                                         fixedValue = 1 ) )
                    myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.4.20.1.5.{}".format(ipIndex),
                                               name = "ipAdEntBcastAddr",
                                     pysnmpBaseType = "Integer32", 
                                         fixedValue = 65535 ) )


    def defaultFwdNeighborIpv4(self,myOidDb,bdsAccessDict):
        self.bdsTable = {'bdsRequest': {'process': 'fwdd', 'urlSuffix': '/bds/table/walk', 'table': 'default.fwd.neighbor.ipv4'}}
        bdsSuccess,responseJSON = bdsAccess.getJson(self.bdsTable,bdsAccessDict)
        if bdsSuccess:
            for ifObject in responseJSON["objects"]:
                remoteAddr = ifObject["attribute"]["address4"]
                ifIndex = bdsMappingFunctions.ifIndexFromIfName(ifObject["attribute"]["ifl"])
                mediaIndex = str(ifIndex) + "." + remoteAddr
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.4.22.1.1.{}".format(mediaIndex),
                                           name = "ipNetToMediaIfIndex",
                                 pysnmpBaseType = "Integer32",
                                     fixedValue = int(ifIndex) ) )
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.4.22.1.2.{}".format(mediaIndex),
                                           name = "ipNetToMediaPhysAddress",
                                 pysnmpBaseType = "OctetString",
                           pysnmpRepresentation = "hexValue",
                                     fixedValue = ifObject["attribute"]["mac_address"].replace(":","") ) )  
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.4.22.1.3.{}".format(mediaIndex),
                                           name = " ipNetToMediaNetAddress",
                                 pysnmpBaseType = "IpAddress",
                           pysnmpRepresentation = "hexValue",
                                     fixedValue = ipaddress.IPv4Address(remoteAddr).packed.hex() ) )  
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.2.1.4.22.1.4.{}".format(mediaIndex),
                                           name = "ipNetToMediaType",
                                 pysnmpBaseType = "Integer32",  
                                     fixedValue = 3 ) )

    def localSystemSoftwareInfoConfd(self,myOidDb,bdsAccessDict):
        self.bdsTable = {'bdsRequest': {'process': 'confd', 'urlSuffix': '/bds/table/walk', 'table': 'local.system.software.info.confd'}}
        bdsSuccess,responseJSON = bdsAccess.getJson(self.bdsTable,bdsAccessDict)
        if bdsSuccess:
            for ifObject in responseJSON["objects"]:
                sequenceNr = ifObject["sequence"]
                libraryString = ifObject["attribute"]["library"]
                libraryChars = [str(ord(c)) for c in libraryString]
                libraryIndex = str(len(libraryChars)) + "." + ".".join(libraryChars)
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.4.1.50058.1.1.1.1.{}".format(sequenceNr),
                                           name = "libraryIndex",
                                 pysnmpBaseType = "Integer32",  
                                     fixedValue = sequenceNr ) )
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.4.1.50058.1.1.1.2.{}".format(sequenceNr),
                                           name = "libraryName",
                                 pysnmpBaseType = "OctetString",
                                     fixedValue = libraryString ) )
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.4.1.50058.1.1.1.3.{}".format(sequenceNr),
                                           name = "libraryVersion",
                                 pysnmpBaseType = "OctetString",
                                     fixedValue = ifObject["attribute"]["version"] ) )
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.4.1.50058.1.1.1.4.{}".format(sequenceNr),
                                           name = "libraryCommitDate",
                                 pysnmpBaseType = "OctetString",
                                     fixedValue = ifObject["attribute"]["commit_date"] ) )


    def localSystemSoftwareInfoConfd_Old(self,myOidDb,bdsAccessDict):
        self.bdsTable = {'bdsRequest': {'process': 'confd', 'urlSuffix': '/bds/table/walk', 'table': 'local.system.software.info.confd'}}
        bdsSuccess,responseJSON = bdsAccess.getJson(self.bdsTable,bdsAccessDict)
        if bdsSuccess:
            for ifObject in responseJSON["objects"]:
                sequenceNr = ifObject["sequence"]
                libraryString = ifObject["attribute"]["library"]
                libraryChars = [str(ord(c)) for c in libraryString]
                #libraryIndex = str(len(libraryChars)) + "." + ".".join(libraryChars)
                libraryIndex = ".".join(libraryChars)
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.4.1.50058.1.1.1.1.{}".format(sequenceNr),
                                           name = "libraryName",
                                 #pysnmpBaseType = "OctetString",
                                 pysnmpBaseType = "Integer32",  
                                     fixedValue = sequenceNr ) )
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.4.1.50058.1.1.1.2.{}".format(sequenceNr),
                                           name = "libraryVersion",
                                 pysnmpBaseType = "OctetString",
                                     fixedValue = ifObject["attribute"]["version"] ) )
                myOidDb.insertOid(oidDbItem(oid = "1.3.6.1.4.1.50058.1.1.1.3.{}".format(sequenceNr),
                                           name = "libraryCommitDate",
                                 pysnmpBaseType = "OctetString",
                                     fixedValue = ifObject["attribute"]["commit_date"] ) )



