
The systemd unit files
----------------------

The `systemd` unit files are intended to keep BDS SNMP tool up and
running. Because of slight differences among Linux distributions,
unit files are shipped on the per-distribution basis.

To install the unit file on your system, first make sure to install
the BDS SNMP tool either from PyPI or local package:

```bash
$ pip install bdsSnmpAdaptor
```

Then copy unit file into the `systemd` configuration directory, reload
`systemd` and make sure the unit file are picked up:

```bash
# cp bdsSnmpAdaptor/systemd/ubuntu/*service /etc/systemd/system/
# systemctl daemon-reload
# systemctl list-unit-files | grep bds
```

Then you can either start the services:

```bash
# systemctl start bds-snmp-adaptor
```

Make sure they are up and running:

```bash
# systemctl status bds-snmp-adaptor
```

Optionally, make the BDS SNMP services started automatically on system boot:

```bash
# systemctl enable bds-snmp-adaptor
```

By default, BDS SNMP daemon picks up its configuration from
`/etc/bdssnmpadaptor/` directory.