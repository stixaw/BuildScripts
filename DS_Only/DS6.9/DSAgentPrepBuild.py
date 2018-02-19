# Prep fo Build script for Dagent based on scmclient.py

import sys
import os
import getopt
import fnmatch
from indent import *
import glob
import subprocess
import string
from os.path import join, abspath
import stat
import time
import tempfile
import shutil

#global variables
DPT_DAGENT = '//depot/Endpoing_Management_Group/dagent...'
top = ''
majorVersion = '6'
minorVersion = '9'
buildNum = ''
workspace = ''
versionName = 'Uinta'
buildDevOutputPath = '\\\\10.105.19.47\\buildtest\\' + versionName
localPath = top + r'\trunk'

#this is for help function to build a commandline
def usage():
	print __doc__
	print """Usage:
DSAgentPrebBuild.py [OPTIONS]
	Options:
"""
	usage = """\
--help|display help
Required Parameters|These are required to run this script --top, --workspace
--top|path to top or top example '--top=c:\ds\trunk'
--workspace|provide the workspace to be used for the local build
--buildnum|if a developer wants to specify the number for the test build example --buildnum=999
"""
	rows = [row.strip().split('|') for row in usage.splitlines()]
	print indent(rows, delim='  ', wrapfunc=lambda x: wrap_onspace_strict(x, 40))

def parseArgs(argv):
	global top, workspace, buildNum

	try:
		opts, args = getopt.getopt(argv, 'hw:b:t', ['help', 'top=', 'workspace=', 'buildnum='])
	except getopt.GetoptError:
		print "Invalid options specified.\n"
		usage()
		sys.exit(2)

	for opt, arg, in opts:
		if opt in ('--help'):
			print "HELP"
			usage()
			sys.exit()
		elif opt in ('--top'):
			top = arg
			print "Local trunk for p4 commands and copy of zip file to distrib to prepare for build =", top
		elif opt in ('--workspace'):
			workspace = arg
			print "workspace for p4 sync commands", workspace
		elif opt in ('--buildnum'):
			buildNum = arg
			print "Specified Buildnumber for this build=", buildNum
	if workspace == '':
		print 'You must specify local workspace for p4 commands to work, example --workspace=angel-ds'
		sys.exit(4)
	if top == '':
		print 'You must specify local trunk path, example --top=<c:\ds\trunk>'
		sys.exit(4)
	
class BuildError(Exception):
	def __init__(self, msg, *args):
		Exception.__init__(self, msg)
		self.msg = msg

def fail(msg):
	print '%s failed: %s' % (sys.argv[0], msg)
	sys.exit(1)

try:
	# set globals from the command line
	parseArgs(sys.argv[1:])
	
	filesThatChange = [
	localPath + '\\apps\\dsagent\\install\\x86\\dagent.wsi',
	localPath + '\\apps\\dsagent\\install\\x86\\wisebuild.ini',
	localPath + '\\apps\\dsagent\\install\\x64\\dagent.wsi',
	localPath + '\\apps\\dsagent\\install\\x64\\wisebuild.ini',
	localPath + '\\apps\\dsagent\\install\\ia64\\dagent.wsi',
	localPath + '\\apps\\dsagent\\install\\ia64\\wisebuild.ini'
	]

except BuildError, e:
	fail(e.msg)
  
def PrepareForBuild():
	global buildNum, buildDevOutputPath
	outputFolder = buildDevOutputPath + '\\Dagent\\Build' + buildNum
	if os.path.exists(outputFolder):
		raise Exception('Build output folder already exists:' + outputFolder)
	else:
		os.makedirs(outputFolder)

def P4vSync():
	global workspace
	#sync up the workspace with depot
	os.system("p4 -c %s sync %s" % (workspace, DPT_DAGENT))

def P4Login():
	global workspace, top
	psswd = top + "//build//scripts//p4psswd.txt"
	os.system("p4 login < %s" % (psswd))

def P4vRevert(list):
	global workspace, user
	# revert files modified by build procses
	for f in list:
		os.system("p4 -c %s sync -f %s#head" % (workspace, f))

def ChngBldFiles(list):
	#changes the read-only files for msi creation
	for f in list:
		print "Accessing", f
		os.chmod(f, stat.S_IWRITE)

def CleanTemp():
	#os.system("del /q /f /s %temp%\*")
	#walkdown temp dir
	temp = os.getenv("TEMP")
	print temp
	for path, dirs, files in os.walk(temp):
		for file in [os.path.join(path, filename) for filename in files if (not(fnmatch.fnmatch(filename, 'hudson*.bat')))]:
			try:
				print "deleting temp: ", file
				os.remove(file)
			except:
				print "can't access", file, "skipping", file
	for path, dirs, files in os.walk(temp):
		for name in dirs:
			print (os.path.join(path, name))
			try:
				os.rmdir(os.path.join(path, name))
			except:
				print "can't access", name, "skipping", name

def Copy(self):
	global localPath
	# Copy english DLL's for localizing
	localizationPath = buildDevOutputPath + '\\Localization\\NewFiles\\DLLs'

	if not os.path.exists(localizationPath):
		os.makedirs(localizationPath)

	shutil.copy(localPath + r'\obj_win\dsagent\release\ui\res_dll\dagentui_EN.dll', localizationPath + '\dagentui-x86_EN.dll')
	shutil.copy(localPath + r'\obj_win_x64\dsagent\release\ui\res_dll\dagentui_EN.dll', localizationPath + '\dagentui-x64_EN.dll')
	shutil.copy(localPath + r'\obj_win_ia64\dsagent\release\ui\res_dll\dagentui_EN.dll', localizationPath + '\dagentui-ia64_EN.dll')

def RunBuild():
	global top, majorVersion, minorVersion, buildNum
	#calling build.py to run the no label manual build to make this command copy to builddev use this switch :--copy-output
	buildCommand = 'localPath' + '\\build\\scripts\\DAgentBuild.bat ' + majorVersion + ' ' + minorVersion + ' ' + buildNum + ' ' + 'localPath'
	print 'CALLING', buildcommand
	os.system(buildcommand)

def FinishBuild():
	global top, majorVersion, minorVersion, buildNum, versionName
	finishCommand = localPath + '\\build\\scripts\\DAgentFinish.bat ' + majorVersion + ' ' + minorVersion + ' ' + buildNum + ' ' +  versionName + ' ' +localPath
	print 'CALLING', finishCommand
	os.system(finishCommand)

#This is the main program
if __name__ == '__main__':
	try:
		CleanTemp()
		PrepareForBuild()
		#P4Login()
		RunBuild()
		ChngBldFiles(filesThatChange)
		FinishBuild()
		#P4vRevert(filesThatChange)
	except BuildError, e:
		fail(e.msg)