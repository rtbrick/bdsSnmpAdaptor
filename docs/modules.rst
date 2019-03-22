.. module:: bdsSnmpTables
.. _MODULES:

Modules
*******

Module-Overview
===============

The `bdsSnmpAdapter` package ships two command-line tools that can be run as
two Linux processes:

- One process implements Command Responder for the RtBrick system

  - bds-snmp-responder

- Another process supports the generation of SNMP notifications in response
  to events in the RtBrick system:

  - bds-snmp-notificator

.. figure::  images/moduleOverview.pdf
   :align:   center

   overview of modules

bdsAccessToRedis
================

.. currentmodule:: bdsAccessToRedis

.. autoclass:: bdsAccessToRedis

bdsSnmpTables
=============

.. currentmodule:: bdsSnmpTables

.. autoclass:: bdsSnmpTables

  ================================== =
  methods
  ================================== =

  .. automethod:: getTableFunctionFromOid

  .. automethod:: run_forever


getOidFromRedis
===============

.. currentmodule:: getOidFromRedis

.. autoclass:: oidDbItem
.. autoclass:: snmpBackEnd
.. autoclass:: MibInstrumController
.. autoclass:: snmpFrontEnd

restServer
==========

.. currentmodule:: restServer

.. autoclass:: restHttpServer

   ================================== =
   methods
   ================================== =

   .. automethod:: handler

   .. automethod:: run_forever

.. module:: bdsSnmpTables

redisToSnmpTrap
===============

.. currentmodule:: redisToSnmpTrap

.. autoclass:: redisToSnmpTrapForwarder
