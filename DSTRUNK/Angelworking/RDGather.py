#Staging Gather.py SUDO CODE to turn to real code
#This py is rdeploy specific to read the source rd.have and rd.want
#to compare with the highest available build form rdbuild\builds\trunk and determine if a gather is necessary
#once determined the script will execute a gather of the listed binaries from external build source rdbuild\builds\trunk
#then the script will execute a zipit process to zip the imaging\rdeploy structure for submittion to Perforce
#script will sync, check out and submit the zip file with the build number as the description of the reason
#this script requires a workspace.txt file at the root of C: to gather to workspace for that machine
#Winzip needs to be installed on the machine
#this script requires the --path parameter for  the staging area to copy and do the work, 
#--top to know where the distrib area is located

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
GatherRD = ''
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
RDGather.py [OPTIONS]

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
  RD_SRC =  r'\\rdbuild\builds\trunk\%s' % version
  RD_LOC_SRC = r'\\builddev\buildtest\Uinta\RapiDeploy\Latest\ProgramFiles'

# Local paths for distrib, and local workspace trunk
  RD_DPT = DPT_TRNK + r'/distrib/imaging/rdeploy...'
  RD_LOCAL_DIR = localtrunk + r'\distrib\imaging\rdeploy'
  DSTRIB_LOCAL = localtrunk + r'\distrib'
  
# List of destination directories
  RD_DST = r'%s\distrib\Imaging\rdeploy' % StagingPath
  RD_x86_DST = RD_DST + r'\x86'
  RD_64_DST = RD_DST + r'\x64'
  RD_LIN_DST = RD_DST + r'\Linux\x86'
  RD_LIN_64_DST = RD_DST + r'\Linux\x64'

  RD_FILES = [
    RD_SRC + '\\tools\\Windows\\x86\\atrsimg.dll',
    RD_SRC + r'\rd\RDeploy\Windows\imgexpl.exe',
    RD_SRC + r'\rd\RDeploy\Windows\rdeploy.exe',
    RD_SRC + r'\rd\RDeploy\Windows\rdeployt.exe',
    RD_SRC + r'\rd\RDeploy\Windows\firm.exe',
    RD_SRC + r'\rd\TechSup\Windows\partgen.exe',
    RD_SRC + r'\rd\TechSup\Windows\showdisk.exe',
    RD_SRC + r'\rd\TechSup\Windows\wipe.exe',
    RD_SRC + r'\rd\TechSup\Windows\fscs.exe',
    RD_SRC + r'\rd\TechSup\Windows\makeimx.exe'
    ]

  RD_X64_FILES = [
    RD_SRC + r'\tools\Windows\x64\atrsimg.dll',
    RD_SRC + r'\rd\RDeploy\Windows\x64\rdeploy.exe',
    RD_SRC + r'\rd\RDeploy\Windows\x64\rdeployt.exe',
    RD_SRC + r'\rd\RDeploy\Windows\x64\firm.exe',
    RD_SRC + r'\rd\TechSup\Windows\x64\partgen.exe',
    RD_SRC + r'\rd\TechSup\Windows\x64\showdisk.exe',
    RD_SRC + r'\rd\TechSup\Windows\x64\wipe.exe',
    RD_SRC + r'\rd\TechSup\Windows\x64\fscs.exe',
    RD_SRC + r'\rd\TechSup\Windows\x64\makeimx.exe'
    ]

  RD_LIN_FILES = [
    RD_SRC + r'\rd\RDeploy\Linux\rdeployt.',
    RD_SRC + r'\rd\RDeploy\Linux\firm.',
    RD_SRC + r'\rd\TechSup\Linux\fscs.',
    RD_SRC + r'\rd\TechSup\Linux\makeimx.',
    RD_SRC + r'\rd\TechSup\Linux\partgen.',
    RD_SRC + r'\rd\TechSup\Linux\showdisk.',
    RD_SRC + r'\rd\TechSup\Linux\wipe.'
    ]

  RD_X64_LIN_FILES = [
    RD_SRC + r'\rd\RDeploy\Linux\x64\rdeployt.',
    RD_SRC + r'\rd\RDeploy\Linux\x64\firm.',
    RD_SRC + r'\rd\TechSup\Linux\x64\fscs.',
    RD_SRC + r'\rd\TechSup\Linux\x64\makeimx.',
    RD_SRC + r'\rd\TechSup\Linux\x64\partgen.',
    RD_SRC + r'\rd\TechSup\Linux\x64\showdisk.',
    RD_SRC + r'\rd\TechSup\Linux\x64\wipe.'
    ]

  zipname = RD_DST + '.zip'
  RD_DPT_ZIP = DPT_TRNK + r'/distrib/rdeploy.zip'
  RD_DPT_HV = DPT_TRNK + r'/distrib/scripts/RD.have'
  RD_DPT_WANT = DPT_TRNK + r'/distrib/scripts/RD.want'

except BuildError, e:
  fail(e.msg)

# def GetBuildNum(dirname):
    # return int('0' + ''.join([x for x in dirname if x.isdigit()]))

def GetVersion():
  global version, localtrunk, GatherRD, want, have
#check to see if --version provided a version if not then we check rd.want for what we want.
#open the .want file to see what version is wanted options in this file are latest, build number
#ie if we always want latest we would have latest as first line in that file, if we wanted a rdbuild it would be 9266
#if this comes from a DS build it would be build9226
#Source for version for rdeploy
  GET_BLD =  r'\\rdbuild\builds\trunk'
  if version == 'latest':
    print "this is the value for version", version
    f = open (localtrunk + '\\distrib\\scripts\\RD.have', 'r')
    have = f.read()
    f.close()
    f = open(localtrunk + '\\distrib\\scripts\\RD.want', 'r')
    want = f.read()
    f.close()
    if want.strip().lower() == 'latest':
      highestbuild = max([int(x) for x in os.listdir(GET_BLD) if x.isdigit()])
      want = highestbuild
    if [int(want)] != [int(have)]:
      print "1 have =", have, "want =", want
      GatherRD = True
      version = want
    else:
      print "2 have =", have, "want =", want
      GatherRD = False
      print "Exiting gather script we have", have, "what we want", want

  else:
    print "I was told to get version", version
    f = open (localtrunk + '\\distrib\\scripts\\RD.have', 'r')
    have = f.read()
    f.close()
    want = version
    if want != have:
      print "3 have =", have, "want =", want
      GatherRD = True
    else:
      print "4 have =", have, "want =", want
      GatherRD = False
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

def UpdateHave():
  global want
#checkout and write to have to match the newly gathered version
  os.system("p4 -c %s edit %s" % (workspace, RD_DPT_HV))
  f = open (localtrunk + '\\distrib\\scripts\\RD.have', 'w')
  f.write(str(want))
  f.close()

def P4vSync():
  global workspace
  #sync up the workspace with depot
  #os.system("p4 -p %s sync //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s sync %s" % (workspace, RD_DPT_ZIP))
  os.system("p4 -c %s sync %s" % (workspace, RD_DPT_HV))
  os.system("p4 -c %s sync %s" % (workspace, RD_DPT_WANT))

def P4Login():
  global workspace, localtrunk
  psswd = localtrunk + "//build//scripts//p4psswd.txt"
  os.system("p4 login < %s" % (psswd))

def P4vCheckout():
  global workspace
 #def CheckOut
 #os.system("p4 -p %s edit //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s edit %s" % (workspace, RD_DPT_ZIP)) 

def P4vRevert():
  global workspace
  #os.system("p4 -p %s revert //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s revert %s" % (workspace, RD_DPT_ZIP)) 

def P4vSubmit():
  global workspace
  #p4 [g-opts] submit [-r] [-f submitoption] -d description
  #os.system("p4 -p %s submit //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s submit -d %s %s " % (workspace, want, RD_DPT_ZIP))
  os.system("p4 -c %s submit -d %s %s " % (workspace, want, RD_DPT_HV))

def CopyRD():
#RD Source location
#copy x86 windows version of rdeploy files
  print "copying RD files from", RD_SRC, "to", RD_DST
  if not os.path.exists(RD_DST):
    os.makedirs(RD_DST)
  for file in RD_FILES:
    print "copying rd files"
    shutil.copy(file, RD_DST)

#copy x86 windows version of rdeploy files
  if not os.path.exists(RD_x86_DST):
    os.makedirs(RD_x86_DST)
  for file in RD_FILES:
    print "copying rd files"
    shutil.copy(file, RD_x86_DST)

#copy x86 windows version of imgexp localized files
  print "copying imgexp localized  from", RD_LOC_SRC
  for file in glob.glob(RD_LOC_SRC + r'\imgexpl_*.dll'):
    print "copying imgexp localized files"
    shutil.copy(file, RD_DST)
    shutil.copy(file, RD_x86_DST)

#copy the x64 windows version of rdeploy
  if not os.path.exists(RD_64_DST):
    os.makedirs(RD_64_DST)
  for file in RD_X64_FILES:
    print "copying rd_64 files"
    shutil.copy(file, RD_64_DST)

#copy the x86 linux version of rdeploy files
  if not os.path.exists(RD_LIN_DST):
    os.makedirs(RD_LIN_DST)
  for file in RD_LIN_FILES:
    print "copying rd_lin files"
    shutil.copy(file, RD_LIN_DST)

#copy the x64 linux version of rdeploy files
  if not os.path.exists(RD_LIN_64_DST):
    os.makedirs(RD_LIN_64_DST)
  for file in RD_X64_LIN_FILES:
    print "copying rd_lin_64 files"
    shutil.copy(file, RD_LIN_64_DST)

def CopyRDZip():
#this function grabs the new zip file and copies it to local distrib for checkin
    shutil.copy(zipname, DSTRIB_LOCAL)

def RDZipIT(fileList, archive): 
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
#removes the local RD_DST files from local hard drive
  print "Deleting", zipname
  if os.path.exists(zipname):
    os.remove(zipname)
  print "Deleting", RD_DST
  if os.path.exists(RD_DST):
    shutil.rmtree(RD_DST)


#This is the main program
if __name__ == '__main__':

  try:
    #GetWorkspace()
    P4Login()
    print "Logging in to PerForce"
    P4vSync()
    print "synchronizing", RD_DPT_ZIP, "and", RD_DPT_HV, "and", RD_DPT_WANT
    GetVersion()
    if GatherRD == True:
      CopyRD()
      print "copying Config.dll files from", RD_SRC
      RDZipIT(dirEntries(RD_DST, True), zipname)
      print "Ziping up the config files for copy to source"
      P4vCheckout()
      print "checkout", RD_DPT_ZIP
      CopyRDZip()
      print "Copy", RD_DPT_ZIP, "to", DSTRIB_LOCAL
      if revert == True:
        P4vRevert()
        print "Reverting", RD_DPT_ZIP
        CleanUP()
        print "Removing gathered binaries from the Staging Path"
      elif submit == True:
        UpdateHave()
        print "Updating have file with what we are going to submit", RD_DPT_HV, "with version", want
        P4vSubmit()
        print "Checking in -c %s submit -d %s %s and %s " % (workspace, want, RD_DPT_ZIP, RD_DPT_HV)
        CleanUP()
        print "Removing gathered binaries from the Staging Path"
      else:
        CleanUP()
        print "Removing gathered binaries from the Staging Path"
        print "files are gathered ready for test build using new", RD_DPT_ZIP, "version", want
        print "please remember to the revert the zipfile when you are done and let Angel know if we need to update the RapidDeploy files"

  except BuildError, e:
    fail(e.msg)