# -*- coding: future_fstrings -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#


def stringFromSoftwareInfo(responseJSON):
    returnString = 'RtBrick Fullstack:'

    for swModule in responseJSON['objects']:
        if swModule['attribute']['library'] in ['libbds', 'libconfd',
                                                'libisis', 'lwip',
                                                'libfwdd', 'libbgp', 'bd']:
            returnString += (
                f' {swModule["attribute"]["library"]}:'
                f'{swModule["attribute"]["version"]}')

    return returnString


def ifIndexFromIfName(ifNameString):
    ifPrefix = ifNameString.split('-')[0]
    if ifPrefix in ['ifp', 'ifc', 'ifl']:
        ifIndexList = ifNameString.split('-')[1].split('/')
        if len(ifIndexList) == 5:
            if int(ifIndexList[4]) == 0:
                ifIndex = int(ifIndexList[0]) * 4096 * 128 * 128 * 8 + int(ifIndexList[1]) * 4096 * 128 * 128 + int(
                    ifIndexList[2]) * 4096 * 128 + int(ifIndexList[3]) * 4096 + (int(ifIndexList[4]) + 1)

            else:
                ifIndex = int(ifIndexList[0]) * 4096 * 128 * 128 * 8 + int(ifIndexList[1]) * 4096 * 128 * 128 + int(
                    ifIndexList[2]) * 4096 * 128 + int(ifIndexList[3]) * 4096 + int(ifIndexList[4])

            return ifIndex

        elif len(ifIndexList) == 4:
            ifIndex = int(ifIndexList[0]) * 4096 * 128 * 128 * 8 + int(ifIndexList[1]) * 4096 * 128 * 128 + int(
                ifIndexList[2]) * 4096 * 128 + int(ifIndexList[3]) * 4096

            return ifIndex

        elif len(ifIndexList) == 3:
            ifIndex = int(ifIndexList[0]) * 4096 * 128 * 128 + int(ifIndexList[1]) * 4096 * 128 + int(
                ifIndexList[2]) * 4096
            return ifIndex
    elif ifPrefix in ['lo']:
        ifIndexList = ifNameString.split('-')[1].split('/')
        ifIndex = (int(ifIndexList[0]) + 8) * 4096 * 128 * 128 * 8 + int(ifIndexList[1]) * 4096 * 128 + int(
            ifIndexList[2]) * 4096
        return ifIndex


def stripIfPrefixFromIfName(ifNameString):
    ifIndexList = ifNameString.split('-')[1].split('/')

    if len(ifIndexList) == 5:
        return '/'.join(ifIndexList)

    elif len(ifIndexList) == 4:
        return '/'.join(ifIndexList[1:])

    elif len(ifIndexList) == 3:
        return '/'.join(ifIndexList)
