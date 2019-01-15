import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from bdsMappingFunctions import bdsMappingFunctions
import logging
import pytablewriter
import yaml

class confd_global_interface_container(object):

    """

    .. code-block:: text
       :caption: setOids settings
       :name: setOids

        self.bdsTableDict = {"bdsRequest": {"process": "confd",
                                    "urlSuffix": "bds/table/walk?format=raw",
                                    "table": "global.interface.container"}}
        oidSegment = "1.3.6.1.2.1.2.2."
        redisKeyPattern = "bdsTableInfo-confd-global.interface.container"

    .. code-block:: json
       :caption: global.interface.container
       :name: global.interface.container example

          {
            "table": {
                    "table_name": "global.interface.container"
                },
                "objects": [
                    {
                        "sequence": 5,
                        "update": true,
                        "attribute": {
                            "interface_name": "ifc-0/0/1/1",
                            "interface_description": "Cont If ifp-0/1/1",
                            "encapsulation_type": "01",
                            "bandwidth": "00000000",
                            "layer2_mtu": "0024",
                            "admin_status": "01",
                            "link_status": "01",
                            "mac_address": "02fe1b2b3a4d",
                            "physical_interfaces": [
                                "ifp-0/1/1"
                            ]
                        }
                    }
                ]
            }


.. csv-table:: oid mapping
    :header: "#", "name", "pysnmpBaseType", "BDS attr", "mapping"
    :widths: 4, 19, 16, 25, 39

    1, "ifIndex", "Integer32", "interface_name", "bdsMappingFunctions.ifIndexFromIfName"
    2, "ifDescr", "DisplayString", "interface_name",
    3, "ifType", "IANAifType", "encapsulation_type", "ifTypeMap: {1:6}"
    4, "ifMtu", "Integer32", "layer2_mtu",
    5, "ifSpeed", "Gauge32", "bandwidth",
    6, "ifPhysAddress", "PhysAddress", "mac_address",
    7, "ifAdminStatus", "INTEGER", "admin_status",
    8, "ifOperStatus", "INTEGER", "link_status", "ifOperStatusMap {0:2, 1:1, 2:3, 3:3}"
    9, "ifLastChange", "TimeTicks", ,
    10, "ifInOctets", "Counter32", ,
    11, "ifInUcastPkts", "Counter32", ,
    13, "ifInDiscards", "Counter32", ,
    14, "ifInErrors", "Counter32", ,
    15, "ifInUnknownProtos", "Counter32", ,
    16, "ifOutOctets", "Counter32", ,
    17, "ifOutUcastPkts", "Counter32", ,
    19, "ifOutDiscards", "Counter32", ,
    20, "ifOutErrors", "Counter32", ,

    """

    #9, "ifLastChange", "TimeTicks,"", ,


    @classmethod
    def setOids(self,bdsSnmpTableObject):
        self.bdsTableDict = {"bdsRequest": {"process": "confd", "urlSuffix": "bds/table/walk?format=raw", "table": "global.interface.container"}}
        oidSegment = "1.3.6.1.2.1.2.2."
        redisKeyPattern = "bdsTableInfo-confd-global.interface.container"
        redisKeysAsList = list(bdsSnmpTableObject.redisServer.scan_iter(redisKeyPattern))
        expiryTimer = 60
        if len(redisKeysAsList) == 0:
            bdsSnmpTableObject.setBdsTableRequest(self.bdsTableDict)
        elif len(redisKeysAsList) == 1:
            checkResult,responseJSON,bdsTableRedisKey = bdsSnmpTableObject.checkBdsTableInfo(redisKeysAsList)
            if checkResult:
                bdsSnmpTableObject.redisServer.set("oidLock-{}".format(oidSegment),"locked",ex=3)
                for ifObject in responseJSON["objects"]:
                    ifName = ifObject["attribute"]["interface_name"]
                    ifIndex =  bdsMappingFunctions.ifIndexFromIfName(ifName)
                    ifTypeMap = { 1 : 6 }
                    ifOperStatusMap = { 0:2,1:1,2:3,3:3 }
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.1."+str(ifIndex),
                                 fullOidDict = {"name":"ifIndex", "pysnmpBaseType":"Integer32",
                                               "value":int(ifIndex)},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.2."+str(ifIndex),
                                 fullOidDict = {"name":"ifDescr","pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["interface_name"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.3."+str(ifIndex),
                                 fullOidDict = { "name" : "ifType","pysnmpBaseType" : "Integer32",
                                               "value" : ifTypeMap[int(ifObject["attribute"]["encapsulation_type"])]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.4."+str(ifIndex),
                                 fullOidDict = {"name":"ifMtu","pysnmpBaseType":"Integer32",
                                               "value": ifObject["attribute"]["layer2_mtu"]     },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.5."+str(ifIndex),
                                 fullOidDict = {"name":"ifSpeed","pysnmpBaseType":"Gauge32",
                                               "value": ifObject["attribute"]["bandwidth"]      },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.6."+str(ifIndex),
                                 fullOidDict = {"name":"ifPhysAddress","pysnmpBaseType":"OctetString","pysnmpRepresentation":"hexValue",
                                               "value":ifObject["attribute"]["mac_address"].replace(":","")   },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.7."+str(ifIndex),
                                 fullOidDict = {"name":"ifAdminStatus",
                                      "pysnmpBaseType":"Integer32",
                                               "value":ifObject["attribute"]["admin_status"] },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.8."+str(ifIndex),
                                 fullOidDict = {"name":"ifOperStatus",
                                      "pysnmpBaseType":"Integer32",
                                               "value": ifOperStatusMap[int(ifObject["attribute"]["link_status"])]    },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.9."+str(ifIndex),
                                 fullOidDict = {"name":"ifLastChange",
                                      "pysnmpBaseType":"TimeTicks",
                                               "value": 0  }, #FIXME - bds mapping not available
                                 expiryTimer = expiryTimer )
                bdsSnmpTableObject.redisServer.delete("oidLock-{}".format(oidSegment))
                bdsSnmpTableObject.redisServer.set(bdsTableRedisKey,"processed",ex=50)
                logging.debug('set {} to processed with timout 50'.format(bdsTableRedisKey))
        else:
            logging.error('insonsistent redis keys: len redisKeysAsList > 1: {}'.format(redisKeysAsList))


if __name__ == "__main__":


    TABLE_HEADER = ["sub OID","OID name", "OID type", "BDS attr", "mapping"]
    TABLE_MATRIX = [
        ["1","ifIndex","InterfaceIndex","interface_name","bdsMappingFunctions.ifIndexFromIfName"],
        ["2","ifDescr","DisplayString","interface_name"],
        ["3","ifType","IANAifType","encapsulation_type","ifTypeMap = {1:6}"],
        ["4","ifMtu","Integer32","layer2_mtu",""],
        ["5","ifSpeed","Gauge32","bandwidth",""],
        ["6","ifPhysAddress","PhysAddress","mac_address",""],
        ["7","ifAdminStatus","INTEGER","admin_status",""],
        ["8","ifOperStatus","INTEGER","link_status","ifOperStatusMap {0:2,1:1,2:3,3:3}"],
        ["9","ifLastChange","TimeTicks,","",""],
        ["10","ifInOctets","Counter32","",""],
        ["11","ifInUcastPkts","Counter32","",""],
        ["13","ifInDiscards","Counter32","",""],
        ["14","ifInErrors","Counter32","",""],
        ["15","ifInUnknownProtos","Counter32","",""],
        ["16","ifOutOctets","Counter32","",""],
        ["17","ifOutUcastPkts","Counter32","",""],
        ["19","ifOutDiscards","Counter32","",""],
        ["20","ifOutErrors","Counter32","",""],
        ]

    writer = pytablewriter.MarkdownTableWriter()
    writer.table_name = "MIB conversation table"
    writer.header_list = TABLE_HEADER
    writer.value_matrix = TABLE_MATRIX
    translationTable = writer.write_table()

    #writer = pytablewriter.RstGridTableWriter()
    writer = pytablewriter.RstCsvTableWriter()
    writer.table_name = "MIB conversation table"
    writer.header_list = TABLE_HEADER
    writer.value_matrix = TABLE_MATRIX
    translationTable = writer.write_table()
