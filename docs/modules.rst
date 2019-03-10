.. module:: bdsSnmpTables
.. _MODULES:

Modules
*******

Module-Overview
===============

`bdsSnmpAdapter` utilizes 6 discrete python modules, which run as separate
linux processes:

- 3 processes support SNMP GET/GETNEXT command for information retrieval:

  - bdsAccessToRedis
  - bdsSnmpTables
  - getOidFromRedis

- 2 processes support the generation of SNMP notifications:

  - restServer
  - redisToSnmpTrap

- 1 management process, which collects control information from the above:

  - bdsSnmpAdapterManager

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
