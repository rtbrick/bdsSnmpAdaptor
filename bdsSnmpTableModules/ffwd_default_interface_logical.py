from bdsMappingFunctions import bdsMappingFunctions
import logging

class ffwd_default_interface_logical(object):

    """

    .. code-block:: text
       :caption: setOids settings
       :name: setOids

        self.bdsTableDict = {'bdsRequest': {'process': 'fwdd',
                                   'urlSuffix': 'bds/table/walk?format=raw',
                                   'table': 'default.interface.logical'}}
        oidSegment = "1.3.6.1.2.1.2.2."
        redisKeyPattern = "bdsTableInfo-fwdd-default.interface.logical"

    .. code-block:: json
       :caption: global.interface.container
       :name: global.interface.container example

        {
            "table": {
                "table_name": "default.interface.logical"
            },
            "objects": [
                {
                    "sequence": 13,
                    "update": true,
                    "attribute": {
                        "interface_name": "ifl-0/0/1/1/0",
                        "interface_description": "Interface enp0s9",
                        "container_interface_name": "ifc-0/0/1/1",
                        "tagged": "00",
                        "ipv4_mtu": "ee05",
                        "ipv4_status": "01000000",
                        "admin_status": "01",
                        "link_status": "01"
                    }
                }
            ]
        }

.. csv-table:: oid mapping
    :header: "#", "name", "pysnmpBaseType", "BDS attr", "mapping"
    :widths: 4, 19, 16, 25, 39

    1, "ifIndex", "Integer32", "interface_name",
                     "bdsMappingFunctions.ifIndexFromIfName"
    2, "ifDescr", "DisplayString", "interface_name",
    3, "ifType", "Integer32",6 ,static (hard coded)
    4, "ifMtu", "Integer32", ,
    5, "ifSpeed", "Gauge32", ,
    6, "ifPhysAddress", "PhysAddress", ,
    7, "ifAdminStatus", "INTEGER", "admin_status",
    8, "ifOperStatus", "INTEGER", "link_status",
                     "ifOperStatusMap {0:2, 1:1, 2:3, 3:3}"
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


    @classmethod
    def setOids(self,bdsSnmpTableObject):
        self.bdsTableDict = {'bdsRequest': {'process': 'fwdd', 'urlSuffix': 'bds/table/walk?format=raw', 'table': 'default.interface.logical'}}
        oidSegment = "1.3.6.1.2.1.2.2."
        expiryTimer = 60
        redisKeyPattern = "bdsTableInfo-fwdd-default.interface.logical"
        redisKeysAsList = list(bdsSnmpTableObject.redisServer.scan_iter(redisKeyPattern))
        if len(redisKeysAsList) == 0:
            bdsSnmpTableObject.setBdsTableRequest(self.bdsTableDict)
        elif len(redisKeysAsList) == 1:
            checkResult,responseJSON,bdsTableRedisKey = bdsSnmpTableObject.checkBdsTableInfo(redisKeysAsList)
            if checkResult:
                bdsSnmpTableObject.redisServer.set("oidLock-{}".format(oidSegment),"locked",ex=3)
                for ifObject in responseJSON["objects"]:
                    ifName = ifObject["attribute"]["interface_name"]
                    ifIndex =  bdsMappingFunctions.ifIndexFromIfName(ifName)
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"1.1."+str(ifIndex),
                                 fullOidDict = {"name":"ifIndex", "pysnmpBaseType":"Integer32",
                                               "value":int(ifIndex)},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"1.2."+str(ifIndex),
                                 fullOidDict = {"name":"ifDescr", "pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["interface_name"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"1.3."+str(ifIndex),
                                 fullOidDict = {"name":"ifType", "pysnmpBaseType":"Integer32",
                                               "value": 6},
                                 expiryTimer = expiryTimer )
                bdsSnmpTableObject.redisServer.delete("oidLock-{}".format(oidSegment))
                bdsSnmpTableObject.redisServer.set(bdsTableRedisKey,"processed",ex=50)
                logging.debug('set {} to processed with timout 50'.format(bdsTableRedisKey))
        else:
            logging.error('insonsistent redis keys: len redisKeysAsList > 1: {}'.format(redisKeysAsList))
