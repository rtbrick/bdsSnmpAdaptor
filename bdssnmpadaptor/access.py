# -*- coding: future_fstrings -*-
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

    POLL_PERIOD = 5

    def __init__(self, args):

        configDict = loadConfig(args.config)

        self._moduleLogger = set_logging(configDict, __class__.__name__)

        self._moduleLogger.debug(f'configDict:{configDict}')
        self._restHost = configDict['access']['rtbrickHost']
        self._restPorts = (configDict['access']['rtbrickPorts'])

        self._staticOidDict = configDict['responder']['staticOidContent']

        self._oidDb = OidDb(args)

        # keeps track of changes to the BDS data
        self._bdsIds = collections.defaultdict(list)

        # 'logging': 'warning'
        # do more stuff here. e.g. connectivity checks etc

    @property
    def oidDb(self):
        """Return OID DB instance"""
        return self._oidDb

    @asyncio.coroutine
    def fetchTable(self, tableInfo):
        """Fetch BDS table from REST API within asyncio loop.

        Args:
            tableInfo (dict): table information to read

        Returns:
            tuple: (status, responseData) where `status` being `True`
                indicates success, `False` indicates failure.
                BDS table contents is returned in the response `dict`.
        """
        process = tableInfo['process']
        suffix = tableInfo['urlSuffix']
        table = tableInfo['table']

        if 'attributes' in tableInfo:
            attributes = tableInfo['attributes']

            requestData = {
                'table': {
                    'table_name': table
                },
                'objects': [
                    {
                        'attribute': attributes
                    }
                ]
            }

        else:
            requestData = {
                'table': {
                    'table_name': table
                }
            }

        ports = [int(x[process]) for x in self._restPorts
                 if process in x]

        url = f'http://{self._restHost}:{ports[0]}/{suffix}'

        session = None

        try:
            session = aiohttp.ClientSession()
            response = yield from session.post(
                url, timeout=5, json=requestData)
            responseData = yield from response.json()

        except Exception as exc:
            self._moduleLogger.error(f'HTTP request for {url} failed: {exc}')
            return False, exc

        finally:
            if session:
                yield from session.close()

        if response.status != 200:
            self._moduleLogger.error(f'received {response.status} for {url}')
            return False, 'status != 200'

        self._moduleLogger.info(f'received HTTP {response.status} for {url}')
        self._moduleLogger.debug(f'HTTP response {responseData}')

        return True, responseData

    @asyncio.coroutine
    def periodicRetriever(self):
        """Periodically fetch BDS information.

        Loops infinitely over asyncio coroutines fetching BDS information
        from BDS REST API and pushing it into OID DB.
        """

        try:
            StaticAndPredefinedOids.setOids(
                self._oidDb, self._staticOidDict, [], 0)

        except Exception as exc:
            self._moduleLogger.error(
                f'failed at populating OID DB with predefined OIDs: {exc}')

        while True:
            yield from asyncio.sleep(self.POLL_PERIOD)

            uptime = int(time.time() - BIRTHDAY * 100)

            for bdsReqKey in REQUEST_MAPPING_DICTS:
                self._moduleLogger.debug(f'working on {bdsReqKey}')

                bdsRequest = REQUEST_MAPPING_DICTS[bdsReqKey]['bdsRequest']

                resultFlag, bdsResponse = yield from self.fetchTable(bdsRequest)

                if not resultFlag:
                    self._moduleLogger.error('BDS information is not available')
                    continue

                tableKey = f'{bdsRequest["process"]}_{bdsRequest["table"]}'

                self._moduleLogger.debug(
                    f'bdsResponses[{tableKey}] {bdsResponse}')

                bdsId = self._bdsIds[bdsReqKey]

                mappingfunc = REQUEST_MAPPING_DICTS[bdsReqKey]['mappingFunc']

                try:
                    mappingfunc.setOids(
                        self._oidDb, bdsResponse, bdsId, uptime)

                except Exception as exc:
                    self._moduleLogger.error(
                        f'failed at populating OID DB from BDS response: {exc}')
                    continue

            self._moduleLogger.debug(f'done refreshing OID DB')
