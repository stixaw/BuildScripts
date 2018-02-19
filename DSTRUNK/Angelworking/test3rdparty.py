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

PL_Dir = '\\\\ali-netapp1.altiris.com\\polaris\\ITMS\\CombinedBuild\\Daily_Builds\\PLTEST'
top = 'C:\\CM-1666\\ITMSCM'


def get3rdParty_MSI(pwd, sol, dict):
	global PL_Dir, top
	privateKey = top + '\\Verisign\\mycredentials.pfx'
	signingToolsDir = top + r'\Verisign'
	sign_tool = top + r'\Verisign\signtool.exe'
	#determine which path to get highest build from
	pprint(sol)
	if sol == 'BC':
		sol_path = r'\\ali-netapp1.altiris.com\polaris\ITMS\CombinedBuild\Daily_Builds\BarcodeSolution'
	if sol == 'ITA':
		sol_path= r'\\ali-netapp1.altiris.com\polaris\ITMS\CombinedBuild\Daily_Builds\ITAnalytics'
	if sol == 'ULMIS':
		sol_path = r'\\ali-netapp1.altiris.com\polaris\ITMS\CombinedBuild\Daily_Builds\ULM_Inventory'
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
			print msitosign
			cmd1 = sign_tool + ' sign /f ' + privateKey +' /p ' + pwd + ' /t http://timestamp.verisign.com/scripts/timstamp.dll ' + msitosign
			print 'Running "' + cmd1 + '"...'
			os.system(cmd1)
		else:
			print "Rename function failed", msi, "does not exist"
			sys.exit(3)


if __name__ == '__main__':
	get3rdParty_MSI('ITMSCMDS', 'BC', msiDict['BC'])
	get3rdParty_MSI('ITMSCMDS', 'ULMIS', msiDict['ULMIS'])