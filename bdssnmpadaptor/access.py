#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import asyncio
import collections
import time

import aiohttp

from bdssnmpadaptor.config import loadConfig
from bdssnmpadaptor.log import set_logging
from bdssnmpadaptor.mapping_modules import confd_global_interface_physical
from bdssnmpadaptor.mapping_modules import confd_global_startup_status_confd
from bdssnmpadaptor.mapping_modules import confd_local_system_software_info_confd
from bdssnmpadaptor.oid_db import OidDb
from bdssnmpadaptor.mapping_modules.predefined_oids import StaticAndPredefinedOids

BIRTHDAY = time.time()

REQUEST_MAPPING_DICTS = {
    'confd_local.system.software.info.confd': {
        'mappingFunc': confd_local_system_software_info_confd.ConfdLocalSystemSoftwareInfoConfd,
        'bdsRequest': {'process': 'confd',
                       'urlSuffix': 'bds/table/walk?format=raw',
                       'table': 'local.system.software.info.confd'}
    },
    'confd_global_startup_status_confd': {
        'mappingFunc': confd_global_startup_status_confd.ConfdGlobalStartupStatusConfd,
        'bdsRequest': {'process': 'confd',
                       'urlSuffix': 'bds/table/walk?format=raw',
                       'table': 'global.startup.status.confd'}
    },
    'confd_global_interface_physical': {
        'mappingFunc': confd_global_interface_physical.ConfdGlobalInterfacePhysical,
        'bdsRequest': {'process': 'confd',
                       'urlSuffix': 'bds/table/walk?format=raw',
                       'table': 'global.interface.physical'}
    }
    # 'ffwd_default_interface_logical' : {
    #     'mappingFunc': ffwd_default_interface_logical.FfwdDefaultInterfaceLogical,
    #     'lastSequenceHash': None,
    #     'bdsRequest': {'process': 'fwdd-hald',      ## Check
#                        'urlSuffix':'bds/table/walk?format=raw',
#                        'table':'default.interface.logical'}
    #  },
    # 'fwdd_global_interface_physical_statistics' : {
    #     'mappingFunc': fwdd_global_interface_physical_statistics.FwddGlobalInterfacePhysicalStatistics,
    #     'bdsRequest': {'process': 'fwdd-hald',      ## Check
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

    def __init__(self, args):

        configDict = loadConfig(args.config)

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        self.moduleLogger.debug(f'configDict:{configDict}')
        self.rtbrickHost = configDict['access']['rtbrickHost']
        self.rtbrickPorts = (configDict['access']['rtbrickPorts'])
        # self.rtbrickCtrldPort = configDict['access']['rtbrickCtrldPort']
        # self.rtbrickContainerName = configDict['access']['rtbrickContainerName']

        self.staticOidDict = configDict['responder']['staticOidContent']

        self._oidDb = OidDb(args)

        # keeps track of changes to the BDS data
        self._bdsIds = collections.defaultdict(list)

        # 'logging': 'warning'
        # do more stuff here. e.g. connectivity checks etc

    @property
    def oidDb(self):
        return self._oidDb

    async def getJson(self, bdsRequest):
        bdsProcess = bdsRequest['process']
        bdsSuffix = bdsRequest['urlSuffix']
        bdsTable = bdsRequest['table']

        if 'attributes' in bdsRequest:
            attributeDict = {}

            for attribute in bdsRequest['attributes']:
                attributeDict[attribute] = bdsRequest['attributes'][attribute]

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
                'table': {
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
                    bdsResponse = await response.json(content_type='application/json')

        except Exception as exc:
            self.moduleLogger.error(f'HTTP request for {url} failed: {exc}')
            return False, exc

        if response.status != 200:
            self.moduleLogger.error(f'received {response.status} for {url}')
            return False, 'status != 200'

        self.moduleLogger.info(f'received HTTP {response.status} for {url}')
        self.moduleLogger.debug(f'HTTP response {response}')

        return True, bdsResponse

    async def run_forever(self):

        while True:
            await asyncio.sleep(5)

            try:
                StaticAndPredefinedOids.setOids(
                    self._oidDb, self.staticOidDict, [], 0)

            except Exception as exc:
                self.moduleLogger.error(
                    f'failed at populating OID DB with predefined OIDs: {exc}')
                continue

            for bdsReqKey in REQUEST_MAPPING_DICTS:
                self.moduleLogger.debug(f'working on {bdsReqKey}')

                bdsRequest = REQUEST_MAPPING_DICTS[bdsReqKey]['bdsRequest']
                mappingfunc = REQUEST_MAPPING_DICTS[bdsReqKey]['mappingFunc']

                resultFlag, bdsResponse = await self.getJson(bdsRequest)

                if not resultFlag:
                    self.moduleLogger.error('BDS JSON is not available')
                    continue

                tableKey = f'{bdsRequest["process"]}_{bdsRequest["table"]}'

                self.moduleLogger.debug(
                    f'bdsResponses[{tableKey}] {bdsResponse}')

                bdsId = self._bdsIds[bdsReqKey]

                try:
                    mappingfunc.setOids(
                        self._oidDb, bdsResponse, bdsId, BIRTHDAY)

                except Exception as exc:
                    self.moduleLogger.error(
                        f'failed at populating OID DB from BDS response: {exc}')
                    continue

            self.moduleLogger.debug(f'done refreshing OID DB')
