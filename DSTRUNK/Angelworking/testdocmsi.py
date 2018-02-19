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
from pprint import pprint
from renamelib import msiDict
from docrenamelib import Doc_Dict

class BuildError(Exception):
	def __init__(self, msg, *args):
		Exception.__init__(self, msg)
		self.msg = msg
		#apply(Exception.__init, (self,) + args)

def fail(msg):
	print '%s failed: %s' % (sys.argv[0], msg)
	sys.exit(1)

def RenameCopyDoc_MSI(pwd,dict):
	privateKey = r'C:\CM-1666\ITMSCM\Verisign\mycredentials.pfx'
	signingToolsDir = r'C:\CM-1666\ITMSCM\Verisign'
	sign_tool = r'C:\CM-1666\ITMSCM\Verisign\signtool.exe'
	PL_Dir = '\\\\ali-netapp1.altiris.com\\polaris\\ITMS\\CombinedBuild\\Daily_Builds\\Docs'
	Doc_Path = '\\\\ali-netapp1.altiris.com\\polaris\\Documentation\\LastBuild'
	for msi in dict.keys():
		if os.path.exists(Doc_Path + "\\" + msi):
			print "Copying ", msi, "to ", PL_Dir, 
			shutil.copy(Doc_Path + "\\" + msi, PL_Dir + "\\" + msi)
			print "renaming ", msi, "to ", dict[msi]
			os.rename(PL_Dir + "\\" + msi, PL_Dir + "\\" + dict[msi])
			msitosign = os.path.join(PL_Dir, dict[msi])
			print msitosign
			cmd1 = sign_tool + ' sign /f ' + privateKey +' /p ' + pwd + ' /t http://timestamp.verisign.com/scripts/timstamp.dll ' + msitosign + '> sign.log'
			print 'Running "' , cmd1
			os.system(cmd1)
		else:
			print "Rename function failed", msi, "does not exist"
			sys.exit(3)


#This is the main program
if __name__ == '__main__':
	RenameCopyDoc_MSI('ITMSCMDS', Doc_Dict['DOCS'])