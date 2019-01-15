.. _OVERVIEW:

Overview
********

The bdsSnmpAdapter modules offer SNMP (v2c and v3) mediation between
RtBrick BDS systems and SNMP Servers.

The SW runs on Linux (tested implemented with Ubuntu18.4) and offers multiple
deployment options. As first step the isolated has been tested.

.. figure::  images/boxOverview.pdf
   :align:   center

   overview

Following SNMP methods are supported (test effort):

- get,
- get-next,
- get-bulk
- trap

bdsSnmpAdptor has been implememnted in python 3.6. Following key libraries are
used:

- Pysnmp 4.4.8 (both snmp agent and client )
- aiohttp (REST server)
- requestsp (REST client)
- Redis 5.0

Use case for bdsSnmpAdapter is the integration of RtBrick Systems in existing
management environment, which uses the SNMP protocol. expected use-cases are the
retrieval of interface statistics or the intiation of SNMP notifications.

The number of OIDs which will be supported in the first release is does 20k.
(testing effort)

For get transactions bdsSnmpAdapter is using a configurable cache mechanism for
bds table data, which means that the retrieved SNMP information has from
timing perspective an accurate of up to 50 Seconds (configurable)

SNMP notifications will be send immediately.

Security:

- both v2c community and v3 USM authentication is supported for SNMPv2
- REST data exchange between RtBrick systems and bdsSnmpAdapter is unencrypted.
  This might change in the future.
- It is expected, that no other application run on the bdsSnmpHost. Redis
  security features are enabled by demand.
