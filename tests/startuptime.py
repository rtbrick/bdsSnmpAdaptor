import binascii
import struct
import time

bigEndianFloatStruct = struct.Struct('>f')
littleEndianIntStruct = struct.Struct('<i')
littleEndianShortStruct = struct.Struct('<h')
IFMTU_LAMBDA = lambda x: int(
    littleEndianShortStruct.unpack(binascii.unhexlify(x))[0])
IFSPEED_LAMBDA = lambda x: int(
    round(bigEndianFloatStruct.unpack(binascii.unhexlify(x))[0] / 1000) / 1000000 * 8) * 1000

timeString = "a03d475c642e696e"
x = timeString[:8]
timeString2 = timeString[8:]

print(int(littleEndianIntStruct.unpack(binascii.unhexlify(x))[0]))


# UINT32 - Little Endian (DCBA)
# 5C 47 3D A0	1548172704
# 6E 69 2E 64	1852386916
