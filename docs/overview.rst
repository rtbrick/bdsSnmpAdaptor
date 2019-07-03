.. _OVERVIEW:

Overview
========

The RtBrick SNMP adaptor software provides SNMP (v1, v2c and v3) mediation
between RtBrick BDS Full Stack operating system and SNMP-based network
management stations (NMS).

Features
--------

* SNMP command responder (`GET`, `GETNEXT` and `GETBULK`) role support
  for BDS operational data
* SNMP notification originator (`TRAP`) role support for BDS events
* Full SNMP v1, v2c and v3 support
* Major SNMPv3 ciphers support, including strong ones
* Full `IF-MIB <http://mibs.snmplabs.com/asn1/IF-MIB>`_ and partial
  `SNMPv2-MIB <http://mibs.snmplabs.com/asn1/SNMPv2-MIB>`_ implementation
* Multiple destinations for SNMP notifications support
* Highly concurrent internal design

RFCs supported
--------------

The following SNMP-related RFCs are supported:

* `RFC-1155 <http://www.ietf.org/rfc/rfc1157.txt?number=1155>`_
* `RFC-1157 <http://www.ietf.org/rfc/rfc1157.txt?number=1157>`_
* `RFC-1901 <http://www.ietf.org/rfc/rfc1157.txt?number=1901>`_
* `RFC-1908 <http://www.ietf.org/rfc/rfc1157.txt?number=1908>`_
* `RFC-1902 <http://www.ietf.org/rfc/rfc1157.txt?number=1902>`_
* `RFC-1905 <http://www.ietf.org/rfc/rfc1157.txt?number=1905>`_
* `RFC-2576 <http://www.ietf.org/rfc/rfc1157.txt?number=2576>`_
* `RFC-2578 <http://www.ietf.org/rfc/rfc1157.txt?number=2578>`_
* `RFC-2579 <http://www.ietf.org/rfc/rfc1157.txt?number=2579>`_
* `RFC-2863 <http://www.ietf.org/rfc/rfc1157.txt?number=2863>`_
* `RFC-3410 <http://www.ietf.org/rfc/rfc1157.txt?number=3410>`_
* `RFC-3411 <http://www.ietf.org/rfc/rfc1157.txt?number=3411>`_
* `RFC-3412 <http://www.ietf.org/rfc/rfc1157.txt?number=3412>`_
* `RFC-3413 <http://www.ietf.org/rfc/rfc1157.txt?number=3413>`_
* `RFC-3414 <http://www.ietf.org/rfc/rfc1157.txt?number=3414>`_
* `RFC-3415 <http://www.ietf.org/rfc/rfc1157.txt?number=3415>`_
* `RFC-3418 <http://www.ietf.org/rfc/rfc1157.txt?number=3418>`_
* `RFC-3826 <http://www.ietf.org/rfc/rfc1157.txt?number=3826>`_
* `RFC-7860 <http://www.ietf.org/rfc/rfc1157.txt?number=7860>`_
* `Reeder AES CFB 192/256 cipher <http://tools.ietf.org/html/draft-blumenthal-aes-usm-04>`_
* `Reeder Triple-DES EDE cipher <https://tools.ietf.org/html/draft-reeder-snmpv3-usm-3desede-00>`_
* `Blumenthal AES CFB 192/256 cipher <http://tools.ietf.org/html/draft-blumenthal-aes-usm-04>`_

System design
-------------

.. figure::  images/boxOverview.pdf
   :align:   center
