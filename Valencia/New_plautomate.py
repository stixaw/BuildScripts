#THIS SCRIPT RUNS a NETWORK CONNECTION TO PL DIRECTORY LOCATION and then creates a PL

import os
import shutil
import sys
from os.path import join, abspath
import win32wnet
import tempfile
import logging
import threading
import stat
import subprocess
import getopt
import time
import fnmatch
import glob

#global ulgies
PLVersion = os.environ['PLVERSION']
Version = os.environ['ITMSVERSION']
Release = os.environ['ITMSRELEASE']
buildnum = os.environ['ITMSBUILDNUM']
spVersion = os.environ['SPVERSION']
pl_tempsrc = r'\\ali-netapp1.linus.sen.symantec.com\Build\Lindon\%s\SMP\PL' % (Release)
pl_template = 'platform.pl.xml'
pl_tempdst = os.environ['WORKSPACE'] + r'\CM\PLXML'
plNameVersion = ''
PL_DIR = ''
repo = ''
repo_relative = ''
linus_unc = ''
estonia_unc = ''
pune_unc = ''
TIM_STMP = ''
	
class BuildError(Exception):
	def __init__(self, msg, *args):
		Exception.__init__(self, msg)
		self.msg = msg
		#apply(Exception.__init, (self,) + args)

def fail(msg):
	print '%s failed: %s' % (sys.argv[0], msg)
	sys.exit(1)
 
def wnet_connect(host, username = None, password = None):
	netpath = r'\\ali-netapp1.linus.sen.symantec.com\polaris'
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

def getPLDir(path):
	global PL_DIR, repo
	# txt file for PL process to use for PL directory location
	f=open(path + r"\VALPLDIR.txt", "r")
	PL_DIR =f.read()
	f.close()
	print "The directory for today's Pl is: ", PL_DIR
	repo = PL_DIR
	return PL_DIR, repo
	
def createRelativeRepo(path):
	global PL_DIR, repo, repo_relative, Version, Release
	#\\ali-netapp1.linus.sen.symantec.com\Build\Lindon\Release\ITMS\7.1.6007.0\20110719220720\PL
	repo = PL_DIR
	print "Repo = ", repo
	print "Version = ", Version
	#repo_relative = repo.replace(r'\\ali-netapp1.linus.sen.symantec.com\Build\Lindon\%s\ITMS\%s'% (Release,Version), r'..\%s' % (Version))
	repo_relative = repo.replace(r'\\ali-netapp1.linus.sen.symantec.com\Build\Lindon\%s' % (Release), r'..')
	print 'Relative path = ', repo_relative
	text_file=open(path + "\\RelativeUNC.txt", "w")
	text_file.write(repo_relative)
	text_file.close()
	return repo_relative

def createRegionRepo(path):
	global repo, linus_unc, estonia_unc, pune_unc 
	# create ITMSPL directory unc path ITMS\PL instead of ITMS\Version\Timestamp\PL
	linus_unc = repo
	print 'Lindon Unc = ', linus_unc
	text_file=open(path + "\\LINUSUNC.txt", "w")
	text_file.write(linus_unc)
	text_file.close()
	estonia_unc = repo.replace(r'\\ali-netapp1.linus.sen.symantec.com', r'\\Eta-netapp1.tales.sen.symantec.com')
	print 'Estonai Unc = ', estonia_unc
	text_file=open(path + "\\ESTUNC.txt", "w")
	text_file.write(estonia_unc)
	text_file.close()
	pune_unc = repo.replace(r'\\ali-netapp1.linus.sen.symantec.com', r'\\Pun-netapp1.punin.sen.symantec.com')
	print 'Pune Unc = ', pune_unc
	text_file=open(path + "\\PUNEUNC.txt", "w")
	text_file.write(pune_unc)
	text_file.close()
	return estonia_unc, pune_unc

def ChngMod(top):
	#changes the read-only files created by Silverlight scons for clean-up
	for path, dirs, files in os.walk(top + r'\CM\PLXML'):
		for file in files:
			tarFiles = abspath(join(path, file))
			print "Accessing", tarFiles
			os.chmod(tarFiles, stat.S_IWRITE)

def grabTemplate(top):
	global pl_tempsrc, pl_template
	pl_tempdst = top + r'\CM\PLXML'
	#check for template in destination if its there remove it.
	if os.path.exists(pl_tempdst + '\\' + pl_template):
		os.remove(pl_tempdst + '\\' + pl_template)
	#copy new copy of template to local directory
	#shutil.copy(pl_tempsrc + '\\' + pl_template, pl_tempdst)
	#new copy of CBP template to local directory
	shutil.copy(pl_tempsrc + '\\' + pl_template, pl_tempdst)
	
def GetplNameVersion():
	global spVersion, plNameVersion
	if spVersion == '':
		print 'debug spversion = ', spVersion
		plNameVersion1 = os.environ['ITMSMARKET'].replace('.','_')
		plNameVersion = plNameVersion1 + '_'
		print "plNameVersion = ", plNameVersion
		return plNameVersion
	else:
		plNameVersion1 = os.environ['ITMSMARKET'].replace('.','_')
		plNameVersion = plNameVersion1 + '_sp' + spVersion + '_'
		print "plNameVersion = ", plNameVersion
		return plNameVersion

def GetTime():
	global TIM_STMP
	TIM_STMP = time.strftime("%Y%m%d", time.gmtime())
	print TIM_STMP
	return TIM_STMP

def callModifyPL(top):
	global PL_DIR, repo, repo_relative, PLVersion, buildnum, pl_template, pl_tempdst, plNameVersion, Release
	#call modify batch file with no repository change will be lindon UNC from PL_DIR (need to rem out repository call in batch file
	cmd = (top + r'\CM\Scripts\%s\CBPITMS_SP2.bat ' % (Release)) + PL_DIR + ' ' + PLVersion + ' ' +  top + ' ' + buildnum
	print "Calling Modifypl with this command: ", cmd
	os.system(cmd)
	#make copy of lindon unc pl:
	shutil.copy(pl_tempdst + '\\' + pl_template, pl_tempdst + '\\lindon_itms_' + plNameVersion + PLVersion + '.pl.xml')
	#write out PL name to text files for email
	path = os.environ['WORKSPACE']
	text_file=open(path + "\\LINUSPLXML.txt", "w")
	text_file.write('lindon_itms_' + plNameVersion + PLVersion + '.pl.xml')
	text_file.close()

def callModifyRelativ(top):
	global PL_DIR, repo_relative, pl_template, pl_tempdst, plNameVersion, Release, PLVersion
	#make copy of relative path pl:
	#shutil.copy(pl_tempdst + '\\' + pl_template, pl_tempdst + '\\relative_itms_' + plNameVersion + PLVersion + '.pl.xml') 
	#call modify batch file with linus unc path for NewRepository
	#cmd_relative = (top + r'\CM\PLXML\ModifyPL.exe -pl:"' + top + r'\CM\PLXML\relative_itms_' + plNameVersion + PLVersion + '.pl.xml' + '" -action:PackagesChangeRepository "-OldRepository:%s" "-NewRepository:%s"'% (PL_DIR, repo_relative))
	cmd_relative = ('cscript ' + top + r'\CM\Scripts\ReplaceMacro.vbs ' + '"' + pl_tempdst + '\\' + pl_template + '" ' + '"' + pl_tempdst + '\\relative_itms_' + plNameVersion + PLVersion + '.pl.xml" ' + (r'"\\\\ali-netapp1.linus.sen.symantec.com\\build\\lindon\\%s" ' % (Release).lower()) + '".."')
	print "Calling Modifypl with this command: ", cmd_relative
	os.system(cmd_relative)
	#cmd_relative1 = ('cscript ' + top + r'\CM\Scripts\ReplaceMacro.vbs ' + '"' + pl_tempdst + '\\relative_itms_' + plNameVersion + PLVersion + '.pl.xml" ' + '"' + pl_tempdst + '\\relative_itms_' + plNameVersion + PLVersion + '.pl.xml" ' + (r'"\\\\ali-netapp1.linus.sen.symantec.com\\Build\\Lindon\\%s" ' % (Release)) + '".."')
	#print "Calling Modifypl with this command: ", cmd_relative1
	#os.system(cmd_relative1)
	#write out PL name to text files for email
	path = os.environ['WORKSPACE']
	text_file=open(path + "\\RelativePLXML.txt", "w")
	text_file.write('relative_itms_' + plNameVersion + PLVersion + '.pl.xml')
	text_file.close()

def callModifyEstoniaUNC(top):
	global PL_DIR, repo, repo_relative, estonia_unc, pl_template, pl_tempdst, plNameVersion, PLVersion
	#make copy of relative path pl:
	#shutil.copy(pl_tempdst + '\\' + pl_template, pl_tempdst + '\\estonia_itms_' + plNameVersion + PLVersion + '.pl.xml') 
	#call modify batch file with linus unc path for NewRepository
	#cmd_estonia = (top + r'\CM\PLXML\ModifyPL.exe -pl:"' + top + r'\CM\PLXML\estonia_itms_' + plNameVersion + PLVersion + '.pl.xml' + '" -action:PackagesChangeRepository "-OldRepository:%s" "-NewRepository:%s"'% (PL_DIR, estonia_unc))
	cmd_estonia = ('cscript ' + top + r'\CM\Scripts\ReplaceMacro.vbs ' + '"' + pl_tempdst + '\\' + pl_template + '" ' + '"' + pl_tempdst + '\\estonia_itms_' + plNameVersion + PLVersion + '.pl.xml" ' + r'"\\\\ali-netapp1.linus.sen.symantec.com" ' + r'"\\eta-netapp1.tales.sen.symantec.com"')
	print "Calling Modifypl with this command: ", cmd_estonia
	os.system(cmd_estonia)
	#write out PL name to text files for email
	path = os.environ['WORKSPACE']
	text_file=open(path + "\\TALESPLXML.txt", "w")
	text_file.write('estonia_itms_' + plNameVersion + PLVersion + '.pl.xml')
	text_file.close()

def callModifyPuneUNC(top):
	global PL_DIR, repo, repo_relative, pune_unc, pl_template, pl_tempdst, plNameVersion, PLVersion
	#make copy of relative path pl:
	#shutil.copy(pl_tempdst + '\\' + pl_template, pl_tempdst + '\\pune_itms_' + plNameVersion + PLVersion + '.pl.xml') 
	#call modify batch file with linus unc path for NewRepository
	#cmd_pune = (top + r'\CM\PLXML\ModifyPL.exe -pl:"' + top + r'\CM\PLXML\pune_itms_' + plNameVersion + PLVersion + '.pl.xml' + '" -action:PackagesChangeRepository "-OldRepository:%s" "-NewRepository:%s"'% (PL_DIR, pune_unc))
	cmd_pune = ('cscript ' + top + r'\CM\Scripts\ReplaceMacro.vbs ' + '"' + pl_tempdst + '\\' + pl_template + '" ' + '"' + pl_tempdst + '\\pune_itms_' + plNameVersion + PLVersion + '.pl.xml" ' + r'"\\\\ali-netapp1.linus.sen.symantec.com" ' + r'"\\pun-netapp1.punin.sen.symantec.com"')
	print "Calling Modifypl with this command: ", cmd_pune
	os.system(cmd_pune)
	#write out PL name to text files for email
	path = os.environ['WORKSPACE']
	text_file=open(path + "\\PUNINPLXML.txt", "w")
	text_file.write('pune_itms_' + plNameVersion + PLVersion + '.pl.xml')
	text_file.close()

def callPLValidate(top):
	global pl_template, pl_tempdst
	path = os.environ['WORKSPACE']
	cmd = (top + r'\CM\PLValidator\Symantec.PLValidator.exe -pl ' + '"' + pl_tempdst + '\\' + pl_template + '" -tests "XML Is Well-Formed,Required Product Attributes Are Present,No Duplicate ProductInstallGuids, No Duplicate MSI Package Code, Dependencies Exist, No Circular Dependencies, Supersedes Exist, No Circular Supersedes, Updates Exist, No Circular Updates" -outputHtmlFile Validate.txt')
	#removed from validation process ,Hotfix Releases Update and Depend On a Product
	try:
		print "Calling ", cmd
		os.system(cmd)
		result = subprocess.call(cmd)
		if result != 0:
			print "Result = ", result
			raise BuildError('Executing %s failed' % (cmd))
	except BuildError, e:
		fail(e.msg)

def copyNewTemplate(top):
# copies good itms build pl to new location
	global PL_DIR, VERSION, pl_tempsrc, pl_template
	pl_tempdst = top + r'\CM\PLXML'
	VerBuild1 = Version[4:8]
	print VerBuild1
	VerBuild = int(VerBuild1)
	print VerBuild
	oldbuild1 = VerBuild -1
	oldbuild = str(oldbuild1)
	print oldbuild
	print "replacing template with today's PL here ", pl_tempsrc
	if os.path.exists(pl_tempsrc + '\\' + pl_template + '.' + oldbuild):
		os.remove(pl_tempsrc + '\\' + pl_template + '.' + oldbuild)
	if os.path.exists(pl_tempsrc + '\\' + pl_template):
		os.rename((pl_tempsrc + '\\' + pl_template), (pl_tempsrc + '\\' + pl_template + '.' + oldbuild))
	shutil.copy(pl_tempdst + '\\' + pl_template, pl_tempsrc)

def copyFinalPL(top):
	# renames existing pl template to the build prior to version for today's run,
	global pl_template, pl_tempdst
	VEGAPL_DIR = r'\\ali-netapp1.linus.sen.symantec.com\Build\Lindon\%s\PL' % (Release)
	pl_tempdst = top + r'\CM\PLXML'
	path = top
	text_file=open(path + "\\PLUNC.txt", "w")
	text_file.write(VEGAPL_DIR)
	text_file.close()

	for path, dirs, files in os.walk(pl_tempdst):
		for xml in [os.path.join(path, filename) for filename in files if fnmatch.fnmatch(filename, '*.pl.xml')]:
			print "Copying : ", xml, "to", VEGAPL_DIR
			shutil.copy(xml, VEGAPL_DIR)
	for xml in glob.glob(VEGAPL_DIR + '\\*_Administrator_*.pl.xml'):
		os.remove(xml)
	shutil.copy(VEGAPL_DIR + '\\' + pl_template,pl_tempsrc+ '\\' + pl_template)
	if os.path.exists(VEGAPL_DIR + '\\' + pl_template):
		os.remove(VEGAPL_DIR + '\\' + pl_template)

def copyPlatformPl():
	global pl_tempdst,pl_template 
	shutil.copy(pl_tempdst + '\\' + pl_template, './pl/' + pl_template)

def subversionCo(usr,pwd):
	src = 'https://engsrc.engba.symantec.com/svn/SMP/NS/trunk/main/CombinedBuild/PL/CBPPL/'
	dest = './pl'
	#checks out template to be updated
	os.system('svn co '+ src + ' ' + dest + ' --username ' + usr + ' --password ' + pwd)

def subversionCi(usr,pwd):
	global pl_template
	os.system('svn ci ./pl/' + pl_template + ' --message "Checking in template from version %s" '% (Version) +  '--username ' + usr + ' --password ' + pwd)
	

#This is the main program
if __name__ == '__main__':
	wnet_connect('ali-netapp1.linus.sen.symantec.com', username = 'linus' + '\\' + 'ITMSBuild', password = '1TMS8uild')
	wnet_connect(os.environ['HUDSONIP'], username = 'administrator', password = 'altiris')
	GetTime()
	GetplNameVersion()
	ChngMod(os.environ['WORKSPACE'])
	getPLDir('\\\\' + os.environ['HUDSONIP'] + '\\slaveshare')
	grabTemplate(os.environ['WORKSPACE'])
	callModifyPL(os.environ['WORKSPACE'])
	callPLValidate(os.environ['WORKSPACE'])
	#subversionCo('itmbuild','1TMBui1d')
	#copyPlatformPl()
	#subversionCi('itmbuild','1TMBui1d')
	createRelativeRepo(os.environ['WORKSPACE'])
	createRegionRepo(os.environ['WORKSPACE'])
	callModifyRelativ(os.environ['WORKSPACE'])
	callModifyEstoniaUNC(os.environ['WORKSPACE'])
	callModifyPuneUNC(os.environ['WORKSPACE'])
	copyNewTemplate(os.environ['WORKSPACE'])
	copyFinalPL(os.environ['WORKSPACE'])
