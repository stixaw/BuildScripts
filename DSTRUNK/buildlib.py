import os
import shutil
import sys
import tempfile

class BuildError(Exception):
  def __init__(self, msg, *args):
    Exception.__init__(self, msg)
    self.msg = msg
    #apply(Exception.__init, (self,) + args)

def fail(msg):
  print '%s failed: %s' % (sys.argv[0], msg)
  sys.exit(1)

def log(msg):
  print msg

def GetTop():
  if os.environ.has_key('TOP'):
    return os.environ['TOP']
  else:
    raise BuildError('TOP environment variable must be set')

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

	
def Copy(src, dest, reportFail=1):
  """copy a file from src to dest"""
  if sys.platform == 'win32':
    try:
      shutil.copy(src, dest)
    except IOError:
      if reportFail:
        raise BuildError('Copy %s to %s failed' % (src, dest))

#def wnet_connect(host, username = None, password = None):
#  unc = ''.join(['\\\\', host])
#  try:
#    win32wnet.WNetAddConnection2(0, None, unc, None, username, password)
#  except Exception, err:
#    if isinstance(err, win32wnet.error):
#      # Disconnect previous connections if detected, and reconnect.
#      if err[0] == 1219:
#        win32wnet.WNetCancelConnection2(unc, 0, 0)
#        return wnet_connect(host, username, password)
#    raise err
