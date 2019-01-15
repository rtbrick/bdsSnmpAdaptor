from bdsMappingFunctions import bdsMappingFunctions
import logging

class confd_global_rtbrick_hostname_config(object):

    """

.. code-block:: text
   :caption: setOids settings
   :name: setOids

    self.bdsTableDict = {'bdsRequest': {'process': 'confd',
                          'urlSuffix': '/bds/table/walk?format=raw',
                          'table': 'global.rtbrick.hostname.config'}}
    oidSegment = "1.3.6.1.2.1.1."
    redisKeyPattern = "bdsTableInfo-confd-global.rtbrick.hostname.config"

.. code-block:: json
   :caption: local.system.software.info.confd
   :name: local.system.software.info.confd example

   {
   }

    attribute: system_hostname (1), type: string (9), length: 8, value: Basesim
    attribute: rtbrick_hostname (2), type: string (9), length: 8, value: Basesim
    attribute: rtbrick_podname (3), type: string (9), length: 12, value: rtbrick-pod

    """

    @classmethod
    def setOids(self,bdsSnmpTableObject):
        self.bdsTableDict = {'bdsRequest': {'process': 'confd', 'urlSuffix': '/bds/table/walk?format=raw', 'table': 'global.rtbrick.hostname.config'}}
        oidSegment = "1.3.6.1.2.1.1."
        redisKeyPattern = "bdsTableInfo-confd-global.rtbrick.hostname.config"
        expiryTimer = 60
        redisKeysAsList = list(bdsSnmpTableObject.redisServer.scan_iter(redisKeyPattern))
        if len(redisKeysAsList) == 0:
            bdsSnmpTableObject.setBdsTableRequest(self.bdsTableDict)
        elif len(redisKeysAsList) == 1:
            checkResult,responseJSON,bdsTableRedisKey = bdsSnmpTableObject.checkBdsTableInfo(redisKeysAsList)
            if checkResult:
                for bdsJsonObject in responseJSON["objects"]:
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"5.0",
                                 fullOidDict = {"name":"sysName", "pysnmpBaseType":"OctetString",
                                               "value":bdsJsonObject["attribute"]["system_hostname"] },
                                 expiryTimer = expiryTimer )
                bdsSnmpTableObject.redisServer.delete("oidLock-{}".format(oidSegment))
                bdsSnmpTableObject.redisServer.set(bdsTableRedisKey,"processed",ex=50)
                logging.debug('set {} to processed with timout 50'.format(bdsTableRedisKey))
        else:
            logging.error('insonsistent redis keys: len redisKeysAsList > 1: {}'.format(redisKeysAsList))
