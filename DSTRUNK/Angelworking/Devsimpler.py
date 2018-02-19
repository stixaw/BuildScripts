#automated python script for simpler tool to generate pl.xml at time of build
#uses top for location of tool and robocopy.exe
#Create Solution7.1 directory
#determine build number from scan of builddev.altiris.com\buildtest\DeploymentSolution\Daily_Builds\trunk
#Get the build number by slicing the 7.1.XXXX.0
#copy the necessary MSI to that directory
#Run the SIMPLER Command
#Copy the Solution7.1 directory to all QA resource Servers

import fnmatch
import getopt
import os
import shutil
import sys
from buildlib import *
from indent import *
from os.path import join, abspath
import stat
import subprocess
import glob

#Global Variables
top = ''
local_repo = '\\\\10.209.184.153\\Builds-G\\Hamton\\DevBuilds'
buildnum = ''

def usage():
  print __doc__
  print """Usage:
simpler.py [OPTIONS]

Options:
"""
  usage = """\
-h, --help|display help
--buildnum=<ver>|sets binary versions to <marketing version>.<buildnum>.0
--lpnum=<ver>|sets binary versions to <marketing version>.<lpnum>.0
--top=<path to top>|sets top
"""
  rows = [row.strip().split('|') for row in usage.splitlines()]
  print indent(rows, delim='  ', wrapfunc=lambda x: wrap_onspace_strict(x, 40))

def parseArgs(argv):
  global top, buildnum

  try:
    opts, args = getopt.getopt(argv, 'h:b:l:t:', ['help', 'buildnum=', 'lpnum=', 'top='])
  except getopt.GetoptError:
    print "Invalid options specified.\n"
    usage()
    sys.exit(2)

  for opt, arg, in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit()
    elif opt in ('--buildnum'):
      buildnum = arg
    elif opt in ('--lpnum'):
      LPBuild = arg
    elif opt in ('--top'):
      top = arg

  if top == '':
    print 'You must specify --top=<top path>'
    sys.exit(4)
	
  if buildnum == '':
    print 'You must specify --buildnum=<build number>'
    sys.exit(4)
	
  print "Command line Arguments are " + top + " and " + buildnum

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

def DoNetUse():

   global local_repo
   os.system("net use %s /user:cmuser cmuser"  % (local_repo)) 
      

def SolMSICopy():

  global buildnum
  msi_dst = 'C:\\Solution7.1'
  msi_src = local_repo + '\\LP_Docs_Lic'
  if not os.path.exists(r'C:\Solution7.1'):
    os.makedirs(r'C:\Solution7.1')
  print " Build Number is " + buildnum
  MSI = [
  r'%s\Altiris_DeploymentDocumentation_7_1_SP1_x64.msi' % msi_src,
  r'%s\DEVTEST_BUILDS\%s\x64\Altiris_DeploymentSolution_7_1_x64.msi' % (top, buildnum),
  r'%s\Altiris_DeploymentSolutionLanguages_7_1_x64.msi' % msi_src,
  r'%s\DEVTEST_BUILDS\%s\x64\Altiris_DeploymentSolutionTaskServerHandler_7_1_x64.msi' % (top, buildnum),
  r'%s\DEVTEST_BUILDS\%s\x86\Altiris_DeploymentSolutionTaskServerHandler_7_1_x86.msi' % (top, buildnum),
  r'%s\DEVTEST_BUILDS\%s\x64\Altiris_DriversDatabase_7_1_x64.msi' % (top, buildnum),
  r'%s\DEVTEST_BUILDS\%s\x64\Altiris_NSLINUX_7_1_x64.msi' % (top, buildnum),
  r'%s\DEVTEST_BUILDS\%s\x86\Altiris_NSLINUX_7_1_x86.msi' % (top, buildnum),
  r'%s\DEVTEST_BUILDS\%s\x64\Altiris_NSWINPE_7_1_64_x64.msi' % (top, buildnum),
  r'%s\DEVTEST_BUILDS\%s\x86\Altiris_NSWINPE_7_1_64_x86.msi' % (top, buildnum),
  r'%s\DEVTEST_BUILDS\%s\x64\Altiris_NSWINPE_7_1_86_x64.msi' % (top, buildnum),
  r'%s\DEVTEST_BUILDS\%s\x86\Altiris_NSWINPE_7_1_86_x86.msi' % (top, buildnum),  
  r'%s\1743815Deployment Solution for Clients.txt' % msi_src
  
    ]
  for f in MSI:
    print "Copying", f, "to", msi_dst
    shutil.copy(f, msi_dst)

def CopySolution():
  global top
 #copies the local solution7.1 directory to local shares for testing
  Src_dir = 'c:\\Solution7.1'
  Dest_dir = local_repo + '\\' + buildnum 
  if os.path.exists(Dest_dir):
     shutil.rmtree(Dest_dir,ignore_errors=True)
  if not os.path.exists(Dest_dir):
     os.makedirs(Dest_dir)	 
  roboOptions = '/Z /R:20 /NP /V'
  DoNetUse()
  os.system("%s\\build\\scripts\\robocopy %s %s %s > robo.log" % (top, Src_dir, Dest_dir, roboOptions))  
  

def CopyGoodXML():
  shutil.copy(top + '\\build\Simpler\\1250\\Altiris Deployment Solution x64.pl.xml', top + "\\build\\Simpler\\Altiris Deployment Solution x64.pl.xml")
  os.chmod(top + "\\build\\Simpler\\Altiris Deployment Solution x64.pl.xml", stat.S_IWRITE)

def CallSimpler():
  global top, buildnum
  #set environment
  print "/prodver =", buildnum
 #calls the simple.bat which runs the simple.exe to update the existing good pl.xml Currently good is x64 1250
  cmd =  (' "' + top + '\\build\\scripts\\Simple.bat" ' + top + ' ' + str(buildnum) + ' > simpbat.log')
  cmdconsole = 'C:\\windows\\system32\\cmd.exe /C'
  print "Calling cmd...", cmdconsole + cmd
  os.system(cmdconsole + cmd)
  if os.path.exists(top + "\\build\\Simpler\\Altiris Deployment Solution x64.pl.xml"):
    os.remove(top + "\\build\\Simpler\\Altiris Deployment Solution x64.pl.xml")

 
#This is the main program
if __name__ == '__main__':
    DoNetUse()
    SolMSICopy()    
    CopyGoodXML()
    CallSimpler()
    CopySolution()