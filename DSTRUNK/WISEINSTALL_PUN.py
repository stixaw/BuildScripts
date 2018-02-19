#test for WISE Installation Studio
#check to see if wise reg key exists
# if it does check to wise path based on registry
# if it doesn't then it calls the Wnet Connect and the install commandline for WISE

import getopt
import os
import shutil
import sys
from indent import *
import subprocess
import win32wnet
import _winreg


#global variables
user = ''
pwrd = ''
domain = ''
netpath = r'\\\\10.209.184.153\Builds-G\WISE'
host = '10.209.184.153'

#this is for help function to build a commandline
def usage():
  print __doc__
  print """Usage:
testwifi.py [OPTIONS]

Options:
"""
  usage = """\
--user|user for connection to host server for wise isntallation example --user=test1'
--pwrd|password for connection to host server for wise isntallation example --pwrd=test1
--dom|Domain to authenticate user to for net connection example --dom=altiris
--help|display help
"""
  rows = [row.strip().split('|') for row in usage.splitlines()]
  print indent(rows, delim='  ', wrapfunc=lambda x: wrap_onspace_strict(x, 40))

def parseArgs(argv):
  global user, pwrd, domain

  try:
    opts, args = getopt.getopt(argv, 'hu:p:d', ['help', 'user=', 'pwrd=', 'dom=',])
  except getopt.GetoptError:
    print "Invalid options specified.\n"
    usage()
    sys.exit(2)

  for opt, arg, in opts:
    if opt in ('--help'):
      print "HELP"
      usage()
      sys.exit()
    elif opt in ('--user'):
      user = arg
      print "network connection to host server using User = ", user
    elif opt in ('--pwrd'):
      pwrd = arg
      print "network connection to host server using password = ", pwrd
    elif opt in ('--dom'):
      domain = arg
      print "network connection to host server using domain = ", domain
  if user == '':
    print 'Username required to access UNC path connection example --user=altiris\test1'
    sys.exit(4)
  if pwrd == '':
    print 'Password required to access UNC path connection example --pwrd=test1'
    sys.exit(4)
  if domain == '':
    print 'Domain required for user authentication to access UNC path connection example --dom=altiris'
    #sys.exit(4)

class BuildError(Exception):
  def __init__(self, msg, *args):
    Exception.__init__(self, msg)
    self.msg = msg
    #apply(Exception.__init, (self,) + args)

try:
  # set globals from the command line
  parseArgs(sys.argv[1:])

except BuildError, e:
  fail(e.msg)

def wiseKeyExists():
  hkey = (_winreg.HKEY_CURRENT_USER)
  regpath = (r"Software\Wise Solutions")
  #check to see if registry exists
  try:
    reg = _winreg.OpenKey(hkey,regpath)
  except WindowsError:
    print 'WiseKeyExists = False'
    return False
  print 'WiseKeyExists = True'
  return  True

def InstallWise():
#simple installation function for WISE install studio
  print 'I will install Wise'
  os.system("c:\WINDOWS\system32\msiexec /i \\\\10.209.184.153\Builds-G\WISE\WISE_7_3_272.msi /q SERIAL=HHFQ-ZCGC-NHQ7-BPFX WISEDOTNETSCAN=0 /lv C:\\WISE.log")

def CheckWisePath():
#read a registry for intalled path of Wise
  if wiseKeyExists() == True:
    wisereg = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r"Software\Wise Solutions\Install\Wise Installation Studio 7")
    wifiPath, type = _winreg.QueryValueEx(wisereg, "WISdir")
    _winreg.CloseKey(wisereg)
    wisePath = r'Windows Installer Editor\wfwi.exe'
    print wifiPath + wisePath
    return wifiPath + wisePath
  else:
    print 'ELSE: Wise not installed'
  sys.exit(2)

def wnet_connect(server, username = None, password = None):
  global user, pwrd, netpath, host, domain
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

#This is the main program
if __name__ == '__main__':
  try:
    if wiseKeyExists() == False:
      print 'Calling Command wnet_connect(',host,', username = ',domain + '\\' + user,', password = ',pwrd,')'
      wnet_connect(host, username = domain + '' + user, password = pwrd)
      InstallWise()
      CheckWisePath()
    else:
      CheckWisePath()
  except BuildError, e:
    fail(e.msg)