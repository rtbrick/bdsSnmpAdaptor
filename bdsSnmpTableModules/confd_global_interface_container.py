from bdsMappingFunctions import bdsMappingFunctions
import logging

class confd_global_interface_container(object):

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
                                               #"value" : ifTypeMap[int(ifObject["attribute"]["encapsulation_type"])]},
                                               "value" : 77777},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.4."+str(ifIndex),
                                 fullOidDict = {"name":"ifMtu","pysnmpBaseType":"Integer32",
                                               "value": ifObject["attribute"]["layer2_mtu"]     },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.5."+str(ifIndex),
                                 fullOidDict = {"name":"ifSpeed","pysnmpBaseType":"Gauge32",
                                               #"value": ifObject["attribute"]["bandwidth"]      },
                                               "value": 0  },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.6."+str(ifIndex),
                                 fullOidDict = {"name":"ifPhysAddress","pysnmpBaseType":"OctetString","pysnmpRepresentation":"hexValue",
                                               "value":ifObject["attribute"]["mac_address"].replace(":","")   },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.7."+str(ifIndex),
                                 fullOidDict = {"name":"ifAdminStatus",
                                      "pysnmpBaseType":"Integer32",
                                               #"value":ifObject["attribute"]["admin_status"] },
                                               "value": 1  },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.2.2.1.8."+str(ifIndex),
                                 fullOidDict = {"name":"ifOperStatus",
                                      "pysnmpBaseType":"Integer32",
                                               #"value": ifOperStatusMap[int(ifObject["attribute"]["link_status"])]    },
                                               "value" : 1 },
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
