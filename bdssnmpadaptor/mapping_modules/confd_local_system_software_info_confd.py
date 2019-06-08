# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#

from bdssnmpadaptor import mapping_functions


class ConfdLocalSystemSoftwareInfoConfd(object):
    """Implement SNMP SNMPv2-MIB for BDS system.

    Populates SNMP managed objects of SNMP `SNMPv2-MIB` module from
    `local.system.software.info.confd` BDS table.

    Notes
    -----

    Expected input:

    .. code-block:: json

    {
      "objects": [
        {
          "sequence": 3,
          "update": true,
          "timestamp": "Tue Apr 09 11:44:57 GMT +0000 2019",
          "attribute": {
            "library": "bd",
            "commit_id": "8d5cc5a8ca9324154568470b1e8be20df57bedb3",
            "commit_date": "Fri Mar 22 12:47:37 2019 +0530",
            "package_date": "Mon, 08 Apr 2019 23:31:43 +0000",
            "vc_checkout": "git checkout 8d5cc5a8ca9324154568470b1e8be20df57bedb3",
            "branch": "master",
            "version": "19.04-29",
            "source_path": "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/bd"
          }
        }
      ]
    }
    """

    @classmethod
    def setOids(cls, oidDb, bdsData, bdsIds, birthday):
        """Populates OID DB with BDS information.

        Takes known objects from JSON document, puts them into
        the OID DB as specific MIB managed objects.

        Args:
            oidDb (OidDb): OID DB instance to work on
            bdsData (dict): BDS information to put into OID DB
            bdsIds (list): list of last known BDS record sequence IDs
            birthday (float): timestamp of system initialization

        Raises:
            BdsError: on OID DB population error
        """

        newBdsIds = [obj['sequence'] for obj in bdsData['objects']]

        if newBdsIds == bdsIds:
            return

        swString = mapping_functions.stringFromSoftwareInfo(bdsData)

        with oidDb.module(__name__) as add:

            add('SNMPv2-MIB', 'sysDescr', 1, value=swString)

            # for index,bdsJsonObject in enumerate(bdsData['objects"]):
            #     #indexString = bdsJsonObject["attribute"]["library"]
            #     #indexCharList = [str(ord(c)) for c in indexString]
            #     #index = str(len(indexCharList)) + "." + ".".join(indexCharList)  # FIXME add description
            #
            #     add('HOST-RESOURCES-MIB', 'hrSWRunIndex', index, value=index)
            #
            #     add('HOST-RESOURCES-MIB', 'hrSWRunName', index,
            #          value=bdsJsonObject["attribute"]["commit_id"])

            #     add('HOST-RESOURCES-MIB', 'commitDate', index,
            #         value=bdsJsonObject["attribute"]["commit_date"])

            #     add('HOST-RESOURCES-MIB', 'packageDate', index,
            #         value=bdsJsonObject["attribute"]["package_date"])

            #     add('HOST-RESOURCES-MIB', 'vcCheckout', index,
            #         value=bdsJsonObject["attribute"]["vc_checkout"])

            #     add('HOST-RESOURCES-MIB', 'branch', index,
            #         value=bdsJsonObject["attribute"]["branch"])

            #     add('HOST-RESOURCES-MIB', 'libraryVersion', index,
            #         value=bdsJsonObject["attribute"]["version"])

            #     add('HOST-RESOURCES-MIB', 'sourcePath', index,
            #         value=bdsJsonObject["attribute"]["source_path"])

            # # in addition the SW Info Flag is set by
            # # creating an abbreviated string over all modules

        bdsIds[:] = newBdsIds
