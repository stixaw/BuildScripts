#this script just zips up the PCTfiles that are submitted to us by the PCT team
#function take the already gathered PCT files and zips them up them copies to distrib\PCT

import getopt
import os
import shutil
import sys
from indent import *
import glob
import zipfile
from os.path import join, abspath
import stat

#ugly global variables
DPT_TRNK = '//depot/Endpoint_Management_Group/notification_server/solutions/deployment_solution/trunk...'
PCT_VER=''
workspace = ''
localtrunk = ''
workspace = ''
StagingPath = ''
submit = False
revert = False

#this is for help function to build a commandline
def usage():
  print __doc__
  print """Usage:
PCTZIPit.py [OPTIONS]

Options:
"""
  usage = """\
--path|path to Drive you want to use for a local distrib by example --path=c:
--top|path to localtrunk example --top=c:\ds\trunk
--version|passes the exact version of PCT which you were given by PCT team --version=6.8.1058
Optional input parameters|By default this script will gather all possible Staging files for rdeploy
--revert|off by default, but if called all files that were changed in source by this script will revert in perforce (zipfile)
--submit|off by default this parameter turns on the P4vSubmit function and the Update have functions, only do this when you are sure we are need to update
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
      PCT_VER = arg
      print "I will not check have or want but use this exact version", PCT_VER
    elif opt in ('--submit'):
      submit = True
      print "I will submit the changed zip file and  update the have"
    elif opt in ('--revert'):
      revert = True
      print "I will revert the changed zipfile."
  if PCT_VER == '':
    print 'You must specify the build of PCT recieved by PCT development team, example --version=6.1.1058'
    sys.exit(4)
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

# Destination Directory
  PCT_DST = StagingPath + '\\distrib\\PCT\\'

# Local paths for distrib, and local workspace trunk
  PCT_DPT = DPT_TRNK + r'/distrib/PCT...'
  PCT_LOCAL_DIR = localtrunk + r'\distrib\PCT'
  DSTRIB_LOCAL = localtrunk + r'\distrib'
  
  zipname = PCT_DST +'PCT.zip'
  PCT_LOC_ZIP = localtrunk + r'\distrib\PCT.zip'
  PCT_LOC_HV = localtrunk + r'\distrib\scripts\PCT.have'

except BuildError, e:
  fail(e.msg)

def P4vSync():
  global workspace
  #sync up the workspace with depot
  #os.system("p4 -p %s sync //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s sync %s" % (workspace, PCT_LOC_ZIP))
  os.system("p4 -c %s sync %s" % (workspace, PCT_LOC_HV))

def P4Login():
  global workspace, localtrunk
  psswd = localtrunk + "//build//scripts//p4psswd.txt"
  os.system("p4 login < %s" % (psswd))
  
def P4vCheckout():
  global workspace
 #def CheckOut
 #os.system("p4 -p %s edit //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s edit %s" % (workspace, PCT_LOC_ZIP))

def P4vSubmit():
  global workspace, PCT_VER
  #p4 [g-opts] submit [-r] [-f submitoption] -d description
  #os.system("p4 -p %s submit //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  os.system("p4 -c %s submit -d '%s' %s " % (workspace, PCT_VER, PCT_LOC_ZIP))
  os.system("p4 -c %s submit -d '%s' %s " % (workspace, PCT_VER, PCT_LOC_HV))
  
def UpdateHave():
  global PCT_VER
#checkout and write to have to match the newly gathered version
  os.system("p4 -c %s edit %s" % (workspace, PCT_LOC_HV))
  f = open (localtrunk + '\\distrib\\scripts\\PCT.have', 'w')
  f.write(str(PCT_VER))
  f.close()

def PCTCopy():
  PCT_SRC ='C:\\PCT'
  if os.path.exists(PCT_DST):
    shutil.rmtree(PCT_DST)
  print "copying PCT directory"
  shutil.copytree(PCT_SRC, PCT_DST)

def CopyPCTZip():
#this function grabs the new zip file and copies it to local distrib for checkin
    shutil.copy(zipname, DSTRIB_LOCAL)

def PCTZipIT(fileList, archive): 
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

def ChngMod():
#changes the read-only files for clean-up
  for path, dirs, files in os.walk(r'C:\distrib\PCT'):
    for file in files:
      tarFiles = abspath(join(path, file))
      print "Accessing", tarFiles
      os.chmod(tarFiles, stat.S_IWRITE)

def CleanUP():
#removes the local PCT_VER_DST files from local hard drive
  print "Deleting", zipname
  if os.path.exists(zipname):
    os.remove(zipname)
  print "Deleting", PCT_DST
  if os.path.exists(PCT_DST):
    shutil.rmtree(PCT_DST, ignore_errors=True)

#This is the main program
if __name__ == '__main__':

  try:
    P4Login()
    print "Logging in to PerForce"
    P4vSync()
    print "synchronizing", PCT_LOC_ZIP, "and", PCT_LOC_HV
    PCTCopy()
    print "copying PCT files for ZIP creation"
    PCTZipIT(dirEntries(PCT_DST, True), zipname)
    print "Ziping up the config files for copy to source"
    P4vCheckout()
    print "checkout", PCT_LOC_ZIP
    CopyPCTZip()
    print "Copy", PCT_LOC_ZIP, "to", DSTRIB_LOCAL
    if revert == True:
      P4vRevert()
      print "Reverting", PCT_LOC_ZIP
      ChngMod()
      CleanUP()
      print "Removing gathered binaries from the Staging Path"
    elif submit == True:
      UpdateHave()
      print "Updating have file with what we are going to submit", PCT_LOC_ZIP, "with version", PCT_VER
      P4vSubmit()
      print "Checking in -c %s submit -d %s %s and %s " % (workspace, PCT_VER, PCT_LOC_ZIP, PCT_LOC_HV)
      ChngMod()
      CleanUP()
      print "Removing gathered binaries from the Staging Path"
    else:
      ChngMod()
      CleanUP()
      print "Removing gathered binaries from the Staging Path"
      print "files are gathered ready for test build using new", PCT_LOC_ZIP, "version", PCT_VER

  except BuildError, e:
    fail(e.msg)