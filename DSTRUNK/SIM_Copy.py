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

#global Variables
top = ''
SIM_SRC = 'C:\\output_msi'

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
	global top
	try:
		opts, args = getopt.getopt(argv, "h:t", [ 'help','top=' ])
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
	if top =='':
		print 'You must speicify --top=%WORKSPACE%'
		sys.exit(3)

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

def GetTime():
	global TIM_STMP
	TIM_STMP = time.strftime("%Y%m%d%H%M", time.gmtime())
	print TIM_STMP
	return TIM_STMP

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

def SignFiles(pwd, dir):
	global top, SIM_SRC
	privateKey = top + '\\CM\\Verisign\\mycredentials.pfx'
	signingToolsDir = top + r'\CM\Verisign'
	sign_tool = top + r'\CM\Verisign\signtool.exe'

	for root, dirs, files in os.walk(dir):
		for msi in files:
			if fnmatch.fnmatch(msi, '*.msi') or fnmatch.fnmatch(msi, '*.exe'):
				msitosign = os.path.join(root, msi)
				print msitosign
				cmd1 = sign_tool + ' sign /f ' + privateKey +' /p ' + pwd + ' /t http://timestamp.verisign.com/scripts/timstamp.dll ' + msitosign
				print 'Running "' + cmd1 + '"...'
				Execute (top, cmd1)  
			else:
				logging.error('Error while signing ' + msi)

def MakeBaseDir():
	global Version, BuildBasePath
	if FirstRun:
		print Version
		BuildBasePath = Dst_Path + '\\' + Version
		if os.path.exists(BuildBasePath):
			print "Directory ", BuildBasePath, " already exists"
		if not os.path.exists(BuildBasePath):
			print "Creating ", BuildBasePath
			os.makedirs(BuildBasePath)
	else:
		print Version
		BuildBasePath = Dst_Path + '\\' + Version
		print BuildBasePath
		return BuildBasePath

def wnet_connect(host, username = None, password = None):
	netpath = r'\\ali-netapp1.altiris.com\polaris'
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
	global Bld_Dir, BuildBasePath
	Bld_Dir = (BuildBasePath + '\\%s' % (TIM_STMP))
	#create the directory for Solution
	if not os.path.exists(Bld_Dir):
		print "Creating ", Bld_Dir
		os.makedirs(Bld_Dir)
	return Bld_Dir

def MakeSolDir(Name):
	global  Bld_Dir, Sol_Dir, SolName
	print Bld_Dir
	print SolName
	Sol_Dir = Bld_Dir + '\\' + SolName
	print Sol_Dir
	if not os.path.exists(Sol_Dir):
		print "Creating ", Sol_Dir
		os.makedirs(Sol_Dir)

def CopyMSI(Src_Dir):
	global Sol_Dir
	#copy the msi to ali-netapp solution directory
	for file in os.listdir(Src_Dir):
		if fnmatch.fnmatch(file, '*.msi'):
			dirfile = os.path.join(Src_Dir, file)
			print "Copying ", dirfile, "to ", Sol_Dir
			shutil.copy(dirfile, Sol_Dir)

def XcopyDir():
	global top, SIM_SRC
	Dst_Path =  '\\\\ali-netapp1.altiris.com\\polaris\\aim\\builds\\archive'
	for root, dirs, files in os.walk(SIM_SRC):
		dest = Dst_Path + root.replace(SIM_SRC, '')
		if not os.path.isdir(dest):
			os.mkdir(dest)
			print "creating directory at:  ", dest
		path = os.environ['WORKSPACE']
		print "path = ", path
		text_file=open(path + "\\builddir.txt", "w")
		text_file.write('%s' % (dest))
		text_file.close()
		for f in files:
			oldLoc = root + '\\' + f
			newLoc = dest + '\\' + f
			if not os.path.isfile(newLoc):
				try:
					shutil.copy(oldLoc, newLoc)
				except IOError:
					print 'file "' + f + '" already exits'
	

def GetBldDir():
	global Dst_Path, Bld_Dir, BuildBasePath
	print BuildBasePath
	highdir = max([int(x) for x in os.listdir(BuildBasePath) if x.isdigit()])
	Bld_Dir  = BuildBasePath + "\\" + str(highdir)
	print "the Build Directory for this run is ", Bld_Dir

#This is the main program
if __name__ == '__main__':
	try:
		wnet_connect('ali-netapp1.altiris.com', username = 'linus' + '\\' + 'ITMSBuild', password = "1TMS8uild")
		SignFiles('ITMSCMDS', SIM_SRC)
		XcopyDir()
	except BuildError, e:
		fail(e.msg)