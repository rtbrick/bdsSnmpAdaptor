# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#


TWO_POWER_29 = 4096 * 128 * 128 * 8
TWO_POWER_26 = 4096 * 128 * 128
TWO_POWER_19 = 4096 * 128
TWO_POWER_12 = 4096


def ifIndexFromIfName(ifName):
    """Parse BDS interface name into SNMP IF-MIB index.

    Args:
        ifName (str): BDS interface name

    Returns:
        int: SNMP IF-MIB interface index or None if interface name
            can't be parsed
    """

    ifName, _ , ifIndex = ifName.partition('-')

    ifIndices = [int(x) for x in ifIndex.split('/')]

    if ifName in ('ifp', 'ifc', 'ifl'):

        if len(ifIndices) == 5:

            if int(ifIndices[4]) == 0:
                return (
                    ifIndices[0] * TWO_POWER_29 +
                    ifIndices[1] * TWO_POWER_26 +
                    ifIndices[2] * TWO_POWER_19 +
                    ifIndices[3] * TWO_POWER_12 +
                    ifIndices[4] +
                    1
                )

            else:
                return (
                    ifIndices[0] * TWO_POWER_29 +
                    ifIndices[1] * TWO_POWER_26 +
                    ifIndices[2] * TWO_POWER_19 +
                    ifIndices[3] * TWO_POWER_12 +
                    ifIndices[4]
                )

        elif len(ifIndices) == 4:

            return (
                ifIndices[0] * TWO_POWER_29 +
                ifIndices[1] * TWO_POWER_26 +
                ifIndices[2] * TWO_POWER_19 +
                ifIndices[3] * TWO_POWER_12
            )

        elif len(ifIndices) == 3:

            return (
                ifIndices[0] * TWO_POWER_26 +
                ifIndices[1] * TWO_POWER_19 +
                ifIndices[2] * TWO_POWER_12
            )

    elif ifName == 'lo':

        return (
            (ifIndices[0] + 8) * TWO_POWER_29 +
            ifIndices[1] * TWO_POWER_19 +
            ifIndices[2] * TWO_POWER_12
        )


def stripIfPrefixFromIfName(ifName):
    """Strip prerix from BDS interface name.

    Args:
        ifName (str): BDS interface name

    Returns:
        str: BDS interface name suffix
    """
    ifName, _ , ifIndex = ifName.partition('-')

    if ifIndex.count('/') in (2, 4):
        return ifIndex

    elif ifIndex.count('/') == 3:
        return ifIndex[ifIndex.index('/') + 1:]
