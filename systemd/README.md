
The systemd unit files
----------------------

The `systemd` unit files are intended to keep BDS SNMP tools up and
running. Because of slight differences among Linux distributions,
unit files are shipped on the per-distribution basis.

To install these unit files on your system, first make sure to install
the BDS SNMP tools either from PyPI or local package:

```bash
$ pip install bdsSnmpAdaptor
```

Then copy unit files into the `systemd` configuration directory, reload
`systemd` and make sure the unit files are picked up:

```bash
# cp bdsSnmpAdaptor/systemd/ubuntu/*service /etc/systemd/system/
# systemctl daemon-reload
# systemctl list-unit-files | grep bds
```

Then you can either start the services:

```bash
# systemctl start bds-snmp-responder bds-snmp-notificator
```

Make sure they are up and running:

```bash
# systemctl status bds-snmp-responder bds-snmp-notificator
```

Optionally, make the BDS SNMP services started automatically on system boot:

```bash
# systemctl enable bds-snmp-responder bds-snmp-notificator
```

By default, BDS SNMP binaries pick up their configuration from
`/etc/bdssnmpadaptor/` directory.