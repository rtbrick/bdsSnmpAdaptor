from bdsMappingFunctions import bdsMappingFunctions
import logging

BDSTABLEDICT = {'bdsRequest': {'process': 'confd', 'urlSuffix': '/bds/table/walk?format=raw', 'table': 'global.rtbrick.hostname.config'}}
OIDSEGMENT = "1.3.6.1.2.1.1."
REDISKEYPATTERN = "bdsTableInfo-confd-global.rtbrick.hostname.config"


class confd_global_rtbrick_hostname_config(object):

    """


.. literalinclude:: ../bdsSnmpTableModules/confd_global_interface_container.py
   :caption: bds request and iod settings
   :name: bds request and iod settings
   :language: text
   :dedent: 0
   :lines: 4-6

.. code-block:: json
   :caption: local.system.software.info.confd
   :name: local.system.software.info.confd example

   {
    "table": {
        "table_name": "global.rtbrick.hostname.config"
    },
    "objects": [
        {
            "sequence": 1,
            "update": true,
            "attribute": {
                "system_hostname": "Basesim",
                "rtbrick_hostname": "Basesim",
                "rtbrick_podname": "rtbrick-pod"
            }
        }
    ]
   }

    """

    @classmethod
    def setOids(self,bdsSnmpTableObject):
        self.bdsTableDict = BDSTABLEDICT
        oidSegment = OIDSEGMENT
        redisKeyPattern = REDISKEYPATTERN
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
