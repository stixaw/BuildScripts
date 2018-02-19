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
from rename_71SP3_lib import msiDict
from DocMsiList import DOC_LIST
from SOLMSILIST import MSILIST	

#global variables
top =''
Bld_Dir = ''
Sol_Dir = ''
Sol_DICT = {}
Src_Dir = ''

SolName = ''
BuildBasePath = ''
GetSingle3rd = ''
msiVersion = ''
spVersion = ''
Sol_List = ''
msicombine = False
msiMarket = os.environ['ITMSMARKET']
Version = os.environ['ITMSVERSION']
Release = os.environ['ITMSRELEASE']
BuildNumber= os.environ['ITMSBUILDNUM']
Get_Docs = os.environ['ITMSDOCS'].lower()
Get3rd_Party = os.environ['ITMS3RDALL'].lower()
#spRelease = os.environ['ITMSSP'].lower() #this wil be true or false if true then provide --sp= the version number
PL_Dir = '\\\\ali-netapp1.linus.sen.symantec.com\Build\Lindon\DevBuilds\%s\PL' % Version
Dst_Path = '\\\\ali-netapp1.linus.sen.symantec.com\Build\Lindon\DevBuilds'
Src_Dir = Dst_Path
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
	--top|%workspace% is needed to run signing functions
  """

def parseArgs(argv):
	global FirstRun, SolName, Src_Dir, top, Sol_DICT, GetSingle3rd, spVersion, msicombine
	try:
		opts, args = getopt.getopt(argv, "h:sm", [ 'help',  'top=' , 'msicombine' ])
	except getopt.GetoptError:
		print "Invalid options specified.\n"
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt == ('--top'):
			top = arg
		elif opt == ('--msicombine'):
			Sol_DICT = 'MSICOMB_LIST'
			msicombine = True
		

	
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


def SolFilesSign(pwd, dir):
	global top
	privateKey = top + '\\CM\\Verisign\\mycredentials.pfx'
	sign_tool = top + r'\CM\Verisign\signtool.exe'

	# for msi in os.listdir(dir):
	for path, dirs, files in os.walk(dir):
		for msi in [os.path.join(path, filename) for filename in files if fnmatch.fnmatch(filename, '*.msi')]:
			msitosign = os.path.join(dir, msi)
			SignFile(pwd, msitosign)

def GetmsiVersion():
	global msiMarket, msiVersion, spRelease, spVersion
	if spVersion == '':
		msiVersion = msiMarket.replace('.','_')
		print 'msiVersion =', msiVersion
		return msiVersion
	else:
		msiVersion1 = msiMarket.replace('.','_')
		msiVersion = msiVersion1 + "_sp" + spVersion
		print 'msiVersion =', msiVersion
		return msiVersion

def get3rdParty_MSI(pwd, sol, dict):
	global PL_Dir, top, msiVersion, Get3rd_Path, Get3rd_Party, GetSingle3rd
	#determine which path to get highest build from
	if sol == 'BC':
		sol_path = Get3rd_Path + r'\BarcodeSolution'
	if sol == 'ITA':
		sol_path= Get3rd_Path + r'\ITAnalytics'
	if sol == 'SEPIC':
		sol_path = Get3rd_Path + r'\SEPICSolution'
	if sol == 'DMC':
		sol_path = Get3rd_Path + r'\DMC'
	if sol == 'ASDK':
		sol_path = Get3rd_Path + r'\ASDK'
	if sol == 'IPADAPP':
		sol_path = Get3rd_Path + r'\IpadApp'
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

def GetSol_LIST(SolName):
	global Sol_List
	Sol_List = SolName + '_LIST'
	print "GetSol_LIST returns = ", Sol_List
	return Sol_List

def SolRenameSign_MSI(pwd, dict, Sol):
    global  Sol_Dir, Bld_Dir, PL_Dir, top, msiVersion, Version
    print "Here"
    for msi in dict.keys():
        cur_path = Src_Dir + "\\" + Version + "\\" + Sol + "\\" + msi
        if os.path.exists(cur_path):
            print "Copying ", msi, "to ", PL_Dir, 
            shutil.copy(cur_path, PL_Dir + "\\" + msi)
            os.rename(PL_Dir + "\\" + msi, PL_Dir + "\\" + dict[msi])
            #msitosign = os.path.join(PL_Dir, dict[msi])
            #SignFile(pwd, msitosign)
        else:
			print "Rename function failed", msi, "does not exist"
			sys.exit(3)

def SolRenameSign_New(brand, pwd, list, Sol):
    global Sol_Dir, Bld_Dir, PL_Dir, top, msiVersion, SolName, Src_Dir, Sol_List, Version
    print "the list for this function: ", list
    for msi in list:
        cur_path = Src_Dir + "\\" + Version + "\\" + Sol + "\\" + msi
        if os.path.exists(cur_path):
            print "Copying ", msi, "to ", PL_Dir, 
            shutil.copy(cur_path, PL_Dir + "\\" + msi)
            name,arch = os.path.splitext(msi)[0].split('_')
            newname = str.lower("%s_%s_%s_%s.msi" %(brand, name, msiVersion, arch))
            print "Renaming ", msi, "to", newname
            os.rename(PL_Dir + "\\" + msi, PL_Dir + "\\" + newname)
        else:
			print "Rename function failed", msi, "does not exist"
			sys.exit(3)

def DocCopyRenamSign_MSI(pwd, list):
    global PL_Dir, top, Doc_Path, msiVersion
    for msi in list:
        if os.path.exists(Doc_Path + "\\" + msi):
			#rename msi based on split
            print "Copying ", msi, "to ", PL_Dir, 
            shutil.copy(Doc_Path + "\\" + msi, PL_Dir + "\\" + msi)
            brand,name,arch = os.path.splitext(msi)[0].split('_')
            newname = str.lower("%s_%s_%s_%s.msi" %(brand, name, msiVersion, arch))
            print "Renaming ", msi, "to", newname
            os.rename(PL_Dir + "\\" + msi, PL_Dir + "\\" + newname)
            msitosign = os.path.join(PL_Dir, newname)
            #SignFile(pwd, msitosign)
        else:
			print "Rename function failed", msi, "does not exist"
			sys.exit(3)

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


def GetBldDir():
	global Dst_Path, Bld_Dir, BuildBasePath
	#finds the highest Build number for placing the  solution and create the text files for email.
	print BuildBasePath
	try:
		highdir = max([int(x) for x in os.listdir(BuildBasePath) if x.isdigit()])
		Bld_Dir  = BuildBasePath + "\\" + str(highdir)
		print "the Build Directory for this run is ", Bld_Dir
		#writing the txt file for directory location for this build
		path = os.environ['WORKSPACE']
		print 'The workspace to save the solutiondir.txt file is ', path
		ROOTDIR = os.environ["ITMSROOTBUILD"]
		print 'ROOTDIR = ', ROOTDIR
		text_file=open(path + "\\solutiondir.txt", "w")
		text_file.write('%s\\%s\\%s' % (ROOTDIR,str(highdir),SolName))
		text_file.close()
	except:
		print "There is no ", Bld_Dir, " if this is the first run of a solution today with this ITMSVERSION then you need to run it with the first run switch"

#This is the main program
if __name__ == '__main__':
    try:
        GetmsiVersion()
        wnet_connect('ali-netapp1.linus.sen.symantec.com', username = 'linus' + '\\' + 'ITMSBuild', password = '1TMS8uild')
        if msicombine:
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST[Sol_DICT], 'MSICOMBINE')
        else:
            print "master run Get docs = ", Get_Docs
            DocCopyRenamSign_MSI('ITMSCMDS', DOC_LIST)
            SolRenameSign_MSI('ITMSCMDS', msiDict['WC'], 'WiseConnector')
            SolRenameSign_New('Symantec', 'ITMSCMDS', MSILIST['SD_LIST'], 'ServiceDesk')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['AC_LIST'], 'Activity')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['AM_CMDB_RP_LIST'], 'AMS_CMDB_RP')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['EC_LIST'], 'EventConsole')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['FTS_LIST'], 'FirstTimeSetup')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['IS_LIST'], 'Inventory')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['ISPACK_LIST'], 'InventoryPackForServers')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['ULMIS_LIST'], 'InventorySolutionUnix')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['MC_LIST'], 'MonitorCore')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['MP_LIST'], 'MonitorPack')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['OOB_LIST'], 'OutofBox')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['PM_LIST'], 'Patch')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['PS_LIST'], 'PowerScheme')
            #SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['RTSM_List'], 'RTSM')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['SM_LIST'], 'SoftwareMgmt')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['SMSP_LIST'], 'SMSP')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['TOP_LIST'], 'Topology')
            SolRenameSign_New('Altiris', 'ITMSCMDS', MSILIST['VMM_LIST'], 'VMM')
		

    except BuildError, e:
        fail(e.msg)
