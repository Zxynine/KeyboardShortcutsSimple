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

import adsk.core, adsk.fusion, adsk.cam

import os
from tkinter import Tk
from collections import defaultdict

# Import relative path to avoid namespace pollution
from .AddinLib import utils, events, manifest, error, settings, geometry, AppObjects
utils.ReImport_List(AppObjects, events, manifest, error, settings, geometry, utils)


NAME = 'Keyboard Shortcuts Simple'
VERSION = '0.1.3'
FILE_DIR = os.path.dirname(os.path.realpath(__file__))

# if os.name == 'nt': from . import windows as platform
# else: from . import mac as platform
from .platformDirs import getUserHotkeys,USER_OPTIONS_DIR
from . import KeyCodeUtil


LIST_CMD_ID = 'thomasa88_keyboardShortcutsSimpleList'
UNKNOWN_WORKSPACE = 'UNKNOWN'

app_:adsk.core.Application = None
ui_:adsk.core.UserInterface = None
error_catcher_ = error.ErrorCatcher(msgbox_in_debug=False)
events_manager_ = events.EventsManager(error_catcher_)
list_cmd_def_:adsk.core.CommandDefinition = None
cmd_def_workspaces_map_:'defaultdict[str, set[str]]' = defaultdict(set)
used_workspaces_ids_:set = set()
ws_filter_map_ = None
ns_hotkeys_:'defaultdict[str, list[HotKey]]' = defaultdict(list)


workspace_input:adsk.core.DropDownCommandInput = None
only_user_input:adsk.core.BoolValueCommandInput = None
shortcut_sort_input:adsk.core.BoolValueCommandInput = None
list_Box:adsk.core.TextBoxCommandInput = None
copy_input:adsk.core.BoolValueCommandInput = None

longestName = 0

# class HotKey:
# 	def __init__(self, hotkeyDict, fusionSeq):
# 		global ns_hotkeys_,longestName

# 		keySeq,baseKey = fusion_key_to_keyboard_key(fusionSeq)

# 		self.command_id = hotkeyDict['command_id']
# 		self.command_argument = hotkeyDict['command_argument']
# 		self.is_default = hotkeyDict['isDefault']
# 		self.fusion_key_sequence = fusionSeq
# 		self.keyboard_key_sequence = keySeq
# 		self.keyboard_base_key = baseKey
		
# 		command = ui_.commandDefinitions.itemById(self.command_id)
# 		self.command_name = (command.name if command else self.command_id)
# 		self.command_name += (f'->{self.command_argument}' * bool(self.command_argument))
# 		self.command_name += ('*'*(not self.is_default))
# 		if len(self.command_name) > longestName: longestName= len(self.command_name)


# 		self.workspaces = cmd_def_workspaces_map_.get(self.command_id, [UNKNOWN_WORKSPACE])
# 		[ns_hotkeys_[workspace].append(self) for workspace in self.workspaces]

# 		self.hid = (self.command_name, self.command_argument)

# 	def getFormatted(self, HTML=False): 
# 		formattedString = f'{self.command_name:<{longestName}} :{self.keyboard_key_sequence}'
# 		return formattedString if not HTML else formattedString.replace('>', '&gt;')
# 	def shouldDisplay(self): return not (only_user_input.value and self.is_default)
# 	def sortKey(self):return (self.keyboard_base_key, self.keyboard_key_sequence) if shortcut_sort_input.value else self.command_name
# 	@staticmethod
# 	def filterSort(hotkeys:'list[HotKey]'):
# 		filtered = {hotkey.hid:hotkey for hotkey in hotkeys if hotkey.shouldDisplay()}
# 		return sorted(list(filtered.values()), key=HotKey.sortKey)



class HotKey:
	def FromJsonObj(hotkeyObj):
		[HotKey(command, hotkeyObj['hotkey_sequence']) for command in hotkeyObj['commands']]

	def __init__(self, hotkeyDict,fusionSeq):
		global ns_hotkeys_,longestName

		keySeq,baseKey = fusion_key_to_keyboard_key(fusionSeq)

		self.command_id = hotkeyDict['command_id']
		self.command_argument = hotkeyDict['command_argument']
		self.is_default = hotkeyDict['isDefault']
		self.fusion_key_sequence = fusionSeq
		self.keyboard_key_sequence = keySeq
		self.keyboard_base_key = baseKey
		
		command = ui_.commandDefinitions.itemById(self.command_id)
		self.command_name = (command.name if command else self.command_id)
		self.command_name += (f'->{self.command_argument}' * bool(self.command_argument))
		self.command_name += ('*'*(not self.is_default))
		if len(self.command_name) > longestName: longestName= len(self.command_name)


		self.workspaces = cmd_def_workspaces_map_.get(self.command_id, [UNKNOWN_WORKSPACE])
		[ns_hotkeys_[workspace].append(self) for workspace in self.workspaces]

		self.hid = (self.command_name, self.command_argument)

	def getFormatted(self, HTML=False): 
		formattedString = f'{self.command_name:<{longestName}} :{self.keyboard_key_sequence}'
		return formattedString if not HTML else formattedString.replace('>', '&gt;')
	def shouldDisplay(self): return not (only_user_input.value and self.is_default)
	def sortKey(self):return (self.keyboard_base_key, self.keyboard_key_sequence) if shortcut_sort_input.value else self.command_name
	@staticmethod
	def filterSort(hotkeys:'list[HotKey]'):
		filtered = {hotkey.hid:hotkey for hotkey in hotkeys if hotkey.shouldDisplay()}
		return sorted(list(filtered.values()), key=HotKey.sortKey)






#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_command_created_handler(args:adsk.core.CommandCreatedEventArgs):
	explore_workspaces(ui_.workspaces)
	sorted_workspaces_ = sorted([ui_.workspaces.itemById(w_id) for w_id in used_workspaces_ids_],  key=lambda w: w.name)

	[HotKey.FromJsonObj(h) for h in getUserHotkeys(USER_OPTIONS_DIR) if 'hotkey_sequence' in h]

	cmd=args.command
	cmd.isRepeatable = False
	cmd.isExecutedWhenPreEmpted = False
	cmd.isOKButtonVisible = False
	cmd.setDialogMinimumSize(350, 200)
	cmd.setDialogInitialSize(400, 500)

	events_manager_.add_handler(cmd.inputChanged, input_changed_handler)
	events_manager_.add_handler(cmd.destroy, destroy_handler)

	inputs = cmd.commandInputs
	global workspace_input, only_user_input, shortcut_sort_input,list_Box,copy_input,ws_filter_map_
	workspace_input = inputs.addDropDownCommandInput('workspace', 'Workspace', adsk.core.DropDownStyles.LabeledIconDropDownStyle)

	ws_filter_map_ = []
	workspace_input.listItems.add('All', True, '', -1)
	ws_filter_map_.append(None)
	workspace_input.listItems.add('----------------------------------', False, '', -1)
	ws_filter_map_.append('SEPARATOR')
	workspace_input.listItems.add('General', False, '', -1)
	ws_filter_map_.append(UNKNOWN_WORKSPACE)
	for workspace in sorted_workspaces_:
		workspace_input.listItems.add(workspace.name, False, '', -1)
		ws_filter_map_.append(workspace.id)
	
	only_user_input = inputs.addBoolValueInput('only_user', 'Only user-defined          ', True, '', True)
	shortcut_sort_input = inputs.addBoolValueInput('shortcut_sort', 'Sort by shortcut keys', True, '', False)

	list_Box = inputs.addTextBoxCommandInput('list', '', get_hotkeys_str(), 30, False)
	list_Box.isReadOnly = True
	inputs.addTextBoxCommandInput('list_info', '', '* = User-defined', 1, True)

	copy_input = inputs.addBoolValueInput('copy', 'Copy', False, f'{utils.get_fusion_deploy_folder()}/Electron/UI/Resources/Icons/Copy')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def input_changed_handler(args:adsk.core.InputChangedEventArgs):
	if args.input.id == 'list': return
	workspace_filter = ws_filter_map_[workspace_input.selectedItem.index]
	isCopy = args.input.id == 'copy'
	if isCopy: copy_to_clipboard(get_hotkeys_str(workspace_filter, html=False))
	else: list_Box.formattedText = get_hotkeys_str(workspace_filter, html=True) # Update list


def get_hotkeys_str(workspace_filter=None, html=True):
	# HTML table is hard to copy-paste. Use fixed-width font instead.
	# Supported HTML in QT: https://doc.qt.io/archives/qt-4.8/richtext-html-subset.html
	def htmlSwitch(trueVal, falseVal):return trueVal if html else falseVal
	newline = htmlSwitch('<br>','\n')
	def header(text, text_underline='-'): return htmlSwitch(f'<b>{text}</b>',  f'{text}\n{text_underline * len(text)}') + newline

	string = htmlSwitch('<pre>', f"{header('Fusion 360 Keyboard Shortcuts', '=')}\n")
	for workspace_id, hotkeys in ns_hotkeys_.items():
		# Make sure to filter before any de-dup operation
		if workspace_filter and workspace_id != workspace_filter: continue

		filteredHotkeys = HotKey.filterSort(hotkeys)
		if not filteredHotkeys: continue

		workspace_name = 'General' if workspace_id == UNKNOWN_WORKSPACE else ui_.workspaces.itemById(workspace_id).name
		string += header(workspace_name,"=")
		
		for hotkey in filteredHotkeys: string += hotkey.getFormatted(html) + newline
		string += newline
	return string + htmlSwitch('<pre>', '* = User-defined')


def explore_workspaces(workspaces:'list[adsk.core.Workspace]'):
	global used_workspaces_ids_
	for workspace in workspaces:
		if CheckProduct(workspace):
			def exploreCtrls(controls:'list[adsk.core.CommandControl]'):
				for control in controls:
					if isinstance(control, adsk.core.DropDownControl):
						exploreCtrls(control.controls)
					elif isinstance(control, adsk.core.CommandControl):
						try: cmd_id = control.commandDefinition.id
						except RuntimeError as e: continue
						cmd_def_workspaces_map_[cmd_id].add(workspace.id)
						used_workspaces_ids_.add(workspace.id)
			panels:'list[adsk.core.ToolbarPanel]'= workspace.toolbarPanels
			for panel in panels: exploreCtrls(panel.controls)







#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def run(context):
	global app_, ui_
	global list_cmd_def_
	with error_catcher_:
		app_, ui_ = AppObjects.GetAppUI()
		if ui_.activeCommand == LIST_CMD_ID: ui_.terminateActiveCommand()
		utils.getDelete(ui_.commandDefinitions, LIST_CMD_ID)
		list_cmd_def_ = ui_.commandDefinitions.addButtonDefinition(LIST_CMD_ID, f'{NAME} {VERSION}', '',)
		events_manager_.add_handler(list_cmd_def_.commandCreated, list_command_created_handler)
		list_cmd_def_.execute()
		adsk.autoTerminate(False)	# Keep the script running.

def destroy_handler(args):	# Force the termination of the command.
	adsk.terminate()
	events_manager_.clean_up()





# Move data extraction to separate function?
# E.g. ! is used for shift+1, so we need to pull out the virtual keycode,
# to get the actual key that the user needs to press. (E.g. '=' is placed
# on different keys on different keyboards and some use shift.)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def fusion_key_to_keyboard_key(key_sequence:str):
	keys = key_sequence.split('+')
	# Application.cast(Application.get()).userInterface.messageBox(str(keys))
	try: vk = KeyCodeUtil.nameToKeyMap[keys[-1].lower()]
	except: 
		try: vk = KeyCodeUtil.valueToKeyMap[ord(keys[-1])]
		except:	
			try: vk = KeyCodeUtil.alternateMappings[keys[-1]]
			except:
				ui_.messageBox(str(ord(keys[-1])))
				return '+'.join(keys), keys[-1]

	keys[-1] = vk.name
	return '+'.join(keys), vk.name


def copy_to_clipboard(string):
	copy_input.value = False
	# From https://stackoverflow.com/a/25476462/106019
	r = Tk()
	r.withdraw()
	r.clipboard_clear()
	r.clipboard_append(string)
	r.update() # now it stays on the clipboard after the window is closed
	r.destroy()



def CheckProduct(obj:adsk.core.Workspace):
	#Tying to get its panels can throw an error
	try: return obj.toolbarPanels and (obj.productType != '')
	except: return False
