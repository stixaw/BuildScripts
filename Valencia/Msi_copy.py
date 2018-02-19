# Copy msi to ali-netapp1

import fnmatch
import getopt
import os
import shutil
import sys
from os.path import join, abspath
import time
import win32wnet
import datetime
import tempfile
import logging
import threading
import string
from pprint import pprint
from renamelib_MP1 import msiDict
from docrenamelib import Doc_Dict

#global variables
top =''
Bld_Dir = ''
Sol_Dir = ''
Sol_DICT = {}
Src_Dir = ''
PL_Dir = ''
SolName = ''
BuildBasePath = ''
FirstRun = False
msiMarket = os.environ['ITMSMARKET']
Version = os.environ['ITMSVERSION']
Release = os.environ['ITMSRELEASE']
Dst_Path = '\\\\ali-netapp1.linus.sen.symantec.com\Build\Lindon\%s\ITMS' % Release
Doc_Path = r'\\ali-netapp1.linus.sen.symantec.com\polaris\ITMS\CombinedBuild\Doc_Builds\%s' % Release
Get3rd_Path = r'\\ali-netapp1.linus.sen.symantec.com\polaris\ITMS\CombinedBuild\3rd_Party\%s' % Release

def usage():
	print __doc__
	print """Usage:
	Msi_copy.py [OPTIONS]
	Options:
	"""
	usage ="""\
	-h, --help|display help
	--solution|Solution Initials, example --solution=DS or -s=AM
	--srcdir|Locaition to find MSI example --srcdir=c:\output_msi
	--firstrun | this specifies to create the base Bld_Dir example --firstrun
	--dict|Dictionary to use for rename function example --dict=DS
	--top|%workspace% is needed to run signing functions
  """

def parseArgs(argv):
	global FirstRun, SolName, Src_Dir, top, Sol_DICT
	try:
		opts, args = getopt.getopt(argv, "hf:s:s:t:d", [ 'help', 'firstrun', 'solution=', 'srcdir=', 'top=', 'dict=' ])
	except getopt.GetoptError:
		print "Invalid options specified.\n"
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		if opt ==("--firstrun"):
			FirstRun = True
		elif opt == ("--solution"):
			SolName = arg
		elif opt == ('--srcdir'):
			Src_Dir = arg
		elif opt == ('--top'):
			top = arg
		elif opt == ("--dict"):
			Sol_DICT = arg

	if Sol_DICT == '':
		print 'You must specify --dict|Dictionary to use for rename function example --dict=DS'
		sys.exit(3)
	if SolName == '':
		print 'You must specify --solution|Solution Initials, example --solution=DS'
		sys.exit(3)
	if Src_Dir == '':
		print 'You must specify --srcdir|Locaition to find MSI example --srcdir=c:\output_msi'
		sys.exit(4)
	if top =='':
		print 'You must speicify --top=%WORKSPACE%'
		sys.exit(6)

class BuildError(Exception):
	def __init__(self, msg, *args):
		Exception.__init__(self, msg)
		self.msg = msg
		#apply(Exception.__init, (self,) + args)
def fail(msg):
	print '%s failed: %s' % (sys.argv[0], msg)
	sys.exit(1)
 
try:
	# set globals from the command line
	parseArgs(sys.argv[1:])

except BuildError, e:
	fail(e.msg)

def Execute(dir, cmd, reportFail=1):
	"""execute a command from a given directory"""
	if sys.platform == 'win32':
		tmpfile = tempfile.mkstemp(suffix='.bat', text=True)
		tmphandle = tmpfile[0]
		tmpname = tmpfile[1]

		os.write(tmphandle, '@echo off\n')
		if dir != '':
			os.write(tmphandle, 'cd %s\n' % dir)
		os.write(tmphandle, '%s\n' % cmd)
		os.close(tmphandle)

		result = os.system(tmpname)
		os.remove(tmpname)
		if result != 0:
			if reportFail:
				raise BuildError('Executing %s from direction %s failed' % (cmd, dir))

def SignFile(pwd,file):
	global top
	privateKey = top + '\\CM\\Verisign\\mycredentials.pfx'
	sign_tool = top + r'\CM\Verisign\signtool.exe'
	signingToolsDir = top + r'\CM\Verisign'
	for retry in range(1, 4):
		try:
			print "msi to sign ", file
			cmd = sign_tool + ' sign /f ' + privateKey +' /p ' + pwd + ' /t http://timestamp.verisign.com/scripts/timstamp.dll ' + file
			print 'Running "' + cmd + '"...'
			Execute (top, cmd)
			break
		except BuildError, e:
			print "Error on attempt (%d)\n" % retry
	else:
		try:
			print "msi to sign ", file
			#sign no timestamp
			cmd1 = sign_tool + ' sign /f ' + privateKey +' /p ' + pwd + ' ' + file
			print 'Running "' + cmd1 + '"...'
			Execute (top, cmd1)
		except BuildError, e:
			raise BuildError("Giving up on ", file, "after (%d) attempts, check to see if the file is an msi." % (retry))

def Rename_MSI(dict):
	global Src_Dir
	for msi in dict.keys():
		if os.path.exists(Src_Dir + "\\" + msi):
			print "renaming ", msi, "to ", dict[msi]
			os.rename(Src_Dir + "\\" + msi, Src_Dir + "\\" + dict[msi])
		else:
			print "Rename function failed", msi, "does not exist"
			sys.exit(3)

def SolFilesSign(pwd, dir):
	global top
	privateKey = top + '\\CM\\Verisign\\mycredentials.pfx'
	sign_tool = top + r'\CM\Verisign\signtool.exe'

	# for msi in os.listdir(dir):
	for path, dirs, files in os.walk(dir):
		for msi in [os.path.join(path, filename) for filename in files if fnmatch.fnmatch(filename, '*.msi')]:
			msitosign = os.path.join(dir, msi)
			SignFile(pwd, msitosign)


def get3rdParty_MSI(pwd, sol, dict):
	global PL_Dir, top, Get3rd_Path
	#determine which path to get highest build from
	if sol == 'BC':
		sol_path = Get3rd_Path + r'\BarcodeSolution'
	if sol == 'ITA':
		sol_path= Get3rd_Path + r'\ITAnalytics'
	if sol == 'ULMIS':
		sol_path = Get3rd_Path + r'\ULM_Inventory'
	if sol == 'ISPACK':
		sol_path = Get3rd_Path + r'\ISPACK_ULM'
	if sol == 'SEPIC':
		sol_path = Get3rd_Path + r'\SEPICSolution'
	if sol == 'DMC':
		sol_path = Get3rd_Path + r'\DMC'
	if sol == 'ASDK':
		sol_path = Get3rd_Path + r'\ASDK'
	print "The sol_path for this run is: ", sol_path
	highbuild = max([(x) for x in os.listdir(sol_path)])
	print highbuild
	IS_PATH = sol_path + '\\' + highbuild
	print IS_PATH

	for msi in dict.keys():
		if os.path.exists(IS_PATH + "\\" + msi):
			print "Copying ", msi, "to ", PL_Dir, 
			shutil.copy(IS_PATH + "\\" + msi, PL_Dir + "\\" + msi)
			print "renaming ", msi, "to ", dict[msi]
			os.rename(PL_Dir + "\\" + msi, PL_Dir + "\\" + dict[msi])
			msitosign = os.path.join(PL_Dir, dict[msi])
			SignFile(pwd, msitosign)
		else:
			print msi, "does not exist"
			sys.exit(3)

def DocCopyRenamSign_MSI(pwd, dict):
	global PL_Dir, top, Doc_Path

	for msi in dict.keys():
		if os.path.exists(Doc_Path + "\\" + msi):
			print "Copying ", msi, "to ", PL_Dir, 
			shutil.copy(Doc_Path + "\\" + msi, PL_Dir + "\\" + msi)
			print "renaming ", msi, "to ", dict[msi]
			os.rename(PL_Dir + "\\" + msi, PL_Dir + "\\" + dict[msi])
			msitosign = os.path.join(PL_Dir, dict[msi])
			SignFile(pwd, msitosign)
		else:
			print "Rename function failed", msi, "does not exist"
			sys.exit(3)

def MakeBaseDir():
	global Version, BuildBasePath
	if FirstRun:
		print 'Version = ', Version
		BuildBasePath = Dst_Path + '\\' + Version
		if os.path.exists(BuildBasePath):
			print "Directory ", BuildBasePath, " already exists"
		if not os.path.exists(BuildBasePath):
			print "Creating ", BuildBasePath
			os.makedirs(BuildBasePath)
	else:
		print Version
		BuildBasePath = Dst_Path + '\\' + Version
		print 'I will be using this BuildBasepath: ', BuildBasePath
	return BuildBasePath

def wnet_connect(host, username = None, password = None):
	#netpath = r'\\ali-netapp1.linus.sen.symantec.com\polaris'
	netpath = r'\\ali-netapp1.linus.sen.symantec.com'
	networkPath = netpath
	unc = ''.join(['\\\\', host])
	print unc
	try:
		win32wnet.WNetAddConnection2(0, None, unc, None, username, password)
	except Exception, err:
		if isinstance(err, win32wnet.error):
			#Disconnect previous connections if detected, and reconnect.
			if err[0] == 1219:
				win32wnet.WNetCancelConnection2(unc, 0, 0)
				return wnet_connect(host, username, password)
		raise err

def MakeBldDir():
	global Bld_Dir, BuildBasePath, SolName
	print BuildBasePath

	#getting BUILD_ID for Directory of First run"
	
	BUILDDIR2 = os.environ["BUILD_ID"]
	print 'Build_ID =  ', BUILDDIR2
	BUILDDIR1 = BUILDDIR2.replace("_",'')
	BUILDDIR = BUILDDIR1.replace("-",'')
	print 'BUILDDIR = ', BUILDDIR
	Bld_Dir = (BuildBasePath + '\\%s' % (BUILDDIR))

	#writing the txt file for directory location for this build
	ROOTDIR = os.environ["ITMSROOTDEST"]
	print 'ROOTDIR = ', ROOTDIR
	path = os.environ['WORKSPACE']
	text_file=open(path + "\\solutiondir.txt", "w")
	text_file.write('%s\\%s\\%s' % (ROOTDIR,BUILDDIR,SolName))
	text_file.close()

	#create the directory for Solution
	if not os.path.exists(Bld_Dir):
		print "Creating ", Bld_Dir
		os.makedirs(Bld_Dir)
	return Bld_Dir

def MakePLDir():
	global Bld_Dir, PL_Dir
	print "For PL Directory path  = ", Bld_Dir + "\\PL"
	PL_Dir = Bld_Dir + "\\PL"

	#create a txt file for PL process to use for PL directory location
	path = os.environ['HUDSONIP'] + '\\slaveshare'
	text_file=open('\\\\' + path + "\\VALPLDIR.txt", "w")
	text_file.write(PL_Dir)
	text_file.close()
	if not os.path.exists(PL_Dir):
		print "Creating ", PL_Dir
		os.makedirs(PL_Dir)
	return PL_Dir

def MakeSolDir(Name):
	global  Bld_Dir, Sol_Dir, SolName
	Sol_Dir = Bld_Dir + '\\' + SolName
	print 'Solution Dir path = ', Sol_Dir
	#check for existing directory for solution if its there then delete it
	# if os.path.exists(Sol_Dir):
		# shutil.rmtree(Sol_Dir)
	#create the Solution directory if it doesn't exist
	if not os.path.exists(Sol_Dir):
		print "Creating ", Sol_Dir
		os.makedirs(Sol_Dir)
	return Sol_Dir

def CopyMSI(Src_Dir):
	global Sol_Dir, Bld_Dir, PL_Dir
	roboOptions = '/Z /R:20 /NP /V'
	print "this is what I think Bld_Dir is ", Bld_Dir
	print "this is what I think PL_Dir is ", PL_Dir
	if SolName == 'MSS':
		if os.path.exists(Sol_Dir):
			shutil.rmtree(Sol_Dir)
		shutil.copytree(Src_Dir, Sol_Dir)
	elif SolName == 'SYM':
		if os.path.exists(Sol_Dir):
			shutil.rmtree(Sol_Dir)
		shutil.copytree(Src_Dir, Sol_Dir)
	#copy the msi to ali-netapp solution directory
	else:
		print "Copying *.msi to ", Sol_Dir, "Check robo.log for details of copy"
		os.system(top + "\\CM\\Scripts\\robocopy %s %s *.msi %s > robo.log" % (Src_Dir, Sol_Dir, roboOptions))

		print "Copying *.msi to ", PL_Dir, "Check robo.log for details of copy"
		os.system(top + "\\CM\\Scripts\\robocopy %s %s *.msi %s > robo.log" % (Src_Dir, PL_Dir, roboOptions))

def GetBldDir():
	global Dst_Path, Bld_Dir, BuildBasePath
	print BuildBasePath
	try:
		highdir = max([int(x) for x in os.listdir(BuildBasePath) if x.isdigit()])
		Bld_Dir  = BuildBasePath + "\\" + str(highdir)
		print "the Build Directory for this run is ", Bld_Dir
			#writing the txt file for directory location for this build
		path = os.environ['WORKSPACE']
		print 'The workspace to save the solutiondir.txt file is ', path
		ROOTDIR = os.environ["ITMSROOTDEST"]
		print 'ROOTDIR = ', ROOTDIR
		text_file=open(path + "\\solutiondir.txt", "w")
		text_file.write('%s\\%s\\%s' % (ROOTDIR,str(highdir),SolName))
		text_file.close()
	except:
		print "There is no ", Bld_Dir, " if this is the first run of a solution today with this ITMSVERSION then you need to run it with the first run switch"

#This is the main program
if __name__ == '__main__':
	try:
		pprint(Sol_DICT)
		if Sol_DICT in msiDict.keys():
			Rename_MSI(msiDict[Sol_DICT])
		SolFilesSign('ITMSCMDS', Src_Dir)
		wnet_connect('ali-netapp1.linus.sen.symantec.com', username = 'linus' + '\\' + 'ITMSBuild', password = '1TMS8uild')
		if FirstRun:
			if SolName == 'master':
				MakeBaseDir()
				MakeBldDir()
				MakePLDir()
				#DocCopyRenamSign_MSI('ITMSCMDS', Doc_Dict['DOCS'])
				get3rdParty_MSI('ITMSCMDS', 'BC', msiDict['BC'])
				#get3rdParty_MSI('ITMSCMDS', 'ITA', msiDict['ITA'])
				#get3rdParty_MSI('ITMSCMDS', 'SEPIC', msiDict['SEPIC'])
				#get3rdParty_MSI('ITMSCMDS', 'ULMIS', msiDict['ULMIS'])
				#get3rdParty_MSI('ITMSCMDS', 'ISPACK', msiDict['ISPACK'])
				#get3rdParty_MSI('ITMSCMDS', 'DMC', msiDict['DMC'])
				#get3rdParty_MSI('ITMSCMDS', 'ASDK', msiDict['ASDK'])
			else:
				MakeBaseDir()
				MakeBldDir()
				MakePLDir()
				MakeSolDir(SolName)
				CopyMSI(Src_Dir)
		else:
			MakeBaseDir()
			GetBldDir()
			MakePLDir()
			MakeSolDir(SolName)
			CopyMSI(Src_Dir)
	except BuildError, e:
		fail(e.msg)
