"""build.py:
Runs all the commands to complete a build from beginning to end.  Before running this script, be sure that the environment PATH is set to be able to find necessary binaries (i.e. svn, python, etc)
"""

import fnmatch
import getopt
import os
import shutil
import sys
import threading
import subprocess
from buildlib import *
from indent import *
import zipfile
from os.path import join, abspath
import _winreg
import stat
# from win32com.client import Dispatch
# import win32api
import glob
import time
import tempfile

# clear ugly global variables
marketingVersion = '7.1'
version = ''
clean = False
cleanall = False
copyAllOutput = False
copyBuilddevOutputOnly = False
signFiles = True
top = ''

def usage():
  print __doc__
  print """Usage:
build.py [OPTIONS]

Options:
"""
  usage = """\
-h, --help|display help
-c, --clean|clean up MSIs, (will not build)
--cleanall|do everything from clean, and also remove binary output directories
-b <buildnum>, --buildnum=<ver>|sets binary versions to <marketing version>.<buildnum>.0
-v <ver>, --version=<ver>|sets binary versions to <ver>
-t, --top=<path to top>|sets top
--copy-output|copy output to local site and to India's server
"""
  rows = [row.strip().split('|') for row in usage.splitlines()]
  print indent(rows, delim='  ', wrapfunc=lambda x: wrap_onspace_strict(x, 40))

def makeFullVersion(buildnum):
  return marketingVersion + '.' + str(buildnum) + '.0'

def parseArgs(argv):
  global top, clean, cleanall, copyAllOutput, copyBuilddevOutputOnly, version, signFiles

  try:
    opts, args = getopt.getopt(argv, 'cnhv:b:t:', ['clean', 'cleanall', 'nosign',
      'help', 'copy-output', 'copy-builddev', 'version=', 'buildnum=', 'top='])
  except getopt.GetoptError:
    print "Invalid options specified.\n"
    usage()
    sys.exit(2)

  for opt, arg, in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit()
    elif opt in ('-v', '--version'):
      version = arg
    elif opt in ('-n', '--nosign'):
      signFiles = False
    elif opt in ('-b', '--buildnum'):
      version = makeFullVersion(arg)
    elif opt in ('-t', '--top'):
      top = arg
    elif opt in ('-c', '--clean'):
      clean = True
    elif opt == '--cleanall':
      clean = True
      cleanall = True
    elif opt == '--copy-output':
      copyAllOutput = True
    elif opt == '--copy-builddev':
      copyBuilddevOutputOnly = True

  if top == '':
    print 'You must specify --top=<top path>'
    sys.exit(4)

  if version == '' and not clean:
    print 'You must specify --version, --buildnum, or --clean'
    sys.exit(3)

try:
  # set globals from the command line
  parseArgs(sys.argv[1:])

  # I wanted the wfwi.exe that is in build\wise, but it is having problems :(
  AGENT_INSTALL_NAME = 'Altiris_Deployment_Agent'
  AGENT_64_INSTALL_NAME = 'Altiris_Deployment_Agent_x64'
  #AGENT_86_INSTALL_64_NAME = 'Altiris_Deployment_Agent_86_x64'
  TASKSERVER_INSTALL_NAME = 'Altiris_Deployment_TaskServerHandler'
  TASKSERVER_64_INSTALL_NAME = 'Altiris_Deployment_TaskServerHandler_x64'
  MAIN_INSTALL_NAME = 'Altiris_Deployment'
  MAIN_64_INSTALL_NAME = 'Altiris_Deployment_x64'
  WINPE_INSTALL_86_NAME = 'altiris_ns_winpe2.1'
  WINPE_64_INSTALL_86_NAME = 'altiris_ns_winpe2.1_x64'
  WINPE_INSTALL_64_NAME = 'altiris_ns_winpe2.1_86_x64'
  WINPE_64_INSTALL_64_NAME = 'altiris_ns_winpe2.1_64_x64'
  GPL_INSTALL_86_NAME = 'altiris_ns_linux_gpl'
  GPL_INSTALL_64_NAME = 'altiris_ns_linux_gpl_x64'
  DRVRDB_INSTALL_86_NAME = 'Altiris_NS_DriversDB'
  DRVRDB_INSTALL_64_NAME = 'Altiris_NS_DriversDB_x64'
  #TS_HOTFIX_NAME = 'Altiris_Deployment_TaskServerHandler_KB_HF'

  AGENT_INSTALL_DIR = r'%s\apps\DeploymentClient\install' % top
  TASKSERVER_INSTALL_DIR = r'%s\apps\DeploymentServer\install' % top
  SOLUTION_INSTALL_DIR = r'%s\apps\DeploymentInstall' % top
  WINPE_INSTALL_DIR = r'%s\apps\DeploymentInstall' % top
  GPL_INSTALL_DIR = r'%s\apps\DeploymentInstall' % top
  DRVRDB_INSTALL_DIR = r'%s\apps\DeploymentInstall' % top

  AGENT_INSTALL_SCRIPT = r'%s\%s.wsi' % (AGENT_INSTALL_DIR, AGENT_INSTALL_NAME)
  AGENT_64_INSTALL_SCRIPT = r'%s\%s.wsi' % (AGENT_INSTALL_DIR, AGENT_64_INSTALL_NAME)
  #AGENT__86_64_INSTALL_SCRIPT = r'%s\%s.wsi' % (AGENT_INSTALL_DIR, AGENT_86_INSTALL_64_NAME)
  TASKSERVER_INSTALL_SCRIPT = r'%s\%s.wsi' % (TASKSERVER_INSTALL_DIR, TASKSERVER_INSTALL_NAME)
  TASKSERVER_64_INSTALL_SCRIPT = r'%s\%s.wsi' % (TASKSERVER_INSTALL_DIR, TASKSERVER_64_INSTALL_NAME)
  MAIN_INSTALL_SCRIPT = r'%s\%s.wsi' % (SOLUTION_INSTALL_DIR, MAIN_INSTALL_NAME)
  MAIN_64_INSTALL_SCRIPT = r'%s\%s.wsi' % (SOLUTION_INSTALL_DIR, MAIN_64_INSTALL_NAME)
  WINPE_86_INSTALL_SCRIPT = r'%s\%s.wsi' % (WINPE_INSTALL_DIR, WINPE_INSTALL_86_NAME)
  WINPE_64_86_INSTALL_SCRIPT = r'%s\%s.wsi' % (WINPE_INSTALL_DIR, WINPE_64_INSTALL_86_NAME)
  WINPE_86_64_INSTALL_SCRIPT = r'%s\%s.wsi' % (WINPE_INSTALL_DIR, WINPE_INSTALL_64_NAME)
  WINPE_64_64_INSTALL_SCRIPT = r'%s\%s.wsi' % (WINPE_INSTALL_DIR, WINPE_64_INSTALL_64_NAME)
  GPL_INSTALL_86_SCRIPT = r'%s\%s.wsi' % (GPL_INSTALL_DIR, GPL_INSTALL_86_NAME)
  GPL_INSTALL_64_SCRIPT = r'%s\%s.wsi' % (GPL_INSTALL_DIR, GPL_INSTALL_64_NAME)
  DRVRDB_INSTALL_86_SCRIPT = r'%s\%s.wsi' % (DRVRDB_INSTALL_DIR, DRVRDB_INSTALL_86_NAME)
  DRVRDB_INSTALL_64_SCRIPT = r'%s\%s.wsi' % (DRVRDB_INSTALL_DIR, DRVRDB_INSTALL_64_NAME)
  #TS_HOTFIX_INSTALL_SCRIPT = r'%s\%s.wsi' % (TASKSERVER_INSTALL_DIR, TS_HOTFIX_NAME)

  AGENT_INSTALL_MSI = r'%s\Altiris_DeploymentSolutionAgent_7_1_x86.msi' % (AGENT_INSTALL_DIR)
  AGENT_64_INSTALL_MSI = r'%s\Altiris_DeploymentSolutionAgent_7_1_x64.msi' % (AGENT_INSTALL_DIR)
  #AGENT_86_INSTALL_64_MSI = r'%s\Altiris_DeploymentSolutionAgent_7_1_86_x64.msi' % (AGENT_INSTALL_DIR)
  TASKSERVER_INSTALL_MSI = r'%s\Altiris_DeploymentSolutionTaskServerHandler_7_1_x86.msi' % (TASKSERVER_INSTALL_DIR)
  TASKSERVER_64_INSTALL_MSI = r'%s\Altiris_DeploymentSolutionTaskServerHandler_7_1_x64.msi' % (TASKSERVER_INSTALL_DIR)
  MAIN_INSTALL_MSI = r'%s\Altiris_DeploymentSolution_7_1_x86.msi' % (SOLUTION_INSTALL_DIR)
  MAIN_64_INSTALL_MSI = r'%s\Altiris_DeploymentSolution_7_1_x64.msi' % (SOLUTION_INSTALL_DIR)
  WINPE_INSTALL_x86_MSI = r'%s\Altiris_NSWINPE_7_1_86_x86.msi' % (WINPE_INSTALL_DIR)
  WINPE_64_INSTALL_86_MSI = r'%s\Altiris_NSWINPE_7_1_64_x86.msi' % (WINPE_INSTALL_DIR)
  WINPE_INSTALL_x64_MSI = r'%s\Altiris_NSWINPE_7_1_86_x64.msi' % (WINPE_INSTALL_DIR)
  WINPE_64_INSTALL_64_MSI = r'%s\Altiris_NSWINPE_7_1_64_x64.msi' % (WINPE_INSTALL_DIR)
  GPL_INSTALL_86_MSI = r'%s\Altiris_NSLINUX_7_1_x86.msi' % (GPL_INSTALL_DIR)
  GPL_INSTALL_64_MSI = r'%s\Altiris_NSLINUX_7_1_x64.msi' % (GPL_INSTALL_DIR)
  DRVRDB_INSTALL_86_MSI = r'%s\Altiris_DriversDatabase_7_1_x86.msi' % (DRVRDB_INSTALL_DIR)
  DRVRDB_INSTALL_64_MSI = r'%s\Altiris_DriversDatabase_7_1_x64.msi' % (DRVRDB_INSTALL_DIR)
  #TS_HOTFIX_INSTALL_MSI = r'%s\Altiris_DeploymentSolutionTaskServerHandler_7_1_KB_HF1_x86.msi' % (TASKSERVER_INSTALL_DIR)

  COPY_TO_PREBOOT_TASKFILES = [
    r'%s\output_win_x86\ClientImaging\release\ClientImaging.dll' % top,
    r'%s\output_win_x86\ClientImagingPrep\release\ClientImagingPrep.dll' % top,
    r'%s\build\ns\dll\BaseTaskHandlers.dll' % top,
    r'%s\output_win_x86\DeploymentSolutionAgent\release\DeploymentSolutionAgent.dll' % top,
    r'%s\output_win_x86\ClientCaptureImage\release\ClientCaptureImage.dll' % top,
    r'%s\output_win_x86\ClientCopyFile\release\ClientCopyFile.dll' % top,
    r'%s\output_win_x86\ClientDeployAnywhere\release\ClientDeployAnywhere.dll' % top,
    r'%s\output_win_x86\ClientImageDeploy\release\ClientImageDeploy.dll' % top,
    r'%s\output_win_x86\ClientInitialDeployment\release\ClientInitialDeployment.dll' % top,
    r'%s\output_win_x86\ClientPartitionDisk\release\ClientPartitionDisk.dll' % top,
    r'%s\output_win_x86\ClientPreImage\release\ClientPreImage.dll' % top,
    r'%s\output_win_x86\ClientRebootTo\release\ClientRebootTo.dll' % top,
    r'%s\output_win_x86\ClientSOI\release\ClientSOI.dll' % top,
    r'%s\output_win_x86\ClientWipe\release\ClientWipe.dll' % top,
    r'%s\output_win_x86\ClientRiloPowerMgmt\release\ClientRiloPowerMgmt.dll' % top
    ]

  COPY_TO_PREBOOT_TASKFILES_X64 = [
    r'%s\output_win_x64\ClientImagingPrep\release\ClientImagingPrep.dll' % top,
    r'%s\build\ns\x64dll\BaseTaskHandlers.dll' % top,
    r'%s\output_win_x64\ClientImaging\release\ClientImaging.dll' % top,
    r'%s\output_win_x64\DeploymentSolutionAgent\release\DeploymentSolutionAgent.dll' % top,
    r'%s\output_win_x64\ClientCaptureImage\release\ClientCaptureImage.dll' % top,
    r'%s\output_win_x64\ClientCopyFile\release\ClientCopyFile.dll' % top,
    r'%s\output_win_x64\ClientDeployAnywhere\release\ClientDeployAnywhere.dll' % top,
    r'%s\output_win_x64\ClientImageDeploy\release\ClientImageDeploy.dll' % top,
    r'%s\output_win_x64\ClientInitialDeployment\release\ClientInitialDeployment.dll' % top,
    r'%s\output_win_x64\ClientPartitionDisk\release\ClientPartitionDisk.dll' % top,
    r'%s\output_win_x64\ClientPreImage\release\ClientPreImage.dll' % top,
    r'%s\output_win_x64\ClientRebootTo\release\ClientRebootTo.dll' % top,
    r'%s\output_win_x64\ClientSOI\release\ClientSOI.dll' % top,
    r'%s\output_win_x64\ClientWipe\release\ClientWipe.dll' % top,
    r'%s\output_win_x64\ClientRiloPowerMgmt\release\ClientRiloPowerMgmt.dll' % top
    ]

  SIGN_FILES_x86CPP = [
  #x86cpp binaries
    r'%s\output_win_x86\ClientConfiguration\release\ClientConfiguration.dll' % top,
    r'%s\output_win_x86\ClientImaging\release\ClientImaging.dll' % top,
    r'%s\output_win_x86\ClientImagingPrep\release\ClientImagingPrep.dll' % top,
    r'%s\output_win_x86\ClientPCT\release\ClientPCT.dll' % top,
    r'%s\output_win_x86\ClientRebootTo\release\ClientRebootTo.dll' % top, 
    r'%s\output_win_x86\ClientWipe\release\ClientWipe.dll' % top,
    r'%s\output_win_x86\ClientInitialDeployment\release\ClientInitialDeployment.dll' % top,
    r'%s\output_win_x86\ConfigService\release\ConfigService.exe' % top,
    r'%s\output_win_x86\DeploymentSolutionAgent\release\DeploymentSolutionAgent.dll' % top,
    r'%s\output_win_x86\ClientBCDEdit\release\ClientBCDEdit.dll' % top,
    r'%s\output_win_x86\ClientCaptureImage\release\ClientCaptureImage.dll' % top,
    r'%s\output_win_x86\ClientDeployAnywhere\release\ClientDeployAnywhere.dll' % top,
    r'%s\output_win_x86\ClientPreImage\release\ClientPreImage.dll' % top,
    r'%s\output_win_x86\ClientSOI\release\ClientSOI.dll' % top,
    r'%s\output_win_x86\ClientImageDeploy\release\ClientImageDeploy.dll' % top,
    r'%s\output_win_x86\ClientCopyFile\release\ClientCopyFile.dll' % top,
    r'%s\output_win_x86\ClientPartitionDisk\release\ClientPartitionDisk.dll' % top,
    r'%s\output_win_x86\ClientConfigPXEServer\release\ClientConfigPXEServer.dll' % top,
    r'%s\output_win_x86\ClientPrebootPolicyChecker\release\ClientPrebootPolicyChecker.dll' % top,
    r'%s\output_win_x86\ClientPXEImage\release\ClientPXEImage.dll' % top,
    r'%s\output_win_x86\ClientUpdateSbsClientInfo\release\ClientUpdateSbsClientInfo.dll' % top,
    r'%s\output_win_x86\ClientRiloPowerMgmt\release\ClientRiloPowerMgmt.dll' % top,
    r'%s\output_win_x86\SbsNSInterface\release\SbsNSInterface.exe' % top,
    r'%s\output_win_x86\CreateDSShare\release\CreateDSShare.exe' % top,
    r'%s\output_win_x86\PECTAgent\release\PECTAgent.exe' % top, #rem unrem this when the PECTAgent.exe is compiled again
    r'%s\distrib\config\config.dll' % top
    ]
  SIGN_FILES_x86CS = [
  # x86cs binaries
    r'%s\output_win\TaskServerHandler\release\TaskServerHandler.dll' % top,
    r'%s\output_win\TaskServerHandler\release\policy.7.1.TaskServerHandler.dll' % top,
    r'%s\output_win\Altiris.Deployment\release\Altiris.Deployment.dll' % top,
    r'%s\output_win\Altiris.Deployment\release\policy.7.1.Altiris.Deployment.dll' % top,
    r'%s\output_win\Altiris.Deployment.Common\release\Altiris.Deployment.Common.dll' % top,
    r'%s\output_win\Altiris.Deployment.Common\release\policy.7.1.Altiris.Deployment.Common.dll' % top,
    r'%s\output_win\Altiris.Deployment.Web\release\Altiris.Deployment.Web.dll' % top,
    r'%s\output_win\Altiris.Deployment.Web.Services\release\Altiris.Deployment.Web.Services.dll' % top,
    r'%s\output_win\RemoteTrace\release\RemoteTrace.exe' % top,
    r'%s\output_win\Altiris.Deployment.Utility\release\Altiris.Deployment.Utility.dll' % top,
    r'%s\output_win\Altiris.Deployment.Utility\release\policy.7.1.Altiris.Deployment.Utility.dll' % top
    ]
  SIGN_FILES_x64CPP = [
  # x64 binaries
    r'%s\output_win_x64\PECTAgent\release\PECTAgent.exe' % top,
    r'%s\output_win_x64\ClientBCDEdit\release\ClientBCDEdit.dll' % top,
    r'%s\output_win_x64\ClientConfigPXEServer\release\ClientConfigPXEServer.dll' % top,
    r'%s\output_win_x64\ClientConfiguration\release\ClientConfiguration.dll' % top,
    r'%s\output_win_x64\ClientImaging\release\ClientImaging.dll' % top,
    r'%s\output_win_x64\ClientImagingPrep\release\ClientImagingPrep.dll' % top,
    r'%s\output_win_x64\ClientPCT\release\ClientPCT.dll' % top,
    r'%s\output_win_x64\ClientPreImage\release\ClientPreImage.dll' % top,
    r'%s\output_win_x64\ClientPrebootPolicyChecker\release\ClientPrebootPolicyChecker.dll' % top,
    r'%s\output_win_x64\ClientPXEImage\release\ClientPXEImage.dll' % top,
    r'%s\output_win_x64\ClientUpdateSbsClientInfo\release\ClientUpdateSbsClientInfo.dll' % top,
    r'%s\output_win_x64\ClientRiloPowerMgmt\release\ClientRiloPowerMgmt.dll' % top,
    r'%s\output_win_x64\ConfigService\release\ConfigService.exe' % top,
    r'%s\output_win_x64\CreateDSShare\release\CreateDSShare.exe' % top,
    r'%s\output_win_x64\SbsNSInterface\release\SbsNSInterface.exe' % top,
    r'%s\output_win_x64\DeploymentSolutionAgent\release\DeploymentSolutionAgent.dll' % top,
    r'%s\output_win_x64\ClientCaptureImage\release\ClientCaptureImage.dll' % top,
    r'%s\output_win_x64\ClientCopyFile\release\ClientCopyFile.dll' % top,
    r'%s\output_win_x64\ClientDeployAnywhere\release\ClientDeployAnywhere.dll' % top,
    r'%s\output_win_x64\ClientImageDeploy\release\ClientImageDeploy.dll' % top,
    r'%s\output_win_x64\ClientInitialDeployment\release\ClientInitialDeployment.dll' % top,
    r'%s\output_win_x64\ClientPartitionDisk\release\ClientPartitionDisk.dll' % top,
    r'%s\output_win_x64\ClientPreImage\release\ClientPreImage.dll' % top,
    r'%s\output_win_x64\ClientRebootTo\release\ClientRebootTo.dll' % top,
    r'%s\output_win_x64\ClientSOI\release\ClientSOI.dll' % top,
    r'%s\output_win_x64\ClientWipe\release\ClientWipe.dll' % top
    ]

  SIGN_MSI = [
    r'%s\apps\DeploymentServer\install\Altiris_DeploymentSolutionTaskServerHandler_7_1_x64.msi' % top,
    r'%s\apps\DeploymentServer\install\Altiris_DeploymentSolutionTaskServerHandler_7_1_x86.msi' % top,
    r'%s\apps\DeploymentInstall\Altiris_DeploymentSolution_7_1_x64.msi' % top,
    #r'%s\apps\DeploymentInstall\Altiris_DeploymentSolution_7_1_x86.msi' % top,
    r'%s\apps\DeploymentClient\install\Altiris_DeploymentSolutionAgent_7_1_x86.msi' % top,
    r'%s\apps\DeploymentClient\install\Altiris_DeploymentSolutionAgent_7_1_x64.msi' % top,
    #r'%s\apps\DeploymentClient\install\Altiris_DeploymentSolutionAgent_7_1_86_x64.msi' % top,
    r'%s\apps\DeploymentInstall\Altiris_NSWINPE_7_1_86_x86.msi' % top,
    r'%s\apps\DeploymentInstall\Altiris_NSWINPE_7_1_64_x86.msi' % top,
    r'%s\apps\DeploymentInstall\Altiris_NSWINPE_7_1_86_x64.msi' % top,
    r'%s\apps\DeploymentInstall\Altiris_NSWINPE_7_1_64_x64.msi' % top,
    r'%s\apps\DeploymentInstall\Altiris_NSLINUX_7_1_x86.msi' % top,
    r'%s\apps\DeploymentInstall\Altiris_NSLINUX_7_1_x64.msi' % top,
    #r'%s\apps\DeploymentInstall\Altiris_DriversDatabase_7_1_x86.msi' % top,
    r'%s\apps\DeploymentInstall\Altiris_DriversDatabase_7_1_x64.msi' % top
    #r'%s\apps\DeploymentServer\install\Altiris_DeploymentSolutionTaskServerHandler_7_1_KB_HF1_x86.msi' % top
    ]

  Check_List = [
    top + '\\distrib\\bootwiz\\Bootwiz.exe',
    top + '\\distrib\\bootwiz\\bootwiz.ini',
    top + '\\distrib\\bootwiz\\default.bdc',
    top + '\\distrib\\bootwiz\\BDC_Engine.dll',
    top + '\\distrib\\SBS\\RpcDll.dll',
    top + '\\distrib\\SBS\\SbsMtftp.exe',
    top + '\\distrib\\SBS\\SbsNSiFace.dll',
    top + '\\distrib\\SBS\\SbsNSiSignal.exe',
    top + '\\distrib\\SBS\\SbsParsePxe.dll',
    top + '\\distrib\\SBS\\SbsServer.exe',
    top + '\\distrib\\SBS_x64\\RpcDll.dll',
    top + '\\distrib\\SBS_x64\\SbsMtftp.exe',
    top + '\\distrib\\SBS_x64\\SbsNSiFace.dll',
    top + '\\distrib\\SBS_x64\\SbsNSiSignal.exe',
    top + '\\distrib\\SBS_x64\\SbsParsePxe.dll',
    top + '\\distrib\\SBS_x64\SbsServer.exe',
    top + '\\distrib\\imaging\\rdeploy\\rdeploy.exe',
    top + '\\distrib\\imaging\\rdeploy\\rdeployt.exe',
    top + '\\distrib\\imaging\\rdeploy\\firm.exe',
    top + '\\distrib\\imaging\\rdeploy\\atrsimg.dll',
    top + '\\distrib\\imaging\\rdeploy\\makeimx.exe',
    top + '\\distrib\\imaging\\rdeploy\\x86\\rdeploy.exe',
    top + '\\distrib\\imaging\\rdeploy\\x86\\rdeployt.exe',
    top + '\\distrib\\imaging\\rdeploy\\x86\\firm.exe',
    top + '\\distrib\\imaging\\rdeploy\\x86\\atrsimg.dll',
    top + '\\distrib\\imaging\\rdeploy\\x86\\makeimx.exe',
    top + '\\distrib\\imaging\\rdeploy\\x64\\rdeploy.exe',
    top + '\\distrib\\imaging\\rdeploy\\x64\\rdeployt.exe',
    top + '\\distrib\\imaging\\rdeploy\\x64\\firm.exe',
    top + '\\distrib\\imaging\\rdeploy\\x64\\atrsimg.dll',
    top + '\\distrib\\imaging\\rdeploy\\x64\\makeimx.exe',
    top + '\\distrib\\imaging\\rdeploy\\Linux\\x86\\makeimx',
    top + '\\distrib\\imaging\\rdeploy\\Linux\\x86\\rdeployt',
    top + '\\distrib\\imaging\\rdeploy\\Linux\\x86\\firm',
    top + '\\distrib\\imaging\\rdeploy\\Linux\\x86\\fscs',
    top + '\\distrib\\imaging\\rdeploy\\Linux\\x64\\makeimx',
    top + '\\distrib\\imaging\\rdeploy\\Linux\\x64\\rdeployt',
    top + '\\distrib\\imaging\\rdeploy\\Linux\\x64\\firm',
    top + '\\distrib\\imaging\\rdeploy\\Linux\\x64\\fscs',
    top + '\\distrib\\config\\config.dll',
    top + '\\distrib\\config\\x86\\config.dll',
    top + '\\distrib\\config\\x64\\config.dll',
    top + '\\distrib\\PCT\\A2iBuilder.exe',
    top + '\\distrib\\PCT\\A2iEditor.exe',
    top + '\\distrib\\PCT\\PCTEdit.exe',
    top + '\\distrib\\PCT\\PCTWiz.exe'
    ]

  Jar_List = [
  top + r'\common\JavaApplet\CopyFolderFile\plugin.jar',
  top + r'\common\JavaApplet\CopyFolderFile\dist\CopyFolderFile.jar'
  ]

  Jar_SRC = top + r'\common\JavaApplet\CopyFolderFile\dist\CopyFolderFile.jar'
  Jar_DST = top + '\\apps\\DeploymentServer\\Altiris.Deployment.Web\\include\\CopyFolderFile.jar'

  COPY_TO_PREBOOT_NSDLL = [
    r'%s\build\ns\dll\AeXNetComms.dll' % top,
    r'%s\build\ns\dll\AeXNSEvent.dll' % top,
    r'%s\build\ns\dll\Client Task Agent.dll' % top,
    r'%s\build\ns\dll\AeXBasicInventory.dll' % top
    ]

  COPY_TO_PREBOOT_X64NSDLL = [
    r'%s\build\ns\x64dll\Client Task Agent.dll' % top,
    r'%s\build\ns\x64dll\CTAgentUI.dll' % top,
    r'%s\build\ns\x64dll\AeXNetComms.dll' % top,
    r'%s\build\ns\x64dll\AeXNSEvent.dll' % top,
    r'%s\build\ns\x64dll\AeXBasicInventory.dll' % top
    ]

  ZipList = [
    r'%s\distrib\bootwiz.zip' % top,
    r'%s\distrib\config.zip' % top,
    r'%s\distrib\rdeploy.zip' % top,
    r'%s\distrib\linuxgpl.zip' % top,
    r'%s\distrib\SBS.zip' % top,
    r'%s\distrib\SBS_x64.zip' % top,
    r'%s\distrib\PCT.zip' % top
    ]

  #COPY_DSPORTAL_XAP = r'%s\distrib\DSPortal\DSPortal.xap' % top
  #COPY_TO_OUTPUT_XAP = r'%s\output_win\Altiris.Deployment.DSPortal\release' % top

  COPY_TO_PREBOOT_AGENT = r'%s\output_win_x86\PECTAgent\release\PECTAgent.exe' % top
  COPY_TO_PREBOOT_AGENT_X64 = r'%s\output_win_x64\PECTAgent\release\PECTAgent.exe' % top

  COPY_TO_PREBOOT_DEST_TASKSFOLDER = r'%s\OEM\DS\winpe2\x86\Base\Program Files\Altiris\Altiris Agent\Agents\Agent Tasks' % top
  COPY_TO_PREBOOT_DEST_AGENTFOLDER = r'%s\OEM\DS\winpe2\x86\Base\Program Files\Altiris\Altiris Agent' % top
  COPY_TO_PREBOOT_DEST_TASKSFOLDER_X64 = r'%s\OEM\DS\winpe2\x64\Base\Program Files\Altiris\Altiris Agent\Agents\Agent Tasks' % top
  COPY_TO_PREBOOT_DEST_AGENTFOLDER_X64 = r'%s\OEM\DS\winpe2\x64\Base\Program Files\Altiris\Altiris Agent' % top

  # removed MAIN_INSTALL_MSI and DRVRDB_INSTALL_86_MSI from package x86 till we are told to support NS as a x86 system again
  packages = {
    'x86':(AGENT_INSTALL_MSI, TASKSERVER_INSTALL_MSI, WINPE_INSTALL_x86_MSI, WINPE_64_INSTALL_86_MSI, GPL_INSTALL_86_MSI),
    'x64':(AGENT_64_INSTALL_MSI, TASKSERVER_64_INSTALL_MSI, MAIN_64_INSTALL_MSI, WINPE_INSTALL_x64_MSI, WINPE_64_INSTALL_64_MSI, GPL_INSTALL_64_MSI, DRVRDB_INSTALL_64_MSI)
  }

  destinationDirectories = {
    'builddev':r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\%MAJOR%.%MINOR%.%BUILD%.0\%PACKAGE%',
    'scratch' :r'\\linus-scratch.altiris.com\Scratch\From_Polaris\DeploymentSolution\Builds\trunk\%MAJOR%.%MINOR%.%BUILD%.0\%PACKAGE%',
    # 'india'   :r'\\192.168.232.12\ForAltiris\Provisioning_Builds\Latest\%MAJOR%.%MINOR%.%BUILD%.0\%PACKAGE%'
    #'local' :r'C:\DS_Builds\trunk\%MAJOR%.%MINOR%.%BUILD%.0\%PACKAGE%'
	}

except BuildError, e:
  fail(e.msg)

def RemoveFile(path):
  if os.path.exists(path):
    os.remove(path)

def removeMSIs():
  """cleans up msi and log files"""  
  installDirs = [AGENT_INSTALL_DIR, TASKSERVER_INSTALL_DIR, SOLUTION_INSTALL_DIR, WINPE_INSTALL_DIR, GPL_INSTALL_DIR, DRVRDB_INSTALL_DIR]
  for installDir in installDirs:
    for path, dirs, files in os.walk(installDir):
      for msi in [os.path.join(path, filename) for filename in files if fnmatch.fnmatch(filename, '*.msi') or fnmatch.fnmatch(filename, '*.log')]:
        RemoveFile(msi)

def ChngMod():
#changes the read-only files created by Silverlight scons for clean-up
  for path, dirs, files in os.walk(r'%s\\output_win\\Altiris.Deployment.DSPortal' %(top)):
    for file in files:
      tarFiles = abspath(join(path, file))
      print "Accessing", tarFiles
      os.chmod(tarFiles, stat.S_IWRITE)

def removeBinaries():
  """deletes output_win directory"""
  for path in (r'%s\output_win' % top,r'%s\output_win_x86' % top, r'%s\output_win_x64' % top, r'%s\distrib\SBS' % top, r'%s\distrib\SBS_x64' % top, r'%s\distrib\bootwiz' % top, r'%s\distrib\PCT' % top, r'%s\distrib\config' % top, r'%s\distrib\Linux_gpl' % top, r'%s\distrib\imaging\rdeploy' % top,):
    if os.path.exists(path):
      shutil.rmtree(path, ignore_errors=True)

def removeBuildfiles():
  """removes .sconsign.dblite and Deployment.dsw before starting next build"""
  RemoveFile(r'%s\.sconsign.dblite' % top)

def CheckFile(files):
  for file in files:
    if os.path.isfile(file):
      # ver_parser = Dispatch('Scripting.FileSystemObject')
      # info = ver_parser.GetFileVersion(file)
      # if info == 'No Version Information Available':
        print  file, "available for build"
      # else:
        # print 'accessing', file, 'version = ',  info
    else:
      print file, "doesn't exist"
      sys.exit(1)

def CheckGPL():
  GPL_SRC = top + '\\distrib\\Linux_gpl'
  for file in glob.glob(GPL_SRC + r'\*.frm'):
    if os.path.isfile(file):
      # ver_parser = Dispatch('Scripting.FileSystemObject')
      # info = ver_parser.GetFileVersion(file)
      # if info == 'No Version Information Available':
        print  file, "available for build"
      # else:
        # print 'accessing', file, 'version = ',  info
    else:
      print file, "doesn't exist"
      sys.exit(1)

def buildDotNet():
#  build('x86cs')
  build('90x86cs')
  build('90x86sl')

def buildAll():
  buildDotNet()
  #build('x86cpp')
  build('90x86cpp')
  build('90x64cpp')

def build(goParameter, options=''):
  build = 'scons version=' + version + ' ' + options
  Execute(top, 'go.bat ' + goParameter + ' & ' + build)

def buildMSI(msiCommand, scriptPath):
  Execute(top, msiCommand % scriptPath)
  scriptPathParts = scriptPath.split('\\')
  scriptParent = '\\'.join(scriptPathParts[:-1])
  print 'MSI creation log:'
  Execute(top, 'type ' + scriptParent + '\\compile.log')

def buildAgentMSIs():
  msiCommand = '"' + GetWisePath() + r'" /c %s /p ProductVersion=' + version
  print 'Creating Agent MSI\'s...', msiCommand
  buildMSI(msiCommand, AGENT_INSTALL_SCRIPT)
  buildMSI(msiCommand, AGENT_64_INSTALL_SCRIPT)
  #buildMSI(msiCommand, AGENT__86_64_INSTALL_SCRIPT)
  print 'Agent MSI creation complete.'

def buildPrebootMSI():
  msiCommand = '"' + GetWisePath() + r'" /c %s /p ProductVersion=' + version
  print 'Creating x64 MSI\'s...', msiCommand
  buildMSI(msiCommand, WINPE_86_64_INSTALL_SCRIPT)
  buildMSI(msiCommand, WINPE_64_64_INSTALL_SCRIPT)
  buildMSI(msiCommand, GPL_INSTALL_64_SCRIPT)
  buildMSI(msiCommand, WINPE_86_INSTALL_SCRIPT)
  buildMSI(msiCommand, WINPE_64_86_INSTALL_SCRIPT)
  buildMSI(msiCommand, GPL_INSTALL_86_SCRIPT)
  print 'WinPE and GPL MSI creation complete.'

def buildTSHMSI():
  msiCommand = '"' + GetWisePath() + r'" /c %s /p ProductVersion=' + version
  print 'Creating x86 MSI\'s...', msiCommand
  buildMSI(msiCommand, TASKSERVER_INSTALL_SCRIPT)
  buildMSI(msiCommand, TASKSERVER_64_INSTALL_SCRIPT)
  print 'Task Server Handler MSI creation complete.'

def buildx86MSIs():
  msiCommand = '"' + GetWisePath() + r'" /c %s /p ProductVersion=' + version
  print 'Creating x86 MSI\'s...', msiCommand
  buildMSI(msiCommand, MAIN_INSTALL_SCRIPT)
  buildMSI(msiCommand, DRVRDB_INSTALL_86_SCRIPT)
  print 'x86MSI creation complete.'

def buildx64MSIs():
  msiCommand = '"' + GetWisePath() + r'" /c %s /p ProductVersion=' + version
  print 'Creating x64 MSI\'s...', msiCommand
  buildMSI(msiCommand, MAIN_64_INSTALL_SCRIPT)
  buildMSI(msiCommand, DRVRDB_INSTALL_64_SCRIPT)
  print 'x64MSI creation complete.'

def buildMSIs():
  buildAgentMSIs()
  buildPrebootMSI()
  buildTSHMSI()
  #buildx86MSIs()
  buildx64MSIs()

# def buildMSIs():
  # msiCommand = '"' + GetWisePath() + r'" /c %s /p ProductVersion=' + version
  # print 'Creating MSI\'s...', msiCommand
  # buildMSI(msiCommand, AGENT_INSTALL_SCRIPT)
  # buildMSI(msiCommand, AGENT_64_INSTALL_SCRIPT)
  # buildMSI(msiCommand, AGENT__86_64_INSTALL_SCRIPT)  
  # buildMSI(msiCommand, WINPE_86_INSTALL_SCRIPT)
  # buildMSI(msiCommand, WINPE_64_86_INSTALL_SCRIPT)
  # buildMSI(msiCommand, WINPE_86_64_INSTALL_SCRIPT)
  # buildMSI(msiCommand, WINPE_64_64_INSTALL_SCRIPT)
  # buildMSI(msiCommand, GPL_INSTALL_86_SCRIPT)
  # buildMSI(msiCommand, GPL_INSTALL_64_SCRIPT)
  # buildMSI(msiCommand, TASKSERVER_INSTALL_SCRIPT)
  # buildMSI(msiCommand, TASKSERVER_64_INSTALL_SCRIPT)
  # buildMSI(msiCommand, MAIN_INSTALL_SCRIPT)
  # buildMSI(msiCommand, MAIN_64_INSTALL_SCRIPT)
  # buildMSI(msiCommand, DRVRDB_INSTALL_86_SCRIPT)
  # buildMSI(msiCommand, DRVRDB_INSTALL_64_SCRIPT)
  # buildMSI(msiCommand, TS_HOTFIX_INSTALL_SCRIPT)
  # print 'MSI creation complete.'

def copyPrebootFiles():
  if not os.path.exists(COPY_TO_PREBOOT_DEST_TASKSFOLDER):
    os.makedirs(COPY_TO_PREBOOT_DEST_TASKSFOLDER)

  if not os.path.exists(COPY_TO_PREBOOT_DEST_TASKSFOLDER_X64):
    os.makedirs(COPY_TO_PREBOOT_DEST_TASKSFOLDER_X64)

  # if not os.path.exists(COPY_TO_OUTPUT_XAP):
    # os.makedirs(COPY_TO_OUTPUT_XAP)
  
  # copy each task binary
  for prebootFile in COPY_TO_PREBOOT_TASKFILES:
    print "accessing prebootfile"
    Copy(prebootFile, COPY_TO_PREBOOT_DEST_TASKSFOLDER)

  #copy 64 bit Task Binary
  for prebootFile in COPY_TO_PREBOOT_TASKFILES_X64:
    print "accessing prebootfile"
    Copy(prebootFile, COPY_TO_PREBOOT_DEST_TASKSFOLDER_X64)

  #copy each ns dll 
  for prebootFile in COPY_TO_PREBOOT_NSDLL:
    print "accessing prebootfile"
    Copy(prebootFile, COPY_TO_PREBOOT_DEST_AGENTFOLDER)

  #copy each ns 64 bit dll	
  for prebootFile in COPY_TO_PREBOOT_X64NSDLL:
    print "accessing prebootfile"
    Copy(prebootFile, COPY_TO_PREBOOT_DEST_AGENTFOLDER_X64)

  # copy agents
  Copy(COPY_TO_PREBOOT_AGENT, COPY_TO_PREBOOT_DEST_AGENTFOLDER)
  Copy(COPY_TO_PREBOOT_AGENT_X64, COPY_TO_PREBOOT_DEST_AGENTFOLDER_X64)

  # copy xap file
  #Copy(COPY_DSPORTAL_XAP, COPY_TO_OUTPUT_XAP)

def SignFiles(pwd, files):
  global signFiles, top

  if signFiles:
    privateKey = top +'\\build\\verisign\\Authenticode\\mycredentials.pfx'
    sign_tool = top +'\\build\\verisign\\signtool.exe'
    if os.path.exists(privateKey):
      for fileToSign in files:
        if os.path.exists(fileToSign):
          filename = os.path.basename(fileToSign)
          #D:\WORKSPACE\Signtool>signtool.exe sign /f mycredentials.pfx /p ITMSCMDS /t http://timestamp.verisign.com/scripts/timstamp.dll Altiris_DeploymentSolutionLanguages_x64.msi
          cmd2 = sign_tool + ' sign /f ' + privateKey +' /p ' + pwd + ' /t http://timestamp.verisign.com/scripts/timstamp.dll ' + fileToSign
          #cmd = 'build\\verisign\\DoPswd.exe signcode -C build\\verisign\\InetSDK\\bin\\SignCode.exe -spc build\\verisign\\Authenticode\\MyCredentials.spc -v ' + privateKey + ' -a SHA1 -t http://timstamp.verisign.com/scripts/timstamp.dll ' + fileToSign + ' -n "' + filename + '"'
          print 'Running "' + cmd2 + '"...'
          Execute (top, cmd2)
        else:
          print fileToSign + ' does not exist.'

def unzip(path, zip):
  for f in ZipList:
    print "unzipping", f
    zip = zipfile.ZipFile(f, 'r')
    isdir = os.path.isdir
    join = os.path.join
    norm = os.path.normpath
    split = os.path.split
    
    for each in zip.namelist():
      if not each.endswith('/'):
        root, name = split(each)
        directory = norm(join(top, path, root))
        print directory
      if not isdir(directory):
        os.makedirs(directory)
      file(join(directory, name), 'wb').write(zip.read(each))
  zip.close()

def MkBWDirs():
  global top
  #creates the necessary paths for new driver management in Bootwiz.exe
  if not os.path.exists(top + '\\distrib\\bootwiz\\Platforms\\Winpe2\\x86\\Drivers\\custom'):
    os.makedirs(top + '\\distrib\\bootwiz\\Platforms\\Winpe2\\x86\\Drivers\\custom')
  if not os.path.exists(top + '\\distrib\\bootwiz\\Platforms\\Winpe2\\x64\\Drivers\\custom'):
    os.makedirs(top + '\\distrib\\bootwiz\\Platforms\\Winpe2\\x64\\Drivers\\custom')
  if not os.path.exists(top + '\\distrib\\bootwiz\\Platforms\\Linux\\x86\\Drivers'):
    os.makedirs(top + '\\distrib\\bootwiz\\Platforms\\Linux\\x86\\Drivers')
  if not os.path.exists(top + '\\distrib\\bootwiz\\Platforms\\Linux\\x86\\Drivers\\custom'):
    os.makedirs(top + '\\distrib\\bootwiz\\Platforms\\Linux\\x86\\Drivers\\custom')
  if not os.path.exists(top + '\\distrib\\bootwiz\\Platforms\\Linux\\x64\\Drivers'):
    os.makedirs(top + '\\distrib\\bootwiz\\Platforms\\Linux\\x64\\Drivers')
  if not os.path.exists(top + '\\distrib\\bootwiz\\Platforms\\Linux\\x64\\Drivers\\custom'):
    os.makedirs(top + '\\distrib\\bootwiz\\Platforms\\Linux\\x64\\Drivers\\custom')

def GetPackageDir(packageName):
  return 'c:\\temp\\msis\\' + packageName

def ReplacePackageTokens(path, pkgName):
  global version, marketingVersion
  major = marketingVersion.split('.')[0]
  minor = marketingVersion.split('.')[1]
  build = version.split('.')[2]

  tokens = {'%MAJOR%':major, '%MINOR%':minor, '%BUILD%':build, '%PACKAGE%':pkgName}

  newPath = path
  for key in tokens.keys():
    newPath = newPath.replace(key, tokens[key])

  return newPath

def VerifyJarSig(pwd, files):
  global top
  #Command used to verify signature
  #C:\scmtools\jdk1.6.0_14_windows\bin>jarsigner.exe -verify C:\ds\trunk\common\JavaApplet\CopyFolderFile\dist\CopyFolderFile.jar
  #response: jar verified.
  JarSig_Tool = 'C:\\scmtools\\jdk1.6.0_14_windows\\bin\\jarsigner.exe'
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

def CopyJar():
  global top
  #copies r'\common\JavaApplet\CopyFolderFile\dist\CopyFolderFile.jar' to  \apps\DeploymentServer\Altiris.Deployment.Web\include\CopyFolderFile.jar
  print "copy signed jar to \\apps\\DeploymentServer\\Altiris.Deployment.Web\\include\\" 
  if os.path.exists(Jar_DST):
    os.remove(Jar_DST)
  shutil.copy(Jar_SRC, top + '\\apps\\DeploymentServer\\Altiris.Deployment.Web\\include\\')

class FileCopyThread(threading.Thread):
    def __init__ (self, localTop, source, destination, filename):
        threading.Thread.__init__(self)
        self.localTop = localTop
        self.source = source
        self.destination = destination
        self.filename = filename
        self.result = False
        self.resultText = ''

    def run(self):
        roboOptions = '/Z /R:20 /NP'
        if self.filename == '':
            po = subprocess.Popen(self.localTop + '\\build\\scripts\\robocopy ' + self.source + ' ' + self.destination + ' /E ' + roboOptions, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.resultText = 'copying directory ' + self.source + ' to ' + self.destination + '\n' + po.stdout.read()
            self.result = po.wait() == 1
        else:
            po = subprocess.Popen(self.localTop + '\\build\\scripts\\robocopy ' + self.source + ' ' + self.destination + ' ' + self.filename + ' ' + roboOptions, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.resultText = 'copying filename ' + self.source + ' to ' + self.destination + ' ' + self.filename + '\n' + po.stdout.read()
            self.result = po.wait() == 1

        if self.result:
            print 'INFO:' + self.resultText
        else:
            print 'ERROR:' + self.resultText


def CopyFiles(filesToCopy):
    global top
    copyList = []

    for source, destination, filename in filesToCopy:
        current = FileCopyThread(top, source, destination, filename)
        copyList.append(current)
        current.start()

    overallResult = []
    for check in copyList:
        check.join()
        overallResult.append(check.result)

    return overallResult


def copyMSIs():
  global copyAllOutput, copyBuilddevOutputOnly, destinationDirectories, packages

  if copyAllOutput or copyBuilddevOutputOnly:
    print 'Copying MSI\'s...'

    # copy packages to local temp directories
    for packageName in packages.keys():
      pkgFiles = packages[packageName]
      pkgDir = GetPackageDir(packageName)

      # delete and recreate pkgDir
      shutil.rmtree(pkgDir, ignore_errors=1)
      os.makedirs(pkgDir)

      for pkgFile in pkgFiles:
        Copy(pkgFile, pkgDir)

    # Add file paths
    fileList = []
    for destDirKey in destinationDirectories.keys():
      if (copyBuilddevOutputOnly and destDirKey == 'builddev') or not copyBuilddevOutputOnly:
        for packageName in packages.keys():
          sourceDir = GetPackageDir(packageName)
          destinationDir = ReplacePackageTokens(destinationDirectories[destDirKey], packageName)
          shutil.rmtree(destinationDir, ignore_errors=1)
          fileList.append([sourceDir, destinationDir,''])

    print 'Copying files locally...'
    result = CopyFiles([x for x in fileList if 'ForAltiris' not in x[1]])
    print 'Done copying files locally.'
    print 'Copying files to India...'
    result += CopyFiles([x for x in fileList if 'ForAltiris' in x[1]])
    print 'Done copying files to India.'

    if False in result:
      print 'At least one of the MSI copies failed!!!'
    else:
      print 'MSI copying completed successfully.'

def wiseKeyExists():
  hkey = (_winreg.HKEY_CURRENT_USER)
  regpath = (r"Software\Wise Solutions")
  #check to see if registry exists
  try:
    reg = _winreg.OpenKey(hkey,regpath)
  except WindowsError:
    print 'wiseKeyExists = False'
    return False
  print 'wiseKeyExists = True'
  return  True

def GetWisePath():
#read a registry for intalled path of Wise
  if wiseKeyExists() == True:
    wisereg = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r"Software\Wise Solutions\Install\Wise Installation Studio 7")
    wifiPath, type = _winreg.QueryValueEx(wisereg, "WISdir")
    print wifiPath
    _winreg.CloseKey(wisereg)
    wisePath = r'Windows Installer Editor\wfwi.exe'
    print wifiPath + wisePath
    return wifiPath + wisePath
  else:
    print 'Cannot find wise!'
    sys.exit(2)

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
        print "can't access", file, "skipping", file
  for path, dirs, files in os.walk(temp):
    for name in dirs:
      print (os.path.join(path, name))
      try:
        os.rmdir(os.path.join(path, name))
      except:
        print "can't access", name, "skipping", name

def ReplaceFileTokens():
  global version, top
  build = version.split('.')[2]
  fileTokenList = {top + '\\apps\\DeploymentServer\\Deployment\\Config\\Altiris.Deployment_Collections.config':{'%CURRENT_BUILD_NUMBER%':build}}
  fileList = []

  for tokenFile in fileTokenList.keys():
    f = open(tokenFile, 'r')
    content = f.read()
    f.close()
    for token in fileTokenList[tokenFile].keys():
      content = content.replace(token, fileTokenList[tokenFile][token])
    f = open(tokenFile, 'w')
    f.write(content)
    f.close()
    fileList.append(tokenFile)

  return fileList

##
##  Main entry point
##
if __name__ == '__main__':

  try:
    if clean:
      removeMSIs()
      if cleanall:
        #ChngMod()
        removeBinaries()
        removeBuildfiles()
    else:
      CleanTemp()
      ReplaceFileTokens()
      buildAll()
      SignFiles('ITMSCMDS', SIGN_FILES_x86CS)
      SignFiles('ITMSCMDS', SIGN_FILES_x86CPP)
      SignFiles('ITMSCMDS', SIGN_FILES_x64CPP)
      VerifyJarSig('ITMSCMDS', Jar_List)
      copyPrebootFiles()
      CopyJar()
      unzip('', zip)
      MkBWDirs()
      CheckFile(Check_List)
      CheckGPL()
      buildMSIs()
      SignFiles('ITMSCMDS', SIGN_MSI)
      copyMSIs()

  except BuildError, e:
    fail(e.msg)
