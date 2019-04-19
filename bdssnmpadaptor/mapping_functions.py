#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import json


class BdsMappingFunctions(object):

    def __init__(self):
        pass

    @classmethod
    def stringFromSoftwareInfo(cls, responseJSON):
        returnString = "RtBrick Fullstack:"

        for swModule in responseJSON["objects"]:
            if swModule["attribute"]["library"] in ["libbds", "libconfd",
                                                    "libisis", "lwip",
                                                    "libfwdd", "libbgp", "bd"]:
                returnString += (" {}:{}".format(
                    swModule["attribute"]["library"], swModule["attribute"]["version"]))

        return returnString

    @classmethod
    def ifIndexFromIfName(cls, ifNameString):
        ifPrefix = ifNameString.split("-")[0]
        if ifPrefix in [ "ifp", "ifc", "ifl" ]:
            ifIndexList = ifNameString.split("-")[1].split("/")
            if len(ifIndexList) == 5:
                if int(ifIndexList[4]) == 0:
                    ifIndex = int(ifIndexList[0]) * 4096 * 128 * 128 * 8 + int(ifIndexList[1]) * 4096 * 128 * 128 + int(
                        ifIndexList[2]) * 4096 * 128 + int(ifIndexList[3]) * 4096 + (int(ifIndexList[4]) + 1)

                else:
                    ifIndex = int(ifIndexList[0]) * 4096 * 128 * 128 * 8 + int(ifIndexList[1]) * 4096 * 128 * 128 + int(
                        ifIndexList[2]) * 4096 * 128 + int(ifIndexList[3]) * 4096 + int(ifIndexList[4])

                return ifIndex

            elif len(ifIndexList) == 4:
                ifIndex = int(ifIndexList[0]) * 4096 * 128 * 128 * 8 + int(ifIndexList[1]) * 4096 * 128 * 128 + int(
                    ifIndexList[2]) * 4096 * 128 + int(ifIndexList[3]) * 4096

                return ifIndex

            elif len(ifIndexList) == 3:
                ifIndex = int(ifIndexList[0]) * 4096 * 128 * 128 + int(ifIndexList[1]) * 4096 * 128 + int(
                    ifIndexList[2]) * 4096
                return ifIndex
        elif ifPrefix in [ "lo" ]:
            ifIndex = (int(ifIndexList[0])+8) * 4096 * 128 * 128 * 8 + int(ifIndexList[1]) * 4096 * 128 + int(
                ifIndexList[2]) * 4096
            return ifIndex
        else:
            return None

    @classmethod
    def stripIfPrefixFromIfName(cls, ifNameString):
        ifIndexList = ifNameString.split("-")[1].split("/")

        if len(ifIndexList) == 5:
            return "/".join(ifIndexList)

        elif len(ifIndexList) == 4:
            return "/".join(ifIndexList[1:])

        elif len(ifIndexList) == 3:
            return "/".join(ifIndexList)


if __name__ == '__main__':
    jsonString = """{
    "table": {
        "table_name": "local.system.software.info.confd"
    },
    "objects": [
        {
            "attribute": {
                "commit_id": "94656913a98cea1b427e6b9ae6c744e27530d45b",
                "version": "18.06-0",
                "vc_checkout": "git checkout 94656913a98cea1b427e6b9ae6c744e27530d45b",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:10:25 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/json-parser",
                "library": "json_parser",
                "commit_date": "Tue Jan 9 16:12:30 2018 +0530"
            },
            "update": true,
            "sequence": 1
        },
        {
            "attribute": {
                "commit_id": "3d298f2d7c52c94d78620a16e444ef28d04f2815",
                "version": "18.06-0",
                "vc_checkout": "git checkout 3d298f2d7c52c94d78620a16e444ef28d04f2815",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:10:29 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/bd",
                "library": "bd",
                "commit_date": "Fri Jun 8 10:23:54 2018 +0530"
            },
            "update": true,
            "sequence": 2
        },
        {
            "attribute": {
                "commit_id": "3f5c9fdcaa00abeb83371876aebae11bf6814fff",
                "version": "18.06-2",
                "vc_checkout": "git checkout 3f5c9fdcaa00abeb83371876aebae11bf6814fff",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:17:28 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--libbgp/DEBUG/source",
                "library": "libbgp",
                "commit_date": "Fri Jun 8 15:04:46 2018 +0530"
            },
            "update": true,
            "sequence": 3
        },
        {
            "attribute": {
                "commit_id": "6b07b093c6a0f1b54dcd9f0f6fd8892a55c109e8",
                "version": "18.06-0",
                "vc_checkout": "git checkout 6b07b093c6a0f1b54dcd9f0f6fd8892a55c109e8",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:21:09 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--libfwdd/DEBUG/source",
                "library": "libfwdd",
                "commit_date": "Wed Jun 13 01:01:55 2018 +0530"
            },
            "update": true,
            "sequence": 6
        },
        {
            "attribute": {
                "commit_id": "6bc9a2b7901fe4a1fd91d571f4bfd5640e32c985",
                "version": "18.06-0",
                "vc_checkout": "git checkout 6bc9a2b7901fe4a1fd91d571f4bfd5640e32c985",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:10:26 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/libqb",
                "library": "libqb",
                "commit_date": "Sun Apr 1 20:38:29 2018 +0530"
            },
            "update": true,
            "sequence": 8
        },
        {
            "attribute": {
                "commit_id": "41e2141b93f28ce2d9c86b7e74d701eaa96c78e4",
                "version": "18.06-0",
                "vc_checkout": "git checkout 41e2141b93f28ce2d9c86b7e74d701eaa96c78e4",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:10:30 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/librtbutils",
                "library": "librtbutils",
                "commit_date": "Fri Jun 8 13:06:08 2018 +0530"
            },
            "update": true,
            "sequence": 9
        },
        {
            "attribute": {
                "commit_id": "68fb6ee310afdd4285e8ecb5a9d180232e13bb75",
                "version": "18.06-0",
                "vc_checkout": "git checkout 68fb6ee310afdd4285e8ecb5a9d180232e13bb75",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:14:31 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--libspf/DEBUG/source",
                "library": "libspf",
                "commit_date": "Fri Mar 30 00:46:28 2018 +0530"
            },
            "update": true,
            "sequence": 10
        },
        {
            "attribute": {
                "commit_id": "97b1c21552537286cfa945637f70b259dc609c3f",
                "version": "18.06-0",
                "vc_checkout": "git checkout 97b1c21552537286cfa945637f70b259dc609c3f",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:10:27 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/libtiger",
                "library": "libtiger",
                "commit_date": "Tue Jun 13 10:38:52 2017 +0530"
            },
            "update": true,
            "sequence": 11
        },
        {
            "attribute": {
                "commit_id": "80f3e6d1f7d826abea9f03c954d9f9cc3b743fa1",
                "version": "18.06-0",
                "vc_checkout": "git checkout 80f3e6d1f7d826abea9f03c954d9f9cc3b743fa1",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:10:28 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/libprotocolinfra",
                "library": "libproto_infra",
                "commit_date": "Tue Jun 12 15:20:37 2018 +0530"
            },
            "update": true,
            "sequence": 14
        },
        {
            "attribute": {
                "commit_id": "e39fef1fa9344a8ce335970a48a02bbb880c180d",
                "version": "18.06-0",
                "vc_checkout": "git checkout e39fef1fa9344a8ce335970a48a02bbb880c180d",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:10:31 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/librtbshark",
                "library": "rtbshark",
                "commit_date": "Wed Mar 21 20:56:13 2018 +0530"
            },
            "update": true,
            "sequence": 15
        },
        {
            "attribute": {
                "commit_id": "49d7575942aa3363023903ecd5a0c6138537c0bd",
                "version": "18.06-0",
                "vc_checkout": "git checkout 49d7575942aa3363023903ecd5a0c6138537c0bd",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:51:27 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--libldp/DEBUG/source",
                "library": "libldp",
                "commit_date": "Sat May 12 15:36:33 2018 +0530"
            },
            "update": true,
            "sequence": 16
        },
        {
            "attribute": {
                "commit_id": "4d2d5393d9ad77749342265d63639705b1c8a3b1",
                "version": "18.06-0",
                "vc_checkout": "git checkout 4d2d5393d9ad77749342265d63639705b1c8a3b1",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:10:25 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/libdict",
                "library": "libdict",
                "commit_date": "Fri Mar 30 02:43:56 2018 +0530"
            },
            "update": true,
            "sequence": 17
        },
        {
            "attribute": {
                "commit_id": "e47c8befcc6f2caa64e9ac1a32bfb0d6c1b6ec4d",
                "version": "18.06-0",
                "vc_checkout": "git checkout e47c8befcc6f2caa64e9ac1a32bfb0d6c1b6ec4d",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:10:30 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/lwip",
                "library": "lwip",
                "commit_date": "Tue Jun 12 10:15:36 2018 +0530"
            },
            "update": true,
            "sequence": 18
        },
        {
            "attribute": {
                "commit_id": "90e29a27bb15df75719b62636277b12c151e3573",
                "version": "18.06-0",
                "vc_checkout": "git checkout 90e29a27bb15df75719b62636277b12c151e3573",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:10:28 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--librtbrickinfra/DEBUG/source/libbds",
                "library": "libbds",
                "commit_date": "Tue Jun 12 12:20:37 2018 +0530"
            },
            "update": true,
            "sequence": 19
        },
        {
            "attribute": {
                "commit_id": "a5996e83f0ab5d223ec879507290b0c73c93369e",
                "version": "18.06-3",
                "vc_checkout": "git checkout a5996e83f0ab5d223ec879507290b0c73c93369e",
                "branch": "fmed5",
                "package_date": "Wed, 13 Jun 2018 08:56:40 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--libisis/DEBUG/source",
                "library": "libisis",
                "commit_date": "Wed Jun 13 14:23:23 2018 +0530"
            },
            "update": true,
            "sequence": 20
        },
        {
            "attribute": {
                "commit_id": "30757439755223c02caa79ea1708cde773eac9a9",
                "version": "18.06-0",
                "vc_checkout": "git checkout 30757439755223c02caa79ea1708cde773eac9a9",
                "branch": "master",
                "package_date": "Wed, 13 Jun 2018 05:16:16 +0000",
                "source_path": "/var/lib/jenkins2/workspace/build--libconfd/DEBUG/source",
                "library": "libconfd",
                "commit_date": "Mon Apr 16 18:16:14 2018 +0530"
            },
            "update": true,
            "sequence": 21
        }
    ]
}"""
    responseJSON = json.loads(jsonString)
    versionStr = BdsMappingFunctions.stringFromSoftwareInfo(responseJSON)
    print(versionStr)
