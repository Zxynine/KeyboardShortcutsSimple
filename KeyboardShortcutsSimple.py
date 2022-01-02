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
from .AddinLib.utils import Scripts

import os
from collections import defaultdict

# Import relative path to avoid namespace pollution
from .AddinLib import utils, events, manifest, error, settings, geometry, AppObjects
utils.ReImport_List(AppObjects, events, manifest, error, settings, geometry, utils)


NAME = 'Keyboard Shortcuts Simple'
VERSION = '0.1.3'
FILE_DIR = os.path.dirname(os.path.realpath(__file__))

from .platformDirs import getUserHotkeys,USER_OPTIONS_DIR
from . import KeyCodeUtil


LIST_CMD_ID = 'thomasa88_keyboardShortcutsSimpleList'
UNKNOWN_WORKSPACE = 'UNKNOWN'

app_:adsk.core.Application = None
ui_:adsk.core.UserInterface = None
errorCatcher = error.ErrorCatcher(msgbox_in_debug=False)
eventManager = events.EventsManager(errorCatcher)
list_cmd_def_:adsk.core.CommandDefinition = None
cmd_def_workspaces_map_:'defaultdict[str, set[str]]' = defaultdict(set)
used_workspaces_ids_:set = set()
ws_filter_map_ = None
ns_hotkeys_:'defaultdict[str, list[HotKey]]' = defaultdict(list)

searchFilterInput:adsk.core.StringValueCommandInput = None
workspace_input:adsk.core.DropDownCommandInput = None
only_user_input:adsk.core.BoolValueCommandInput = None
shortcut_sort_input:adsk.core.BoolValueCommandInput = None
list_Box:adsk.core.TextBoxCommandInput = None
copy_input:adsk.core.BoolValueCommandInput = None
ShortcutsGroup:adsk.core.GroupCommandInput = None
InfoGroup:adsk.core.GroupCommandInput = None

longestName = 0

class HotKeyCommand:
	def __init__(self,commandDict:dict):
		global longestName

		self.id=commandDict['command_id']
		self.argument = commandDict['command_argument']
		self.isDefault = commandDict['isDefault']
		
		command = ui_.commandDefinitions.itemById(self.id)
		self.name = (command.name if command else self.id)
		self.name += (f'->{self.argument}' * bool(self.argument))
		self.name += ('**'*(not self.isDefault))
		if len(self.name) > longestName: longestName= len(self.name)



class HotKey:
	def ParseJson(HotKeyJSON:'list[dict]'):
		for h in HotKeyJSON: [HotKey(command, h['hotkey_sequence']) for command in h['commands']]
		

	def __init__(self, commandDict,fusionSeq):
		global ns_hotkeys_,longestName
		self.command = HotKeyCommand(commandDict)

		self.fusion_key_sequence = fusionSeq
		self.FullSequence = fusion_key_to_keyboard_key(fusionSeq)
		self.keySequence, self.BaseKey = self.FullSequence

		self.workspaces = cmd_def_workspaces_map_.get(self.command.id, [UNKNOWN_WORKSPACE])
		[ns_hotkeys_[workspace].append(self) for workspace in self.workspaces]

		self.hid = (self.command.name, self.command.argument)

	def getFormatted(self, HTML=False): 
		formattedString = f'{self.command.name:<{longestName}} :{self.keySequence}'
		return formattedString if not HTML else formattedString.replace('>', '&gt;')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_command_created_handler(args:adsk.core.CommandCreatedEventArgs):
	sorted_workspaces_ = exploreWorkspaces(ui_.workspaces)
	HotKey.ParseJson(filter(lambda h:'commands' in h, getUserHotkeys(USER_OPTIONS_DIR)))

	cmd=args.command
	cmd.isRepeatable = False
	cmd.isExecutedWhenPreEmpted = False
	cmd.isOKButtonVisible = False
	cmd.setDialogMinimumSize(400, 500)
	cmd.setDialogInitialSize(600, 650)

	eventManager.add_handler(cmd.inputChanged, input_changed_handler)
	eventManager.add_handler(cmd.destroy, destroy_handler)


	ListItems=dict( #This is just to make it visually digestible as opposed to how it was
		All=None,
		General= UNKNOWN_WORKSPACE,
		**{'----------------------------------':'SEPARATOR'}, #Cannot use string as argument :/
		**{workspace.name:workspace.id for workspace in sorted_workspaces_})

	inputs = cmd.commandInputs
	global workspace_input, only_user_input, shortcut_sort_input,list_Box,copy_input,ws_filter_map_,searchFilterInput
	global ShortcutsGroup, InfoGroup
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	workspace_input = inputs.addDropDownCommandInput('workspace', 'Workspace', adsk.core.DropDownStyles.LabeledIconDropDownStyle)
	ws_filter_map_ = [name for id,name in ListItems.items() if workspace_input.listItems.add(id, False, '', -1)]
	workspace_input.listItems.item(0).isSelected = True #Selects the first list option

	only_user_input = inputs.addBoolValueInput('only_user', 'Only user-defined          ', True, '', True)
	shortcut_sort_input = inputs.addBoolValueInput('shortcut_sort', 'Sort by shortcut keys', True, '', False)
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	ShortcutsGroup = inputs.addGroupCommandInput('ShortcutsGroup', 'Keyboard Shortcuts')
	ShortcutsGroup.isEnabledCheckBoxDisplayed = False

	searchFilterInput = inputs.addStringValueInput('filter_input', 'Search:', '')
	list_Box = inputs.addTextBoxCommandInput('list', '', get_hotkeys_str(), 30, False)
	list_Box.isReadOnly = True

	InfoGroup = inputs.addGroupCommandInput('InfoGroup', '** = User-defined')
	InfoGroup.isEnabledCheckBoxDisplayed = False
	InfoGroup.isExpanded = False
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	copy_input = inputs.addBoolValueInput('copy', 'Copy', False, f'{utils.get_fusion_deploy_folder()}/Electron/UI/Resources/Icons/Copy')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def input_changed_handler(args:adsk.core.InputChangedEventArgs):
	if args.input.id == 'list': return
	if args.input.id == ShortcutsGroup.id: ShortcutsGroup.isExpanded = True
	if args.input.id == InfoGroup.id: InfoGroup.isExpanded = False
	if args.input.id == 'copy': utils.copy_to_clipboard(get_hotkeys_str(html=False))
	else: list_Box.formattedText = get_hotkeys_str(html=True) # Update list



# HTML table is hard to copy-paste. Use fixed-width font instead.
# Supported HTML in QT: https://doc.qt.io/archives/qt-4.8/richtext-html-subset.html
def get_hotkeys_str(html=True):
	selectedWorkspace = ws_filter_map_[workspace_input.selectedItem.index]
	searchFilter = searchFilterInput.value
	def sortKey(hotkey: HotKey):return hotkey.FullSequence if shortcut_sort_input.value else hotkey.command.name
	def filterFunc(hotkey: HotKey): return not (only_user_input.value and hotkey.command.isDefault)
	def htmlSwitch(trueVal, falseVal):return trueVal if html else falseVal

	newline = htmlSwitch('<br>','\n')
	def header(text, text_underline='-'): return htmlSwitch(f'<b><u>{text}</u></b>',  f'{text}\n{text_underline * len(text)}') + newline

	string = htmlSwitch('<pre>', f"{header('Fusion 360 Keyboard Shortcuts', '=')}\n")
	for workspace_id, hotkeys in ns_hotkeys_.items():
		if selectedWorkspace and workspace_id != selectedWorkspace: continue
		

		filteredHotkeys = sorted(filter(filterFunc, hotkeys), key=sortKey)
		if not filteredHotkeys: continue

		hotkeyStrings = []
		for hotkey in filteredHotkeys: 
			if searchFilter == '' or hotkey.command.name.startswith(searchFilter):
				hotkeyStrings.append(hotkey.getFormatted(html))
		if not hotkeyStrings: continue

		workspace_name = 'General' if workspace_id == UNKNOWN_WORKSPACE else ui_.workspaces.itemById(workspace_id).name
		string += header(workspace_name,"=")
		string += newline.join(hotkeyStrings) + newline*2
		
	return string + htmlSwitch('<pre>', '** = User-defined')




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def exploreCtrls(workspaceID, controls:'list[adsk.core.CommandControl]'): # Needed so it can be recursive
	for control in controls:
		if isinstance(control, adsk.core.DropDownControl):
			exploreCtrls(workspaceID, control.controls)
		elif isinstance(control, adsk.core.CommandControl):
			with utils.Ignore(RuntimeError):
				cmd_id = control.commandDefinition.id
				cmd_def_workspaces_map_[cmd_id].add(workspaceID)
				used_workspaces_ids_.add(workspaceID)

def exploreWorkspaces(workspaces:'list[adsk.core.Workspace]'):
	for workspace in workspaces:
		if CheckProduct(workspace):
			for i in range(workspace.toolbarPanels.count):
				exploreCtrls(workspace.id, workspace.toolbarPanels.item(i).controls)
	return sorted([ui_.workspaces.itemById(w_id) for w_id in used_workspaces_ids_],  key=lambda w: w.name)





#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@errorCatcher # I added functionality to make this into a decorator :3
def run(context):
	global app_, ui_
	app_, ui_ = AppObjects.GetAppUI()
	
	utils.getDelete(ui_.commandDefinitions, LIST_CMD_ID)
	list_cmd_def_:adsk.core.CommandDefinition = ui_.commandDefinitions.addButtonDefinition(LIST_CMD_ID, f'{NAME} {VERSION}', '',)
	eventManager.add_handler(list_cmd_def_.commandCreated, list_command_created_handler)
	list_cmd_def_.execute()
	Scripts.DontTerminate()# Keep the script running.

def destroy_handler(args):
	eventManager.clean_up()
	utils.getDelete(ui_.commandDefinitions, LIST_CMD_ID)
	Scripts.Terminate()# Force the termination of the command.




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def fusion_key_to_keyboard_key(key_sequence:str):
	keys = key_sequence.split('+')
	# Either ord OR the dict access will throw an error
	vk = KeyCodeUtil.GetKeyCode(keys[-1])
	# Make each word capital and replace the end key with the representation
	keys = list(map(str.capitalize,keys[:-1]))+[vk.repr,]
	return '+'.join(keys), vk.repr




def CheckProduct(obj:adsk.core.Workspace):
	#Tying to get its panels can throw an error
	try: return obj.toolbarPanels and (obj.productType != '')
	except: return False
