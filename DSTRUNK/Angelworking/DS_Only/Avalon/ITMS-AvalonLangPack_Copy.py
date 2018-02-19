#Copy python script for Language pack plus msi creation call

import fnmatch
import getopt
import os
import shutil
import string
import sys
import time
from buildlib import *
from indent import *
import build
from os.path import join, abspath
import stat
import subprocess
import win32wnet

workspace = os.environ['P4CLIENT']
Build = build.version
top = build.top
MSI_DIR = top + r'\build\LP-2008\Deployment\Deployment\DeploymentSolution_LanguagePack\Release'
dpt_trunk = os.environ['DEPOTTRUNK']

def HasValue(listObj, value):
  for val in listObj:
    if (val == value):
      return True
  return False
  
def Win32Copy(src, dest, reportFail=1):
  """copy a file from src to dest using the Win32 CopyFile API"""
  if sys.platform == 'win32':
    try:
      shutil.copy2(src, dest)
    except IOError:
      if reportFail:
        raise BuildError('Copy %s to %s failed' % (src, dest))

def GetBuildNum(dirname):
  return str('0' + ''.join([x for x in dirname if x.isdigit()]))


def GetBuild():
  global Build, top
  if Build == ' ':
    GET_BLD = r'\\builddev.altiris.com\buildtest\DeploymentSolution\Daily_Builds\trunk'
    highBuild = max([GetBuildNum(x) for x in os.listdir(GET_BLD)])
    Build1 = highBuild[4:8]
    Build2 = int(Build1)
    Build = Build2 + 1
    print "build version = ", Build
  else:
    print "Build number for this build: ", Build
  
def ChngMod():
  global top
#changes the read-only files created by Silverlight scons for clean-up
  for path, dirs, files in os.walk(r'%s\build\LP-2008' % (top)):
    for file in files:
      tarFiles = abspath(join(path, file))
      print "Accessing", tarFiles
      os.chmod(tarFiles, stat.S_IWRITE)
  for path, dirs, files in os.walk(r'%s\output\win' % (top)):
    for file in files:
      tarFiles = abspath(join(path, file))
      print "Accessing", tarFiles
      os.chmod(tarFiles, stat.S_IWRITE)

def CleanBuildPy():
  global top
  #calling build.py to clean up all binaries and distrib extracted zip files
  cleancommand = ('python ' + top + '\\build\\scripts\\build.py ' +'--top='+ top + ' --cleanall')
  print 'Calling', cleancommand
  os.system(cleancommand)

def P4vCheckout():
  global top
  LPFILES = top + '\\build\\LP-2008\\...'
  #checkout LP-2008 modifed in build process
  os.system("p4 -c %s edit %s" % (workspace, LPFILES))
  
def P4Login():
  global workspace, top
  psswd = top + "//build//scripts//p4psswd.txt"
  os.system("p4 login < %s" % (psswd))

def P4vSync():
  #function to sync up the workspace with depot
  global workspace, top
  TRNK = top + "\\..."
  print "syncing", TRNK
  os.system("p4 -c %s sync %s" % (workspace, TRNK))

def P4Submit():
  #function to submit the output_lin directory with a comment of Date and Time of check in
  global workspace, Build, top, dpt_trunk
  LPFILES = dpt_trunk + '\\build\\LP-2008\\...'
  #submit changes
  print "Calling p4 -c %s submit -d '%s' %s " % (workspace, Build, LPFILES)
  os.system("p4 -c %s submit -d '%s' %s " % (workspace, Build, LPFILES))

def FileFilterMatch(file, filters):
  for afilter in filters:
    if fnmatch.fnmatch(file, afilter):
      print 'file: ' + file + ' matches ' + afilter
      return True
  return False

def CleanDirectory(srcDir, destDir, filters, ignoreFiles):	  
  print 'Cleaning directory of relavant files in'
  print destDir

  for path, dirs, files in os.walk(destDir):
    for file in [os.path.join(path, filename) for filename in files if FileFilterMatch(filename, filters)]:  #if fnmatch.fnmatch(filename, '*.cs') or fnmatch.fnmatch(filename, '*.resx')]:
      if (not HasValue(ignoreFiles, file)): #ignoreFiles.has_value(file)):  
        os.remove(file)
	  	  
def FullFileCopy(srcDir, destDir, filters, ignoreFiles):
  print 'Copying build files over'
  print ' From: ' + srcDir
  print ' To: ' + destDir
  #CodeSource_Dir = r'%s\apps\DeploymentServer\Altiris.Deployment' % top 
  #CodeDestination_Dir = r'%s\build\VSBUILD\Deployment\Deployment\Altiris.Deployment' % top
  
  for path, dirs, files in os.walk(srcDir):
    subPath = path.replace(srcDir, '')
    subDestination = destDir + subPath
    for dest, src in [(os.path.join(subDestination, filename), os.path.join(path, filename)) for filename in files if FileFilterMatch(filename, filters)]: #fnmatch.fnmatch(filename, '*.cs') or fnmatch.fnmatch(filename, '*.resx')]:
      if ((os.path.exists(subDestination)) and (not HasValue(ignoreFiles, src))):
        Win32Copy(src, dest)

def ExecBuildLP():
  global Build, top
  #calls the simple.bat which runs the simple.exe to update the existing good pl.xml Currently good is x64 1017
  cmd =  (' "' + top + '\\build\\scripts\\ITMS-AVALONDSLP.bat" ' + top + ' ' + str(Build))
  cmdconsole = 'C:\\windows\\system32\\cmd.exe /C'
  print "Calling cmd...", cmdconsole + cmd
  subprocess.call(cmdconsole + cmd, shell=True)

def wnet_connect(host, username = None, password = None):
	netpath = r'\\builddev.altiris.com\buildtest'
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

def FilesToSign(pwd, dir):
  for path, dirs, files in os.walk(dir):
    for msi in [os.path.join(path, filename) for filename in files if fnmatch.fnmatch(filename, '*.msi')]:
	  msitosign = os.path.join(dir, msi)
	  SignFile(pwd, msitosign)

def SignFile(pwd,file):
  global top
  top = os.environ['WORKSPACE']
  privateKey = top + '\\CM\\Verisign\\mycredentials.pfx'
  sign_tool = top + r'\CM\Verisign\signtool.exe'
  for retry in range(1, 4):
    try:
      cmd = sign_tool + ' sign /f ' + privateKey +' /p ' + pwd + ' /t http://timestamp.verisign.com/scripts/timstamp.dll ' + file
      #cmd = signingToolsDir + '\\DoPswd.exe signcode -C ' + top + '\\CM\\Verisign\\SignCode.exe -spc ' + top + '\\CM\\Verisign\\mycredentials.spc -v ' + privateKey + ' -a SHA1 -t http://timestamp.verisign.com/scripts/timstamp.dll ' + msitosign + ' -n "' + filename + '"'
      print 'Running "' + cmd + '"...'
      Execute (top, cmd)
      break
    except BuildError, e:
      print "Error on attempt (%d)\n" % retry
  else:
    try:
      #sign no timestamp
      cmd1 = sign_tool + ' sign /f ' + privateKey +' /p ' + pwd + ' ' + file
      print 'Running "' + cmd1 + '"...'
      Execute (top, cmd1)
    except BuildError, e:
      raise BuildError("Giving up on ", file, "after (%d) attempts, check to see if the file is an msi." % (retry))

def Rename_LPMSI():
  global MSI_DIR, top
  print 'MSI_DIR = ', MSI_DIR
  print "renaming x86 MSI"
  if os.path.exists(MSI_DIR + '\\Altiris_DeploymentSolutionLanguages_x86.msi'):
    os.rename(MSI_DIR + '\\Altiris_DeploymentSolutionLanguages_x86.msi', MSI_DIR + '\\Altiris_DeploymentSolutionLanguages_7_1_x86.msi')
  print "renaming x64 MSI"
  if os.path.exists(MSI_DIR + '\\Altiris_DeploymentSolutionLanguages_x64.msi'):
    os.rename(MSI_DIR + '\\Altiris_DeploymentSolutionLanguages_x64.msi', MSI_DIR + '\\Altiris_DeploymentSolutionLanguages_7_1_x64.msi')

def Copy_LPMSI():
  global Build, MSI_DIR, top
  print "build version = ", Build
  # Build1 = Build[0:8]
  # print Build1
  BLDLP_DST = r'\\builddev.altiris.com\buildtest\DeploymentSolution\Daily_Builds\Avalon\LanguagePacks\%s' % Build
  if not os.path.exists('C:\\output_msi'):
    os.makedirs('C:\\output_msi')
  if not os.path.exists(BLDLP_DST):
    os.makedirs(BLDLP_DST)
  #copy renamed MSI To output_msi
  print "copying Altiris_DeploymentSolutionLanguages_7_1_x86.msi to C:\\output_msi"
  shutil.copy(MSI_DIR + '\\Altiris_DeploymentSolutionLanguages_7_1_x86.msi', 'C:\\output_msi')
  for path, dirs, files in os.walk(MSI_DIR):
    for msi in [os.path.join(path, filename) for filename in files if fnmatch.fnmatch(filename, '*.msi')]:
      print "copying %s to %s" % (MSI_DIR, BLDLP_DST)
      shutil.copy(msi, BLDLP_DST)  

def CleanupMSI():
  global top
  MSI_DIR = top + r'\build\LP-2008\Deployment\Deployment\DeploymentSolution_LanguagePack\Release'
  for path, dirs, files in os.walk(MSI_DIR):
    for msi in [os.path.join(path, filename) for filename in files if fnmatch.fnmatch(filename, '*.msi')]:
      os.remove(msi)
##
##  Main entry point
##
if __name__ == '__main__':
  try:
    CleanBuildPy()
    print "Cleaning up old Binaries"
    P4Login()
    print "Logging in to PerForce"
    P4vSync()
    print "syncing trunk"
    P4vCheckout()
    print "checking out LP-2008"
    ChngMod()
    print "change Mod on files in LP-2008"
    print "copy files from Trunk\\apps\\DeploymentServer\\ to LP-2008 Solution directories"
    baseProjectSource = r'%s\apps\DeploymentServer' % top 
    baseprojectDestination2k8 = r'%s\build\LP-2008\Deployment\Deployment' % top
	
    mainProjectFilters = [ '*.cs', '*.resx' ]
    webProjectFilters = [ '*.cs', '*.asmx', '*.resx', '*.asax', '*.aspx', '*.config' ]
    DSPortalProjectFilters = [ '*.cs', '*.xaml', '*.resx', '*.png', '.*.xml', '*.PNG' ]
    configProjectFilters = [ '*.config' ]
    DSCommonProjectFilters = [ '*.cs', '*.resx' ]
    DSUtilityProjectFilters = [ '*.cs', '*.resx' ]

    mainProjectSource = baseProjectSource + r'\Altiris.Deployment'
    mainProjectDestination2k8 = baseprojectDestination2k8 + r'\Altiris.Deployment'

    webProjectSource = baseProjectSource + r'\Altiris.Deployment.Web'
    webProjectDestination2k8 = baseprojectDestination2k8 + r'\Altiris.Deployment.Web'

    DSPortalProjectSource = baseProjectSource + r'\Altiris.Deployment.DSPortal'
    DSPortalProjectDestination2k8 = baseprojectDestination2k8 + r'\Altiris.Deployment.DSPortal'	

    DSCommonProjectSource = r'%s\Common' % top
    DSCommonProjectDestination2k8 = baseprojectDestination2k8 + r'\Altiris.Deployment.Common'

    DSUtilityProjectSource = r'%s\Common' % top
    DSUtilityProjectDestination2k8 = baseprojectDestination2k8 + r'\Altiris.Deployment.Utility'	
    
    configProjectSource = baseProjectSource + r'\Deployment\Config'
    configProjectDestination2k8 = baseprojectDestination2k8 + r'\Deployment\Config'
	
    mainProjectIgnoredFiles = [ ]
    configProjectIgnoredFiles = [ ]
    DSPortalProjectIgnoredFiles = [ ]	
    DSCommonProjectIgnoredFiles = [ ]
    DSUtilityProjectIgnoredFiles = [ ]
    webProjectIgnoredFiles = [
      webProjectSource + r'\Services\Altiris.Deployment.Web.Services.csproj', 
      webProjectSource + r'\Services\AssemblyInfo.cs', 
      webProjectSource + r'\Services\SConscript_cs',
      mainProjectSource + r'\Classes\AssemblyInfo.cs'
      ]
    if (len(sys.argv) > 1):
      print 'debug 1'
      commands = sys.argv[1:]
      print commands
      functions = {
        'clean': CleanDirectory,
        'build': FullFileCopy
        }
      for command in commands:
        if (functions.has_key(command.lower())):
          functions[command.lower()](mainProjectSource, mainProjectDestination2k8, mainProjectFilters, mainProjectIgnoredFiles)
          functions[command.lower()](configProjectSource, configProjectDestination2k8, configProjectFilters, configProjectIgnoredFiles)
          functions[command.lower()](webProjectSource, webProjectDestination2k8, webProjectFilters, webProjectIgnoredFiles)
          functions[command.lower()](DSPortalProjectSource, DSPortalProjectDestination2k8, DSPortalProjectFilters, DSPortalProjectIgnoredFiles)
          functions[command.lower()](DSCommonProjectSource, DSCommonProjectDestination2k8, DSCommonProjectFilters, DSCommonProjectIgnoredFiles)
          functions[command.lower()](DSUtilityProjectSource, DSUtilityProjectDestination2k8, DSUtilityProjectFilters, DSUtilityProjectIgnoredFiles)
          if (command.lower() == 'build'):
            build.removeBinaries()
            build.removeBuildfiles()
    else:
      print 'debug 2'
      FullFileCopy(mainProjectSource, mainProjectDestination2k8, mainProjectFilters, mainProjectIgnoredFiles)
      FullFileCopy(configProjectSource, configProjectDestination2k8, configProjectFilters, configProjectIgnoredFiles)
      FullFileCopy(webProjectSource, webProjectDestination2k8, webProjectFilters, webProjectIgnoredFiles)
      FullFileCopy(DSPortalProjectSource, DSPortalProjectDestination2k8, DSPortalProjectFilters, DSPortalProjectIgnoredFiles)
      FullFileCopy(DSCommonProjectSource, DSCommonProjectDestination2k8, DSCommonProjectFilters, DSCommonProjectIgnoredFiles)
      FullFileCopy(DSUtilityProjectSource, DSUtilityProjectDestination2k8, DSUtilityProjectFilters, DSUtilityProjectIgnoredFiles)
      build.removeBinaries()
      build.removeBuildfiles()
    wnet_connect('builddev.altiris.com', username = 'altiris' + '\\' + 'build', password = 'build1')
    GetBuild()
    print "Executing the Extraction, Update and Build of LP build ", Build
    ExecBuildLP()
    Rename_LPMSI()
    FilesToSign('ITMSCMDS', MSI_DIR)
    Copy_LPMSI()
    print "Submit LP files back to Source"
    P4Submit()
    print "Cleaning up MSI and Binaries"
    CleanupMSI()
    CleanBuildPy()

  except BuildError, e:
    fail(e.msg)
