import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from bdsMappingFunctions import bdsMappingFunctions
import logging
from oidDb import oidDbItem

class confd_local_system_software_info_confd(object):
    """


    """
    @classmethod
    def setOids(self,bdsJsonResponseDict,targetOidDb):
        oidSegment = "1.3.6.1.4.1.50058.101.1.1."
        for bdsJsonObject in bdsJsonResponseDict["objects"]:
            indexString = bdsJsonObject["attribute"]["library"]
            indexCharList = [str(ord(c)) for c in indexString]
            index = str(len(indexCharList)) + "." + ".".join(indexCharList)
            targetOidDb.insertOid(newOidItem = oidDbItem(oid = oidSegment+"1."+str(index),
                               name="name", pysnmpBaseType="OctetString",
                               value=indexString ))
