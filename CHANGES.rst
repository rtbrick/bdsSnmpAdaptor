
Release 0.0.1, 30.06.2019
=========================

First production release featuring IF-MIB and partial SNMPv2-MIB
implementation, complete SNMPv1/v2c/v3 support and asynchronous, highly
concurrent internal design.

New features
------------

* Added strong encryption support to SNMPv3 command responder and notification
  originator components.
* Added the ability to configure predefined SNMP MIB managed objects using MIB
  names as opposed to OIDs
* Added the ability to configure Python code snippets producing dynamic values
  for SNMP managed objects at runtime.

Improvements and bug fixes
--------------------------

* Reworked MIB implementation to fully rely on SNMP MIBs, as opposed to
  manual OID/type configuration.
* Joint SNMP command responder and notification originator components into
  a single process. This also led to joining SNMP configuration for both
  tools.
* The whole application has been backported to Python 3.4 for platform
  compatibility reasons.
* Optimized internal in-memory database (OID DB) for higher performance at
  larger scales.
* Added stateful SNMP engine `boots` counter to keep track of SNMP engine
  reboots.
* Added extensive unit test coverage.
* Added stale BDS objects expiration in the SNMP MIB being served.
* Added Python packaging information including dependencies, GitHub CI
  hooks etc.
