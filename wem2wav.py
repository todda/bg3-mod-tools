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
#   Localization/English/Soundbanks/vcb3b1e87b8a943e5ae99b698dba67c25_hffce03afg32a0g40f2gb806gcf916df48203.wem
#
#   WEM Files are named by <actor>_<localization_xml_contentuid>.wem
#
#   Actor id's are:
#       vNARRATOR - Main Narrator
#       vc774d7644a1748dcb47032ace9ce447d - Wyll
#       v7628bc0e52b842a7856a13a6fd413323 - Halsin
#       v3ed74f063c6042dc83f6f034cb47c679 - Shadowheart
#       v0de603c542e248119dadf652de080eba - Minsc
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
