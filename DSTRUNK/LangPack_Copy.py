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

workspace = ' '
Build = build.version

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
  global Build
  top = build.top
  if Build == ' ':
    #GET_BLD = r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk'
    #highBuild = max([GetBuildNum(x) for x in os.listdir(GET_BLD)])
    #Build1 = highBuild[4:8]
    #Build2 = int(Build1)
    #Build = Build2 + 1
    print "build version = ", Build
  else:
    print "Build number for this build: ", Build
  
def ChngMod():
  top = build.top
#changes the read-only files created by Silverlight scons for clean-up
  for path, dirs, files in os.walk(r'%s\\build\LP-2008' %(top)):
    for file in files:
      tarFiles = abspath(join(path, file))
      print "Accessing", tarFiles
      os.chmod(tarFiles, stat.S_IWRITE)
  for path, dirs, files in os.walk(r'%s\\output\win' %(top)):
    for file in files:
      tarFiles = abspath(join(path, file))
      print "Accessing", tarFiles
      os.chmod(tarFiles, stat.S_IWRITE)

def CleanBuildPy():
  #calling build.py to clean up all binaries and distrib extracted zip files
  cleancommand = ('python ' + top + '\\build\\scripts\\build.py ' +'--top='+ top + ' --cleanall')
  print 'Calling', cleancommand
  os.system(cleancommand)

def P4vCheckout():
  top = build.top
  print 'build.top is ', top
  LPFILES = top + '\\build\\LP-2008\\...'
#checkout LP-2008 modifed in build process
  os.system("p4 edit %s" % (LPFILES))
  
def P4Login():
  global workspace, top
  psswd = top + "//build//scripts//p4psswd.txt"
  os.system("p4 login < %s" % (psswd))

def P4vSync():
  #function to sync up the workspace with depot
  global workspace
  top = build.top
  TRNK = top + "\\..."
  print "syncing", TRNK
  os.system("p4 sync %s" % (TRNK))

def P4Submit():
  #function to submit the output_lin directory with a comment of Date and Time of check in
  global workspace, Build
  top = build.top
  LPFILES = top + '\\build\\LP-2008\\...'
  #submit changes
  print "Calling p4 submit -d '%s' %s " % (Build, LPFILES)
  os.system("p4 submit -d '%s' %s " % (Build, LPFILES))

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
  global Build
  top = build.top
 #calls the simple.bat which runs the simple.exe to update the existing good pl.xml Currently good is x64 1017
  cmd =  (' "' + top + '\\build\\scripts\\BuildDSLP.bat" ' + top + ' ' + str(Build) + ' > LP.log')
  cmdconsole = 'C:\\windows\\system32\\cmd.exe /C'
  print "Calling cmd...", cmdconsole + cmd
  subprocess.call(cmdconsole + cmd)
  
def Copy_LPMSI():
  global Build
  top = build.top
  print "build version = ", Build
  Build = Build[0:8]
  print Build
  MSI_DIR = top + r'\build\LP-2008\Deployment\Deployment\DeploymentSolution_LanguagePack\Release'
  #if os.path.isfile(MSI_DIR + '\\Altiris_DeploymentSolutionLanguages_x64_7_1.msi'):
      #os.rename(MSI_DIR + '\\Altiris_DeploymentSolutionLanguages_x64_7_1.msi', MSI_DIR + '\\Altiris_DeploymentSolutionLanguages_7_1_x64.msi')
  print "copy to output_msi for ITMS BUILD"
  if os.path.exists('C:\\output_msi'):
      os.rmdir('C:\output_msi')
  if not os.path.exists('C:\\output_msi'):
      os.makedirs('C:\\output_msi')
  print  "copy MSI To output_msi"
  shutil.copy(MSI_DIR + '\\deploymentsolutionlanguages_x64.msi', 'C:\\output_msi')

def CleanupMSI():
  top=build.top
  MSI_DIR = top + r'\build\LP-2008\Deployment\Deployment\DeploymentSolution_LanguagePack\Release'
  for path, dirs, files in os.walk(MSI_DIR):
    for msi in [os.path.join(path, filename) for filename in files if fnmatch.fnmatch(filename, '*.msi')]:
      os.remove(msi)
##
##  Main entry point
##
if __name__ == '__main__':
  try:
    top = build.top
    CleanBuildPy()
    print "Cleaning up old Binaries"
    P4Login()
    print "Logging in to PerForce"
    #P4vSync()
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
    
    webProjectServicesSource = baseProjectSource + r'\Altiris.Deployment.Web.Services'
    webProjectServicesDestination2k8 = baseprojectDestination2k8 + r'\Altiris.Deployment.Web\Services'

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
    webProjectIgnoredFiles = [ ]
    webServicesProjectIgnoredFiles = [
      webProjectServicesSource + r'\Symantec.Deployment.Web.Services.csproj', 
      webProjectServicesSource + r'\AssemblyInfo.cs', 
      webProjectServicesSource + r'\SConscript_cs',
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
          functions[command.lower()](webProjectServicesSource, webProjectServicesDestination2k8, webProjectFilters, webServicesProjectIgnoredFiles)
          functions[command.lower()](DSPortalProjectSource, DSPortalProjectDestination2k8, DSPortalProjectFilters, DSPortalProjectIgnoredFiles)
          functions[command.lower()](DSCommonProjectSource, DSCommonProjectDestination2k8, DSCommonProjectFilters, DSCommonProjectIgnoredFiles)
          functions[command.lower()](DSUtilityProjectSource, DSUtilityProjectDestination2k8, DSUtilityProjectFilters, DSUtilityProjectIgnoredFiles)
          if (command.lower() == 'build'):
            build.removeBinaries()
            build.removeBuildfiles()
            #build.buildDotNet()

    else:
      print 'debug 2'
      FullFileCopy(mainProjectSource, mainProjectDestination2k8, mainProjectFilters, mainProjectIgnoredFiles)
      FullFileCopy(configProjectSource, configProjectDestination2k8, configProjectFilters, configProjectIgnoredFiles)
      FullFileCopy(webProjectSource, webProjectDestination2k8, webProjectFilters, webProjectIgnoredFiles)
      FullFileCopy(webServicesProjectSource, webProjectServicesDestination2k8, webProjectFilters, webServicesProjectIgnoredFiles)
      FullFileCopy(DSPortalProjectSource, DSPortalProjectDestination2k8, DSPortalProjectFilters, DSPortalProjectIgnoredFiles)
      FullFileCopy(DSCommonProjectSource, DSCommonProjectDestination2k8, DSCommonProjectFilters, DSCommonProjectIgnoredFiles)
      FullFileCopy(DSUtilityProjectSource, DSUtilityProjectDestination2k8, DSUtilityProjectFilters, DSUtilityProjectIgnoredFiles)
      build.removeBinaries()
      build.removeBuildfiles()
      #build.buildDotnet()
    print "Geting Latest Build", Build
    GetBuild()
    print "Executing the Extraction, Update and Build of LP build ", Build
    ExecBuildLP()
    print "copy and rename MSI"
    Copy_LPMSI()
    print "Submit LP files back to Source"
    P4Submit()
    print "Cleaning up MSI and Binaries"
    CleanupMSI()
    CleanBuildPy()

  except BuildError, e:
    fail(e.msg)
