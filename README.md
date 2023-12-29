# bg3-mod-tools
***
Various scripts and utilities for working with game assets for Baldurs Gate 3

Using Norbytes previous work in https://github.com/Norbyte/lslib as reference, I've created a few very simple python scripts to work specifically with the BG3 assets.

The main desire was to have native-ish tools/scripts running on MacOS, because that's my developer environment.  I had 2 options:

1.  Convert Norbyte's C# project over to mono
2.  Just convert it to a script

I've never been a fan of IDE build projects, so I went the second route.

## Requirements
***
LZ4 Compression Support<br>
    `pip3 install lz4`

Audio Conversion<br>
    `brew install vgmstream`

## Installation
todo

## Example usage
print out all the files contained in the Voice.pak:<br>
    `python3 unpak.py ~/Library/Application\ Support/Steam/steamapps/common/Baldurs\ Gate\ 3/Baldur\'s\ Gate\ 3.app/Contents/Data/Localization/Voice.pak print`<br>

extract the first ten localized audio tracks:<br>
    `python3 unpak.py ~/Library/Application\ Support/Steam/steamapps/common/Baldurs\ Gate\ 3/Baldur\'s\ Gate\ 3.app/Contents/Data/Localization/Voice.pak extract 0:10`<br>

convert an audio file to WAV format:<br>
    `python3 wem2wav.py extracted/Mods/Gustav/Localization/English/Soundbanks/v7628bc0e52b842a7856a13a6fd413323_hd485718agde2dg4cb5g934fg368d69db1da8.wem`<br>

