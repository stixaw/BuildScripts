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

#global ulgies
PL_DIR = ''
Version = os.environ['PLVERSION']
repo = ''
buildnum = os.environ['ITMSBUILDNUM']
tmplate_src = r'\\ali-netapp1.altiris.com\polaris\aim\builds\productlisting\7.1 sp2'
grabpl = ''
plversion = 'latest'
have = ''
want = ''
pl_tempsrc = r'\\ali-netapp1.altiris.com\polaris\ITMS\CombinedBuild\ITMSPL_Template'
pl_template = 'itms_7_1_sp2.pl.xml'

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

def fail(msg):
	print '%s failed: %s' % (sys.argv[0], msg)
	sys.exit(1)
 
def getPLDir(path):
	global PL_DIR
	# txt file for PL process to use for PL directory location
	f=open(path + r"\PLDIR.txt", "r")
	PL_DIR =f.read()
	f.close()
	print "The directory for today's Pl is: ", PL_DIR
	return PL_DIR

def createHttpRepo(path):
	global PL_DIR, repo
	#\\ali-netapp1.altiris.com\polaris\ITMS\CombinedBuild\Daily_Builds\7.1.6007.0\20110719220720\PL
	#http://install.altiris.com/ITMS/CombinedBuild/Daily_Builds/7.1.6007.0/20110719220720/PLrepo1 = PL_DIR.replace('\\', '/')
	repo1 = PL_DIR.replace('\\', '/')
	print repo1
	repo =  repo1.replace('//ali-netapp1.altiris.com/polaris','http://install.altiris.com')
	print repo
	text_file=open(path + "\\PLURL.txt", "w")
	text_file.write(repo)
	text_file.close()
	return repo

def ChngMod(top):
	#changes the read-only files created by Silverlight scons for clean-up
	for path, dirs, files in os.walk(top + r'\CM\PLXML'):
		for file in files:
			tarFiles = abspath(join(path, file))
			print "Accessing", tarFiles
			os.chmod(tarFiles, stat.S_IWRITE)

def FindLatest(top):
	global tmplate_src, grabpl, plversion, have, want
#check to see if --version provided a version if not then we check BDC.want for what we want.
#open the .want file to see what version is wanted options in this file are latest, build number
#ie if we always want latest we would have latest as first line in that file, if we wanted a rdbuild it would be 9266
#if this comes from a DS build it would be build9226
#Source for version for rdeploy
	if plversion == 'latest':
		print "this is the value for version", plversion
		f = open ( top + r'\CM\Scripts\pl.have', 'r')
		have = f.read()
		print 'have =', have
		f.close()
		f = open( top + r'\CM\Scripts\pl.want', 'r')
		want = f.read()
		print 'want = ', want
		f.close()
		if want.strip().lower() == 'latest':
			highestbuild=max([(x) for x in os.listdir(tmplate_src) if x.replace('_','').isdigit()])
			print 'highestbuild = ', highestbuild
			want = highestbuild
			print 'want from highestbuild = ', want
		if [str(want)] != [str(have)]:
			print "1 have =", have, "want =", want
			grabpl = True
			plversion = want
		else:
			print "2 have =", have, "want =", want
			grabpl = False
			print "Exiting gather script we have", have, "what we want", want

	else:
		print "I was told to get version", plversion
		f = open (top + r'\CM\Scripts\pl.have', 'r')
		have = f.read()
		f.close()
		want = plversion
		if want != have:
			print "3 have =", have, "want =", want
			grabpl = True
		else:
			print "4 have =", have, "want =", want
			grabpl = False
			print "Exiting gather script we have", have, "what we want", want

def CopyTemplate():
	global have, want, tmplate_src, pl_tempsrc, pl_template
	pl_tempdst = top + r'\CM\PLXML'
	#copies current template from ali-netapp1 to ITMS template location
	#check for template in destination if its there remove it.
	if os.path.exists(pl_tempsrc + '\\' + pl_template):
		os.rename(pl_tempsrc + '\\' + pl_template, pl_tempsrc + '\\' + pl_template + "." + have)
	#copy new copy of template to local directory
	shutil.copy(tmplate_src + "\\" + want + "\\" + pl_template, pl_tempsrc)

def UpdateHave(top):
	global want
	#checkout and write to have to match the newly gathered version
	#os.system("p4 -c %s edit %s" % (workspace, BDC_DPT_HV))
	f = open (top + '\\scripts\\pl.have', 'w')
	f.write(str(want))
	f.close()

def grabTemplate(top):
	global pl_tempsrc, pl_template
	pl_tempdst = top + r'\CM\PLXML'
	#check for template in destination if its there remove it.
	if os.path.exists(pl_tempdst + '\\' + pl_template):
		os.remove(pl_tempdst + '\\' + pl_template)
	#copy new copy of template to local directory
	shutil.copy(pl_tempsrc + '\\' + pl_template, pl_tempdst)

def callModifyPL(top):
	global PL_DIR, repo, Version, buildnum
	#call modify batch file
	cmd = top + r'\CM\Scripts\ITMSCB_SP2.bat ' + PL_DIR + ' ' + Version + ' ' +  repo + ' ' + top + ' ' + buildnum
	print "Calling ", cmd
	os.system(cmd)	

def P4Login(top):
  psswd = top + "//scripts//p4psswd.txt"
  os.system("p4 login < %s" % (psswd))
 
def P4vCheckout(workspace, top):
	#checkout files modifed in build process
    os.system("p4 -c %s edit %s + r'\CM\Scripts\pl.have'" % (workspace, top))

def P4vSubmit(workspace, top):
  global want
  #p4 [g-opts] submit [-r] [-f submitoption] -d description
  #os.system("p4 -p %s submit //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s submit -d %s %s + r'\CM\Scripts\pl.have " % (workspace, want))

def copyFinalPL(top):
	global PL_DIR, VERSION
	pl_tempsrc = r'\\ali-netapp1.altiris.com\polaris\ITMS\CombinedBuild\ITMSPL_Template'
	pl_template = 'itms_7_1_sp2.pl.xml'
	pl_tempdst = top + r'\CM\PLXML'
	VerBuild1 = Version[4:8]
	print VerBuild1
	VerBuild = int(VerBuild1)
	print VerBuild
	oldbuild1 = VerBuild -1
	oldbuild = str(oldbuild1)
	print oldbuild
	print "Copy pl to ", PL_DIR
	shutil.copy(pl_tempdst + r'\itms_7_1_sp2.pl.xml', PL_DIR)
	print "replacing template with today's PL here ", pl_tempsrc
	if os.path.exists(pl_tempsrc + r'\itms_7_1_sp2.pl.xml' + '.' + oldbuild):
		os.remove(pl_tempsrc + r'\itms_7_1_sp2.pl.xml' + '.' + oldbuild)
	if os.path.exists(pl_tempsrc + r'\itms_7_1_sp2.pl.xml'):
		os.rename((pl_tempsrc + r'\itms_7_1_sp2.pl.xml'), (pl_tempsrc + r'\itms_7_1_sp2.pl.xml' + '.' + oldbuild))
	shutil.copy(pl_tempdst + r'\itms_7_1_sp2.pl.xml', pl_tempsrc)
	

#This is the main program
if __name__ == '__main__':
	wnet_connect('ali-netapp1.altiris.com', username = 'linus' + '\\' + 'ITMSBuild', password = '1TMS8uild')
	wnet_connect(os.environ['HUDSONIP'], username = 'administrator', password = 'altiris')
	ChngMod(os.environ['WORKSPACE'])
	getPLDir('\\\\' + os.environ['HUDSONIP'] + '\\slaveshare')
	createHttpRepo(os.environ['WORKSPACE'])
	FindLatest(os.environ['WORKSPACE'])
	if grabpl == True:
		P4Login(os.environ['WORKSPACE'])
		P4vCheckout(os.environ['P4CLIENT'], os.environ['WORKSPACE'])
		CopyTemplate(os.environ['WORKSPACE'])
		UpdateHave(os.environ['WORKSPACE'])
		P4vSubmit(os.environ['P4CLIENT'], os.environ['WORKSPACE'])
	grabTemplate(os.environ['WORKSPACE'])
	callModifyPL(os.environ['WORKSPACE'])
	copyFinalPL(os.environ['WORKSPACE'])

