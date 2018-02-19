# Jar verify signature and sign command

import os
import sys
import fnmatch

Jar_List = [
]

def VerifyJarSig(pwd, files):
	global top
	#Command used to verify signature
	#C:\scmtools\jdk1.6.0_14_windows\bin>jarsigner.exe -verify C:\ds\trunk\common\JavaApplet\CopyFolderFile\dist\CopyFolderFile.jar
	#response: jar verified.
	Jarsign_tool = top + '\\CM\\Verisign\\jarsigner.exe'
	for jar in files:
		print (JarSig_Tool + ' -verify %s > '+ top + '\\jar.txt') % jar
		os.system((JarSig_Tool + ' -verify %s > '+ top + '\\jar.txt') % (jar))
		f = open (top + '\\' + 'jar.txt', 'r')
		ver_sig = f.read()
		f.close()
		if 'verified' in ver_sig:
			print jar, " is already signed"
		else:
			print jar, " is not signed, calling signJar function"
			certpath = top + '\\build\\verisign\\Authenticode\\dssym_cs.pfx'
			pvktmp = ' pvktmp:B529B5D4-FCA9-11DF-9200-CC62DFD72085'
			cmd = JarSig_Tool + ' -keystore ' + certpath + ' -storepass ' + pwd + ' -sigfile SIG ' + jar + pvktmp
			print cmd
			Execute (top, cmd)

##  Main entry point
##
if __name__ == '__main__':
	
	VerifyJarSig('ITMSCMDS', Jar_List)