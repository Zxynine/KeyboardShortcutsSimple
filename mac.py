#Author-Thomas Axelsson
#Description-Lists all keyboard shortcuts

# This file is part of KeyboardShortcutsSimple, a Fusion 360 add-in for naming
# features directly after creation.
#
# Copyright (C) 2020  Thomas Axelsson
#
# KeyboardShortcutsSimple is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KeyboardShortcutsSimple is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with KeyboardShortcutsSimple.  If not, see <https://www.gnu.org/licenses/>.

# Platform-specific code

import pathlib

import Quartz
from AppKit import NSSystemDefined, NSEvent

# Taken from events.h
# /System/Library/Frameworks/Carbon.framework/Versions/A/Frameworks/HIToolbox.framework/Versions/A/Headers/Events.h
character_translate_table = {
    'a': 0x00,
    's': 0x01,
    'd': 0x02,
    'f': 0x03,
    'h': 0x04,
    'g': 0x05,
    'z': 0x06,
    'x': 0x07,
    'c': 0x08,
    'v': 0x09,
    'b': 0x0b,
    'q': 0x0c,
    'w': 0x0d,
    'e': 0x0e,
    'r': 0x0f,
    'y': 0x10,
    't': 0x11,
    '1': 0x12,
    '2': 0x13,
    '3': 0x14,
    '4': 0x15,
    '6': 0x16,
    '5': 0x17,
    '=': 0x18,
    '9': 0x19,
    '7': 0x1a,
    '-': 0x1b,
    '8': 0x1c,
    '0': 0x1d,
    ']': 0x1e,
    'o': 0x1f,
    'u': 0x20,
    '[': 0x21,
    'i': 0x22,
    'p': 0x23,
    'l': 0x25,
    'j': 0x26,
    '\'': 0x27,
    'k': 0x28,
    ';': 0x29,
    '\\': 0x2a,
    ',': 0x2b,
    '/': 0x2c,
    'n': 0x2d,
    'm': 0x2e,
    '.': 0x2f,
    '`': 0x32,
    ' ': 0x31,
    '\r': 0x24,
    '\t': 0x30,
    '\n': 0x24,
    'return' : 0x24,
    'tab' : 0x30,
    'space' : 0x31,
    'delete' : 0x33,
    'escape' : 0x35,
    'command' : 0x37,
    'shift' : 0x38,
    'capslock' : 0x39,
    'option' : 0x3A,
    'alternate' : 0x3A,
    'control' : 0x3B,
    'rightshift' : 0x3C,
    'rightoption' : 0x3D,
    'rightcontrol' : 0x3E,
    'function' : 0x3F,
    'left' : 0x7B,
    'right' : 0x7C,
    'down' : 0x7D,
    'up' : 0x7E,
}

#inverse of character_translate_table for key code to name lookups
key_code_translate_table = dict((key_code, key_name) for key_name, key_code in character_translate_table.items())

# Taken from ev_keymap.h
# http://www.opensource.apple.com/source/IOHIDFamily/IOHIDFamily-86.1/IOHIDSystem/IOKit/hidsystem/ev_keymap.h
special_key_translate_table = {
    'KEYTYPE_SOUND_UP': 0,
    'KEYTYPE_SOUND_DOWN': 1,
    'KEYTYPE_BRIGHTNESS_UP': 2,
    'KEYTYPE_BRIGHTNESS_DOWN': 3,
    'KEYTYPE_CAPS_LOCK': 4,
    'KEYTYPE_HELP': 5,
    'POWER_KEY': 6,
    'KEYTYPE_MUTE': 7,
    'UP_ARROW_KEY': 8,
    'DOWN_ARROW_KEY': 9,
    'KEYTYPE_NUM_LOCK': 10,
    'KEYTYPE_CONTRAST_UP': 11,
    'KEYTYPE_CONTRAST_DOWN': 12,
    'KEYTYPE_LAUNCH_PANEL': 13,
    'KEYTYPE_EJECT': 14,
    'KEYTYPE_VIDMIRROR': 15,
    'KEYTYPE_PLAY': 16,
    'KEYTYPE_NEXT': 17,
    'KEYTYPE_PREVIOUS': 18,
    'KEYTYPE_FAST': 19,
    'KEYTYPE_REWIND': 20,
    'KEYTYPE_ILLUMINATION_UP': 21,
    'KEYTYPE_ILLUMINATION_DOWN': 22,
    'KEYTYPE_ILLUMINATION_TOGGLE': 23
}





#Each platform should assign, where applicable/possible, the bit masks for
#modifier keys initially set to 0 here. Not all modifiers are recommended
#for cross-platform use
modifier_bits = {	
	'Shift': 1,
	'Lock': 2,
	'Control': 4,
	'Mod1': 8,  # X11 dynamic assignment
	'Mod2': 16,  # X11 dynamic assignment
	'Mod3': 32,  # X11 dynamic assignment
	'Mod4': 64,  # X11 dynamic assignment
	'Mod5': 128,  # X11 dynamic assignment
	'Alt': 0,
	'Caps_Lock': 0,
	'Command': 0,  # Mac key without generic equivalent
	'Num_Lock': 0,
	'Super': 0,  # X11 key, sometimes equivalent to Windows
	'Windows': 0}  # Windows key, sometimes equivalent to Super












def fusion_key_to_keyboard_key(key_sequence):
    # TODO
    keys = key_sequence.split('+')
    return key_sequence, keys[-1]

def find_options_file(app):
    # Seems that Macs can have the files in different locations:
    # https://forums.autodesk.com/t5/fusion-360-support/cannot-find-fuision360-documents-locally-in-macos/td-p/8324149

    # * /Users/<username>/Library/Application Support/Autodesk
    # * /Users/<username>/Library/Containers/com.autodesk.mas.fusion360/Data/Library/Application Support/Autodesk
    # append: /Neutron Platform/Options/<user id>\<file.xml>
    # Idea: If neededn, check where our add-in is running to determine which path to use.

    autodesk_paths = [
        pathlib.Path.home() / 'Library/Application Support/Autodesk',
        pathlib.Path.home() / 'Library/Containers/com.autodesk.mas.fusion360/Data/Library/Application Support/Autodesk'
    ]

    for autodesk_path in autodesk_paths:
        if autodesk_path.exists(): break
    else: raise Exception("Could not find Autodesk directory")

    options_path = autodesk_path / 'Neutron Platform' / 'Options' / app.userId / 'NGlobalOptions.xml'
    return options_path
