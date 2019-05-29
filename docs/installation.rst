
BDS Adaptor installation
========================

The BDS Adaptor tool is packaged, distributed and can be installed along
the lines of a regular Python package. Python 3 is required because of
the newer Python features being used.

Package installation
--------------------

To install the `bdsSnmpAdaptor` package one can just run `pip3 install`
against the tarball package:

.. code-block:: bash

   # pip3 install bdsSnmpAdaptor-*.tar.gz

The command-line utilities `bds-snmp-notificator` and `bds-snmp-responder`
will be installed into the system binaries directory.

System configuration
--------------------

Thee BDS system requires configuration, logs and state directories:

.. code-block:: bash

   $ sudo mkdir -p /etc/bds-snmp-adaptor/mibs
   $ sudo mkdir /var/log/bds-snmp-adaptor
   $ sudo mkdir /var/run/bds-snmp-adaptor

The BDS tools are driven by a single configuration file expressed in the
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

For the SNMP command responder tool, the following configuration changes
might be required:

.. code-block:: yaml

    bdsSnmpAdapter:
      loggingLevel: info
      rotatingLogFile: /var/log/bds-snmp-responder
      stateDir: /var/run/bds-snmp-responder
      access:
        rtbrickHost: 10.0.3.10
        rtbrickPorts:
         - confd: 2002  # Define the rest port on which confd listens"
         - fwdd-hald: 5002  # Define the rest port on which fwwd listens"
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
      responder:
        listeningIP: 0.0.0.0  # SNMP get/getNext listening IP address
        listeningPort: 161  # SNMP get/getNext listening port
        staticOidContent:
          sysDescr: l2.pod2.nbg2.rtbrick.net
          sysContact: stefan@rtbrick.com
          sysName: l2.pod2.nbg2.rtbrick.net
          sysLocation: nbg2.rtbrick.net

System start up configuration
-----------------------------

Depending on the Linux distribution being used, the BDS system can be invoked
on system start up either through `systsmd` or `SYSV` init scripts. BDS adaptor
distribution includes start up configuration for both cases.

For `systemd` unit files the installation procedure would be:

.. code-block:: bash

    $ sudo cp bdsSnmpAdaptor/systemd/ubuntu/*service /etc/systemd/system/
    $ sudo systemctl daemon-reload
    $ sudo systemctl start bds-snmp-responder bds-snmp-notificator
    $ sudo systemctl enable bds-snmp-responder bds-snmp-notificator
    $ sudo systemctl status bds-snmp-responder bds-snmp-notificator

For `SYSV` init scripts:

.. code-block:: bash

    $ tar zxvf bdsSnmpAdaptor-*.tar.gz bdsSnmpAdaptor-*/sysvinit
    $ sudo cp bdsSnmpAdaptor-0.0.1/sysvinit/onl/* /etc/init.d
    $ for x in 2 3 4 5
        sudo ln -s /etc/init.d/bds-snmp-responder /etc/rc.$xd/S02bds-snmp-responder
        sudo ln -s /etc/init.d/bds-snmp-notificator /etc/rc.$xd/S02bds-snmp-notificator
    done
    $ sudo /etc/init.d/bds-snmp-responder start
    $ sudo /etc/init.d/bds-snmp-notificator start

Verification and troubleshooting
--------------------------------

Once everything is installed, one can check out the BDS daemon processes:

.. code-block:: bash

    # ps -ef | grep bds-snmp
    root     14405     1  0 Mar24 ?        00:08:47 /usr/bin/python3 /usr/local/bin/bds-snmp-responder
    root     14405     1  0 Mar24 ?        00:08:47 /usr/bin/python3 /usr/local/bin/bds-snmp-notificator

Their logs in the `/var/log/bds-snmp-adaptor` directory and test SNMP command
responder by running SNMP queries against it:

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
