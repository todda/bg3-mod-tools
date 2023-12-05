import os
import pathlib
import sys
import ctypes
import zlib
import lz4.block
from dataclasses import dataclass

FileSignature = bytes([0x4C, 0x53, 0x50, 0x4B])
ExpectedFileFingerprint = bytes([0]) * 16

@dataclass
class PAKHeader:
    version: ctypes.c_uint32 = 0
    offset: ctypes.c_uint64 = 0
    size: ctypes.c_uint32 = 0
    flags: ctypes.c_byte = 0
    priority: ctypes.c_byte = 0
    fingerprint: [ctypes.c_byte] * 16 = 0
    parts: ctypes.c_uint16 = 0

@dataclass
class FileEntry:
    name = bytes(256)
    offsetInFile1: ctypes.c_uint32 = 0
    offsetInFile2: ctypes.c_uint16 = 0
    archivePart: ctypes.c_byte = 0
    flags: ctypes.c_byte = 0
    sizeOnDisk: ctypes.c_uint32 = 0
    uncompressedSize: ctypes.c_uint32 = 0

def printUsage():
    print('USAGE:\n    bg3-unpak [options] <input.pak>')
    print('    options:')
    print('        print - print out the listing of embedded files')
    print('        extract[number] - extract embedded file data default is all files')
    print('        verbose - print out extra PAK information and operation warnings')

def readHeader(input):
    returnHeader: PAKHeader = PAKHeader()
    returnHeader.version = int.from_bytes(input.read(4), "little")
    returnHeader.offset = int.from_bytes(input.read(8), "little")
    returnHeader.size = int.from_bytes(input.read(4), "little")
    returnHeader.flags = int.from_bytes(input.read(1), "little")
    returnHeader.priority = int.from_bytes(input.read(1), "little")
    returnHeader.fingerprint = input.read(16)
    returnHeader.parts = int.from_bytes(input.read(2), "little")
    return returnHeader

def dumpHeader(header: PAKHeader):
    print('PAK Header')
    print('    version:', header.version)
    print('    offset:', header.offset)
    print('    size:', header.size)
    print('    flags:', header.flags)
    print('    priority:', header.priority)
    print('    fingerprint:', header.fingerprint)
    print('    parts:', header.parts, '\n')

def dumpFileEntry(entry: FileEntry):
    print('File Entry')
    print('    name:', entry.name)
    print('    offset:', entry.offsetInFile1)
    print('    archive:', entry.archivePart)
    print('    flags:', entry.flags)
    print('    sizeOnDisk:', entry.sizeOnDisk)
    print('    uncompressedSize:', entry.uncompressedSize)

def getDecompressedFileObject(input, offset):
    entry = FileEntry()
    entry.name = (input[offset:offset+256].decode("ascii").replace('\x00', ''))
    entry.offsetInFile1 = int.from_bytes(input[offset+256:offset+260], "little")
    entry.offsetInFile2 = int.from_bytes(input[offset+260:offset+262], "little")
    entry.archivePart = input[offset+262]
    entry.flags = input[offset+263]
    entry.sizeOnDisk = int.from_bytes(input[offset+264:offset+268], "little")
    entry.uncompressedSize = int.from_bytes(input[offset+268:offset+272], "little")

    if verbose:
        dumpFileEntry(entry)
    return entry

def parseDecompressedData(input):
    parsedNames = []
    stepSize = (256 + 4 + 2 + 1 + 1 + 4 + 4)

    for i in range(0, len(input), stepSize):
        parsedNames.append(input[i:i+256].decode("ascii").replace('\x00', ''))
    return parsedNames

def decompressData(pakPayload, bufferSize):
    return lz4.block.decompress(pakPayload, uncompressed_size=bufferSize)

def getFileList(input):
    chunkOffset = 0
    nameCount = int.from_bytes(input.read(4), "little")
    pakSize = int.from_bytes(input.read(4), "little")
    bufferSize = (256 + 4 + 2 + 1 + 1 + 4 + 4) * nameCount
    pakPayload = input.read(pakSize)

    # d = lz4.frame.decompress(pakPayload)
    unpakPayload = lz4.block.decompress(pakPayload, uncompressed_size=bufferSize)

    if len(unpakPayload) == bufferSize:
        return unpakPayload
    else:
        print('decompression size not correct: ', len(unpakPayload), bufferSize)

def printPakFiles(inputList):
    print("PAK contents for file", pathlib.Path(fileName).resolve().name, ":")
    for name in inputList:
        print('    ', name)

def extractPakElement(inputFile, pakFileData, index):
        stepSize = (256 + 4 + 2 + 1 + 1 + 4 + 4) * index

        fileObject = getDecompressedFileObject(pakFileData, stepSize)

        newName = pathlib.Path('extracted', fileObject.name)
        newPath = newName.resolve().parent

        try:
            os.makedirs(newPath, exist_ok=True)
            newFile = open(newName, "wb")
        except:
            print('unable to create file', newName)
            return

        offset = ((fileObject.offsetInFile2 << 32) + fileObject.offsetInFile1)
        inputFile.seek(offset)
        compressedBytes = inputFile.read(fileObject.sizeOnDisk)

        print('extracting file', fileObject.name)
        if ((fileObject.flags & 0x0F) == 2):
            decompressedBytesToExtract = decompressData(compressedBytes, fileObject.uncompressedSize)
        elif ((fileObject.flags & 0x0F) == 3):
            print('file is zlib compressed', len(compressedBytes))
            decompressedBytesToExtract = zlib.decompress(compressedBytes, bufsize=fileObject.uncompressedSize)
        else:
            print('file is uncompressed', len(compressedBytes))
            decompressedBytesToExtract = compressedBytes

        sizeWritten = newFile.write(decompressedBytesToExtract)
        if (sizeWritten != len(decompressedBytesToExtract)):
            print('Only wrote ', sizeWritten, ' of ', len(decompressedBytesToExtract), ' for file: ', newName)

        newFile.close


#
### Globals
#

if len(sys.argv) < 3:
    printUsage()
    exit

fileName = sys.argv[1]
verbose = sys.argv.__contains__("verbose")

with open(file=fileName, mode="rb") as inputFile:
    signature = inputFile.read(4)
    if signature != FileSignature:
        print('signature invalid ', signature, FileSignature)
        exit

    version = int.from_bytes(inputFile.read(2), "little")
    if version != 18:
        print('version unsupported ', version)
        exit

    inputFile.seek(4)
    header = readHeader(inputFile)

    if (header.version != 18 or header.size == 0 or header.fingerprint != ExpectedFileFingerprint):
        print('invalid PAK header ', header)
        exit

    if verbose:
        dumpHeader(header)

    inputFile.seek(header.offset)
    pakFileData = getFileList(inputFile)
    pakFileList = parseDecompressedData(pakFileData)

    if sys.argv.__contains__("print"):
        printPakFiles(pakFileList)

    if sys.argv.__contains__("extract"):
        argIndex = sys.argv.index("extract") + 1
        try:
            startIndex = int(sys.argv[argIndex])
            endIndex = int(sys.argv[argIndex]) + 1
        except:
            startIndex = 0
            endIndex = len(pakFileList)

        for n in range(startIndex, endIndex):
            extractPakElement(inputFile, pakFileData, n)


print("completed")