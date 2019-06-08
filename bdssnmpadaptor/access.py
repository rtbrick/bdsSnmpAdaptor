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

from bdssnmpadaptor.config import loadConfig
from bdssnmpadaptor.log import set_logging
from bdssnmpadaptor.mapping_modules import confd_global_interface_physical
from bdssnmpadaptor.mapping_modules import confd_global_startup_status_confd
from bdssnmpadaptor.mapping_modules import confd_local_system_software_info_confd
from bdssnmpadaptor.oidDb import OidDb
from bdssnmpadaptor.mapping_modules.predefined_oids import StaticAndPredefinedOids

BIRTHDAY = time.time()

REQUEST_MAPPING_DICTS = {
    'confd_local.system.software.info.confd': {
        'mappingFunc': confd_local_system_software_info_confd.ConfdLocalSystemSoftwareInfoConfd,
        'bdsRequestDict': {'process': 'confd',
                           'urlSuffix': 'bds/table/walk?format=raw',
                           'table': 'local.system.software.info.confd'}
    },
    'confd_global_startup_status_confd': {
        'mappingFunc': confd_global_startup_status_confd.ConfdGlobalStartupStatusConfd,
        'bdsRequestDict': {'process': 'confd',
                           'urlSuffix': 'bds/table/walk?format=raw',
                           'table': 'global.startup.status.confd'}
    },
    'confd_global_interface_physical': {
        'mappingFunc': confd_global_interface_physical.ConfdGlobalInterfacePhysical,
        'bdsRequestDict': {'process': 'confd',
                           'urlSuffix': 'bds/table/walk?format=raw',
                           'table': 'global.interface.physical'}
    }
    # 'ffwd_default_interface_logical' : {
    #     'mappingFunc': ffwd_default_interface_logical.FfwdDefaultInterfaceLogical,
    #     'lastSequenceHash': None,
    #     'bdsRequestDict': {'process': 'fwdd-hald',      ## Check
    #                        'urlSuffix':'bds/table/walk?format=raw',
    #                        'table':'default.interface.logical'}
    #  },
    # 'fwdd_global_interface_physical_statistics' : {
    #     'mappingFunc': fwdd_global_interface_physical_statistics.FwddGlobalInterfacePhysicalStatistics,
    #     'bdsRequestDict': {'process': 'fwdd-hald',      ## Check
    #                        'urlSuffix':'bds/table/walk?format=raw',
    #                        'table':'global.interface.physical.statistics'}
    #   }
}


class BdsAccess(object):
    """Populate SNMP managed objects database from BDS.

    Within asyncio loop, perform BDS REST API call, pull configured
    documents, turn them into SNMP managed objects and cache them
    in the in-memory OID DB.
    """

    def __init__(self, cliArgsDict):

        configDict = loadConfig(cliArgsDict['config'])

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.moduleLogger.debug(f'configDict:{configDict}')
        self.rtbrickHost = configDict['access']['rtbrickHost']
        self.rtbrickPorts = (configDict['access']['rtbrickPorts'])
        # self.rtbrickCtrldPort = configDict['access']['rtbrickCtrldPort']
        # self.rtbrickContainerName = configDict['access']['rtbrickContainerName']
        self.staticOidDict = {}

        self.staticOidDict = configDict['responder']['staticOidContent']

        self.expirytimer = 50  ### FIXME
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

        if 'attributes' in bdsRequestDict:
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

        url = f'http://{self.rtbrickHost}:{rtbrickPort}/{bdsSuffix}'

        try:
            headers = {
                'Content-Type': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, timeout=5,
                                        headers=headers,
                                        json=requestData) as response:
                    responseJsonDict = await response.json(content_type='application/json')

        except Exception as exc:
            self.moduleLogger.error(f'HTTP request for {url} failed: {exc}')
            return False, exc

        if response.status != 200:
            self.moduleLogger.error(f'received {response.status} for {url}')
            return False, 'status != 200'

        self.moduleLogger.info(f'received HTTP {response.status} for {url}')
        self.moduleLogger.debug(f'HTTP response {response}')

        return True, responseJsonDict

    def setTableSequenceDict(self, bdsRequestDictKey, responseJsonDict):
        sequenceNumberList = []

        for i, bdsJsonObject in enumerate(responseJsonDict['objects']):
            sequenceNumberList.append(bdsJsonObject['sequence'])

        self.tableSequenceListDict[bdsRequestDictKey] = sequenceNumberList

    async def run_forever(self):

        while True:
            await asyncio.sleep(5)

            try:
                StaticAndPredefinedOids.setOids(
                    self.oidDb, self.staticOidDict, [], 0)

            except Exception as exc:
                self.moduleLogger.error(
                    f'failed at populating OID DB with predefined OIDs: {exc}')
                continue

            for bdsRequestDictKey in REQUEST_MAPPING_DICTS:
                self.moduleLogger.debug(f'working on {bdsRequestDictKey}')

                bdsRequestDict = REQUEST_MAPPING_DICTS[bdsRequestDictKey]['bdsRequestDict']
                mappingfunc = REQUEST_MAPPING_DICTS[bdsRequestDictKey]['mappingFunc']
                bdsProcess = bdsRequestDict['process']
                bdsTable = bdsRequestDict['table']

                resultFlag, responseJsonDict = await self.getJson(bdsRequestDict)

                if not resultFlag:
                    self.moduleLogger.error('BDS JSON is not available')
                    continue

                responseTableKey = f'{bdsProcess}_{bdsTable}'

                self.responseJsonDicts[responseTableKey] = responseJsonDict

                self.moduleLogger.debug(
                    f'responseJsonDicts[{responseTableKey}] {responseJsonDict}')

                if bdsRequestDictKey in self.tableSequenceListDict:
                    tableSequenceList = self.tableSequenceListDict[bdsRequestDictKey]

                else:
                    tableSequenceList = []  # required for the first run

                try:
                    mappingfunc.setOids(
                        self.oidDb, responseJsonDict, tableSequenceList, BIRTHDAY)

                except Exception as exc:
                    self.moduleLogger.error(
                        f'failed at populating OID DB from BDS response: {exc}')
                    continue

                self.setTableSequenceDict(bdsRequestDictKey, responseJsonDict)

            self.moduleLogger.debug(f'done refreshing OID DB')
