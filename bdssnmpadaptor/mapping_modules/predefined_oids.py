# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#


class StaticAndPredefinedOids(object):
    """Implement multiple SNMP MIBs based on static configuration.

    Populates some of SNMP managed objects of SNMP `HOST-RESOURCES-MIB`,
    `SNMPv2-MIB` and `ENTITY-MIB` modules based on statically configured data.
    """

    ENT_TABLE_COLUMNS = [
        'entPhysicalIndex',
        'entPhysicalDescr',
        'entPhysicalVendorType',
        'entPhysicalContainedIn',
        'entPhysicalClass',
        'entPhysicalParentRelPos',
        'entPhysicalName',
        'entPhysicalHardwareRev',
        'entPhysicalFirmwareRev',
        'entPhysicalSoftwareRev',
        'entPhysicalSerialNum',
        'entPhysicalMfgName',
        'entPhysicalModelName',
        'entPhysicalAlias',
        'entPhysicalAssetID',
        'entPhysicalIsFRU',
        'entPhysicalMfgDate',
        'entPhysicalUris'
    ]

    ENT_PHYSICAL_TABLE = [
        [
            1,  # entPhysicalIndex
            'Rtbrick Fullstack on AS5912-54',
            '1.3.6.1.4.1.50058.102.1',  # entPhysicalVendorType
            0,  # entPhysicalContainedIn
            3,  # entPhysicalClass
            0,  # entPhysicalParentRelPos
            'chassis',
            '',
            '',
            '',
            '591654XK1848008',
            'Accton',
            'Edgecore Networks AS5912-54 port 10GB SFP+ plus 6 port QSFP28',
            '5916-54XK-O-AC-F',
            '',
            2,
            '2019-5-26,13:30:15.0,-4:0',
            ''
        ],
        [
            2,  # entPhysicalIndex
            'AS5912 Compute Board',
            '1.3.6.1.4.1.50058.102.1',  # entPhysicalVendorType
            1,  # entPhysicalContainedIn
            9,  # entPhysicalClass
            0,  # entPhysicalParentRelPos
            'AS5916-54XK',
            'R02A',
            'AS5916 V36 20180815',
            '',
            '591654XK1848017',
            'Accton',
            'Intel(R) Xeon(R) CPU D-1518 @ 2.20GHz',
            'AS5916-54XK',
            '',
            1,
            '2019-5-26,13:30:15.0,-4:0',
            ''
        ],
        [
            3,  # entPhysicalIndex
            'PSU-1',  # entPhysicalDescr
            '1.3.6.1.4.1.50058.102.1',  # entPhysicalVendorType
            1,  # entPhysicalContainedIn
            6,  # entPhysicalClass
            0,  # entPhysicalParentRelPos
            '',  # entPhysicalName
            '',
            '',
            '',
            'NULL',
            'Accton',
            '',
            '',
            '',
            1,
            '2019-5-26,13:30:15.0,-4:0',
            ''
        ],
        [
            4,  # entPhysicalIndex
            'PSU-2',  # entPhysicalDescr
            '1.3.6.1.4.1.50058.102.1',  # entPhysicalVendorType
            1,  # entPhysicalContainedIn
            6,  # entPhysicalClass
            0,  # entPhysicalParentRelPos
            '',  # entPhysicalName
            '',
            '',
            '',
            'NULL',
            'Accton',
            '',
            '',
            '',
            1,
            '2019-5-26,13:30:15.0,-4:0',
            ''
        ],
        [
            5,  # entPhysicalIndex
            'Chassis Fan - 1',  # entPhysicalDescr
            '1.3.6.1.4.1.50058.102.1',  # entPhysicalVendorTyp
            1,  # entPhysicalContainedIn
            7,  # entPhysicalClass
            0,  # entPhysicalParentRelPos
            '',  # entPhysicalName
            '',
            '',
            '',
            'NULL',
            'Accton',
            '',
            '',
            '',
            1,
            '2019-5-26,13:30:15.0,-4:0',
            ''
        ],
        [
            6,  # entPhysicalIndex
            'Chassis Fan - 2',  # entPhysicalDescr
            '1.3.6.1.4.1.50058.102.1',  # entPhysicalVendorTyp
            1,  # entPhysicalContainedIn
            7,  # entPhysicalClass
            0,  # entPhysicalParentRelPos
            '',  # entPhysicalName
            '',
            '',
            '',
            'NULL',
            'Accton',
            '',
            '',
            '',
            1,
            '2019-5-26,13:30:15.0,-4:0',
            ''
        ]
    ]

    @classmethod
    def setOids(cls, oidDb, staticOidDict, bdsIds, uptime):
        """Populates OID DB with BDS information.

        Takes known objects from JSON document, puts them into
        the OID DB as specific MIB managed objects.

        Args:
            oidDb (OidDb): OID DB instance to work on
            bdsData (dict): BDS information to put into OID DB
            bdsIds (list): list of last known BDS record sequence IDs
            uptime (int): system uptime in hundreds of seconds

        Raises:
            BdsError: on OID DB population error
        """

        add = oidDb.add

        for objectName, objectInfo in staticOidDict.items():
            mibName, mibSymbol = objectName.split('::', 1)

            add(mibName, mibSymbol, 0, value=objectInfo.get('value'),
                code=objectInfo.get('code'))

        for i, phyValueList in enumerate(cls.ENT_PHYSICAL_TABLE):

            row = cls.ENT_PHYSICAL_TABLE[i]

            for j, scalar in enumerate(cls.ENT_TABLE_COLUMNS):
                add('ENTITY-MIB', scalar, row[0], value=row[j])
