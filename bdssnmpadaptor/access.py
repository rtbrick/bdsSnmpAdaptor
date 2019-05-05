#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import asyncio
import time

import aiohttp

from bdssnmpadaptor.config import loadBdsSnmpAdapterConfigFile
from bdssnmpadaptor.log import set_logging
from bdssnmpadaptor.mapping_modules import confd_global_interface_physical
from bdssnmpadaptor.mapping_modules import confd_global_startup_status_confd
from bdssnmpadaptor.mapping_modules import confd_local_system_software_info_confd
from bdssnmpadaptor.oidDb import OidDb
from bdssnmpadaptor.predefined_oids import StaticAndPredefinedOids

BIRTHDAY = time.time()

REQUEST_MAPPING_DICTS = {
    "confd_local.system.software.info.confd": {
        "mappingFunc": confd_local_system_software_info_confd.ConfdLocalSystemSoftwareInfoConfd,
        "bdsRequestDict": {'process': 'confd',
                           'urlSuffix': 'bds/table/walk?format=raw',
                           'table': 'local.system.software.info.confd'}
    },
    "confd_global_startup_status_confd": {
        "mappingFunc": confd_global_startup_status_confd.ConfdGlobalStartupStatusConfd,
        "bdsRequestDict": {'process': 'confd',
                           'urlSuffix': 'bds/table/walk?format=raw',
                           'table': 'global.startup.status.confd'}
    },
    "confd_global_interface_physical": {
        "mappingFunc": confd_global_interface_physical.ConfdGlobalInterfacePhysical,
        "bdsRequestDict": {'process': 'confd',
                           'urlSuffix': 'bds/table/walk?format=raw',
                           'table': 'global.interface.physical'}
    }
    # "ffwd_default_interface_logical" : {
    #     "mappingFunc": ffwd_default_interface_logical.FfwdDefaultInterfaceLogical,
    #     "lastSequenceHash": None,
    #     "bdsRequestDict": {'process': 'fwdd-hald',      ## Check
    #                        'urlSuffix':'bds/table/walk?format=raw',
    #                        'table':'default.interface.logical'}
    #  },
    # "fwdd_global_interface_physical_statistics" : {
    #     "mappingFunc": fwdd_global_interface_physical_statistics.FwddGlobalInterfacePhysicalStatistics,
    #     "bdsRequestDict": {'process': 'fwdd-hald',      ## Check
    #                        'urlSuffix':'bds/table/walk?format=raw',
    #                        'table':'global.interface.physical.statistics'}
    #   }
}


class BdsAccess(object):

    def __init__(self, cliArgsDict):

        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["config"], "access")

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.moduleLogger.debug("configDict:{}".format(configDict))
        self.rtbrickHost = configDict['rtbrickHost']
        self.rtbrickPorts = (configDict['rtbrickPorts'])
        # self.rtbrickCtrldPort = configDict['rtbrickCtrldPort']
        # self.rtbrickContainerName = configDict['rtbrickContainerName']
        self.staticOidDict = {}

        d = loadBdsSnmpAdapterConfigFile(cliArgsDict["config"], "responder")
        if "staticOidContent" in d:
            for oidName in ["sysDesc", "sysContact", "sysName", "sysLocation"]:
                if oidName in d["staticOidContent"]:
                    self.staticOidDict[oidName] = d["staticOidContent"][oidName]
                else:
                    self.staticOidDict[oidName] = "to be defined"

            for oidName in ["engineId"]:
                if oidName in d["staticOidContent"]:
                    self.staticOidDict[oidName] = d["staticOidContent"][oidName]

                else:
                    self.staticOidDict[oidName] = "to be defined"

        self.expirytimer = 50  ### FIXME
        self.responseSequence = 0
        self.responseJsonDicts = {}
        self.oidDb = OidDb(cliArgsDict)

        # used for hashing numbers of objects and hash over sequence numbers
        self.tableSequenceListDict = {}

        # 'logging': 'warning'
        # do more stuff here. e.g. connecectivity checks etc

    def getOidDb(self):
        return self.oidDb

    async def getJson(self, bdsRequestDict):
        bdsProcess = bdsRequestDict['process']
        bdsSuffix = bdsRequestDict['urlSuffix']
        bdsTable = bdsRequestDict['table']

        if "attributes" in bdsRequestDict:
            attributeDict = {}

            for attribute in bdsRequestDict['attributes']:
                attributeDict[attribute] = bdsRequestDict['attributes'][attribute]

            requestData = {
                'table': {
                    'table_name': bdsTable
                },
                'objects': [
                    {
                        'attribute': attributeDict
                    }
                ]
            }

        else:
            requestData = {
                'table':
                    {
                        'table_name': bdsTable
                    }
            }

        rtbrickProcessPortDict = [
            x for x in self.rtbrickPorts if list(x)[0] == bdsProcess][0]

        rtbrickPort = int(rtbrickProcessPortDict[bdsProcess])

        url = "http://{}:{}/{}".format(
            self.rtbrickHost, rtbrickPort, bdsSuffix)

        # url = "http://{}:{}/api/application-rest-proxy/{}/{}/{}".format(self.rtbrickHost,
        #                                self.rtbrickCtrldPort,
        #                                self.rtbrickContainerName,
        #                                bdsProcess,
        #                                bdsSuffix)
        try:
            headers = {
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, timeout=5,
                                        headers=headers,
                                        json=requestData) as response:
                    responseJsonDict = await response.json(content_type='application/json')

        except Exception as e:
            print("Exception: #{}#".format(e))
            return False, e

        else:
            if response.status != 200:
                self.moduleLogger.error("received {} for {}".format(response.status, url))
                return False, "status != 200"

            else:
                self.moduleLogger.info("received {} for {}".format(response.status, url))
                self.moduleLogger.debug(response)
                return True, responseJsonDict

    async def setTableSequenceDict(self, bdsRequestDictKey, responseJsonDict):
        sequenceNumberList = []

        for i, bdsJsonObject in enumerate(responseJsonDict["objects"]):
            sequenceNumberList.append(bdsJsonObject["sequence"])

        self.tableSequenceListDict[bdsRequestDictKey] = sequenceNumberList

    async def run_forever(self):

        while True:
            await StaticAndPredefinedOids.setOids(self.oidDb, self.staticOidDict)

            for bdsRequestDictKey in REQUEST_MAPPING_DICTS:
                self.moduleLogger.debug("working on {}".format(bdsRequestDictKey))

                bdsRequestDict = REQUEST_MAPPING_DICTS[bdsRequestDictKey]["bdsRequestDict"]
                mappingfunc = REQUEST_MAPPING_DICTS[bdsRequestDictKey]["mappingFunc"]
                bdsProcess = bdsRequestDict['process']
                bdsTable = bdsRequestDict['table']
                resultFlag, responseJsonDict = await self.getJson(bdsRequestDict)

                if resultFlag:
                    responseTableKey = "{}_{}".format(bdsProcess, bdsTable)
                    self.responseJsonDicts[responseTableKey] = responseJsonDict
                    self.moduleLogger.debug(
                        "self.responseJsonDicts[{}] {}".format(responseTableKey, responseJsonDict))

                    if bdsRequestDictKey in self.tableSequenceListDict:
                        tableSequenceList = self.tableSequenceListDict[bdsRequestDictKey]

                    else:
                        tableSequenceList = []  # required for the first run

                    # print(bdsRequestDictKey)
                    await mappingfunc.setOids(responseJsonDict, self.oidDb, tableSequenceList, BIRTHDAY)
                    # except Exception as e:
                    #    print(e)
                    #    self.moduleLogger.error(
                    #        "mappingfunc {} raise Exception: {}".format(mappingfunc, e))
                    await self.setTableSequenceDict(bdsRequestDictKey, responseJsonDict)

            # print(self.tableSequenceListDict)
            await asyncio.sleep(5)
