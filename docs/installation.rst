
BDS Adaptor installation
========================

The BDS Adaptor tool is packaged, distributed and can be installed along
the lines of a regular Python package, e.g. via `pip` package manager.
Python 3.4+ is required.

Package installation
--------------------

To install the `bdsSnmpAdaptor` package, along with its dependencies, one
can just run `pip3 install` against the tarball package:

.. code-block:: bash

   sudo pip3 install bdsSnmpAdaptor-*.tar.gz

The command-line utility `bds-snmp-adaptor` will be installed into
the system binaries directory.

Using older Python version
++++++++++++++++++++++++++

If you are using Python 3.4, chances are that you will need to install `pip`
first. The boot strap `pip` installation can be done like this:

.. code-block:: bash

    curl --silent --show-error https://bootstrap.pypa.io/get-pip.py | sudo python3.4
    sudo pip3.4 install bdsSnmpAdaptor-*.tar.gz

The rest of the installation process on Python 3.4 is no different than
on other Python versions.

.. note::

    The `aiohttp` dependency currently requires Python 3.5+. To keep
    `bdsSnmpAdapter` package compatible with Python 3.4, the `aiohttp`
    dependency is pinned to version < 2.3. This inhibits any further updates
    and may eventually cause conflicts with other dependencies.

    This Python 3.4 compatibility is thought to be a temporary measure,
    the ultimate plan is to unpin all the dependencies.

System configuration
--------------------

The BDS system requires configuration, logs and state directories:

.. code-block:: bash

   $ sudo mkdir -p /etc/bds-snmp-adaptor/mibs
   $ sudo mkdir /var/log/bds-snmp-adaptor
   $ sudo mkdir /var/run/bds-snmp-adaptor

The BDS tool is driven by a single configuration file expressed in the
YAML mark up. First, one need to copy the prototype configuration file
to its final location:

.. code-block:: bash

   $ tar zxvf bdsSnmpAdaptor-*.tar.gz bdsSnmpAdaptor-*/conf
   bdsSnmpAdaptor-0.0.1/conf/
   bdsSnmpAdaptor-0.0.1/conf/bds-snmp-adaptor.yml
   $
   $ cd bdsSnmpAdaptor
   $ sudo cp conf/bds-snmp-adaptor.yml /etc/bds-snmp-adaptor
   $ sudo cp mibs/* /etc/bds-snmp-adaptor/mibs

Here is the example of BDS configuration file driving all conceptual parts
of the BDS adaptor - SNMP command responder, SNMP notification originator,
BDS REST API client and REST API server.

.. code-block:: yaml

    bdsSnmpAdapter:
      loggingLevel: debug
      rotatingLogFile: /var/log/bds-snmp-adaptor
      stateDir: /var/run/bds-snmp-adaptor
      # BDS REST API endpoints
      access:
        rtbrickHost: 10.0.3.10
        rtbrickPorts:
         - confd: 2002  # confd REST API listens on this port"
         - fwdd-hald: 5002  # fwwd REST API listens on this port"
      # Common SNMP engine configuration, used by both command responder and
      # notification originator
      snmp:
        # Paths to ASN.1 MIB files in form of directories or URI, in
        # desired search order
        mibs:
          - /etc/bds-snmp-adaptor/mibs
          - /usr/share/snmp/mibs
        # SNMP engine ID uniquely identifies SNMP engine within an administrative
        # domain. For SNMPv3 crypto feature to work, the same SNMP engine ID value
        # should be configured at the TRAP receiver.
        engineId: 80:00:C3:8A:04:73:79:73:4e:61:6d:65:31:32:33
        # User-based Security Model (USM) configuration:
        # http://snmplabs.com/pysnmp/docs/api-reference.html#security-parameters
        versions:  # SNMP versions map, choices=['1', '2c', '3']
          1:  # map of configuration maps
            manager-A:  # SNMP security name
              community: public
          2c:  # map of configuration maps
            manager-B:  # SNMP security name
              community: public
          3:
            usmUsers:  # map of USM users and their configuration
              user1:  # descriptive SNMP security name
                user: testUser1  # USM user name
                authKey: authkey123
                authProtocol: md5  # md5, sha224, sha256, sha384, sha512, none
              user2:  # descriptive SNMP security name
                user: testUser2  # USM user name
                authKey: authkey123
                authProtocol: md5  # md5, sha224, sha256, sha384, sha512, none
                privKey: privkey123
                privProtocol: des  # des, 3des, aes128, aes192, aes192blmt, aes256, aes256blmt, none
      # SNMP command responder configuration
      responder:
        listeningIP: 0.0.0.0  # SNMP command responder listens on this address
        listeningPort: 161  # SNMP command responder listens on this port
        staticOidContent:
          SNMPv2-MIB::sysDescr:
            value:
              l2.pod2.nbg2.rtbrick.net

          SNMPv2-MIB::sysContact:
            value:
              stefan@rtbrick.com

          SNMPv2-MIB::sysName:
            value:
              l2.pod2.nbg2.rtbrick.net

          SNMPv2-MIB::sysLocation:
            value:
              nbg2.rtbrick.net

          # FIXME get from BDS entity table
          SNMPv2-MIB::sysObjectID:
            value:
              1.3.6.1.4.1.50058.102.1

          SNMPv2-MIB::sysUpTime:
            value:
              0
            code: |+
              import time

              BIRTHDAY = time.time()

              def value(*args, **kwargs):
                return int((time.time() - BIRTHDAY) * 100)

          SNMPv2-MIB::sysServices:
            value:
              72

          HOST-RESOURCES-MIB::hrSystemUptime:
            value:
              0
            code: |+
              import time

              BIRTHDAY = time.time()

              def value(*args, **kwargs):
                return int((time.time() - BIRTHDAY) * 100)

      # SNMP notification originator configuration
      notificator:
        # temp config lines to test incomming graylog message end #
        listeningIP: 0.0.0.0  # our REST API listens on this address
        listeningPort: 5000 # our REST API listens on this port
        # A single REST API call will cause SNMP notifications to all the listed targets
        snmpTrapTargets:  # array of SNMP trap targets
          target-I:  # descriptive name of this notification target
            address: 127.0.0.1  # send SNMP trap to this address
            port: 162  # send SNMP trap to this port
            security-name: manager-B  # use this SNMP security name
          target-II:  # descriptive name of this notification target
            address: 127.0.0.2  # send SNMP trap to this address
            port: 162  # send SNMP trap to this port
            security-name: user1  # use this SNMP security name

System start up configuration
-----------------------------

Depending on the Linux distribution being used, the BDS system can be invoked
on system start up either through `systsmd` or `SYSV` init scripts. BDS adaptor
distribution includes start up configuration for both cases.

For `systemd` unit files the installation procedure would be:

.. code-block:: bash

    $ sudo cp bdsSnmpAdaptor/systemd/ubuntu/*service /etc/systemd/system/
    $ sudo systemctl daemon-reload
    $ sudo systemctl start bds-snmp-adaptor
    $ sudo systemctl enable bds-snmp-adaptor
    $ sudo systemctl status bds-snmp-adaptor

For `SYSV` init scripts:

.. code-block:: bash

    $ tar zxvf bdsSnmpAdaptor-*.tar.gz bdsSnmpAdaptor-*/sysvinit
    $ sudo cp bdsSnmpAdaptor-0.0.1/sysvinit/generic/* /etc/init.d
    $ for x in 2 3 4 5
        sudo ln -s /etc/init.d/bds-snmp-adaptor /etc/rc.$xd/S02bds-snmp-adaptor
    done
    $ sudo /etc/init.d/bds-snmp-adaptor start

.. note::

   As of OpenNetworkLinux based on Ubuntu Trusty distribution, `onl` startup
   script shipped with `bdsSnmpAdaptor` does not seem to work reliably.
   It appears that the `start-stop-daemon` system tool is crashing and hanging
   occasionally. Because of that it's recommended to use
   *sysvinit/generic* script even on the ONL platform.

Verification and troubleshooting
--------------------------------

Once everything is installed, one can check out the BDS daemon process:

.. code-block:: bash

    # ps -ef | grep bds-snmp
    root     14405     1  0 May24 ?        00:08:47 /usr/bin/python3 /usr/local/bin/bds-snmp-adaptor

The logs reside in the `/var/log/bds-snmp-adaptor` directory, they are organized by
system component:

.. code-block:: bash

    $ ls -l /var/log/bds-snmp-adaptor/
    -rw-rw-rw- 1 root root      0 Jun 30 07:55 AsyncioRestServer.log
    -rw-rw-rw- 1 root root 812249 Jun 30 14:01 BdsAccess.log
    -rw-rw-rw- 1 root root 457943 Jun 30 13:04 MibInstrumController.log
    -rw-rw-rw- 1 root root 228362 Jun 30 13:04 OidDb.log
    -rw-rw-rw- 1 root root   2670 Jun 30 07:55 SnmpCommandResponder.log
    -rw-rw-rw- 1 root root   5191 Jun 30 07:55 SnmpNotificationOriginator.log

Incoming SNMP command queries should leave the imprint in the
`SnmpCommandResponder.log`, periodic BDS system access for the purpose of
mirroring its state information onto SNMP MIBs being served is noted in the
`BdsAccess.log`.

Out-of-band event from the BDS system should be logged in the
`AsyncioRestServer.log`, SNMP notification caused by them are logged
in the `SnmpNotificationOriginator.log`.

End-to-end verification can be done via `Net-SNMP` tools, e.g. SNMP command
responder can be queries by running `snmpwalk` or `snmpbulkwalk` tools.

Example of using SNMPv3 and default SNMPv3 USM credentials:

.. code-block:: bash

    $ snmpwalk -v3 -l authPriv -u testUser2 -A authkey123 -X privkey123  192.168.202.126
    iso.3.6.1.2.1.1.1.0 = STRING: "RtBrick Fullstack: bd:19.01-32 lwip:19.01-32 libbds:19.01-32
                                   libbgp:19.01-40 libfwdd:19.01-32 libconfd:19.01-26"
    iso.3.6.1.2.1.1.2.0 = OID: iso.3.6.1.4.1.50058.102.1
    iso.3.6.1.2.1.1.3.0 = Timeticks: (802) 0:00:08.02
    iso.3.6.1.2.1.1.4.0 = STRING: "stefan@rtbrick.com"
    iso.3.6.1.2.1.1.5.0 = STRING: "l2.pod2.nbg2.rtbrick.net"
    iso.3.6.1.2.1.1.6.0 = STRING: "nbg2.rtbrick.net"
    iso.3.6.1.2.1.1.7.0 = INTEGER: 6
    iso.3.6.1.2.1.2.1.0 = INTEGER: 54
    ...

Example of using SNMPv2c and default SNMP community name:

.. code-block:: bash

    $ snmpwalk -v2c -c public 192.168.202.126
    iso.3.6.1.2.1.1.1.0 = STRING: "RtBrick Fullstack: bd:19.01-32 lwip:19.01-32 libbds:19.01-32
                                   libbgp:19.01-40 libfwdd:19.01-32 libconfd:19.01-26"
    iso.3.6.1.2.1.1.2.0 = OID: iso.3.6.1.4.1.50058.102.1
    iso.3.6.1.2.1.1.3.0 = Timeticks: (802) 0:00:08.02
    iso.3.6.1.2.1.1.4.0 = STRING: "stefan@rtbrick.com"
    iso.3.6.1.2.1.1.5.0 = STRING: "l2.pod2.nbg2.rtbrick.net"
    iso.3.6.1.2.1.1.6.0 = STRING: "nbg2.rtbrick.net"
    iso.3.6.1.2.1.1.7.0 = INTEGER: 6
    iso.3.6.1.2.1.2.1.0 = INTEGER: 54
    ...
