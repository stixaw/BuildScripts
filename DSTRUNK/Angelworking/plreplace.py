#THIS SCRIPT RUNS a NETWORK CONNECTION TO PL DIRECTORY LOCATION and then creates a PL
import os
import sys

PL_DIR = ''
Version = '7.1.6008'
repo = ''


def getpldir():
	global PL_DIR
	# txt file for PL process to use for PL directory location
	path = 'C:\\slaveshare'
	f=open(path + "\\PLDIR.txt", "r")
	PL_DIR =f.read()
	f.close()
	print "The directory for today's Pl is: ", PL_DIR
	return PL_DIR

def createhttprepo():
	global PL_DIR, repo
	#\\ali-netapp1.altiris.com\polaris\ITMS\CombinedBuild\Daily_Builds\7.1.6007.0\20110719220720\PL
	#http://install.altiris.com/ITMS/CombinedBuild/Daily_Builds/7.1.6007.0/20110719220720/PLrepo1 = PL_DIR.replace('\\', '/')
	repo1 = PL_DIR.replace('\\', '/')
	print repo1
	repo =  repo1.replace('//ali-netapp1.altiris.com/polaris','http://install.altiris.com')
	print repo
	return repo

def CallModifyPL():
	global PL_DIR, repo, Version
	#call modify batch file
	cmd = 'C:\CM-1666\ITMSCM\Scripts\TMSCB_SP2.bat ' + PL_DIR + ' ' + Version + ' ' +  repo
	print "Calling ", cmd
	os.system(cmd)	

#def copyPl():
#	global PL_DIR


#This is the main program
if __name__ == '__main__':
	getpldir()
	createhttprepo()
	CallModifyPL()