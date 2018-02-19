import os
import sys
import string
import _winreg



def ProcKey32Exists():
  hkey = (_winreg.HKEY_LOCAL_MACHINE)
  regpath = (r"Software\Classes\CLSID\1A5AC6AE-7B95-478C-B422-0E994FD727D6\InProcServer32")
  #check to see if registry exists
  try:
    reg = _winreg.OpenKey(hkey,regpath)
  except WindowsError:
    print 'ProcKey 32 Exists = False'
    return False
  print 'ProcKey 32 Exists = True'
  return  True


def GetProc32Value():
#read a registry for intalled path of Wise
  if ProcKey32Exists() == True:
    Procreg = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"Software\Classes\CLSID\1A5AC6AE-7B95-478C-B422-0E994FD727D6 7")
    ProcValue, type = _winreg.QueryValueEx(Procreg, "InProcServer32")
    _winreg.CloseKey(Procreg)
    print ProcValue
  else:
    print 'ELSE: InProcServer32 has no value'
  sys.exit(2)
  
def ProcKey64Exists():
  hkey = (_winreg.HKEY_LOCAL_MACHINE)
  regpath = (r"Software\Classes\Wow6432Node\CLSID\1A5AC6AE-7B95-478C-B422-0E994FD727D6\InProcServer32")
  #check to see if registry exists
  try:
    reg = _winreg.OpenKey(hkey,regpath)
  except WindowsError:
    print 'ProcKeyExists = False'
    return False
  print 'ProcKeyExists = True'
  return  True

def GetProc64Value():
#read a registry for intalled path of Wise
  if ProcKey64Exists() == True:
    Procreg = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r"Software\Classes\Wow6432Node\CLSID\1A5AC6AE-7B95-478C-B422-0E994FD727D6\InProcServer32 7")
    ProcValue, type = _winreg.QueryValueEx(Procreg, "InProcServer32")
    _winreg.CloseKey(Procreg)
    print ProcValue
  else:
    print 'ELSE: InProcServer32 has no value'
  sys.exit(2)
  
#This is the main program
if __name__ == '__main__':

    if ProcKey32Exists() == False:
      print "The CLSID\1A5AC6AE-7B95-478C-B422-0E994FD727D6\InProcServer32 is not there"
    if ProcKey32Exists() == True:
      print "The CLSID\1A5AC6AE-7B95-478C-B422-0E994FD727D6\InProcServer32 is not there"
      GetProc32Value()
    if ProcKey64Exists() == False:
      print "The Software\Classes\Wow6432Node\CLSID\1A5AC6AE-7B95-478C-B422-0E994FD727D6\InProcServer32 is not there"
    if ProcKey64Exists() == True:
      print "The Software\Classes\Wow6432Node\CLSID\1A5AC6AE-7B95-478C-B422-0E994FD727D6\InProcServer32 is not there"
      GetProc64Value()