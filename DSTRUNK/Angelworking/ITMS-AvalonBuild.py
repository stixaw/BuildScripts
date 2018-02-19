#buildprep script
#needs to do the following:
#First parse the arguments done
#check for WISE installation done (testwifi.py)
#sync Workspace done
#gatherAll files if needed TODO: Gather all function it will do all or none:
#call build.py --cleanall
#call build.py command to build
#call CopyMSI to Copy MSI to top + \DEVTEST_BUILDS\%s

import fnmatch
import getopt
import os
import shutil
import sys
from indent import *
import glob
import zipfile
import random
import subprocess
import string
import win32wnet
import _winreg
from os.path import join, abspath
import stat

#ugly global variables:
rnum = ''
want = ''
have =''
StagingPath = ''
version = 'latest'
DPT_TRNK = '//depot/Endpoint_Management_Group/notification_server/solutions/deployment_solution/Avalon/...'
top = ''
workspace = ''
tools = ''
submit = False
All = False

# BDC = False
# RD = False
# SBS = False
# GPL = False
# CFG = False

#this is for help function to build a commandline
def usage():
  print __doc__
  print """Usage:
BuildPrep.py [OPTIONS]

Options:
"""
  usage = """\
Required Parameters|These are required to run this script --top, --tools, and --workspace
--tools| scmtools workspace
--top|path to top or top example --top=c:\ds\trunk
--workspace|provide the workspace to be used for the local build
Optional input parameters|By default this script will gather all possible Staging files BDC, RD, SBS, GPL, nogather, nosubmit
--path|path to Drive you want to use for a local distrib by example --path=c:
--buildnum|if a developer wants to specify the number for the test build example --buildnum=999
--gatherALL|Turns on the gather ALL function for preboot files from Rdbuild/Builddev
--version|Designates a specific version set to latest by default example Rdbuild: --version=9598 builddev: --version=build447
--help|display help
"""
  rows = [row.strip().split('|') for row in usage.splitlines()]
  print indent(rows, delim='  ', wrapfunc=lambda x: wrap_onspace_strict(x, 40))

def parseArgs(argv):
  global StagingPath, All, version, top, submit, workspace, rnum, tools

  try:
    opts, args = getopt.getopt(argv, 'hgw:bt:v:p:t', ['help','gatherALL','workspace=','buildnum=','tools=','version=','path=','top='])
  except getopt.GetoptError:
    print "Invalid options specified.\n"
    usage()
    sys.exit(2)

  for opt, arg, in opts:
    if opt in ('--help'):
      print "HELP"
      usage()
      sys.exit()
    elif opt in ('--path'):
      StagingPath = arg
      print "I am using this drive", StagingPath, "for distrib staging area"
    elif opt in ('--top'):
      top = arg
      print "Local trunk for p4 commands and copy of zip file to distrib to prepare for build =", top
    elif opt in ('--workspace'):
      workspace = arg
      print "workspace for p4 sync commands", workspace
    elif opt in ('--tools'):
      tools = arg
      print "workspace for p4 sync commands", tools
    elif opt in ('--version'):
      version = arg
      print "Specified version of gather files", version
    elif opt in ('--gatherALL'):
      All = True
      print "Calling all current gather functions, SBS, BDC, Rdeploy, LinuxGpl, and Config.dll"
    elif opt in ('--buildnum'):
      rnum = arg
      print "Specified Buildnumber for this test build=", rnum
  if workspace == '':
    print 'You must specify local workspace for p4 commands to work, example --workspace=angel-ds'
    sys.exit(4)
  if top == '':
    print 'You must specify local trunk path, example --top=<c:\ds\trunk>'
    sys.exit(4)
  if tools == '':
    print 'You must specify scmtools workspace, example --tools=angel-tools'
    sys.exit(4)
  if StagingPath == '' and All == True:
    print ' If you are running a gather for preboot files you must specify --path=C:'
    sys.exit(4)
	
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

  BUILD_FILES = [
    DPT_TRNK + r'apps/DeploymentClient/install/Altiris_Deployment_Agent.wsi',
    DPT_TRNK + r'apps/DeploymentInstall/Altiris_Deployment.wsi',
    DPT_TRNK + r'distrib/DriversDatabase/Altiris_NS_DriversDB.wsi',
    DPT_TRNK + r'distrib/Linux_gpl/altiris_ns_linux_gpl.wsi',
    DPT_TRNK + r'distrib/WAIK/altiris_ns_winpe2.1.wsi',
    DPT_TRNK + r'distrib/WAIK/altiris_ns_winpe2.1_x64.wsi',
    DPT_TRNK + r'apps/DeploymentServer/install/Altiris_Deployment_TaskServerHandler.wsi',
    DPT_TRNK + r'apps/DeploymentServer/Deployment/Config/Altiris.Deployment_Collections.config',
    DPT_TRNK + r'distrib/bootwiz/...',
    DPT_TRNK + r'distrib/config/config.dll',
    DPT_TRNK + r'distrib/DSPortal/DSPortal.xap'
    ]

  X86_MSI = [
    r'%s\apps\DeploymentServer\install\Altiris_DeploymentSolutionTaskServerHandler_7_1_x86.msi' % top,
    r'%s\apps\DeploymentInstall\Altiris_DeploymentSolution_7_1_x86.msi' % top,
    r'%s\apps\DeploymentClient\install\Altiris_DeploymentSolutionAgent_7_1_x86.msi' % top,
    r'%s\distrib\WAIK\Altiris_NSWINPE_7_1_x64.msi' % top,
    r'%s\distrib\WAIK\Altiris_NSWINPE_7_1_x86.msi' % top,
    r'%s\distrib\Linux_gpl\Altiris_NSLINUX_7_1_x86.msi' % top,
    r'%s\distrib\DriversDatabase\Altiris_DriversDatabase_7_1_x86.msi' % top
    ]

except BuildError, e:
  fail(e.msg)

def GetRnum():
  global rnum
  if rnum =='':
    print "generating random buildnumber"
    #produces a random build number for the command --buildnum
    rnum = random.randrange(900, 1000) -1
    print rnum
  else:
    print "using", rnum

def GetBuildNum(dirname):
  return str('0' + ''.join([x for x in dirname if x.isdigit()]))

def GetBuild():
  global rnum
  if rnum == '':
    GET_BLD = r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\Avalon'
    highBuild = max([GetBuildNum(x) for x in os.listdir(GET_BLD)])
    SolBuild1 = highBuild[3:7]
    SolBuild = int(SolBuild1)
    rnum = SolBuild +1

    print "solution build version = ", rnum

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

# def InstallWise():
# simple installation function for WISE install studio
  # print 'I will install Wise'
  # os.system("msiexec /i \\\\builddev.altiris.com\\buildtest\\DeploymentSolution\\WIFI\\WISE_7_3_272.msi /q SERIAL=HHFQ-ZCGC-NHQ7-BPFX WISEDOTNETSCAN=0 /lv C:\\WISE.log")

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

# def wnet_connect(host, username = None, password = None):
  # networkPath = '\\\\builddev.altiris.com\\buildtest'
  # host = 'builddev.altiris.com'
  # unc = ''.join(['\\\\', host])
  # print unc
  # try:
   # win32wnet.WNetAddConnection2(0, None, unc, None, username, password)
  # except Exception, err:
   # if isinstance(err, win32wnet.error):
     # Disconnect previous connections if detected, and reconnect.
     # if err[0] == 1219:
       # win32wnet.WNetCancelConnection2(unc, 0, 0)
       # return wnet_connect(host, username, password)
   # raise err
   
#def GatherAllPreboot():
# Call all Gather scripts
# or Common function of gather?
 
def P4vSync():
  global workspace
  #sync up the workspace with depot
  os.system("p4 -c %s sync %s" % (workspace, DPT_TRNK))

def P4Login():
  global workspace, top
  psswd = top + "//build//scripts//p4psswd.txt"
  os.system("p4 login < %s" % (psswd))

def toolsSync():
  global tools
 #sync up all tools directory
  os.system("p4 -c %s sync //depot/tools/batch/..." % (tools))
  os.system("p4 -c %s sync //depot/tools/Microsoft.NET/..." % (tools))
  os.system("p4 -c %s sync //depot/tools/MSSDKv6.0A/..." % (tools))
  os.system("p4 -c %s sync //depot/tools/MSVC80SP1.X86/..." % (tools))
  os.system("p4 -c %s sync //depot/tools/msvc90sp1-ATLFix.x86/..." % (tools))
  os.system("p4 -c %s sync //depot/tools/Silverlight/..." % (tools))

def ChngMod():
  global top
#changes the read-only files created by Silverlight scons for clean-up
  DEV_OEM_X64_AGNT_DIR = top + r'\distrib\bootwiz\oem\DS\winpe2\x64\Base'
  DEV_OEM_X86_AGNT_DIR = top + r'\distrib\bootwiz\oem\DS\winpe2\x86\Base'  
  for path, dirs, files in os.walk(DEV_OEM_X64_AGNT_DIR):
    for file in files:
      tarFiles = abspath(join(path, file))
      print "Accessing", tarFiles
      os.chmod(tarFiles, stat.S_IWRITE)
  for path, dirs, files in os.walk(DEV_OEM_X86_AGNT_DIR):
    for file in files:
      tarFiles = abspath(join(path, file))
      print "Accessing", tarFiles
      os.chmod(tarFiles, stat.S_IWRITE)

def CleanTemp():
  #os.system("del /q /f /s %temp%\*")
  #walkdown temp dir
  temp = os.getenv("TEMP")
  print temp
  for path, dirs, files in os.walk(temp):
    for file in [os.path.join(path, filename) for filename in files if (not(fnmatch.fnmatch(filename, 'hudson*.bat')))]:
      try:
        print "deleting temp: ", file
        os.remove(file)
      except:
        print "moving on"
    for path, dirs, files in os.walk(temp):
      for name in dirs:
        print (os.path.join(path, name))
      try:
        os.rmdir(os.path.join(path, name))
      except:
        print "keep going"

def DevClean():
  global top
  DEV_OEM_X64_AGNT_DIR = top + r'\distrib\bootwiz\oem\DS\winpe2\x64\Base\Program Files\Altiris\Altiris Agent'
  DEV_OEM_X64_TASKS_DIR = top + r'\distrib\bootwiz\oem\DS\winpe2\x64\Base\Program Files\Altiris\Altiris Agent\Agents\Agent Tasks'
  DEV_OEM_X86_AGNT_DIR = top + r'\distrib\bootwiz\oem\DS\winpe2\x64\Base\Program Files\Altiris\Altiris Agent'
  DEV_OEM_X86_TASKS_DIR = top + r'\distrib\bootwiz\oem\DS\winpe2\x64\Base\Program Files\Altiris\Altiris Agent\Agents\Agent Tasks'
  PrebootDirs = [DEV_OEM_X64_AGNT_DIR, DEV_OEM_X64_TASKS_DIR, DEV_OEM_X86_AGNT_DIR, DEV_OEM_X86_TASKS_DIR]
  for PrebootDir in PrebootDirs:
    for path, dirs, files in os.walk(PrebootDir):
      for file in [os.path.join(path, filename) for filename in files if fnmatch.fnmatch(filename, '*.dll') or fnmatch.fnmatch(filename, '*.exe')]:
        RemoveFile(file)  

def RunBuildPy():
  global top, rnum
#calling build.py to run the no label manual build
  buildcommand = ('python ' + top + '\\build\\scripts\\build.py ' + '--top=' + top + ' --version=7.1. --buildnum=%s' % (rnum))
  print 'CALLING', buildcommand
  os.system(buildcommand)

def CleanBuildPy():
  #calling build.py to clean up all binaries and distrib extracted zip files
  cleancommand = ('python ' + top + '\\build\\scripts\\build.py ' +'--top='+ top + ' --cleanall')
  print 'Calling', cleancommand
  os.system(cleancommand)

def P4vCheckout():
  global workspace
#checkout files modifed in build process
  for f in BUILD_FILES:
    os.system("p4 -c %s edit %s" % (workspace, f)) 

def P4vRevert():
  global workspace, user
# rever files modified by build procses
  for f in BUILD_FILES:
    os.system("p4 -c %s revert %s" % (workspace, f))

 #def CallGather():
#this function calls all gather scripts with correct parameters for all gather
  
def RemoveFile(path):
  if os.path.exists(path):
    os.remove(path)

def CopyMSI():
  global rnum
  output = "C:\\output_msi"

  if not os.path.exists(output):
    os.makedirs(output)

  for MSI in X86_MSI:
    print "Copying x86 MSI"
    shutil.copy(MSI, output)

  if os.path.exists('C:\\output_msi\\Altiris_DeploymentSolutionAgent_7_1_x64.msi'):
    try:
      os.remove('C:\\output_msi\\Altiris_DeploymentSolutionAgent_7_1_x64.msi')
    except:
      print "C:\\output_msi\\Altiris_DeploymentSolutionAgent_7_1_x64.msi does not exist"



#This is the main program
if __name__ == '__main__':

  try:
    if wiseKeyExists() == False:
      print "PLEASE INSTALL WISE using \\build\\scripts\\WISEINSTALL_*.py for your location."
    else:
      P4Login()
      toolsSync()
      P4vSync()
      ChngMod()
      DevClean()
      CleanBuildPy()
      P4vCheckout()
      # GetBuild()
      RunBuildPy()
      P4vRevert()
      CopyMSI()

  except BuildError, e:
    fail(e.msg)