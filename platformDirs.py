# import adsk.core, adsk.fusion, adsk.cam
import os,json
import platform as osInfo
import subprocess
import tempfile
from pathlib import Path



# def StringInstantiator(count): return ['']*count
# (USER_DIR, DESKTOP_DIR, TEMP_DIR, APPDATA_DIR, LOCAL_APPDATA_DIR, 
# USERDATA_DIR, USERDATA_DIR, PYTHON_DIR, 
# AUTODESK_DIR, AUTODESK_LOCAL_DIR, API_PYTHON_DIR, 
# FUSION_DIR, FUSION_CPP_DIR, FUSION_PYTHON_DIR, FUSION_RES_DIR, 
# PLUGINS_DIR, SCRIPTS_DIR, ADDINS_DIR,NEUTRON_OPTIONS) = StringInstantiator(19)





def getOS() -> str:
	osMap = dict( 	Windows='Windows',	win32='Windows',
					Darwin='Darwin',	Linux='Linux')
	osName = osMap.get(osInfo.system(), None)
	if osName is not None: return osName
	raise OSError(2, "Operating System Not Supported", f"{osInfo.system()}")
_osType = getOS()
iswindows = (_osType == 'Windows')


def PathExists(path, *args): return path is not '' and os.path.exists(os.path.join(path, *args))

def GetPath(fileDir, fileName):
	if not os.path.exists(fileDir): os.makedirs(fileDir)
	return os.path.join(fileDir, fileName)











USER_DIR=DESKTOP_DIR=TEMP_DIR=APPDATA_DIR=''
AUTODESK_DIR=PLUGINS_DIR=SCRIPTS_DIR=ADDINS_DIR=''
NEUTRON_OPTIONS=USER_OPTIONS_DIR=''




from xml.etree import ElementTree as XMLTree
def getUserID(neutronPath):
	optionsFile = os.path.join(neutronPath,'NMachineSpecificOptions.xml')
	return XMLTree.parse(optionsFile).getroot().find('./NetworkOptionGroup/LastUserOptionId').attrib['Value']

def getUserHotkeys(userOptionsPath)->'list[dict["commands":list,"hotkey_sequence":"A+B+C", "isDefault":bool]]':#command_argument
	optionsFile = os.path.join(userOptionsPath,'NGlobalOptions.xml')
	return json.loads(XMLTree.parse(optionsFile).getroot().find('./HotKeyGroup/HotKeyJSONString').attrib['Value'])['hotkeys']


def join(*args): 
	newPath = os.path.join(*args)
	if PathExists(newPath):return newPath

USER_DIR=			os.path.expanduser('~')
DESKTOP_DIR=		join(USER_DIR,'Desktop')
APPDATA_DIR=		join(os.getenv('APPDATA'))	if iswindows else	join(USER_DIR,'Library','Application Support')
TEMP_DIR=			os.getenv('TMP') 			if iswindows else 	"/tmp" if _osType== "Darwin" else tempfile.gettempdir()

AUTODESK_DIR=		join(APPDATA_DIR,'Autodesk')
PLUGINS_DIR=		join(AUTODESK_DIR,'ApplicationPlugins')
SCRIPTS_DIR= 		join(AUTODESK_DIR,'Autodesk Fusion 360','API','Scripts')
ADDINS_DIR= 		join(AUTODESK_DIR,'Autodesk Fusion 360','API','AddIns')

NEUTRON_OPTIONS=	join(AUTODESK_DIR,'Neutron Platform','Options')
USER_OPTIONS_DIR=	join(NEUTRON_OPTIONS,getUserID(NEUTRON_OPTIONS))






def OpenFile(path):
	if iswindows: os.startfile(path)
	else: subprocess.check_call(["open", "--", path])





if __name__ == '__main__':
	print(	USER_DIR,DESKTOP_DIR,APPDATA_DIR,TEMP_DIR, '\n',
			AUTODESK_DIR,PLUGINS_DIR,SCRIPTS_DIR,ADDINS_DIR,'\n',
			NEUTRON_OPTIONS,USER_OPTIONS_DIR,'\n', sep='\n')
# getUserHotkeys(USER_OPTIONS_DIR)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# thisAddinPath = os.path.dirname(os.path.realpath(__file__))


# Mac: /Users/xxx/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns
# windows: C:\Users\xxx\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns


# def GetTempDir():		return os.getenv('TMP') 		if iswindows else 	"/tmp" if _osType== "Darwin" else tempfile.gettempdir()

# def getDefaultControls(addinName):
# 	global 	USER_DIR, DESKTOP_DIR, TEMP_DIR, APPDATA_DIR, LOCAL_APPDATA_DIR
# 	global 	USERDATA_DIR, USERDATA_DIR, PYTHON_DIR
# 	global 	AUTODESK_DIR, AUTODESK_LOCAL_DIR, FUSION_DIR
# 	global 	FUSION_CPP_DIR, FUSION_PYTHON_DIR, API_PYTHON_DIR, FUSION_RES_DIR
# 	global 	PLUGINS_DIR, SCRIPTS_DIR, ADDINS_DIR

# 	def join(*args): os.path.join(*args)
# 	USER_DIR=		os.path.expanduser('~')				if iswindows else	os.path.expanduser('~')
# 	TEMP_DIR=		GetTempDir()						if iswindows else	GetTempDir()
# 	DESKTOP_DIR=	join(USER_DIR,'Desktop')			if iswindows else	join(USER_DIR,'Desktop')
# 	APPDATA_DIR=	join(os.getenv('APPDATA'))			if iswindows else	join(USER_DIR,'Library','Application Support')

# 	AUTODESK_DIR=	join(APPDATA_DIR,'Autodesk')		if iswindows else	join(APPDATA_DIR,'Autodesk')
# 	PYTHON_DIR=		Path(os.__file__).parents[1]		if iswindows else	Path(os.__file__).parents[2] / "bin"

# 	PLUGINS_DIR=	join(AUTODESK_DIR,'ApplicationPlugins')						if iswindows else	join(AUTODESK_DIR,'ApplicationPlugins')
# 	SCRIPTS_DIR= 	join(AUTODESK_DIR,'Autodesk Fusion 360','API','Scripts')	if iswindows else 	join(AUTODESK_DIR,'Autodesk Fusion 360','API','Scripts')
# 	ADDINS_DIR= 	join(AUTODESK_DIR,'Autodesk Fusion 360','API','AddIns')		if iswindows else 	join(AUTODESK_DIR,'Autodesk Fusion 360','API','AddIns')





# 	FUSION_DIR=			fusion_install_dir(AUTODESK_DIR)					if iswindows else	fusion_install_dir(AUTODESK_DIR)
# 	FUSION_RES_DIR=		get_fusion_ui_resource_folder()						if iswindows else	get_fusion_ui_resource_folder()
# 	FUSION_CPP_DIR=		join(FUSION_DIR,'CPP')								if iswindows else	join(FUSION_DIR,'Libraries','Neutron','CPP')
# 	FUSION_PYTHON_DIR=	join(FUSION_DIR,'Python')							if iswindows else	join(FUSION_DIR,'Frameworks','Python.framework','Versions')
# 	API_PYTHON_DIR=		join(FUSION_DIR,'Api','Python')						if iswindows else	join(FUSION_DIR,'Api','Python')


# PYTHON_DIR=		Path(os.__file__).parents[1]		if iswindows else	Path(os.__file__).parents[2] / "bin"



# Strip the suffix from the UI resource folder, i.e.:
# Windows: /Fusion/UI/FusionUI/Resources
# Mac: /Autodesk Fusion 360.app/Contents/Libraries/Applications/Fusion/Fusion/UI/FusionUI/
# NOTE! The structure within the deploy folder is not the same on Windows and Mac!
# 	E.g. see the examples for get_fusion_ui_resource_folder(). 
# def fusion_install_dir(autodeskDir):
# 	def join(*args): os.path.join(*args)
# 	if iswindows:
# 		fusionAppPath = join(AUTODESK_LOCAL_DIR, 'webdeploy', 'production')
# 		return max([join(fusionAppPath,d) for d in os.listdir(fusionAppPath)], key=os.path.getctime)
# 	else: 
# 		fusionAppPath = os.path.realpath(join(AUTODESK_LOCAL_DIR, 'webdeploy', 'production', 'Autodesk Fusion 360.app'))
# 		return join(fusionAppPath, 'Contents')


# def get_fusion_deploy_folder():
# 	''' Get the Fusion 360 deploy folder.
# 	### Typically:
# 	* Windows: C:/Users/<user>/AppData/Local/Autodesk/webdeploy/production/<userhash>
# 	* Mac: /Users/<user>/Library/Application Support/Autodesk/webdeploy/production/<userhash> '''
# 	_DEPLOY_FOLDER_PATTERN = re.compile(r'.*/webdeploy/production/[^/]+')
# 	return _DEPLOY_FOLDER_PATTERN.match(get_fusion_ui_resource_folder()).group(0)

# def get_fusion_clean_config():
# 	#C:\Users\<user>\AppData\Local\Autodesk\webdeploy\production\4c84784f9b312b4c6ccb78d46529ebb70d7a5a09\resources
# 	deployFolder = get_fusion_deploy_folder()
# 	os.path.join(deployFolder, 'resources', 'clean_config.json')

# def get_fusion_ui_resource_folder():
# 	'''Get the Fusion UI resource folder. Note: Not all resources reside here.
# 	### Typically:
# 	* Windows: C:/Users/<user>/AppData/Local/Autodesk/webdeploy/production/<hash>/Fusion/UI/FusionUI/Resources
# 	* Mac: /Users/<user>/Library/Application Support/Autodesk/webdeploy/production/<hash>/Autodesk Fusion 360.app/Contents/Libraries/Applications/Fusion/Fusion/UI/FusionUI/Resources
# 	'''
# 	return os.path.abspath(AppObjects.GetUi().workspaces.itemById('FusionSolidEnvironment').resourceFolder.replace('/Environment/Model', ''))

# def get_python_dir_and_pip():
# 	if iswindows:
# 		return Path(os.__file__).parents[1]
# 	else:
# 		PYTHON_DIR = Path(os.__file__).parents[2] / "bin"
# 		# fetches pip if it doesn't already exist in the correct directory
# 		if not os.path.exists(os.path.join(PYTHON_DIR, "get-pip.py")):# fetch the pip installer
# 			subprocess.run(f'curl https://bootstrap.pypa.io/get-pip.py -o \"{PYTHON_DIR / "get-pip.py"}\"', shell=True)
# 			subprocess.run(f'\"{PYTHON_DIR / "python"}\" \"{PYTHON_DIR / "get-pip.py"}\"', shell=True)	# runs the process to install pip
# 		return PYTHON_DIR

# def GetPythonDir():
# 	dir = Path(os.__file__)
# 	return dir.parents[1] if iswindows else dir.parents[2]/"bin"




# def CheckDir(*dataPath, makeDir = True):
# 	dataPath = os.path.join(*dataPath)
# 	if dataPath and os.path.exists(dataPath): return dataPath
# 	if makeDir:	os.makedirs(dataPath); return dataPath
# 	else: AppObjects.messageBox('Path not found: ' + dataPath)
