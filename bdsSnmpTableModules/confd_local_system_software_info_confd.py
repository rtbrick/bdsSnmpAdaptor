import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from bdsMappingFunctions import bdsMappingFunctions
import logging

class confd_local_system_software_info_confd(object):

    """

    .. code-block:: text
       :caption: setOids settings
       :name: setOids

        self.bdsTableDict = {'bdsRequest': {'process': 'confd',
                              'urlSuffix': '/bds/table/walk?format=raw',
                              'table': 'local.system.software.info.confd'}}
        oidSegment = "1.3.6.1.4.1.50058.101.1.1."
        redisKeyPattern = "bdsTableInfo-confd-local.system.software.info.confd"

    .. code-block:: json
       :caption: local.system.software.info.confd
       :name: local.system.software.info.confd example

          {
          "table": {
              "table_name": "local.system.software.info.confd"
          },
          "objects": [
              {
                  "attribute": {
                      "commit_id": "94656913a98cea1b427e6b9ae6c744e27530d45b",
                      "version": "18.06-0",
                      "vc_checkout":\
"git checkout 94656913a98cea1b427e6b9ae6c744e27530d45b",
                      "branch": "master",
                      "package_date": "Wed, 13 Jun 2018 05:10:25 +0000",
                      "source_path":\
 "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/json-parser",
                      "library": "json_parser",
                      "commit_date": "Tue Jan 9 16:12:30 2018 +0530"
                  },
                  "update": true,
                  "sequence": 1
              }

.. csv-table:: oid mapping
    :header: "#", "name", "pysnmp type", "BDS attr", "mapping"
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
        oidSegment = "1.3.6.1.4.1.50058.101.1.1."
        expiryTimer = 60
        redisKeyPattern = "bdsTableInfo-confd-local.system.software.info.confd"
        redisKeysAsList = list(bdsSnmpTableObject.redisServer.scan_iter(redisKeyPattern))
        if len(redisKeysAsList) == 0:
            bdsSnmpTableObject.setBdsTableRequest(self.bdsTableDict)
        elif len(redisKeysAsList) == 1:
            checkResult,responseJSON,bdsTableRedisKey = bdsSnmpTableObject.checkBdsTableInfo(redisKeysAsList)
            if checkResult:
                for bdsJsonObject in responseJSON["objects"]:
                    indexString = bdsJsonObject["attribute"]["library"]
                    indexCharList = [str(ord(c)) for c in indexString]
                    index = str(len(indexCharList)) + "." + ".".join(indexCharList)
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"1."+str(index),
                                 fullOidDict = {"name":"name", "pysnmpBaseType":"OctetString",
                                               "value":indexString },
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"2."+str(index),
                                 fullOidDict = {"name":"commitId", "pysnmpBaseType":"OctetString",
                                               "value":bdsJsonObject["attribute"]["commit_id"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"3."+str(index),
                                 fullOidDict = {"name":"commitDate", "pysnmpBaseType":"OctetString",
                                               "value":bdsJsonObject["attribute"]["commit_date"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"4."+str(index),
                                 fullOidDict = {"name":"packageDate", "pysnmpBaseType":"OctetString",
                                               "value":bdsJsonObject["attribute"]["package_date"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"5."+str(index),
                                 fullOidDict = {"name":"vcCheckout", "pysnmpBaseType":"OctetString",
                                               "value":bdsJsonObject["attribute"]["vc_checkout"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"6."+str(index),
                                 fullOidDict = {"name":"branch", "pysnmpBaseType":"OctetString",
                                               "value":bdsJsonObject["attribute"]["branch"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"7."+str(index),
                                 fullOidDict = {"name":"libraryVersion", "pysnmpBaseType":"OctetString",
                                               "value":bdsJsonObject["attribute"]["version"]},
                                 expiryTimer = expiryTimer )
                    bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"8."+str(index),
                                 fullOidDict = {"name":"sourcePath", "pysnmpBaseType":"OctetString",
                                               "value":bdsJsonObject["attribute"]["source_path"]},
                                 expiryTimer = expiryTimer )
                bdsSnmpTableObject.redisServer.delete("oidLock-{}".format(oidSegment))
                # in addition the SW Info Flag is set
                swString = bdsMappingFunctions.stringFromSoftwareInfo (responseJSON) #creates an abbreviated string over all modules
                bdsSnmpTableObject.setOidHash (fullOid = "1.3.6.1.2.1.1.1.0",
                             fullOidDict = {"name":"sysDescr", "pysnmpBaseType":"OctetString",
                                           "value":swString},
                             expiryTimer = expiryTimer )
                bdsSnmpTableObject.redisServer.set(bdsTableRedisKey,"processed",ex=50)
                logging.debug('set {} to processed with timout 50'.format(bdsTableRedisKey))
        else:
            logging.error('insonsistent redis keys: len redisKeysAsList > 1: {}'.format(redisKeysAsList))
