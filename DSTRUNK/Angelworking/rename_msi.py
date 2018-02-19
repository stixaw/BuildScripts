# rename msi for solutoins

import os
import sys
import getopt
from pprint import pprint
from renamelib import msiDict
from docrenamelib import Doc_Dict

Sol_DICT = {}

def usage():
	print __doc__
	print """Usage:
	Msi_copy.py [OPTIONS]
	Options:
	"""
	usage ="""\
	-h, --help|display help
	--dict|Dictionary to use for rename function example --dict=DS
  """
  
def parseArgs(argv):
	global SolName, Sol_DICT
	try:
		opts, args = getopt.getopt(argv, "h:d", [ 'help', 'dict=' ])
	except getopt.GetoptError:
		print "Invalid options specified.\n"
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt == ("--dict"):
			Sol_DICT = arg

	if Sol_DICT == '':
		print 'You must specify --dict|Dictionary to use for rename function example --dict=DS'
		sys.exit(3)

class BuildError(Exception):
	def __init__(self, msg, *args):
		Exception.__init__(self, msg)
		self.msg = msg
		#apply(Exception.__init, (self,) + args)
def fail(msg):
	print '%s failed: %s' % (sys.argv[0], msg)
	sys.exit(1)
 
try:
	# set globals from the command line
	parseArgs(sys.argv[1:])

	src_dir2 = "c:\\output_msi"
	src_dir = "\\\\ali-netapp1.altiris.com\\polaris\\ITMS\\CombinedBuild\\Doc_Builds\\7.1_SP2"
	
	
except BuildError, e:
	fail(e.msg)

def Rename_MSI(dict):
	for msi in dict.keys():
		if os.path.exists(src_dir + "\\" + msi):
			print "renaming ", msi, "to ", dict[msi]
			os.rename(src_dir + "\\" + msi, src_dir + "\\" + dict[msi])
		else:
			print "Rename function failed", msi, "does not exist"
			sys.exit(3)

#This is the main program
if __name__ == '__main__':
	try:
		pprint(Sol_DICT)
		if Sol_DICT in Doc_Dict.keys():
			Rename_MSI(Doc_Dict[Sol_DICT])
	except BuildError, e:
		fail(e.msg)