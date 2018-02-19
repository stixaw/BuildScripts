# Create IIS Web sites for VS builds which require them.
#parameters needed: SolutionName for website IE Deployment.Web
# Path to Directory example %WORKSPACE%\\trunk\\apps\\Altiris.Deployment.Web
#Additional Sub directory from Default Web Site if needed example 'Default Web Site/Altiris'

import os
import sys
import getopt

#ugly global variables
WebSite = 'Default Web Site'
Virt_Dir_Path = ''
Sol_WebName = ''
top = ''

def usage():
	print __doc__
	print """Usage:
	IISWEB_create.py [OPTIONS]
	Options:
	"""
	usage ="""\
	-h, --help|display help
	--virtdir| Locaition source directory of Web Site example --virtdir=\trunk\app\Altiris.Deployment.Web
	--subsite | If the solution requires something different from "Default Web Site" example --subsite=Default Web Site/Altiris this creates "Default Web Site/Altiris"
	--solname | Solution's Web Site name ie: --solname=Altiris.Deployment.Web
	--top | Top is workspace
  """

def parseArgs(argv):
	global WebSite, Virt_Dir_Path, Sol_WebName, top
	try:
		opts, args = getopt.getopt(argv, "hv:s:s:t", [ 'help', 'virtdir=', 'subsite=', 'solname=', 'top='])
	except getopt.GetoptError:
		print "Invalid options specified.\n"
		usage()
		sys.exit(1)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		if opt ==("--virtdir"):
			Virt_Dir_Path = arg
		elif opt == ("--subsite"):
			WebSite = arg
		elif opt == ("--solname"):
			Sol_WebName = arg
		elif opt == ("--top"):
			top= arg

	if Virt_Dir_Path == '':
		print 'You must specify the path to the directory for source of the Web site ie: --virtdir=%WORKSPACE%\\trunk\\app\\Altiris.Deployment.Web (path must start with %WORKSPACE%)'
		sys.exit(2)
	if Sol_WebName == '':
		print 'You must specify the solution Web site ie: --solname=Altiris.Deployment.Web'
		sys.exit(3)
	if top =='':
		print 'you must specify top ie --top=%WORKSPACE%'
		sys.exit(4)
	

class BuildError(Exception):
	def __init__(self, msg, *args):
		Exception.__init__(self, msg)
		self.msg = msg
		#apply(Exception.__init, (self,) + args)

try:
	# set globals from the command line
	parseArgs(sys.argv[1:])
	

except BuildError, e:
	fail(e.msg)

def CreateWebSite():
	global WebSite, Virt_Dir_Path, Sol_WebName, top
	#commandline
	cmd = (' cscript "%windir%\\system32\\iisvdir.vbs" /create' + ' "' + WebSite + '" ' + Sol_WebName + ' "' + top + Virt_Dir_Path + '"')
	cmdconsole = 'C:\\windows\\system32\\cmd.exe /C'
	print cmd
	os.system(cmdconsole + cmd)
 

#This is the main program
if __name__ == '__main__':
	try:
		CreateWebSite()

	except BuildError, e:
		fail(e.msg)