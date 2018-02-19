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
from indent import *
import zipfile
from os.path import join, abspath
import stat
import subprocess
import glob
import ftplib
import webbrowser

#Global Variables
top = ''
SolBuild = ''
LPBuild = ''
oldbuild = ''
zip = False

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
--zipit | This switch turns on the zip function of the Solution7.1 directory for submission to WIKI
"""
  rows = [row.strip().split('|') for row in usage.splitlines()]
  print indent(rows, delim='  ', wrapfunc=lambda x: wrap_onspace_strict(x, 40))

def parseArgs(argv):
  global top, SolBuild, LPbuild, zip

  try:
    opts, args = getopt.getopt(argv, 'hz:b:l:t:', ['help', 'zipit', 'buildnum=', 'lpnum=', 'top='])
  except getopt.GetoptError:
    print "Invalid options specified.\n"
    usage()
    sys.exit(2)

  for opt, arg, in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit()
    elif opt in ('--buildnum'):
      SolBuild = arg
    elif opt in ('--lpnum'):
      LPBuild = arg
    elif opt in ('--top'):
      top = arg
    elif opt in ('--zipit'):
      zip = True

  if top == '':
    print 'You must specify --top=<top path>'
    sys.exit(4)

class BuildError(Exception):
  def __init__(self, msg, *args):
    Exception.__init__(self, msg)
    self.msg = msg
    #apply(Exception.__init, (self,) + args)

try:
  # set globals from the command line
  parseArgs(sys.argv[1:])

  #zip information
  SRC_SOL = 'C:\\Solution7.1'
  zipname = SRC_SOL + '.zip'
  FTP_Files = ['C:\\Solution7.1.zip']
  
except BuildError, e:
  fail(e.msg)

def GetBuildNum(dirname):
  return str('0' + ''.join([x for x in dirname if x.isdigit()]))
  
def GetSolBuild():
  global SolBuild, oldbuild
  if SolBuild == '':
    GET_BLD = r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk'
    highBuild = max([GetBuildNum(x) for x in os.listdir(GET_BLD)])
    SolBuild1 = highBuild[3:7]
    SolBuild = int(SolBuild1)
    oldbuild = SolBuild -1
    print "solution build version = ", SolBuild, "and oldbuild = ", oldbuild
    return oldbuild
    return SolBuild

def SolMSICopy():
  global SolBuild, oldbuild
  msi_dst = 'C:\\Solution7.1'
  if not os.path.exists(r'C:\Solution7.1'):
    os.makedirs(r'C:\Solution7.1')
  MSI = [
  #r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x86\Altiris_DeploymentSolution_7_1_x86.msi' % SolBuild,
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x86\Altiris_DeploymentSolutionTaskServerHandler_7_1_x86.msi' % SolBuild,
  #r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x86\Altiris_DriversDatabase_7_1_x86.msi' % SolBuild,
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x86\Altiris_NSLINUX_7_1_x86.msi' % SolBuild,
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x86\Altiris_NSWINPE_7_1_64_x86.msi' % SolBuild,
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x86\Altiris_NSWINPE_7_1_86_x86.msi' % SolBuild,
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x64\Altiris_DeploymentSolution_7_1_x64.msi' % SolBuild,
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x64\Altiris_DeploymentSolutionTaskServerHandler_7_1_x64.msi' % SolBuild,
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x64\Altiris_DriversDatabase_7_1_x64.msi' % SolBuild,
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x64\Altiris_NSLINUX_7_1_x64.msi' % SolBuild,
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x64\Altiris_NSWINPE_7_1_64_x64.msi' % SolBuild,
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\7.1.%s.0\x64\Altiris_NSWINPE_7_1_86_x64.msi' % SolBuild
    ]
  for f in MSI:
    print "Copying", f, "to", msi_dst
    shutil.copy(f, msi_dst)

def LPMsiCopy():
  global LPBuild
  if LPBuild == '':
    GET_BLD = r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\LanguagePacks'
    highestBuild = max([GetBuildNum(x) for x in os.listdir(GET_BLD)])
    print highestBuild
    LPBuild1 = highestBuild[3:7]
    LPBuild = int(LPBuild1)
    print "language pack version = ", LPBuild
  msi_dst = 'C:\\Solution7.1'
  LPMSI = [
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\LanguagePacks\7.1.%s\Altiris_DeploymentSolutionLanguages_7_1_x64.msi' % LPBuild
  #r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\LanguagePacks\7.1.%s\Altiris_DeploymentSolutionLanguages_7_1_x86.msi' % LPBuild
    ]
  for f in LPMSI:
    print "Copying", f, "to", msi_dst
    shutil.copy(f, msi_dst)
  

def RenameOldSol():
  global oldbuild
  src2_dir = 'C:\\Solution7.1'
  dst2_dir = 'C:\\Solution7.1.%s.0' % oldbuild
  src_dir = r'\\builddev\buildtest\DeploymentSolution\Latest_TEST\Hampton\Solution7.1'
  dst_dir = r'\\builddev\buildtest\DeploymentSolution\Latest_TEST\Hampton\Solution7.1.%s.0' % oldbuild
  print "renaming existing Solution7.1 directory to Solution7.1.", oldbuild
  if os.path.exists(src2_dir):
    os.rename(src2_dir, dst2_dir)
  else:
    os.makedirs(src2_dir)
  if os.path.exists(src_dir):
     os.rename(src_dir, dst_dir) 	 

def SOLZipIT(fileList, archive):
  #'fileList' is a list of file names - full path each name 
  #'archive' is the file name for the archive with a full path
  try: 
    a = zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) 
    for f in fileList:
      print "archiving file %s" % (f) 
      a.write(f) 
    a.close() 
    return True 
  except: return False

def dirEntries(dir_name, subdir):
  fileList = []
  #Return a list of file names found in directory 'dir_name' 
  #If 'subdir' is True, recursively access subdirectories under 'dir_name'. 
  #Example usage: fileList = dirEntries(r'H:\TEMP', True) 
  #All files and all the files in subdirectories under H:\TEMP will be added 
  #to the list. 
  for file in os.listdir(dir_name): 
      dirfile = os.path.join(dir_name, file) 
      if os.path.isfile(dirfile): 
         fileList.append(dirfile) 
  # recursively access file names in subdirectories 
      elif os.path.isdir(dirfile) and subdir: 
          print "Accessing directory:", dirfile 
          fileList.extend(dirEntries(dirfile, subdir))

  return fileList

def CopySolution():
  global top
 #copies the local solution7.1 directory to local shares for testing
  Src_dir = 'C:\\Solution7.1'
  builddev = r'\\builddev\buildtest\DeploymentSolution\Latest_TEST\Hampton\Solution7.1'
  roboOptions = '/Z /R:20 /NP /V'
  os.system(top + "\\build\\scripts\\robocopy %s %s %s > robo.log" % (Src_dir, builddev, roboOptions))
  # os.system("C:\\ds\\trunk\\build\\scripts\\robocopy %s %s %s > robo.log" % (Src_dir, scratch, roboOptions))

def UploadFtp(server, user, password, files):
    global top, SolBuild
	#files and function specific variables
    SolDir = '7.1.%s.0' % (SolBuild)
    wkdir = '//cm//ds//Hampton'
	#logon to Ftp
    ftp = ftplib.FTP(server)
    ftp.login (user, password)
    print ftp.getwelcome()
    #get to hampton directory
    ftp.cwd(wkdir)
    print "Currently in:", ftp.pwd()
	#check for directory that we copy file to
    try:
        direxists = ftp.cwd(wkdir + '//' + SolDir)
        ftp.cwd(wkdir + '//' + SolDir)
    except:
        ftp.mkd(SolDir)
        ftp.cwd(wkdir + '//' + SolDir)

    print "Currently in:", ftp.pwd()
    #copy files from list to cwd
    for file in files:
        print file
        filename = os.path.split(file)[1]
	print filename
        ext = os.path.splitext(filename)[1]
        if ext in ('.txt', 'htm', '.html'):
	    print "Uploading...", filename
            ftp.storlines('STOR ' + filename, open(file))
	else:
	    print "Uploading...", filename
	    ftp.storbinary('STOR ' + filename, open(file, "rb"), 1024)
    print ftp.retrlines('LIST')
    ftp.quit()

def ZipCopyScratch():
  global top, SolBuild
  SrcDir = 'C:\\'
  Src_File = 'Solution7.1.zip'
  roboOptions = '/Z /R:20 /NP /V'
  scratch = r'\\linus-scratch.altiris.com\scratch\From_Polaris\DeploymentSolution\Builds\trunk\Solution7.1.%s.0' % SolBuild
  #create Solution build directory on Scratch
  if not os.path.exists(scratch):
    os.makedirs(scratch)
  #Copy Solution.zip to New Directory
  print "Copying: ", Src_File, "to", scratch
  os.system("C:\\ds\\trunk\\build\\scripts\\robocopy %s %s %s > robo.log" % (SrcDir, scratch, Src_File))
  
def CopyGoodXML():
  global top
  PLFILE = 'Altiris Deployment Solution x64.pl.xml'
  DST_XML_PATH = '\\build\\Simpler\\'
  if os.path.exists(top + DST_XML_PATH + PLFILE):
    os.remove(PLFILE)
    shutil.copy(top + '\\build\\Simpler\\1030\\Altiris Deployment Solution x64.pl.xml', top + "\\build\\Simpler\\Altiris Deployment Solution x64.pl.xml")
    os.chmod(top + "\\build\\Simpler\\Altiris Deployment Solution x64.pl.xml", stat.S_IWRITE)

def CleanupZip():
  zip = 'C:\\Solution7.1.zip'
  print "Deleting", zip
  if os.path.exists(zip):
    os.remove(zip)

def CallSimpler():
  global top, SolBuild
  #set environment
  print "/prodver =", SolBuild
 #calls the simple.bat which runs the simple.exe to update the existing good pl.xml Currently good is x64 1017
  cmd =  (' "' + top + '\\build\\scripts\\Simple.bat" ' + top + ' ' + str(SolBuild) + ' > simpbat.log')
  cmdconsole = 'C:\\windows\\system32\\cmd.exe /C'
  print "Calling cmd...", cmdconsole + cmd
  os.system(cmdconsole + cmd)
  if os.path.exists(top + "\\build\\Simpler\\Altiris Deployment Solution x64.pl.xml"):
    os.remove(top + "\\build\\Simpler\\Altiris Deployment Solution x64.pl.xml")

def CopyLic():
  #copies the latest license txt file and Documenation msi into C:\solution7.1 directory
  Lic_Src = top + '\\build\\Simpler\\LicenseFile'
  for file in glob.glob(Lic_Src + r'\*.txt'):
    print "copy License file"
    shutil.copy(file, 'C:\\Solution7.1')

def DocMsiCopy():
 #gets the most recent Documentation msi and copies to C:\Solution7.1
  GET_BLD = r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\Documentation'
  highestBuild = max([GetBuildNum(x) for x in os.listdir(GET_BLD)])
  print highestBuild
  Doc_Bld1 = highestBuild[3:7]
  Doc_Bld = int(Doc_Bld1)
  print "Documentation version = ", Doc_Bld
  msi_dst = 'C:\\Solution7.1'
  Doc_MSI = [
  r'\\builddev\buildtest\DeploymentSolution\Daily_Builds\trunk\Documentation\7.1.%s\Altiris_DeploymentDocumentation_7_1_SP1_x64.msi' % Doc_Bld,
    ]
  for f in Doc_MSI:
    print "Copying", f, "to", msi_dst
    shutil.copy(f, msi_dst)
	

#This is the main program
if __name__ == '__main__':

  try:
    GetSolBuild()
    RenameOldSol()
    SolMSICopy()
    LPMsiCopy()
    DocMsiCopy()
    CopyLic()
    CopyGoodXML()
    CallSimpler()
    CopySolution()
    if zip == True:
      SOLZipIT(dirEntries(SRC_SOL, True), zipname)
      ZipCopyScratch()
      UploadFtp('wiki.epmg.symantec.com', 'cm', 'Iamcm', FTP_Files)
      CleanupZip()

  except BuildError, e:
    fail(e.msg)	