REM @echo off
REM This batch file is used to stop and start Hudson slaves.
REM The name of the file must match the name of the Node.  ie node name is mynode, batch file name is mynode.bat

REM Set ENV variables
set VMRUNPATH="C:\Program Files (x86)\VMware\VMware VIX\vmrun.exe"
set VMX_FILE="[ITMSCB] ACX64WINBUILD/ACX64WINBUILD.vmx"
set VCENTER_URL=10.105.1.205
set HUDSON_URL=http://10.105.19.89/hudson/
set VC_USER=linus\ITMSBUILD
set VC_PASS=1TMS8uild
set VM_USER=administrator
set VM_PASS=altiris
set VM_IP=10.105.19.51
set NODE_NAME=ACX64WINBUILD

if "%1" == "start" goto start_node
if "%1" == "stop" goto stop_node
goto syntax

:start_node
echo Starting the node
REM Revert to clean snapshot
echo Reverting the snapshot
%VMRUNPATH% -T server -h %VCENTER_URL% -u %VC_USER% -p %VC_PASS% revertToSnapshot %VMX_FILE% BUILDSTART

REM Start up the VM
%VMRUNPATH% -T server -h %VCENTER_URL% -u %VC_USER% -p %VC_PASS% start %VMX_FILE% 

REM Pause for 2 minutes while server starts up
rem PING 1.1.1.1 -n 1 -w 120000

Rem Start up the Hudson slave with VIX
REM %VMRUNPATH% -T server -h %VCENTER_URL% -u %VC_USER% -p %VC_PASS% -gu %VM_USER% -gp %VM_PASS% runProgramInGuest %VMX_FILE% -noWait "C:\Program Files\Java\jre6\bin\java.exe" -jar c:/Hudson/slave.jar  -jnlpUrl http://10.160.72.62/computer/DSBUILD-SVR-4/slave-agent.jnlp

Rem Run a VIX command to wait for the server to startup before starting slave
%VMRUNPATH% -T server -h %VCENTER_URL% -u %VC_USER% -p %VC_PASS% -gu %VM_USER% -gp %VM_PASS% runProgramInGuest %VMX_FILE% C:\WINDOWS\system32\cmd.exe /c dir
echo VM is started, starting slave
REM Start the slave with SSH
"C:\Program Files (x86)\Openssh\bin\ssh" -v %VM_USER%@%VM_IP% java -jar c:/hudson/slave.jar -text
goto end

:stop_node
REM Disconnect the slave befoe stopping the VM.  Using Hudson CLI with authentication
echo Stopping the slave
java -jar c:\hudson\hudson-cli.jar -s %HUDSON_URL%  disconnect-node %NODE_NAME% -m "stopping node after build" --username admin --password altiris


REM Stop the VM
echo Stopping the VM
%VMRUNPATH% -T server -h %VCENTER_URL% -u %VC_USER% -p %VC_PASS% stop %VMX_FILE% 
goto end

:syntax
echo syntax: %0 [start, stop]
goto end

:end