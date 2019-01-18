from bdsMappingFunctions import bdsMappingFunctions
import logging


class confd_global_startup_status_confd(object):

    """


    """


    @classmethod
    def setOids(self,bdsJsonResponseDict,targetOidDb):
        for bdsJsonObject in bdsJsonResponseDict["objects"]:
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
