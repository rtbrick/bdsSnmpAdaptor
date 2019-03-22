.. _OVERVIEW:

Overview
********

The `bdsSnmpAdapter` modules offer SNMP (v2c and v3) mediation between
RtBrick BDS systems and SNMP NMS.

The SW runs on Linux (tested implemented with Ubuntu18.4) and offers multiple
deployment options. As the first step, the isolated setup has been tested.

.. figure::  images/boxOverview.pdf
   :align:   center

   overview

The following SNMP operations are supported (on the test effort basis):

- get,
- get-next,
- get-bulk
- trap

The `bdsSnmpAdaptor` tool has been developed and tested under Python 3.6.
The following key libraries are used:

- pysnmp 4.4.8 (both SNMP agent and manager parts)
- aiohttp (REST server)
- requestsp (REST client)
- pyyaml

The use-case for `bdsSnmpAdapter` is the integration of RtBrick Systems with
the existing management environment, which relies upon SNMP for management
purposes. Expected use-cases include retrieval of network interfaces statistics
and emission of SNMP notifications.

The number of OIDs, which will be supported in the first release, is up to 20K
(testing effort).

For get transactions `bdsSnmpAdapter` is using a configurable cache mechanism for
te bds table data, which means that the retrieved SNMP information is, from
the timing perspective, accurate for up to 50 seconds (configurable).

SNMP notifications will be send immediately.

Security:

- both SNMP v2c community name and SNMP v3 USM authentication is supported for SNMP
- REST data exchange between RtBrick systems and bdsSnmpAdapter is unencrypted.
  This might change in the future.
- It is expected that no other application runs on the bdsSnmpHost.
