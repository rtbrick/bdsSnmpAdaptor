from bdsMappingFunctions import bdsMappingFunctions
import logging

class confd_local_system_software_info_confd(object):

    """

    .. code-block:: text
       :caption: setOids settings
       :name: setOids

        self.bdsTableDict = {'bdsRequest': {'process': 'confd', 'urlSuffix': '/bds/table/walk?format=raw', 'table': 'local.system.software.info.confd'}}
        oidSegment = "1.3.6.1.4.1.50058.1.101.1."
        redisKeyPattern = "bdsTableInfo-confd-local.system.software.info.confd"

    .. code-block:: json
       :caption: local.system.software.info.confd
       :name: local.system.software.info.confd example

          {}

.. csv-table:: oid mapping
    :header: "#", "name", "pysnmpBaseType", "BDS attr", "mapping"
    :widths: 4, 19, 16, 25, 39

    1, "name", "OctetString", "library",
    2, "commitId", "OctetString", "commit_id",
    3, "commitDate", "OctetString", "commit_date",
    4, "packageDate", "OctetString", "package_date",
    5, "vcCheckout", "OctetString", "vc_checkout",
    6, "branch", "OctetString", "branch",
    7, "libraryVersion", "OctetString", "version",
    8, "sourcePath", "OctetString", "source_path",

    """

    @classmethod
    def setOids(self,bdsSnmpTableObject):
        self.bdsTableDict = {'bdsRequest': {'process': 'confd', 'urlSuffix': '/bds/table/walk?format=raw', 'table': 'local.system.software.info.confd'}}
        oidSegment = "1.3.6.1.4.1.50058.1.101.1."
        expiryTimer = 60
        redisKeyPattern = "bdsTableInfo-confd-local.system.software.info.confd"
        redisKeysAsList = list(bdsSnmpTableObject.redisServer.scan_iter(redisKeyPattern))
        if len(redisKeysAsList) == 0:
            bdsSnmpTableObject.setBdsTableRequest(self.bdsTableDict)
        elif len(redisKeysAsList) == 1:
            checkResult,responseJSON,bdsTableRedisKey = bdsSnmpTableObject.checkBdsTableInfo(redisKeysAsList)
            if checkResult:
                for ifObject in responseJSON["objects"]:
                    indexString = ifObject["attribute"]["library"]
                    indexCharList = [str(ord(c)) for c in indexString]
                    index = str(len(indexCharList)) + "." + ".".join(indexCharList)
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"1."+str(index),
                                 fullOidDict = {"name":"name", "pysnmpBaseType":"OctetString",
                                               "value":indexString },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"2."+str(index),
                                 fullOidDict = {"name":"commitId", "pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["commit_id"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"3."+str(index),
                                 fullOidDict = {"name":"commitDate", "pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["commit_date"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"4."+str(index),
                                 fullOidDict = {"name":"packageDate", "pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["package_date"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"5."+str(index),
                                 fullOidDict = {"name":"vcCheckout", "pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["vc_checkout"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"6."+str(index),
                                 fullOidDict = {"name":"branch", "pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["branch"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"7."+str(index),
                                 fullOidDict = {"name":"libraryVersion", "pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["version"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"8."+str(index),
                                 fullOidDict = {"name":"sourcePath", "pysnmpBaseType":"OctetString",
                                               "value":ifObject["attribute"]["source_path"]},
                                 expiryTimer = expiryTimer )
                bdsSnmpTableObject.redisServer.delete("oidLock-{}".format(oidSegment))
                bdsSnmpTableObject.redisServer.set(bdsTableRedisKey,"processed",ex=50)
                logging.debug('set {} to processed with timout 50'.format(bdsTableRedisKey))
        else:
            logging.error('insonsistent redis keys: len redisKeysAsList > 1: {}'.format(redisKeysAsList))
