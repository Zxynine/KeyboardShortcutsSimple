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
from .AddinLib.CommandInputs import CommandInputs
from .AddinLib import KeyCodeUtil, platformDirs as platform

import os
from collections import defaultdict

# Import relative path to avoid namespace pollution
from .AddinLib import utils, events, manifest, error, settings, geometry, AppObjects
utils.ReImport_List(AppObjects, events, manifest, error, settings, geometry, utils)


NAME = 'Keyboard Shortcuts Simple'
VERSION = '0.1.3'
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
LIST_CMD_ID = 'thomasa88_keyboardShortcutsSimpleList'

errorCatcher = error.ErrorCatcher(msgbox_in_debug=False)
eventManager = events.EventsManager(errorCatcher)
UNKNOWN_WORKSPACE = 'UNKNOWN'

app_:adsk.core.Application = None
ui_:adsk.core.UserInterface = None
ws_filter_map_:list = None
list_cmd_def_:adsk.core.CommandDefinition = None
ns_hotkeys_:'defaultdict[str, list[HotKey]]' = defaultdict(list)
cmdToWorkspaces:'defaultdict[str, set[str]]' = defaultdict(set)

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
		self.FullSequence = KeyCodeUtil.GetSequenceRepr(fusionSeq)
		self.keySequence, self.BaseKey = self.FullSequence

		self.workspaces = cmdToWorkspaces.get(self.command.id, [UNKNOWN_WORKSPACE])
		[ns_hotkeys_[workspace].append(self) for workspace in self.workspaces]

	def getFormatted(self, HTML=False): 
		name,seqence = f'{self.command.name:<{longestName}}', self.keySequence
		if HTML: name,seqence = utils.toHtml(name), f'<b>{utils.toHtml(seqence)}</b>' 
		return f'{name} : {seqence}'

	def inSearch(self, searchStr:str): 
		if not searchStr: return True
		if shortcut_sort_input.value: return searchStr.lower() in self.keySequence.lower()
		else: return self.command.name.lower().startswith(searchStr.lower())

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def list_command_created_handler(args:adsk.core.CommandCreatedEventArgs):
	sorted_workspaces_ = exploreWorkspaces(ui_.workspaces)
	HotKey.ParseJson(filter(lambda h:'commands' in h, platform.getUserHotkeys()))

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

	inputs = CommandInputs(cmd.commandInputs)
	global workspace_input, only_user_input, shortcut_sort_input,list_Box,copy_input,ws_filter_map_,searchFilterInput
	global ShortcutsGroup, InfoGroup
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	workspace_input = inputs.addRadioButtonDropDownInput('workspace', 'Workspace', *ListItems.keys())
	ws_filter_map_ = list(ListItems.values())

	only_user_input = inputs.addCheckboxInput('only_user', 'Only user-defined', True)
	shortcut_sort_input = inputs.addCheckboxInput('shortcut_sort', 'Sort by shortcut keys', False)
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	ShortcutsGroup = inputs.addVisualDividerInput('ShortcutsGroup', 'Keyboard Shortcuts',True)

	searchFilterInput = inputs.addStringValueInput('filter_input', 'Search:', '')

	list_Box = inputs.addTextBoxCommandInput('list', '', get_hotkeys_str(), 30, True)

	InfoGroup = inputs.addVisualDividerInput('InfoGroup', '** = User-defined')
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	copy_input = inputs.addButtonInput('copy', 'Copy', utils.GetCommandIcon('Electron::Copy'))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def input_changed_handler(args:adsk.core.InputChangedEventArgs):
	if args.input.id == 'list': return
	if args.input.id == ShortcutsGroup.id: ShortcutsGroup.isExpanded = True
	if args.input.id == InfoGroup.id: InfoGroup.isExpanded = False
	if args.input.id == 'copy': utils.copy_to_clipboard(get_hotkeys_str(html=False), True)
	else: list_Box.formattedText = get_hotkeys_str(html=True) # Update list



# HTML table is hard to copy-paste. Use fixed-width font instead.
# Supported HTML in QT: https://doc.qt.io/archives/qt-4.8/richtext-html-subset.html
def get_hotkeys_str(html=True):
	selectedWorkspace = ws_filter_map_[workspace_input.selectedItem.index]
	searchFilter = searchFilterInput.value
	def sortKey(hotkey: HotKey):return hotkey.FullSequence if shortcut_sort_input.value else hotkey.command.name
	def filterFunc(hotkey: HotKey): return not (only_user_input.value and hotkey.command.isDefault)

	newline = ('<br>' if html else '\n')
	def header(text, underlineChar='-'): return (f'<b><u>{text}</u></b>' if html else f'{text}\n{underlineChar*len(text)}') + newline
	start,end = (('<pre>','<pre>') if html else (f"{header('Fusion 360 Keyboard Shortcuts', '=')}\n", '** = User-defined'))

	string = start
	for workspace_id, hotkeys in ns_hotkeys_.items():
		if selectedWorkspace and workspace_id != selectedWorkspace: continue
		
		filteredHotkeys = sorted(filter(filterFunc, hotkeys), key=sortKey)
		if not filteredHotkeys: continue

		hotkeyStrings = [hotkey.getFormatted(html) for hotkey in filteredHotkeys if hotkey.inSearch(searchFilter)]
		if not hotkeyStrings: continue

		workspace_name = 'General' if workspace_id == UNKNOWN_WORKSPACE else ui_.workspaces.itemById(workspace_id).name
		string += header(workspace_name,"=") + newline.join(hotkeyStrings) + newline*2
	return string + end




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




def exploreWorkspaces(workspaces:'list[adsk.core.Workspace]'):
	uniqueWorkspaces = set()
	for workspace in workspaces:
		if utils.CheckWorkspace(workspace):
			for i in range(workspace.toolbarPanels.count):
				def exploreCtrls(workspaceID, controls:'list[adsk.core.CommandControl]'): # Needed so it can be recursive
					for control in controls:
						if isinstance(control, adsk.core.DropDownControl):
							exploreCtrls(workspaceID, control.controls)
						elif isinstance(control, adsk.core.CommandControl):
							with utils.Ignore(RuntimeError): #Getting the command def can throw errors
								cmdToWorkspaces[control.commandDefinition.id].add(workspaceID)
								
				exploreCtrls(workspace.id, workspace.toolbarPanels.item(i).controls)
			uniqueWorkspaces.add(workspace.id)
	return sorted(filter(None, map(ui_.workspaces.itemById, uniqueWorkspaces)),  key=lambda w:w.name)




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
