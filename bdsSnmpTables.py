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




class bdsSnmpTables():

    def __init__():
        pass

    @classmethod
    def getSortedList(self,oidDict):
        oidMatrix = []
        for oid in oidDict.keys():
            oidSplit = oid.spplit(".")
            print(oidSplit)
            


class ifTable(bdsSnmpTables):

    def __init__():
        self.tableOid = "1.3.6.1.2.1.2.2.1."
        pass

    @classmethod
    def delIfOIDs(self,oidDict):
        self.tableOid = "1.3.6.1.2.1.2.2.1."
        newOidDict = deepcopy(oidDict)
        delList = []
        for oid in oidDict.keys():
            if oid.startswith(self.tableOid):
                delList.append(oid)
        for oid in delList:
            del oidDict[oid]
            logging.debug("oid {} deleted".format(oid))
        return oidDict


    @classmethod
    def addTableEntry(self,oidDict,ifIndex):


        #returnDict = {}
        oidDict["1.3.6.1.2.1.2.2.1.1."+str(ifIndex)] =\
                 {"name": "ifIndex" ,
                 "pysnmpBaseType": "Integer32",
                 "fixedValue": int(ifIndex) }
        oidDict["1.3.6.1.2.1.2.2.1.2."+str(ifIndex)] =\
                 {"name": "ifDescr",
                 "pysnmpBaseType": "OctetString",
                 "bdsRequest": "confd::/bds/object/get::global.interface.physical::interface_name=ifp-0/1/1",
                 "bdsEvalString": 'responseJSON["objects"][0]["attribute"]["interface_name"]'}
        oidDict["1.3.6.1.2.1.2.2.1.3.{}".format(ifIndex)] =\
                 {"name": "ifType",
                 "pysnmpBaseType": "Integer32",
                 "fixedValue": 6 }
        oidDict["1.3.6.1.2.1.2.2.1.4.{}".format(ifIndex)] =\
                 {"name": "ifMtu",
                 "pysnmpBaseType": "Integer32",
                 "bdsRequest": "confd::/bds/object/get::global.interface.physical::interface_name=ifp-0/1/1",
                 "bdsEvalString": 'responseJSON["objects"][0]["attribute"]["layer2_mtu"]'}
        oidDict["1.3.6.1.2.1.2.2.1.5.{}".format(ifIndex)] =\
                 {"name": "ifSpeed",
                 "pysnmpBaseType": "Gauge32",
                 "fixedValue": 10000000 }
        oidDict["1.3.6.1.2.1.2.2.1.6.{}".format(ifIndex)] =\
                  {"name": "ifPhysAddress",
                "pysnmpBaseType": "OctetString",
                "pysnmpRepresentation": "hexValue",
                 "bdsRequest": "confd::/bds/object/get::global.interface.physical::interface_name=ifp-0/1/1",
                 "bdsEvalString": 'responseJSON["objects"][0]["attribute"]["mac_address"].replace(":","")'}
        oidDict["1.3.6.1.2.1.2.2.1.7.{}".format(ifIndex)] =\
                {"name": "ifAdminStatus",
                 "pysnmpBaseType": "Integer32",
                 "fixedValue": 2 }
        oidDict["1.3.6.1.2.1.2.2.1.8.{}".format(ifIndex)] =\
                {"name": "ifOperStatus",
                 "pysnmpBaseType": "Integer32",
                 "fixedValue": 2 }
        oidDict["1.3.6.1.2.1.2.2.1.9.{}".format(ifIndex)] =\
                {"name": "ifLastChange",
                 "pysnmpBaseType": "TimeTicks",
                 "fixedValue": 2 }
        oidDict["1.3.6.1.2.1.2.2.1.10.{}".format(ifIndex)] =\
                {"name": "ifInOctets",
                 "pysnmpBaseType": "Counter32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.11.{}".format(ifIndex)] =\
                {"name": "ifInUcastPkts",
                 "pysnmpBaseType": "Counter32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.12.{}".format(ifIndex)] =\
                {"name": "ifInNUcastPkts",
                 "pysnmpBaseType": "Counter32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.13.{}".format(ifIndex)] =\
                {"name": "ifInDiscards",
                 "pysnmpBaseType": "Counter32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.14.{}".format(ifIndex)] =\
                {"name": "ifInErrors",
                 "pysnmpBaseType": "Counter32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.15.{}".format(ifIndex)] =\
                {"name": "ifInUnknownProtos",
                 "pysnmpBaseType": "Counter32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.16.{}".format(ifIndex)] =\
                {"name": "ifOutOctets",
                 "pysnmpBaseType": "Counter32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.17.{}".format(ifIndex)] =\
                {"name": "ifOutUcastPkts",
                 "pysnmpBaseType": "Counter32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.18.{}".format(ifIndex)] =\
                {"name": "ifOutNUcastPkts",
                 "pysnmpBaseType": "Counter32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.19.{}".format(ifIndex)] =\
                {"name": "ifOutDiscards",
                 "pysnmpBaseType": "Counter32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.20.{}".format(ifIndex)] =\
                {"name": "ifOutErrors",
                 "pysnmpBaseType": "Counter32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.21.{}".format(ifIndex)] =\
                {"name": "ifOutQLen",
                 "pysnmpBaseType": "Gauge32",
                 "fixedValue": 0 }
        oidDict["1.3.6.1.2.1.2.2.1.22.{}".format(ifIndex)] =\
                {"name": "ifSpecific",
                 "pysnmpBaseType": "ObjectIdentifier",
                 "fixedValue": "0.0" }
        return oidDict



if __name__ == '__main__':

    oidDict = {}
    oidDict = ifTable.addTableEntry(oidDict,1)
    
    pprint.pprint(oidDict)

    oidDict = ifTable.delIfOIDs(oidDict)

    pprint.pprint(oidDict)

    bdsResponse = {"table": { "table_name": "global.interface.physical"},
                   "objects": [ { "update": true,
                    "attribute": {
                        "layer2_mtu": 9216,
                        "pci_addr": 100664064,
                        "link_status": "up",
                        "admin_status": "up",
                        "interface_type": "ethernet",
                        "interface_description": "Physical interface #1 from node 0, chip 1",
                        "bandwidth": "0.000 Kbps",
                        "mac_address": "3c:fd:fe:b6:57:bb",
                        "interface_name": "ifp-0/1/1"},
                    "sequence": 2 }]}


