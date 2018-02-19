#calls the build for lin_build srver
#sync source
#checkout output_lin
#clean up
# call scons build process
#rename and copy built.so files
# re tgz the agent with the new .so files

import fnmatch
import getopt
import glob
import os
import shutil
import sys
import threading
import subprocess
from indent import *
import zipfile
from os.path import join, abspath
import time


#global Variables
clean = False
cleanall = False
top = ''
workspace = os.environ['P4CLIENT']
buildnum = ''
p4user = 'dsbuilder'
marketingVersion = '7.1'


  
def usage():
  print __doc__
  print """Usage:
linux-build.py [OPTIONS]

Options:
"""
  usage = """\
-h, --help|display help
--cleanall|do everything from clean, and also remove binary output directories
-t, --top=<path to top>|sets top
-w, --workspace| workspace for synch up
-v, --buildnum| build number like 1146

"""
  rows = [row.strip().split('|') for row in usage.splitlines()]
  print indent(rows, delim='  ', wrapfunc=lambda x: wrap_onspace_strict(x, 40))

class BuildError(Exception):
  def __init__(self, msg, *args):
    Exception.__init__(self, msg)
    self.msg = msg
    #apply(Exception.__init, (self,) + args) 


#parse args:
def parseArgs(argv):
  global top, cleanall, workspace, buildnum

  try:
    opts, args = getopt.getopt(argv, 'hct:w:b', ['help', 'cleanall', 'top=', 'workspace=' ,'buildnum='])
  except getopt.GetoptError:
    print "Invalid options specified.\n"
    usage()
    sys.exit(2)

  for opt, arg, in opts:
    if opt in ('--help'):
      print "HELP"
      usage()
      sys.exit()
    elif opt in ('--workspace'):
      workspace = arg
    elif opt in ('-t', '--top'):
      top = arg
    elif opt == '--cleanall':
      clean = True
      cleanall = True
    elif opt == '--buildnum':
      buildnum = arg
  if workspace == '':
   print 'You must specify a workspace example --workspace= angel-ds'
   sys.exit(4)

  if top == '':
    print 'You must specify top (local trunk) --top=/root/LIN_WORKSPACE/trunk'
    sys.exit(4)

  if buildnum == '':
    print ' You must specify buildnum eg : --buildnum=1146'
    sys.exit(4)


try:
  # set globals from the command line
  parseArgs(sys.argv[1:])

except BuildError, e:
  fail(e.msg)

def makeFullVersion():
  global buildnum
  global marketingVersion
  return marketingVersion + '.' + str(buildnum) + '.0'

def GetDate():
  localtime=time.asctime( time.localtime(time.time()) )
  print "local current time :", localtime
  
def P4Login():
  global workspace, top
  psswd = top + "//build//scripts//p4psswd.txt"
  os.system("p4 login < %s" % (psswd))
  
def P4vSync():
  #function to sync up the workspace with depot
  global workspace, top
  TRNK = top + "/..."
  print "syncing", TRNK
  os.system("p4  sync %s" % (TRNK))

def P4vCheckout():
  #function which checks out 
  #TODO: added the tgz file to this check out
  global workspace, top
  LIN_OUTPUT = top + '/output_lin/...'
  LIN_TGZ = top + '/OEM/DS/Linux/x86/Base/ULMagent.tgz'
  LIN_PBS = top + '/PackageBuild/package.pbs'
  LIN_ROLLOUT = top + '/OEM/DS/Linux/x86/automation/rollout-auto.sh'
 #check out files for modifying
  print "checking out",
  os.system("p4 edit %s" % (LIN_OUTPUT))
  os.system("p4 edit %s" % (LIN_TGZ))
  os.system("p4 edit %s" % (LIN_PBS))
  os.system("p4 edit %s" % (LIN_ROLLOUT))
  
def P4Submit():
  #function to submit the output_lin directory with a comment of Date and Time of check in
  global workspace, top
  localtime=time.asctime( time.localtime(time.time()) )
  LIN_OUTPUT = top + '/output_lin/...'
  LIN_TGZ = top + '/OEM/DS/Linux/x86/Base/ULMagent.tgz'
  LIN_PBS = top + '/PackageBuild/package.pbs'
  LIN_ROLLOUT = top + '/OEM/DS/Linux/x86/automation/rollout-auto.sh'
  #submit changes
  print "Calling p4 -c %s submit -d '%s' %s and %s " % (workspace, localtime, LIN_OUTPUT, LIN_TGZ)
  os.system("p4 -c %s submit -d '%s' %s " % (workspace, localtime, LIN_OUTPUT))
  os.system("p4 -c %s submit -d '%s' %s " % (workspace, localtime, LIN_TGZ))
  os.system("p4 -c %s submit -d '%s' %s " % (workspace, localtime, LIN_PBS))
  os.system("p4 -c %s submit -d '%s' %s " % (workspace, localtime, LIN_ROLLOUT))
  
  
def CopyRename():
  global top
    #function which renames and moves the libxx.so files from release directories to Release directories for pick up by the MSI creation process
   #ClientImageDeploy.so
  if os.path.exists(top + '//output_lin//ClientImageDeploy//Release//ClientImageDeploy.so'):
    os.remove(top + '//output_lin//ClientImageDeploy//Release//ClientImageDeploy.so')
    #copy and rename libClientImageDeploy.so
    print "copy libClientImageDeploy.so file"
    shutil.copy(top + '//output_lin//ClientImageDeploy//release//libClientImageDeploy.so', top + '//output_lin//ClientImageDeploy//Release//ClientImageDeploy.so')
  #ClientLinuxPostImageConfigService
  if os.path.exists(top + '//output_lin//ClientLinuxPostImageConfigService//Release//ClientLinuxPostImageConfigService'):
    os.remove(top + '//output_lin//ClientLinuxPostImageConfigService//Release//ClientLinuxPostImageConfigService')
    #copy and rename ClientLinuxPostImageConfigService.so
    print "copy ClientLinuxPostImageConfigService file"
    shutil.copy(top + '//output_lin//ClientLinuxPostImageConfigService//release//ClientLinuxPostImageConfigService', top + '//output_lin//ClientLinuxPostImageConfigService//Release//ClientLinuxPostImageConfigService')
  #ClientLinuxPreImage
  if os.path.exists(top + '//output_lin//ClientLinuxPreImage//Release//ClientPreImage.so'):
    os.remove(top + '//output_lin//ClientLinuxPreImage//Release//ClientPreImage.so')
    #copy and rename libClientLinuxPreImage.so
    print "copy libClientLinuxPreImage.so file"
    shutil.copy(top + '//output_lin//ClientLinuxPreImage//release//libClientLinuxPreImage.so', top + '//output_lin//ClientLinuxPreImage//Release//ClientPreImage.so')
  #ClientLinuxSOI
  if os.path.exists(top + '//output_lin//ClientLinuxSOI//Release//ClientLinuxSOI.so'):
    os.remove(top + '//output_lin//ClientLinuxSOI//Release//ClientLinuxSOI.so')
    #copy and rename libClientLinuxSOI.so
    print "copy libClientLinuxSOI.so file"
    shutil.copy(top + '//output_lin//ClientLinuxSOI//release//libClientLinuxSOI.so', top + '//output_lin//ClientLinuxSOI//Release//ClientLinuxSOI.so')
  #ClientWipe
  if os.path.exists(top + '//output_lin//ClientWipe//Release//ClientWipe.so'):
    os.remove(top + '//output_lin//ClientWipe//Release//ClientWipe.so')
    #copy and rename libClientWipe.so
    print "copy libClientWipe.so file"
    shutil.copy(top + '//output_lin//ClientWipe//release//libClientWipe.so', top + '//output_lin//ClientWipe//Release//ClientWipe.so')
  #DeploymentSolutionAgent Files
  if os.path.exists(top + '//output_lin//DeploymentSolutionAgent//Release//DeploymentSolutionAgent.so'):
    os.remove(top + '//output_lin//DeploymentSolutionAgent//Release//DeploymentSolutionAgent.so')
  if os.path.exists(top + '//output_lin//DeploymentSolutionAgent//Release//DeploymentSolutionAgent.rpm'):
    os.remove(top + '//output_lin//DeploymentSolutionAgent//Release//DeploymentSolutionAgent.rpm')
  if os.path.exists(top + '//output_lin//DeploymentSolutionAgent//Release//rollout.sh'):
    os.remove(top + '//output_lin//DeploymentSolutionAgent//Release//rollout.sh')
    #copy DeploymentSolutionAgent Files
    print "copy DeploymentSolutionAgent Files"
    shutil.copy(top + '//output_lin//DeploymentSolutionAgent//release//DeploymentSolutionAgent.so', top + '//output_lin//DeploymentSolutionAgent//Release//DeploymentSolutionAgent.so')
    shutil.copy(top + '//output_lin//DeploymentSolutionAgent//release//DeploymentSolutionAgent.rpm', top + '//output_lin//DeploymentSolutionAgent//Release//DeploymentSolutionAgent.rpm')
    shutil.copy(top + '//output_lin//DeploymentSolutionAgent//release//rollout.sh', top + '//output_lin//DeploymentSolutionAgent//Release//rollout.sh')
  #ClientCaptureImage
  if os.path.exists(top + '//output_lin//ClientCaptureImage//Release//ClientCaptureImage.so'):
    os.remove(top + '//output_lin//ClientCaptureImage//Release//ClientCaptureImage.so')
    #copy and rename libClientCaptureImage.so
    print "copy libClientCaptureImage.so file"
    shutil.copy(top + '//output_lin//LinuxClientCaptureImage//release//libClientCaptureImage.so', top + '//output_lin//ClientCaptureImage//Release//ClientCaptureImage.so')
  #ClientConfiguration
  if os.path.exists(top + '//output_lin//ClientConfiguration//Release//ClientConfiguration.so'):
    os.remove(top + '//output_lin//ClientConfiguration//Release//ClientConfiguration.so')
    #copy and rename libClientConfiguration.so
    print "copy libClientConfiguration.so file"
    shutil.copy(top + '//output_lin//LinuxClientConfiguration//release//libClientConfiguration.so', top + '//output_lin//ClientConfiguration//Release//ClientConfiguration.so')
  #ClientCopyFile
  if os.path.exists(top + '//output_lin//ClientCopyFile//Release//ClientCopyFile.so'):
    os.remove(top + '//output_lin//ClientCopyFile//Release//ClientCopyFile.so')
    #copy and rename libClientCopyFile.so
    print "copy libClientCopyFile.so file"
    shutil.copy(top + '//output_lin//LinuxClientCopyFile//release//libClientCopyFile.so', top + '//output_lin//ClientCopyFile//Release//ClientCopyFile.so')
  #ClientPartitionDisk
  if os.path.exists(top + '//output_lin//ClientPartitionDisk//Release//ClientPartitionDisk.so'):
    os.remove(top + '//output_lin//ClientPartitionDisk//Release//ClientPartitionDisk.so')
    #copy and rename libClientPartitionDisk.so
    print "copy libClientPartitionDisk.so file"
    shutil.copy(top + '//output_lin//LinuxClientPartitionDisk//release//libClientPartitionDisk.so', top + '//output_lin//ClientPartitionDisk//Release//ClientPartitionDisk.so')
  #ClientRebootTo
  if os.path.exists(top + '//output_lin//ClientRebootTo//Release//ClientRebootTo.so'):
    os.remove(top + '//output_lin//ClientRebootTo//Release//ClientRebootTo.so')
    #copy and rename libClientRebootTo.so
    print "copy libClientRebootTo.so file"
    shutil.copy(top + '//output_lin//LinuxClientRebootTo//release//libClientRebootTo.so', top + '//output_lin//ClientRebootTo//Release//ClientRebootTo.so')

def CallTgzUpdate():
  global top
  tgzupdate = ('/build/scripts/UpdateULMAgent.sh')
  print " Calling", top + tgzupdate
  os.system(top + tgzupdate)

def CallPBSUpdate():
  global top
  version = makeFullVersion()
  #updates update OEM/DS/Linux/x86/automation/rollout-auto.sh as well
  pbsupdate = ('/build/scripts/updatepbs.sh ')
  os.system(top + pbsupdate + version)
  
def CleanAll():
  #function to clean up all binaries which are built by scons
  clean = ('. go.sh'  ' & ' + '. build/scons/scons.sh -c')
  os.system(top + clean)

def removeDroppings():
  """deletes output_lin directories"""
  for path in (r'%s/output_lin/ClientCaptureImage/release' % top,r'%s/output_lin/ClientImageDeploy/release' % top, r'%s/output_lin/ClientLinuxPostImageConfigService/release' % top, r'%s/output_lin/ClientLinuxPreImage/release' % top, r'%s/output_lin/ClientLinuxSOI/release' % top, r'%s\distrib\config' % top, r'%s/output_lin/ClientWipe/release' % top, r'%s/output_lin/DeploymentSolutionAgent/release' % top, r'%s/output_lin/ClientLinuxCopyFile/release' % top, r'%s/output_lin/LinuxClientConfiguration/release' % top, r'%s/output_lin/LinuxClientConfiguration/release' % top, r'%s/output_lin/LinuxClientRebootTo/release' % top):
    print "removing path %s" % (path)
    if os.path.exists(path):
      shutil.rmtree(path)

def buildAll():
  #function to call scons for building of linux binaries
  global top
  build = ('. go.sh '  ' & ' + '. build/scons/scons.sh')
  print "Calling Scons.sh", build
  os.system(top + build)

##  Main entry point
##
if __name__ == '__main__':

  try:
    if cleanall:
      CleanAll()
      removeDroppings()
    else:
      P4Login()
      #P4vSync()
      P4vCheckout()
      CallPBSUpdate()
      buildAll()
      CopyRename()
      CallTgzUpdate()
      #P4Submit()

  except BuildError, e:
    fail(e.msg)
