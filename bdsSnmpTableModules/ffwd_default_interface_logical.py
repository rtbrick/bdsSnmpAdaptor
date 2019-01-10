from bdsMappingFunctions import bdsMappingFunctions
import logging

class ffwd_default_interface_logical(object):

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
