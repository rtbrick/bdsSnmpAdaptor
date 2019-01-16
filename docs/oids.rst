.. _OIDS:

OID-Mapping
***********


.. module:: global_rtbrick_hostname_config

confd_global_rtbrick_hostname_config
====================================

.. currentmodule:: confd_global_rtbrick_hostname_config

.. autoclass:: confd_global_rtbrick_hostname_config

.. module:: confd_global_rtbrick_hostname_config


1.3.6.1.2.1.5
-------------
MIB Info: http://www.circitor.fr/Mibs/Html/S/SNMPv2-MIB.php

.. csv-table:: oid mapping
    :header: "#", "name", "pysnmp type", "BDS attr", "mapping"
    :widths: 4, 19, 16, 25, 39

    1, "sysName", "OctetString", "system_hostname",

confd_global_interface_container
================================
.. module:: confd_global_interface_container

.. currentmodule:: confd_global_interface_container

.. autoclass:: confd_global_interface_container

.. module:: confd_local_system_software_info_confd


1.3.6.1.2.1.2.2
---------------

MIB Info: http://www.circitor.fr/Mibs/Html/I/IF-MIB.php


.. csv-table:: oid mapping
    :header: "#", "name", "pysnmp type", "BDS attr", "mapping"
    :widths: 4, 19, 16, 25, 39

    1, "ifIndex", "Integer32", "interface_name", "ifIndexFromIfName"
    2, "ifDescr", "DisplayString", "interface_name",
    3, "ifType", "IANAifType", "encapsulation_type", "ifTypeMap"
    4, "ifMtu", "Integer32", "layer2_mtu",
    5, "ifSpeed", "Gauge32", "bandwidth",
    6, "ifPhysAddress", "PhysAddress", "mac_address",
    7, "ifAdminStatus", "INTEGER", "admin_status",
    8, "ifOperStatus", "INTEGER", "link_status", "ifOperStatusMap"
    9, "ifLastChange", "TimeTicks", ,
    10, "ifInOctets", "Counter32", ,
    11, "ifInUcastPkts", "Counter32", ,
    13, "ifInDiscards", "Counter32", ,
    14, "ifInErrors", "Counter32", ,
    15, "ifInUnknownProtos", "Counter32", ,
    16, "ifOutOctets", "Counter32", ,
    17, "ifOutUcastPkts", "Counter32", ,
    19, "ifOutDiscards", "Counter32", ,
    20, "ifOutErrors", "Counter32", ,

ffwd_default_interface_logical
==============================

.. currentmodule:: ffwd_default_interface_logical

.. autoclass:: ffwd_default_interface_logical

.. module:: ffwd_default_interface_logical

1.3.6.1.2.1.2.2
---------------

MIB Info: http://www.circitor.fr/Mibs/Html/I/IF-MIB.php

.. csv-table:: oid mapping
    :header: "#", "name", "pysnmp type", "BDS attr", "mapping"
    :widths: 4, 19, 16, 25, 39

    1, "ifIndex", "Integer32", "interface_name",\
                                "bdsMappingFunctions.ifIndexFromIfName"
    2, "ifDescr", "DisplayString", "interface_name",
    3, "ifType", "Integer32",6 ,static (hard coded)
    4, "ifMtu", "Integer32", ,
    5, "ifSpeed", "Gauge32", ,
    6, "ifPhysAddress", "PhysAddress", ,
    7, "ifAdminStatus", "INTEGER", "admin_status",
    8, "ifOperStatus", "INTEGER", "link_status","ifOperStatusMap"
    9, "ifLastChange", "TimeTicks", ,
    10, "ifInOctets", "Counter32", ,
    11, "ifInUcastPkts", "Counter32", ,
    13, "ifInDiscards", "Counter32", ,
    14, "ifInErrors", "Counter32", ,
    15, "ifInUnknownProtos", "Counter32", ,
    16, "ifOutOctets", "Counter32", ,
    17, "ifOutUcastPkts", "Counter32", ,
    19, "ifOutDiscards", "Counter32", ,
    20, "ifOutErrors", "Counter32", ,

confd_local_system_software_info_confd
======================================

.. currentmodule:: confd_local_system_software_info_confd

.. autoclass:: confd_local_system_software_info_confd

.. module:: confd_global_startup_status_confd

1.3.6.1.4.1.50058.101.1
-----------------------

MIB Info: RTBRICK-SYS-SW-INFO-TABLE-MIB

confd_global_startup_status_confd
=================================

.. currentmodule:: confd_global_startup_status_confd

.. autoclass:: confd_global_startup_status_confd

1.3.6.1.2.1.1
-------------
MIB Info: http://www.circitor.fr/Mibs/Html/S/SNMPv2-MIB.php

.. csv-table:: oid mapping
    :header: "#", "name", "pysnmp type", "BDS attr", "mapping"
    :widths: 4, 19, 16, 25, 39

    1, "sysDesc", "OctetString", "system_hostname",

1.3.6.1.4.1.50058.101.3
-----------------------

MIB Info: RTBRICK-STARTUP-STATS-TABLE-MIB
