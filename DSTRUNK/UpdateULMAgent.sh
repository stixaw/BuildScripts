cd $TOP/OEM/DS/Linux/x86/Base

tar xvfz ULMagent.tgz

cp $TOP/output_lin/ClientCaptureImage/Release/ClientCaptureImage.so   opt/altiris/notification/DeploymentSolutionAgent/lib/plugins/
cp $TOP/output_lin/ClientCopyFile/Release/ClientCopyFile.so   opt/altiris/notification/DeploymentSolutionAgent/lib/plugins/
cp $TOP/output_lin/ClientImageDeploy/Release/ClientImageDeploy.so   opt/altiris/notification/DeploymentSolutionAgent/lib/plugins/
cp $TOP/output_lin/ClientLinuxSOI/Release/ClientLinuxSOI.so   opt/altiris/notification/DeploymentSolutionAgent/lib/plugins/
cp $TOP/output_lin/ClientPartitionDisk/Release/ClientPartitionDisk.so   opt/altiris/notification/DeploymentSolutionAgent/lib/plugins/
cp $TOP/output_lin/ClientRebootTo/Release/ClientRebootTo.so   opt/altiris/notification/DeploymentSolutionAgent/lib/plugins/
cp $TOP/output_lin/ClientWipe/Release/ClientWipe.so   opt/altiris/notification/DeploymentSolutionAgent/lib/plugins/
cp $TOP/output_lin/DeploymentSolutionAgent/Release/DeploymentSolutionAgent.so   opt/altiris/notification/DeploymentSolutionAgent/lib/plugins/
cp $TOP/output_lin/ClientLinuxPreImage/Release/ClientPreImage.so  opt/altiris/notification/DeploymentSolutionAgent/lib/plugins/


rm -f ULMagent.tgz

tar cvfz ULMagent.tgz opt/

cd $TOP

