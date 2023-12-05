###
#
#   LOCA files are localization files.  After they are unpacked/decompressed
#   from a language .PAK file, they exist in the following format:
#
#   +------------------+
#   |[signature]
#   |[number of entries]
#   |[address string table]
#   |[fixed element data]
#   |[fixed element data]
#  . . .# entries long . . .
#   |[fixed element data]
#   |[utf-8 string data]
#   |[utf-8 string data]
#  . . .# entries long . . .
#   |[utf-8 string data]
#   | EOF
#   +------------------+
#
#   Where:
#   signature is 4 bytes [0x4C, 0x4F, 0x43, 0x41]
#   element struct is
#       64-byte string, null padded
#       UInt16 version number (although older versions seem pruned), and
#       UInt32 size of the string data
#
#   XML/HTML seems to be the original format, as you sometimes see embedded:
#       <LSTag Tooltip=...>
#       <i>
#       <b>
#       <br>
#
###

import os
import pathlib
import sys
import ctypes
from dataclasses import dataclass

FileSignature = bytes([0x4C, 0x4F, 0x43, 0x41]) # 'LOCA'
XMLPreamble = '<?xml version="1.0" encoding="UTF-8"?>'
verbose = True

@dataclass
class LocaleHeader:
    signature: ctypes.c_uint32 = 0
    entries: ctypes.c_uint32 = 0
    textOffset: ctypes.c_uint32 = 0

@dataclass
class LocaleEntry:
    key = bytes(64)
    version: ctypes.c_uint16 = 0
    length: ctypes.c_uint32 = 0

def readHeader(input):
    returnHeader: LocaleHeader = LocaleHeader()
    returnHeader.signature = input.read(4)
    returnHeader.entries = int.from_bytes(input.read(4), "little")
    returnHeader.textOffset = int.from_bytes(input.read(4), "little")
    return returnHeader

def readEntry(input, header: LocaleHeader, index):
    returnEntry: LocaleEntry = LocaleEntry()
    accumulatedOffset = 0

    for currentEntry in range(0, index+1):
        input.seek((currentEntry*(64+2+4)) + 12)
        returnEntry.key = input.read(64)
        returnEntry.version = int.from_bytes(input.read(2), "little")
        returnEntry.length = int.from_bytes(input.read(4), "little")
        if currentEntry < index:
            accumulatedOffset += returnEntry.length

    input.seek(header.textOffset + accumulatedOffset)
    if verbose:
        print(f'<content contentuid="{returnEntry.key.decode("UTF-8")}" version="{returnEntry.version}">{input.read(returnEntry.length).decode("UTF-8")}</content>')

    return returnEntry

fileName = sys.argv[1]
with open(file=fileName, mode="rb") as inputFile:
    header = readHeader(inputFile)

    if header.signature != FileSignature:
        print('signature invalid ', header.signature, FileSignature)
        exit

    print('found', header.entries, 'entries')

    print('<contentList>')
    for entryNumber in range(0, header.entries):
        readEntry(inputFile, header, entryNumber)
    print('</contentList>')

print('completed')