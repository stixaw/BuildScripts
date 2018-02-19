#This py is SBS specific to read the source SBS.have and SBS.want
#to compare with the highest available build form \\rdbuild\builds\trunk and determine if a gather is necessary
#once determined the script will execute a gather of the listed binaries from external build source rdbuild\builds\trunk
#then the script will execute a zipit process to zip the SBS structure for submittion to Perforce
#script will sync, check out and submit the zip file with the build number as the description of the reason
#this script requires a workspace.txt file at the root of C: to gather to workspace for that machine
#Winzip needs to be installed on the machine
#this script requires the --path parameter for  the staging area to copy and do the work, 
#--top to know where the distrib area is located
#To staging area, so when prepare for build or build.py is called the files are available for the MSI

import getopt
import os
import shutil
import sys
from indent import *
import glob
import zipfile

#ugly global variables:
want = ''
have =''
StagingPath = ''
GatherSBS = ''
version = 'latest'
DPT_TRNK = '//depot/Endpoint_Management_Group/notification_server/solutions/deployment_solution/trunk...'
localtrunk = ''
workspace = ''
submit = False
revert = False
#possible parameters for p4
#username = ''
#password = ''
#workspace = ''

#this is for help function to build a commandline
def usage():
  print __doc__
  print """Usage:
SBSGather.py [OPTIONS]

Options:
"""
  usage = """\
--path|path to Drive you want to use for a local distrib by example --path=c:
--top|path to localtrunk example --top=c:\ds\trunk
--workspace|provide the workspace to be used for the local build
Optional input parameters|By default this script will gather all possible Staging files for rdeploy
--revert|off by default, but if called all files that were changed in source by this script will revert in perforce (zipfile)
--submit| off by default this parameter turns on the P4vSubmit function and the Update have functions, only do this when you are sure we are need to update
--version|passes the exact version of rdbuild preboot files that you want, example --version=9234
--help|display help
"""
  rows = [row.strip().split('|') for row in usage.splitlines()]
  print indent(rows, delim='  ', wrapfunc=lambda x: wrap_onspace_strict(x, 40))

def parseArgs(argv):
  global submit, version, StagingPath, localtrunk, revert, workspace

  try:
    opts, args = getopt.getopt(argv, 'hnsrvwp:t', ['help', 'submit', 'revert', 'version=', 'workspace=', 'path=', 'top=',])
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
      print "I am going to copy the binaries to this drive and create the distrib directory there for staging", StagingPath
    elif opt in ('--top'):
      localtrunk = arg
      print "i will be using localtrunk", localtrunk
    elif opt in ('--workspace'):
      workspace = arg
      print "Perforce workspace to sync", workspace
    elif opt in ('--version'):
      version = arg
      print "I will not check have or want but grab this exact version", version
    elif opt in ('--submit'):
      submit = True
      print "I will submit the changed zip file and  update the have"
    elif opt in ('--revert'):
      revert = True
      print "I will revert the changed zipfile."
  if localtrunk == '':
    print 'You must specify local trunk path, example --top=<c:\ds\trunk>'
    sys.exit(4)
  if workspace == '':
    print 'You must specify local workspace, example --workspace=angel-work'
    sys.exit(4)
  if StagingPath == '':
    print 'You must specify the drive for the distrib staging area example --path=C: or --path=d:'
    sys.exit(4)

class BuildError(Exception):
  def __init__(self, msg, *args):
    Exception.__init__(self, msg)
    self.msg = msg
    #apply(Exception.__init, (self,) + args)
try:
  # set globals from the command line
  parseArgs(sys.argv[1:])
	
# Source directory
  SBS_SRC = r'\\rdbuild\builds\trunk\%s\PXE\SBS' % version
  SBS_X64_SRC = r'\\rdbuild\builds\trunk\%s\PXE\SBS_x64' % version
  
# Destination Directory
  SBS_DST = StagingPath + r'\distrib\SBS'
  SBS_X64_DST = StagingPath + r'\distrib\SBS_x64'

# Local paths for distrib, and local workspace trunk
  SBS_LOCAL_DIR = localtrunk + r'\distrib\SBS'
  SBS_X64_LOCAL_DIR = localtrunk + r'\distrib\SBS_x64'
  DSTRIB_LOCAL = localtrunk + r'\distrib'
  
  zipname = SBS_DST +'.zip'
  zipname_X64 = SBS_X64_DST + '.zip'
  SBS_DPT_ZIP = DPT_TRNK + r'/distrib/SBS.zip'
  SBS_X64_DPT_ZIP = DPT_TRNK + r'/distrib/SBS_x64.zip'
  SBS_DPT_HV = DPT_TRNK + r'/distrib/scripts/SBS.have'
  SBS_DPT_WANT = DPT_TRNK + r'/distrib/scripts/SBS.want'

except BuildError, e:
  fail(e.msg)

# def GetBuildNum(dirname):
    # return int('0' + ''.join([x for x in dirname if x.isdigit()]))

def GetVersion():
  global version, localtrunk, GatherSBS, want, have
#check to see if --version provided a version if not then we check SBS.want for what we want.
#open the .want file to see what version is wanted options in this file are latest, build number
#ie if we always want latest we would have latest as first line in that file, if we wanted a rdbuild it would be 9266
#if this comes from a DS build it would be build9226
#Source for version for rdeploy
  GET_BLD =  r'\\rdbuild\builds\trunk'
  if version == 'latest':
    print "this is the value for version", version
    f = open (localtrunk + '\\distrib\\scripts\\SBS.have', 'r')
    have = f.read()
    f.close()
    f = open(localtrunk + '\\distrib\\scripts\\SBS.want', 'r')
    want = f.read()
    f.close()
    if want.strip().lower() == 'latest':
      highestbuild = max([int(x) for x in os.listdir(GET_BLD) if x.isdigit()])
      want = highestbuild
    if [int(want)] != [int(have)]:
      print "1 have =", have, "want =", want
      GatherSBS = True
      version = want
    else:
      print "2 have =", have, "want =", want
      GatherSBS = False
      print "Exiting gather script we have", have, "what we want", want

  else:
    print "I was told to get version", version
    f = open (localtrunk + '\\distrib\\scripts\\SBS.have', 'r')
    have = f.read()
    f.close()
    want = version
    if want != have:
      print "3 have =", have, "want =", want
      GatherSBS = True
    else:
      print "4 have =", have, "want =", want
      GatherSBS = False
      print "Exiting gather script we have", have, "what we want", want

def GetWorkspace():
  global workspace
  #find c:\workspace.txt
  #open and read C:\workspace.txt first line should be the -c workspace name used by that person
  #ie angel-ds is my workspace on SITHLORD-ANGEL
  f = open('c:\\workspace.txt', 'r')
  workspace1 = f.read()
  workspace = workspace1.strip()
  print workspace
  f.close

def CopySBS():
# SBS (x86) tree command because we get all *.* including structure
  print "copying SBS files from", SBS_SRC
  if os.path.exists(SBS_DST):
    shutil.rmtree(SBS_DST)
#copy the directory of SBS to local staging
  print "Copying SBS directory"
  if not os.path.exists("c:\\distrib"):
    os.makedirs("c:\\distrib")
  shutil.copytree(SBS_SRC, SBS_DST)
  print 'deleting SbsNSiSignal.ini'
  if os.path.exists(SBS_DST + '\\SbsNSiSignal.ini'):
    os.remove(SBS_DST + '\\SbsNSiSignal.ini')
  if os.path.exists(SBS_DST + '\\SBSNsiAppData.txt'):
    os.remove(SBS_DST + '\\SBSNsiAppData.txt')
 # SBS (x64) tree command because we get all *.* including structure
  if os.path.exists(SBS_X64_DST):
    shutil.rmtree(SBS_X64_DST)
#copy the directory of SBS to local staging
  print "Copying SBS directory"
  shutil.copytree(SBS_X64_SRC, SBS_X64_DST)
  print 'deleting SbsNSiSignal.ini'
  if os.path.exists(SBS_X64_DST + '\\SbsNSiSignal.ini'):
    os.remove(SBS_X64_DST + '\\SbsNSiSignal.ini')
  if os.path.exists(SBS_X64_DST + '\\SBSNsiAppData.txt'):
    os.remove(SBS_X64_DST + '\\SBSNsiAppData.txt')
 

def UpdateHave():
  global want
#checkout and write to have to match the newly gathered version
  os.system("p4 -c %s edit %s" % (workspace, SBS_DPT_HV))
  f = open (localtrunk + '\\distrib\\scripts\\SBS.have', 'w')
  f.write(str(want))
  f.close()

def P4vSync():
  global workspace
  #sync up the workspace with depot
  #os.system("p4 -p %s sync //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s sync %s" % (workspace, SBS_DPT_ZIP))
  os.system("p4 -c %s sync %s" % (workspace, SBS_X64_DPT_ZIP))
  os.system("p4 -c %s sync %s" % (workspace, SBS_DPT_HV))
  os.system("p4 -c %s sync %s" % (workspace, SBS_DPT_WANT)) 

def P4Login():
  global workspace, localtrunk
  psswd = localtrunk + "//build//scripts//p4psswd.txt"
  os.system("p4 login < %s" % (psswd))

def P4vCheckout():
  global workspace
 #def CheckOut
 #os.system("p4 -p %s edit //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s edit %s" % (workspace, SBS_DPT_ZIP))
  os.system("p4 -c %s edit %s" % (workspace, SBS_X64_DPT_ZIP))

def P4vRevert():
  global workspace
  #os.system("p4 -p %s revert //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s revert %s" % (workspace, SBS_DPT_ZIP))
  os.system("p4 -c %s revert %s" % (workspace, SBS_X64_DPT_ZIP))

def P4vSubmit():
  global workspace, want
  #p4 [g-opts] submit [-r] [-f submitoption] -d description
  #os.system("p4 -p %s submit //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s submit -d %s %s " % (workspace, (str(want)), SBS_DPT_ZIP))
  os.system("p4 -c %s submit -d %s %s " % (workspace, (str(want)), SBS_X64_DPT_ZIP))
  os.system("p4 -c %s submit -d %s %s " % (workspace, (str(want)), SBS_DPT_HV))
 
def CopySBSZip():
#this function grabs the new zip file and copies it to local distrib for checkin
    shutil.copy(zipname, DSTRIB_LOCAL)
    shutil.copy(zipname_X64, DSTRIB_LOCAL)

def SBSZipIT(fileList, archive): 
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

def CleanUP():
#removes the local SBS_DST files from local hard drive
  print "Deleting", zipname
  if os.path.exists(zipname):
    os.remove(zipname)
  print "Deleting", SBS_DST
  if os.path.exists(SBS_DST):
    shutil.rmtree(SBS_DST, ignore_errors=True)
  print "Deleting", zipname_X64
  if os.path.exists(zipname_X64):
    os.remove(zipname_X64)
  print "Deleting", SBS_X64_DST
  if os.path.exists(SBS_X64_DST):
    shutil.rmtree(SBS_X64_DST, ignore_errors=True)

#This is the main program
if __name__ == '__main__':

  try:
    #GetWorkspace()
    P4Login()
    print "Logging in to PerForce"
    P4vSync()
    print "synchronizing", SBS_DPT_ZIP, "and", SBS_DPT_HV, "and", SBS_DPT_WANT
    print "synchronizing", SBS_X64_DPT_ZIP, "and", SBS_DPT_HV, "and", SBS_DPT_WANT
    GetVersion()
    if GatherSBS == True:
      print "copying files from", SBS_SRC, "&", SBS_X64_SRC
      CopySBS()
      print "Ziping up the SBS files for copy to source"
      SBSZipIT(dirEntries(SBS_DST, True), zipname)
      SBSZipIT(dirEntries(SBS_X64_DST, True), zipname_X64)      
      print "checkout", SBS_DPT_ZIP
      print "checkout", SBS_X64_DPT_ZIP
      P4vCheckout()
      print "Copy", SBS_DPT_ZIP, "to", DSTRIB_LOCAL
      print "Copy", SBS_X64_DPT_ZIP, "to", DSTRIB_LOCAL
      CopySBSZip()
      if revert == True:
        P4vRevert()
        print "Reverting", SBS_DPT_ZIP
        print "Reverting", SBS_X64_DPT_ZIP
        CleanUP()
        print "Removing gathered binaries from the Staging Path"
      elif submit == True:
        UpdateHave()
        print "Updating have file with what we are going to submit", SBS_DPT_ZIP, "&", SBS_X64_DPT_ZIP, "with version", want
        P4vSubmit()
        print "Checking in -c %s submit -d %s %s and %s " % (workspace, want, SBS_DPT_ZIP, SBS_DPT_HV)
        print "Checking in -c %s submit -d %s %s and %s " % (workspace, want, SBS_X64_DPT_ZIP, SBS_DPT_HV)
        CleanUP()
        print "Removing gathered binaries from the Staging Path"
      else:
        CleanUP()
        print "Removing gathered binaries from the Staging Path"
        print "files are gathered ready for test build using new", SBS_DPT_ZIP, "and", SBS_X64_DPT_ZIP, "version", want
        print "please remember to the revert the zipfile when you are done and let Angel know if we need to update the SBS FILES"

  except BuildError, e:
    fail(e.msg)