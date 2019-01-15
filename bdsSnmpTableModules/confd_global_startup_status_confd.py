from bdsMappingFunctions import bdsMappingFunctions
import logging


class confd_global_startup_status_confd(object):

    """

    .. code-block:: text
       :caption: setOids settings
       :name: setOids

        self.bdsTableDict = {'bdsRequest': {'process': 'confd', 'urlSuffix': '/bds/table/walk?format=raw', 'table': 'global.startup.status.confd'}}
        oidSegment = "1.3.6.1.4.1.50058.101.3.1."
        redisKeyPattern = "bdsTableInfo-confd-global.startup.status.confd"

    .. code-block:: json
       :caption: global.startup.status.confd
       :name: global.startup.status.confd example

        {
        "table": {
            "table_name": "global.startup.status.confd"
        },
        "objects": [
            {
                "sequence": 5,
                "update": true,
                "attribute": {
                    "module_name": "bd",
                    "startup_status": "02",
                    "up_time": "19482b5c642e696e",
                    "bd_name": "confd"
                }
            }
        }



.. csv-table:: oid mapping
    :header: "#", "name", "pysnmp type", "BDS attr", "mapping"
    :widths: 4, 19, 16, 25, 39

    1, "moduleName", "OctetString", "module_name",
    2, "bdName", "OctetString", "bd_name",
    3, "upTime", "OctetString", "encapsulation_type",
    4, "startupStatus", "OctetString", "startup_status",

    """


    @classmethod
    def setOids(self,bdsSnmpTableObject):
        self.bdsTableDict = {'bdsRequest': {'process': 'confd', 'urlSuffix': '/bds/table/walk?format=raw', 'table': 'global.startup.status.confd'}}
        oidSegment = "1.3.6.1.4.1.50058.101.3.1."
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
