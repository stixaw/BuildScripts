import os
import sys
import shutil

tmplate_src = r'\\ali-netapp1.altiris.com\polaris\aim\builds\productlisting\7.1 sp2'
grabpl = ''
plversion = 'latest'
have = ''
want = ''
top = r'C:\CM-1666\ITMSCM'


def FindLatest():
	global tmplate_src, grabpl, plversion, top, have, want
#check to see if --version provided a version if not then we check BDC.want for what we want.
#open the .want file to see what version is wanted options in this file are latest, build number
#ie if we always want latest we would have latest as first line in that file, if we wanted a rdbuild it would be 9266
#if this comes from a DS build it would be build9226
#Source for version for rdeploy
	if plversion == 'latest':
		print "this is the value for version", plversion
		f = open ( top + '\\scripts\\pl.have', 'r')
		have = f.read()
		print 'have =', have
		f.close()
		f = open( top + '\\scripts\\pl.want', 'r')
		want = f.read()
		print 'want = ', want
		f.close()
		if want.strip().lower() == 'latest':
			highestbuild=max([(x) for x in os.listdir(tmplate_src) if x.replace('_','').isdigit()])
			print 'highestbuild = ', highestbuild
			want = highestbuild
			print 'want from highestbuild = ', want
		if [str(want)] != [str(have)]:
			print "1 have =", have, "want =", want
			grabpl = True
			plversion = want
		else:
			print "2 have =", have, "want =", want
			grabpl = False
			print "Exiting gather script we have", have, "what we want", want

	else:
		print "I was told to get version", plversion
		f = open (localtrunk + '\\distrib\\scripts\\BDC.have', 'r')
		have = f.read()
		f.close()
		want = plversion
		if want != have:
			print "3 have =", have, "want =", want
			grabpl = True
		else:
			print "4 have =", have, "want =", want
			grabpl = False
			print "Exiting gather script we have", have, "what we want", want
     

def CopyTemplate():
	global have, want
	#copies current template from ali-netapp1 to tools directory local
	pl_tempsrc = r'\\ali-netapp1.altiris.com\polaris\ITMS\CombinedBuild\ITMSPL_Template'
	pl_template = 'itms_7_1_sp2.pl.xml'
	#check for template in destination if its there remove it.
	if os.path.exists(pl_tempsrc + '\\' + pl_template):
		os.rename(pl_tempsrc + '\\' + pl_template, pl_tempsrc + '\\' + pl_template + "." + have)
	#copy new copy of template to local directory
	shutil.copy(tmplate_src + "\\" + want + "\\" + pl_template, pl_tempsrc)


def UpdateHave():
	global want, top
	#checkout and write to have to match the newly gathered version
	#os.system("p4 -c %s edit %s" % (workspace, BDC_DPT_HV))
	f = open (top + '\\scripts\\pl.have', 'w')
	f.write(str(want))
	f.close()

#This is the main program
if __name__ == '__main__':
	FindLatest()
	if grabpl == True:
		CopyTemplate()
		UpdateHave()