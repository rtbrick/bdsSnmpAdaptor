from bdsMappingFunctions import bdsMappingFunctions
import logging

class confd_global_startup_status_confd(object):


    @classmethod
    def setOids(self,bdsSnmpTableObject):
        self.bdsTableDict = {'bdsRequest': {'process': 'confd', 'urlSuffix': '/bds/table/walk?format=raw', 'table': 'global.startup.status.confd'}}
        oidSegment = "1.3.6.1.4.1.50058.1.3.1."
        expiryTimer = 60
        redisKeyPattern = "bdsTableInfo-confd-global.startup.status.confd"
        redisKeysAsList = list(bdsSnmpTableObject.redisServer.scan_iter(redisKeyPattern))
        if len(redisKeysAsList) == 0:
            bdsSnmpTableObject.setBdsTableRequest(self.bdsTableDict)
        elif len(redisKeysAsList) == 1:
            checkResult,responseJSON,bdsTableRedisKey = bdsSnmpTableObject.checkBdsTableInfo(redisKeysAsList)
            if checkResult:
                for ifObject in responseJSON["objects"]:
                    indexString = ifObject["attribute"]["module_name"]
                    indexCharList = [str(ord(c)) for c in indexString]
                    index = str(len(indexCharList)) + "." + ".".join(indexCharList)
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"1."+str(index),
                                 fullOidDict = {"name":"moduleName", "pysnmpBaseType":"OctetString",
                                               "value":indexString },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"2."+str(index),
                                 fullOidDict = {"name":"bdName", "pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["bd_name"] },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"3."+str(index),
                                 fullOidDict = {"name":"upTime", "pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["up_time"] },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"4."+str(index),
                                 fullOidDict = {"name":"startupStatus", "pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["startup_status"] },
                                 expiryTimer = expiryTimer )
                bdsSnmpTableObject.redisServer.delete("oidLock-{}".format(oidSegment))
                bdsSnmpTableObject.redisServer.set(bdsTableRedisKey,"processed",ex=50)
                logging.debug('set {} to processed with timout 50'.format(bdsTableRedisKey))
        else:
            logging.error('insonsistent redis keys: len redisKeysAsList > 1: {}'.format(redisKeysAsList))
