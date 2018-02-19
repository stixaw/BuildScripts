import os, logging
import bldutils


class BuildClient:

    def __init__(self, options):
	self.options = options

	# Files that need to be checked out before the build and reverted
	# afterward because they get changed by build tools.
	# TODO: We now have two copies of this list.  One here, one in
	# build.py.  We need to figure out how to combine these!
	self.filesThatChange = (
	    self.options['localPath'] + r'\apps\DeploymentServer\Deployment\Config\Altiris.Deployment_Collections.config',
	    self.options['localPath'] + r'\apps\DeploymentClient\install\Altiris_Deployment_Agent.wsi',
	    self.options['localPath'] + r'\apps\DeploymentClient\install\Altiris_Deployment_Agent_x64.wsi',
	    self.options['localPath'] + r'\apps\DeploymentClient\install\Altiris_Deployment_Agent_86_x64.wsi',
	    self.options['localPath'] + r'\apps\DeploymentServer\install\Altiris_Deployment_TaskServerHandler.wsi',
	    self.options['localPath'] + r'\apps\DeploymentServer\install\Altiris_Deployment_TaskServerHandler_x64.wsi',
	    self.options['localPath'] + r'\apps\DeploymentServer\install\Altiris_Deployment_TaskServerHandler_KB_HF.wsi',
	    self.options['localPath'] + r'\apps\DeploymentInstall\Altiris_Deployment.wsi',
	    self.options['localPath'] + r'\apps\DeploymentInstall\Altiris_Deployment_x64.wsi',
	    self.options['localPath'] + r'\apps\DeploymentInstall\altiris_ns_winpe2.1.wsi',
	    self.options['localPath'] + r'\apps\DeploymentInstall\altiris_ns_winpe2.1_x64.wsi',
	    self.options['localPath'] + r'\apps\DeploymentInstall\altiris_ns_winpe2.1_86_x64.wsi',
	    self.options['localPath'] + r'\apps\DeploymentInstall\altiris_ns_winpe2.1_64_x64.wsi',
	    self.options['localPath'] + r'\apps\DeploymentInstall\altiris_ns_linux_gpl.wsi',
	    self.options['localPath'] + r'\apps\DeploymentInstall\altiris_ns_linux_gpl_x64.wsi',
	    self.options['localPath'] + r'\apps\DeploymentInstall\Altiris_NS_DriversDB.wsi',
	    self.options['localPath'] + r'\apps\DeploymentInstall\Altiris_NS_DriversDB_x64.wsi',
	    self.options['localPath'] + r'\OEM\DS\Linux\x86\Base\tmp\.aex-agent-install-config.xml',
        self.options['localPath'] + r'\common\JavaApplet\CopyFolderFile\plugin.jar',
        self.options['localPath'] + r'\common\JavaApplet\CopyFolderFile\dist\CopyFolderFile.jar',
        self.options['localPath'] + r'\apps\DeploymentServer\Altiris.Deployment.Web\include\CopyFolderFile.jar'
	    # self.options['localPath'] + r'\distrib\bootwiz.zip',
	    # self.options['localPath'] + r'\distrib\rdeploy.zip',
	    # self.options['localPath'] + r'\distrib\config.zip',
	    # self.options['localPath'] + r'\distrib\linuxgpl.zip',
	    # self.options['localPath'] + r'\distrib\PCT.zip',
	    # self.options['localPath'] + r'\distrib\SBS.zip',
	    # self.options['localPath'] + r'\distrib\SBS_x64.zip'
	)


    # If you want the SCM code to auto-number, return None.  Otherwise, you go
    # find out what you want your next build number to be, based on the
    # branch, and return the next build number here.
    def GetNextBuildNumber(self):
	return None


    def GetToolList(self):
	return ['batch', 'MSVC80SP1.X86', 'msvc90sp1-ATLFix.x86',
		'Silverlight/v3.0', 'Silverlight/Chiron', 'Microsoft.NET',
		'jdk1.6.0_14_windows', 'MSSDKv6.0A']

    # This will let the SCM code show the log to the web interface, etc.
    def GetLogFilePath(self):
	logFilePath = self.options['localPath'] + '\\build.log'
	logging.debug('Returning log file path:' + logFilePath)
	return logFilePath


    def GetMergeSkipList(self):
	mergeSkipList = [
	'\\apps\DeploymentServer\Deployment\Config\Altiris.Deployment_Collections.config',
	'\\apps\\DeploymentClient\\install\\Altiris_Deployment_Agent.wsi',
	'\\apps\\DeploymentClient\\install\\Altiris_Deployment_Agent_x64.wsi',
	'\\apps\\DeploymentClient\\install\\Altiris_Deployment_Agent_86_x64.wsi',
	'\\apps\\DeploymentServer\\install\\Altiris_Deployment_TaskServerHandler.wsi',
	'\\apps\\DeploymentServer\\install\\Altiris_Deployment_TaskServerHandler_x64.wsi',
	'\\apps\\DeploymentServer\\install\\Altiris_Deployment_TaskServerHandler_KB_HF.wsi',
	'\\apps\\DeploymentInstall\\Altiris_Deployment.wsi',
	'\\apps\\DeploymentInstall\\Altiris_Deployment_x64.wsi',
	'\\apps\\DeploymentInstall\\altiris_ns_winpe2.1.wsi',
	'\\apps\\DeploymentInstall\\altiris_ns_winpe2.1_x64.wsi',
	'\\apps\\DeploymentInstall\\altiris_ns_winpe2.1_86_x64.wsi',
	'\\apps\\DeploymentInstall\\altiris_ns_winpe2.1_64_x64.wsi',
	'\apps\\DeploymentInstall\\altiris_ns_linux_gpl.wsi',
	'\\apps\\DeploymentInstall\\altiris_ns_linux_gpl_x64.wsi',
	'\\apps\\DeploymentInstall\\Altiris_NS_DriversDB.wsi',
	'\\apps\\DeploymentInstall\\Altiris_NS_DriversDB_x64.wsi',
	'\\build\\scripts\\build.py',
	'\\build\\scripts\\scmclient.py',
	'\\distrib...'
	]
	logging.debug('GetMergeSkipList() returning:' + str(mergeSkipList))
	return mergeSkipList


    # Check your own build server out and raise an exception if there's a
    # problem that should stop a build from occurring.
    def CheckStatus(self):
	logging.debug('CheckStatus(' + self.options['branch'] + ')')

	connectList = [
#			('w', '\\\\192.168.232.12\\ForAltiris\\Provisioning_Builds\\Latest'),
#			('w', '\\\\builddev.altiris.com\\buildtest\\DeploymentSolution'),
#			('w', '\\\\linus-scratch.altiris.com\\Scratch\\From_Polaris\\DeploymentSolution')
		      ]

	buildStatus = bldutils.CheckConnectivity(connectList)

#	buildStatus += '\n' + bldutils.CheckSpace('u:\\', 10)
#	buildStatus += '\n' + bldutils.CheckSpace('r:\\', 10)
#	buildStatus += '\n' + bldutils.CheckSpace('s:\\', 10)
#	buildStatus += '\n' + bldutils.CheckSpace('t:\\', 2)
#
#	# Also check drive letters of above shares!
#	try:
#	    bldutils.CheckDriveMappings({'s:':'\\\\builddev.altris.com\\buildtest',
#					 'r:':'\\\\rdbuild.altiris.com\\builds',
#					 't:':'\\\\192.168.232.12\\ForAltiris',
#                    'u:':'\\\\linus-scratch.altiris.com\\Scratch'
#				       })
#
#	    buildStatus += '\n  Drive mappings OK.'
#	except Exception, instance:
#	    buildStatus += '\n\n  ' + str(instance)
#	    raise Exception(buildStatus)

	statusGood = True
	badText = ['NO WRITE', 'NO READ', 'ONLY']
	for text in badText:
	    if text in buildStatus:
		statusGood = False

	if not statusGood:
	    raise Exception(buildStatus)

	    
    def RunBuildPy(self, args):
	command = 'python ' + self.options['localPath'] + '\\build\\scripts\\build.py --top=' + self.options['localPath'] + ' ' + args
	bldutils.Execute(command, self.GetLogFilePath())


    # If there's anything that needs to happen BEFORE the label is created
    # (e.g. checking in a librev.h type file) do it here.
    def PrepareForBuild(self):
	logging.info('BuildClient.PrepareForBuild:' + self.options['branch'] + ', build ' + self.options['buildnum'])
	self.RunBuildPy('--cleanall')


    # Build your stuff.  The label has now been created and
    # "self.options['localPath']" points to the top of the source code for you
    # to build.
    def Build(self):
	logging.info('BuildClient.Build:' + self.options['branch'] + ', build ' + self.options['buildnum'])

	# Check out files that will be changed (make not readonly)
	for file in self.filesThatChange:
	    self.options['srcFacade'].CheckOut(file)

	if self.options['labelWillBeCreated']:
	    copyType = '--copy-output'
	else:
	    if self.options['buildAlreadyExists']:
		copyType = ''
	    else:
		copyType = '--copy-builddev'

	try:
	    self.RunBuildPy(copyType + ' --buildnum ' + self.options['buildnum'])
	finally:
	    # Revert changed files
	    for file in self.filesThatChange:
		self.options['srcFacade'].Revert(file)


    # Copy your output to servers here.  If this fails, it will not fail the
    # build so that you can retry the copy, for example.
    def Copy(self):
	logging.info('BuildClient.Copy:' + self.options['branch'] + ', build ' + self.options['buildnum'])


    # Clean up your area before you leave if you want to.
    def CleanupAfterBuild(self):
	logging.info('BuildClient.CleanupAfterBuild:' + self.options['branch'] + ', build ' + self.options['buildnum'])
	self.RunBuildPy('--clean')
