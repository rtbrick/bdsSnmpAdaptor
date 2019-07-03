# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import os
import time

from pysnmp.proto.api import v2c
from pysnmp.smi import instrum

from bdssnmpadaptor.config import loadConfig
from bdssnmpadaptor.log import set_logging

BIRTHDAY = time.time()


class MibInstrumController(instrum.AbstractMibInstrumController):
    """Create MIB instrumentation controller.

    Implements SNMP agent interface to OID DB in form of MIB
    instrumentation controller complying with pysnmp API.

    Methods of this class will be invoked by pysnmp to handle SNMP
    command.
    """

    def createVarbindFromOidDbItem(self, oidDbItem):
        """Create SNMP variable-bindings from OID DB item.

        Creates pysnmp object representing SNMP variable-binding from OID DB
        item. Depending on the type of OID DB item (static value or code object),
        might execute attached Python code snippet to generate a payload value.
        In case of errors, `noSuchObject` sentinel value might be set on the
        variable-binding.

        Args:
            oidDbItem (OidItem): OID DB item to create SNMP var-binds from

        Returns:
            VarBind: pysnmp variable-binding object
        """

        if oidDbItem.code:
            scope = {}

            try:
                exec(oidDbItem.code, globals(), scope)

                value = scope['value']

                if callable(value):
                    value = value(oidDbItem.oid, oidDbItem.value)

                value = oidDbItem.value.clone(value)

            except Exception as ex:
                self.moduleLogger.error(f'code snippet execution error for object '
                                        f'{oidDbItem.name}: {ex}')
                return oidDbItem.oid, v2c.NoSuchObject()

        else:
            value = oidDbItem.value

        if value is None:
            return oidDbItem.oid, v2c.NoSuchObject()

        self.moduleLogger.debug(
            f'createVarbindFromOidDbItem returning oid '
            f'{oidDbItem.oid} with value {value}')

        return oidDbItem.oid, value

    def setOidDbAndLogger(self, oidDb, args):
        """Attach OID DB and logging objects

        Args:
            oidDb (OidDb): OID DB object to operate on
            args (object): argparse namespace object holding
                command-line options
        """
        self._oidDb = oidDb

        configDict = loadConfig(args.config)

        self.moduleLogger = set_logging(configDict, __class__.__name__)

        return self

    def readVars(self, varBinds, *args, **kwargs):
        """Handle SNMP GET command.

        Take pysnmp variable-bindings that come in SNMP GET command request,
        fetch OID DB items corresponding to the requested SNMP MIB objects
        to produce response variable-bindings.

        The length of the response list is guaranteed to be of the same length
        as request list. Response variable-bindings match their request
        counterparts positionally.

        In case of an error in processing individual variable-binding,
        `NoSuchObject` sentinel pysnmp object will be returned as a value
        for the failed variable binding.

        Args:
            varBinds (list): pysnmp variable-binding objects
            *args (object): opaque pysnmp options
            **kawrgs (object): opaque pysnmp options

        Returns:
            list: list of pysnmp variable-binding objects to respond with

        Note:
            This method is called from pysnmp to handle SNMP GET command.
        """

        self.moduleLogger.info(f'GET request var-binds: {varBinds}')

        returnList = []

        for oid, value in varBinds:
            try:
                oidDbItemObj = self._oidDb.getObjectByOid(oid)

            except Exception as exc:
                self.moduleLogger.error(f'oidDb read failed for {oid}: {exc}')
                returnList.append((oid, v2c.NoSuchInstance()))
                continue

            self.moduleLogger.debug(
                f'oidDb GET returned {oidDbItemObj} for oid: {oid}')

            if oidDbItemObj is None:
                returnList.append((oid, v2c.NoSuchObject()))
                continue

            returnList.append(self.createVarbindFromOidDbItem(oidDbItemObj))

        self.moduleLogger.debug(
            f'GET response var-binds: {returnList}')

        return returnList

    def readNextVars(self, varBinds, *args, **kwargs):
        """Handle SNMP GETNEXT and GETBULK commands.

        Take pysnmp variable-bindings that come in SNMP GETNEXT or GETBULK
        command request, fetch OID DB items corresponding to lexicographically
        *next* SNMP MIB objects relative to the requested ones to produce
        response variable-bindings.

        The length of the response list is guaranteed to be of the same length
        as request list. Response variable-bindings match their request
        counterparts positionally.

        In case of an error in processing individual variable-binding,
        `NoSuchObject` sentinel pysnmp object will be returned as a value
        for the failed variable binding.

        If no more objects is found in OID DB, `EndOfMib` sentinel pysnmp
        object will be returned as a value for the requested managed object.

        Args:
            varBinds (list): pysnmp variable-binding objects
            *args (object): opaque pysnmp options
            **kawrgs (object): opaque pysnmp options

        Returns:
            list: list of pysnmp variable-binding objects to respond with

        Note:
            This method is called from pysnmp to handle SNMP GETNEXT or GETBULK
            commands.
        """

        self.moduleLogger.info(f'GETNEXT request var-binds: {varBinds}')

        returnList = []

        for oid, value in varBinds:
            nextOidString = self._oidDb.getNextOid(oid)

            self.moduleLogger.debug(
                f'request OID is {oid}, next OID is {nextOidString}')

            try:
                oidDbItemObj = self._oidDb.getObjectByOid(nextOidString)

            except Exception as exc:
                self.moduleLogger.error(f'oidDb read failed for {oid}: {exc}')
                returnList.append((oid, v2c.EndOfMibView()))
                continue

            self.moduleLogger.debug(
                f'oidDb GETNEXT/GETBULK returned {oidDbItemObj} for oid: {oid}')

            if oidDbItemObj is None:
                returnList.append((oid, v2c.EndOfMibView()))
                continue

            returnList.append(self.createVarbindFromOidDbItem(oidDbItemObj))

        self.moduleLogger.debug(
            f'GETNEXT/GETBULK response var-binds: {returnList}')

        return returnList
