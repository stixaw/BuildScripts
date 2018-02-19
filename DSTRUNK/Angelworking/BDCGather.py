#This py is Bootwiz specific to read the source BDC.have and BDC.want
#to compare with the highest available build form \\rdbuild\builds\trunk and determine if a gather is necessary
#once determined the script will execute a gather of the listed binaries from external build source rdbuild\builds\trunk
#then the script will execute a zipit process to zip the bootwiz structure for submittion to Perforce
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
GatherBDC = ''
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
BDCGather.py [OPTIONS]

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
    print 'You must specify local workspace trunk path, example --top=<c:\ds\trunk>'
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
  BDC_SRC =  r'\\rdbuild\builds\trunk\%s\bootwiz\bootwiz' % version
  BDC_LOC_SRC = r'\\builddev\buildtest\Uinta\Bootwiz\Latest\ProgramFiles\Bootwiz'
  
# Destination Directory
  BDC_DST = StagingPath + '\\distrib\\bootwiz'

# Local paths for distrib, and local workspace trunk
  BDC_DPT = DPT_TRNK + r'/distrib/bootwiz...'
  BDC_LOCAL_DIR = localtrunk + r'\distrib\bootwiz'
  DSTRIB_LOCAL = localtrunk + r'\distrib'
  
  zipname = BDC_DST + '.zip'
  BDC_DPT_ZIP = DPT_TRNK + r'/distrib/bootwiz.zip'
  BDC_DPT_HV = DPT_TRNK + r'/distrib/scripts/BDC.have'
  BDC_DPT_WANT = DPT_TRNK + r'/distrib/scripts/BDC.want'

except BuildError, e:
  fail(e.msg)

# def GetBuildNum(dirname):
    # return int('0' + ''.join([x for x in dirname if x.isdigit()]))

def GetVersion():
  global version, localtrunk, GatherBDC, want, have
#check to see if --version provided a version if not then we check BDC.want for what we want.
#open the .want file to see what version is wanted options in this file are latest, build number
#ie if we always want latest we would have latest as first line in that file, if we wanted a rdbuild it would be 9266
#if this comes from a DS build it would be build9226
#Source for version for rdeploy
  GET_BLD =  r'\\rdbuild\builds\trunk'
  if version == 'latest':
    print "this is the value for version", version
    f = open (localtrunk + '\\distrib\\scripts\\BDC.have', 'r')
    have = f.read()
    f.close()
    f = open(localtrunk + '\\distrib\\scripts\\BDC.want', 'r')
    want = f.read()
    f.close()
    if want.strip().lower() == 'latest':
      highestbuild = max([int(x) for x in os.listdir(GET_BLD) if x.isdigit()])
      want = highestbuild
    if [int(want)] != [int(have)]:
      print "1 have =", have, "want =", want
      GatherBDC = True
      version = want
    else:
      print "2 have =", have, "want =", want
      GatherBDC = False
      print "Exiting gather script we have", have, "what we want", want

  else:
    print "I was told to get version", version
    f = open (localtrunk + '\\distrib\\scripts\\BDC.have', 'r')
    have = f.read()
    f.close()
    want = version
    if want != have:
      print "3 have =", have, "want =", want
      GatherBDC = True
    else:
      print "4 have =", have, "want =", want
      GatherBDC = False
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

def CopyBDC():
# bootwiz tree command because we get all *.* including structure
  print "copying BDC files from", BDC_SRC
  if os.path.exists(BDC_DST):
    shutil.rmtree(BDC_DST)
  print "copying BDC directory"
  shutil.copytree(BDC_SRC, BDC_DST)
#CD %DST_DIR%\bootwiz and call the build.bat to finalize the bootwiz for DS consumption
  print "Calling build.bat NS"
  os.chdir(BDC_DST)
  os.system('build.bat NS')
  os.remove('build.bat')

  for file in glob.glob(BDC_LOC_SRC + r'\BootWiz_*.dll'):
    print "copying localized BDC files"
    shutil.copy(file, BDC_DST)

def UpdateHave():
  global want, workspace, localtrunk, DPT_TRNK
#checkout and write to have to match the newly gathered version
  os.system("p4 -c %s edit %s" % (workspace, BDC_DPT_HV))
  f = open (localtrunk + '\\distrib\\scripts\\BDC.have', 'w')
  f.write(str(want))
  f.close()

def P4vSync():
  global workspace, DPT_TRNK, localtrunk
  #sync up the workspace with depot
  #os.system("p4 -p %s sync //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s sync %s" % (workspace, BDC_DPT_ZIP))
  os.system("p4 -c %s sync %s" % (workspace, BDC_DPT_HV))
  os.system("p4 -c %s sync %s" % (workspace, BDC_DPT_WANT))

def P4Login():
  global workspace, localtrunk
  psswd = localtrunk + "//build//scripts//p4psswd.txt"
  os.system("p4 login < %s" % (psswd))

def P4vCheckout():
  global workspace
 #def CheckOut
 #os.system("p4 -p %s edit //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s edit %s" % (workspace, BDC_DPT_ZIP))

def P4vRevert():
  global workspace
  #os.system("p4 -p %s revert //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s revert %s" % (workspace, BDC_DPT_ZIP))

def P4vSubmit():
  global workspace, want
  #p4 [g-opts] submit [-r] [-f submitoption] -d description
  #os.system("p4 -p %s submit //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s submit -d %s %s " % (workspace, want, BDC_DPT_ZIP))
  os.system("p4 -c %s submit -d %s %s " % (workspace, want, BDC_DPT_HV))
 
def CopyBDCZip():
#this function grabs the new zip file and copies it to local distrib for checkin
  if os.path.exists(DSTRIB_LOCAL + zipname):
    os.remove(zipname)
    print "removing zipname"
  shutil.copy(zipname, DSTRIB_LOCAL)

def BDCZipIT(fileList, archive): 
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
#removes the local BDC_DST files from local hard drive
  print "Deleting", zipname
  if os.path.exists(zipname):
    os.remove(zipname)
  print "Deleting", BDC_DST
  if os.path.exists(BDC_DST):
    shutil.rmtree(BDC_DST, ignore_errors=True)

#This is the main program
if __name__ == '__main__':

  try:
    #GetWorkspace()
    P4Login()
    print "Logging in to PerForce"
    P4vSync()
    print "synchronizing", BDC_DPT_ZIP, "and", BDC_DPT_HV, "and", BDC_DPT_WANT
    GetVersion()
    if GatherBDC == True:
      CopyBDC()
      print "copying Config.dll files from", BDC_SRC
      BDCZipIT(dirEntries(BDC_DST, True), zipname)
      print "Ziping up the config files for copy to source"
      P4vCheckout()
      print "checkout", BDC_DPT_ZIP
      CopyBDCZip()
      print "Copy", zipname, "to", DSTRIB_LOCAL
      if revert == True:
        P4vRevert()
        print "Reverting", BDC_DPT_ZIP
        CleanUP()
        print "Removing gathered binaries from the Staging Path"
      elif submit == True:
        print "I am running updatehave now"
        UpdateHave()
        print "Updating have file with what we are going to submit", BDC_DPT_ZIP, "with version", want
        P4vSubmit()
        print "Checking in -c %s submit -d %s %s and %s " % (workspace, [int(want)], BDC_DPT_ZIP)
        CleanUP()
        print "Removing gathered binaries from the Staging Path"
      else:
        #CleanUP()
        print "Removing gathered binaries from the Staging Path"
        print "files are gathered ready for test build using new", BDC_DPT_ZIP, "version", want
        print "please remember to the revert the zipfile when you are done and let Angel know if we need to update Bootwiz in source"

  except BuildError, e:
    fail(e.msg)