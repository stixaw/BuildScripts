#this script is created to sign the Jar files which are in Deployment Solution
#it only needs to run when new file are compiled by Dev team

import fnmatch
import getopt
import os
import shutil
import sys
from indent import *
import time
import tempfile

#global variables
top = ''
pwd = ''
workspace = ''
tools = ''

def usage():
  print __doc__
  print """Usage:
Signjar.py [OPTIONS]

Options:
"""
  usage = """\
-h, --help|display help
--top|sets top example top=c:\BuildClient\Deployment_Solution\trunk
--workspace| sets workspace for perforce  example --workspace=scm-Deployment_Solution
--tools| sets tools workspace for access to jre tools example --tools=scm-DSBUILDSVR-tools

"""
  rows = [row.strip().split('|') for row in usage.splitlines()]
  print indent(rows, delim='  ', wrapfunc=lambda x: wrap_onspace_strict(x, 40))

def parseArgs(argv):
  global top, workspace, tools

  try:
    opts, args = getopt.getopt(argv, 'h:t:w:t', ['help','top=', 'workspace=', 'tools='])
  except getopt.GetoptError:
    print "Invalid options specified.\n"
    usage()
    sys.exit(2)

  for opt, arg, in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit()
    elif opt in ('--tools'):
      tools = arg
    elif opt in ('--workspace'):
      workspace = arg
    elif opt in ('--top'):
      top = arg
  if top == '':
    print 'You must specify --top=<top path>'
    sys.exit(3)
  if top == '':
    print 'You must specify --tools  this is the perforce workspace name for scmtools on this machin example --tools=aw-tools'
    sys.exit(4)
  if top == '':
    print 'You must specify --workspace this is the perforce workspace name for DS Source --workspace=angel-ds'
    sys.exit(5)

class BuildError(Exception):
  def __init__(self, msg, *args):
    Exception.__init__(self, msg)
    self.msg = msg
    #apply(Exception.__init, (self,) + args)

try:
  # set globals from the command line
  parseArgs(sys.argv[1:])

  Jar_List = [
  top + r'\common\JavaApplet\CopyFolderFile\plugin.jar',
  top + r'\common\JavaApplet\CopyFolderFile\dist\CopyFolderFile.jar'
  ]

  Jar_SRC = top + r'\common\JavaApplet\CopyFolderFile\dist\CopyFolderFile.jar'
  Jar_DST = top + '\\apps\\DeploymentServer\\Altiris.Deployment.Web\\include\\CopyFolderFile.jar'
 
except BuildError, e:
  fail(e.msg)


def GetPwd():
  global pwd, top
#this function finds the pwdjar.txt file on buildserver and inserts it to command
  print "getting password for sign commands"
  f = open(top +'\\build\\scripts\\pwdjar.txt', 'r')
  pwd1 = f.read()
  pwd = pwd1.strip()
  return pwd
  f.close

def GetWorkspace():
  global workspace
  #find c:\workspace.txt
  #open and read C:\workspace.txt first line should be the -c workspace name used by that person
  #ie angel-ds is my workspace on SITHLORD-ANGEL
  f = open('c:\\workspace.txt', 'r')
  workspace1 = f.read()
  workspace = workspace1.strip()
  print workspace
  return tools
  f.close

def Execute(dir, cmd, reportFail=1):
  """execute a command from a given directory"""
  if sys.platform == 'win32':
    tmpfile = tempfile.mkstemp(suffix='.bat', text=True)
    tmphandle = tmpfile[0]
    tmpname = tmpfile[1]
    
    os.write(tmphandle, '@echo off\n')
    if dir != '':
      os.write(tmphandle, 'cd %s\n' % dir)
    os.write(tmphandle, '%s\n' % cmd)
    os.close(tmphandle)
    
    result = os.system(tmpname)
    os.remove(tmpname)
    if result != 0:
      if reportFail:
        raise BuildError('Executing %s from direction %s failed' % (cmd, dir))

def fail(msg):
  print '%s failed: %s' % (sys.argv[0], msg)
  sys.exit(1)

def GetTools():
  global tools
  #find c:\workspace.txt
  #open and read C:\workspace.txt first line should be the -c workspace name used by that person
  #ie angel-ds is my workspace on SITHLORD-ANGEL
  f = open('c:\\tools.txt', 'r')
  tools1 = f.read()
  tools = tools1.strip()
  print workspace
  return tools
  f.close

def VerifyJarSig(pwd,files):
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
      certpath = top + '\\build\\verisign\\Authenticode\\sym_cs.pfx'
      pvktmp = ' pvktmp:6e06cab1-6ba5-48f5-8c37-8060f8466a4f'
      cmd = JarSig_Tool + ' -storetype pkcs12 -keystore ' + certpath + ' -storepass ' + pwd + ' -sigfile SIG ' + jar + pvktmp
      print cmd
      Execute (top, cmd)

def SignJar():
  global pwd, top
# this function signs the jar files
  certpath = top + '\\build\\verisign\\Authenticode\\sym_cs.pfx'
  pvktmp = 'pvktmp:6e06cab1-6ba5-48f5-8c37-8060f8466a4f'
  cmd1 = 'C:\\scmtools\\jdk1.6.0_14_windows\\bin\\jarsigner.exe -storetype pkcs12 -keystore ' + certpath + ' -storepass ' + pwd + ' -sigfile SIG ' + top + '\\common\\JavaApplet\\CopyFolderFile\plugin.jar ' + pvktmp

  cmd2 = 'C:\\scmtools\\jdk1.6.0_14_windows\\bin\\jarsigner.exe -storetype pkcs12 --keystore ' + certpath + ' -storepass ' + pwd + ' -sigfile SIG' + top + '\\common\\JavaApplet\\CopyFolderFile\\dist\\CopyFolderFile.jar ' + pvktmp
  
  print cmd1
  Execute (top, cmd1)
  print cmd2
  Execute (top, cmd2)
  
def CopyJar():
  global top
  #copies r'\common\JavaApplet\CopyFolderFile\dist\CopyFolderFile.jar' to  \apps\DeploymentServer\Altiris.Deployment.Web\include\CopyFolderFile.jar
  print "copy signed jar to \\apps\\DeploymentServer\\Altiris.Deployment.Web\\include\\" 
  if os.path.exists(Jar_DST):
    os.remove(Jar_DST)
  shutil.copy(Jar_SRC, top + '\\apps\\DeploymentServer\\Altiris.Deployment.Web\\include\\')

def ToolsSync():
  global tools
 #sync up all tools directory
  os.system("p4 -c %s sync //depot/tools/jdk1.6.0_14_windows/..." % (tools))

def P4vSync(files):
  global workspace
  #sync up the workspace with depot
  #os.system("p4 -p %s sync //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  for f in files:
    os.system("p4 -c %s sync %s" % (workspace, f)) 
    os.system("p4 -c %s sync %s" % (workspace, Jar_DST))

def P4vCheckout(files):
  global workspace
 #def CheckOut
 #os.system("p4 -p %s edit //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  for f in files:
    os.system("p4 -c %s edit %s" % (workspace, f)) 
  os.system("p4 -c %s edit %s" % (workspace, Jar_DST))

def P4vSubmit(files):
  global workspace
  localtime=time.asctime( time.localtime(time.time()) )
  print localtime
  #p4 [g-opts] submit [-r] [-f submitoption] -d description
  #os.system("p4 -p %s submit //depot/EMG/NS/Solutions/DS/Trunk/file.ext" % (P4PORT))
  for f in files:
    print 'p4 -c %s submit -d "%s" %s ' % (workspace, localtime, f)
    os.system('p4 -c %s submit -d "%s" %s ' % (workspace, localtime, f))
  os.system('p4 -c %s submit -d "%s" %s ' % (workspace, localtime, Jar_DST))

#This is the main program
if __name__ == '__main__':

  try:
    #GetPwd()
    #GetWorkspace()
    #GetTools()
    ToolsSync()
    P4vSync(Jar_List)
    P4vCheckout(Jar_List)
    VerifyJarSig('DODNTINT', Jar_List)
    CopyJar()
    P4vSubmit(Jar_List)
  
  except BuildError, e:
    fail(e.msg)