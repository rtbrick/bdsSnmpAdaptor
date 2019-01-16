from bdsMappingFunctions import bdsMappingFunctions
import logging

class static_oid_settings (object):

    """


    """


    @classmethod
    def setOids(self,bdsSnmpTableObject):
        bdsSnmpTableObject.setOidHash (fullOid = oidSegment+"1.1."+str(ifIndex),
                     fullOidDict = {"name":"ifIndex", "pysnmpBaseType":"Integer32",
                                   "value":int(ifIndex)},
                     expiryTimer = expiryTimer )
