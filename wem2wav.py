###
#
#   WEM files are uncompressed RIFF payloads. They exist mostly in
#   the localized Voice.pak file. All files have the following format:
#
#     sample rate: 48000 Hz
#     channels: 1
#     channel mask: 0x4 / FC
#     stream total samples: 27389 (0:00.571 seconds)
#     encoding: Opus
#     layout: flat
#     metadata from: Audiokinetic Wwise RIFF header
#     bitrate: 47 kbps
#
#  Conversion is best handled with the vgmstream-cli utility

import os
import sys
import pathlib
import subprocess

fileName = sys.argv[1]
with open(file=fileName, mode="rb") as inputFile:
    newName = pathlib.Path(fileName + '.wav')
    newPath = newName.resolve().parent

    try:
        os.makedirs(newPath, exist_ok=True)
    except:
        print('unable to create file', newName)
        exit(-1)

    print('converting to file', newName)
    subprocess.run(["vgmstream-cli", "-o", newName, fileName])
