@echo off
====================================================================================
REM need to supply a commandline argument for Destination folder path
if "%~1" == "" echo Must supply arg path to trunk example gather C:\ds\trunk
if "%~1" == "" goto :eof

====================================================================================
@REM Remove this to actually do the work
@REM Leave it here, to disable the work

====================================================================================
REM Define some common xcopy options
set FIL_OPTS=/C /I /V /Y /R /K
set DIR_OPTS=/S /E %FIL_OPTS%

====================================================================================
REM Destination location
set DST_DIR=%~1\distrib

====================================================================================
REM Source locations for the various components
set GHT_DIR=\\builddev.altiris.com\buildtest\Uinta\DeploymentServer\Build430-DS69sp3\ProgramFiles\Ghost
set BDC_DIR=\\rdbuild.altiris.com\builds\trunk\9140\bootwiz
set RD_DIR=\\rdbuild.altiris.com\builds\trunk\9147\rd
set SBS_DIR=\\builddev.altiris.com\Transfer\Avalon\SBS_20090420
set DA_DIR=\\builddev.altiris.com\buildtest\Longbow\Dagent\Build375-DS69sp2-Release\ProgramFiles\Agents\AClient\altiris-config-6.9.375.X86.dll
set PCT_DIR=\\builddev.altiris.com\buildtest\Uinta\PCTransplantPro\v6.8\Latest
Set DDB_DIR=\\builddev.altiris.com\buildtest\Uinta\DeploymentServer\Build430-DS69sp3\ProgramFiles\DriversDB

REM New locations...
set GHT_DIR=\\builddev.altiris.com\buildtest\Uinta\DeploymentServer\Build430-DS69sp3\ProgramFiles\Ghost
set BDC_DIR=\\rdbuild.altiris.com\builds\trunk\latest\bootwiz
set RD_DIR=\\rdbuild.altiris.com\builds\trunk\latest
set SBS_DIR=\\rdbuild.altiris.com\builds\trunk\latest\PXE
set DA_DIR=\\builddev.altiris.com\buildtest\Uinta\Dagent\Build430\ProgramFiles\Agents\AClient\altiris-config-6.9.430.X86.dll
set PCT_DIR=\\builddev.altiris.com\buildtest\Uinta\PCTransplantPro\v6.8\Latest
set DDB_DIR=\\builddev.altiris.com\buildtest\Uinta\DeploymentServer\Build430-DS69sp3\ProgramFiles\DriversDB
set FRM_DIR=\\rdbuild.altiris.com\builds\trunk\latest\bootwiz

==================================================================================
REM subroutines per copy
REM call :Ghost
REM call :BDC
REM call :rdeploy
call :SBS
REM call :CONFIG
REM Call :PCT
REM Call :DDB
REM Call :FRM

goto :eof

echo FAILURE!


====================================================================================
REM Gather Ghost files for DS
====================================================================================
:Ghost
echo Copying Ghost files from "%GHT_DIR%"...
REM downloaded .rar Files and extracted those found in Subversion

xcopy "%GHT_DIR%\omnifs32.exe" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\SMEUTIL.SYS" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\gdisk32.exe" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\GhConfig32.exe" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\ghDplyAw32.exe" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\ghost32.exe" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\GhostCast.chm" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\Ghostexp.chm" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\Ghostexp.exe" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\Ghost_imp_guide.pdf" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\GhRegEdit32.exe" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\GhWalk32.exe" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\Ghost Boot Wizard.exe" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%
xcopy "%GHT_DIR%\Ghost Boot Wizard.chm" "%DST_DIR%\Imaging\ghost\" %FIL_OPTS%

xcopy "%GHT_DIR%\Gdisk64.exe" "%DST_DIR%\Imaging\ghost\x64\" %FIL_OPTS%
xcopy "%GHT_DIR%\GhConfig64.exe" "%DST_DIR%\Imaging\ghost\x64\" %FIL_OPTS%
xcopy "%GHT_DIR%\Ghost64.exe" "%DST_DIR%\Imaging\ghost\x64\" %FIL_OPTS%
xcopy "%GHT_DIR%\GhRegEdit64.exe" "%DST_DIR%\Imaging\ghost\x64\" %FIL_OPTS%
xcopy "%GHT_DIR%\OmniFs64.exe" "%DST_DIR%\Imaging\ghost\x64\" %FIL_OPTS%
goto :eof


====================================================================================
REM Gather DRIVERDB directory and Files 
====================================================================================
:DDB
echo Copying DRIVERDB files from "%DDB_DIR%"...
xcopy "%DDB_DIR%\*.*" "%DST_DIR%\DriversDatabase\DriversDB\" %DIR_OPTS%

goto :eof

====================================================================================
REM Gather Bootwiz
====================================================================================
:BDC
echo Copying Bootwiz files from "%BDC_DIR%"...
xcopy "%BDC_DIR%\Bootwiz\*.*" "%DST_DIR%\bootwiz" %DIR_OPTS%
CD %DST_DIR%\bootwiz
call build.bat NS
del build.bat

goto :eof

====================================================================================
REM Gather BDCGPL.frm
====================================================================================
:FRM
echo Copying GPL.FRM files from "%FRM_DIR%"...
xcopy "%FRM_DIR%\*.frm" "%DST_DIR%\Linux_gpl\" %FIL_OPTS%
if exist "%DST_DIR%\Linux_gpl\BdcGpl.frm" del "%DST_DIR%\Linux_gpl\BdcGpl.frm"
rename "%DST_DIR%\Linux_gpl\*.frm" BdcGpl.frm

goto :eof
====================================================================================
REM Gather SBS directory and Files (PXE for NS)
====================================================================================
:SBS
echo Copying SBS files from "%SBS_DIR%"...
xcopy "%SBS_DIR%\SBS\*.*" "%DST_DIR%\SBS" %DIR_OPTS%

goto :eof
====================================================================================
REM Gather Imaging Utilities
=====================================================================================
:RDEPLOY
echo Copying RDeploy files from "%RD_DIR%"...
xcopy "%RD_DIR%\tools\Windows\x86\atrsimg.dll" "%DST_DIR%\Imaging\rdeploy\" %FIL_OPTS%
xcopy "%RD_DIR%\tools\Windows\x86\atrsimg.dll" "C:\ds\trunk\build\image\" %FIL_OPTS%

xcopy "%RD_DIR%\rd\RDeploy\Windows\imgexpl.exe"  "%DST_DIR%\Imaging\rdeploy\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\RDeploy\Windows\rdeploy.exe"  "%DST_DIR%\Imaging\rdeploy\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\RDeploy\Windows\rdeployt.exe" "%DST_DIR%\Imaging\rdeploy\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\RDeploy\Windows\firm.exe"     "%DST_DIR%\Imaging\rdeploy\" %FIL_OPTS%

xcopy "%RD_DIR%\rd\TechSup\Windows\partgen.exe"  "%DST_DIR%\Imaging\rdeploy\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Windows\showdisk.exe" "%DST_DIR%\Imaging\rdeploy\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Windows\wipe.exe"     "%DST_DIR%\Imaging\rdeploy\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Windows\fscs.exe      "%DST_DIR%\Imaging\rdeploy\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Windows\makeimx.exe   "%DST_DIR%\Imaging\rdeploy\" %FIL_OPTS%

xcopy "%RD_DIR%\rd\RDeploy\Windows\x64\rdeploy.exe"  "%DST_DIR%\Imaging\rdeploy\x64\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\RDeploy\Windows\x64\rdeployt.exe" "%DST_DIR%\Imaging\rdeploy\x64\" %FIL_OPTS% 
xcopy "%RD_DIR%\rd\RDeploy\Windows\x64\firm.exe"     "%DST_DIR%\Imaging\rdeploy\x64\" %FIL_OPTS%

xcopy "%RD_DIR%\rd\TechSup\Windows\x64\partgen.exe"  "%DST_DIR%\Imaging\rdeploy\x64\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Windows\x64\showdisk.exe" "%DST_DIR%\Imaging\rdeploy\x64\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Windows\x64\wipe.exe"     "%DST_DIR%\Imaging\rdeploy\x64\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Windows\x64\fscs.exe      "%DST_DIR%\Imaging\rdeploy\x86\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Windows\x64\makeimx.exe   "%DST_DIR%\Imaging\rdeploy\x86\" %FIL_OPTS%

xcopy "%RD_DIR%\rd\RDeploy\Linux\rdeployt." "%DST_DIR%\imaging\rdeploy\Linux\x86\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\RDeploy\Linux\firm."     "%DST_DIR%\imaging\rdeploy\Linux\x86\" %FIL_OPTS%

xcopy "%RD_DIR%\rd\TechSup\Linux\fscs."     "%DST_DIR%\imaging\rdeploy\Linux\x86\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Linux\makeimx."  "%DST_DIR%\imaging\rdeploy\Linux\x86\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Linux\partgen."  "%DST_DIR%\imaging\rdeploy\Linux\x86\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Linux\showdisk." "%DST_DIR%\imaging\rdeploy\Linux\x86\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Linux\wipe."     "%DST_DIR%\imaging\rdeploy\Linux\x86\" %FIL_OPTS%

xcopy "%RD_DIR%\rd\RDeploy\Linux\x64\rdeployt." "%DST_DIR%\imaging\rdeploy\Linux\x64\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\RDeploy\Linux\x64\firm."     "%DST_DIR%\imaging\rdeploy\Linux\x64\" %FIL_OPTS%

xcopy "%RD_DIR%\rd\TechSup\Linux\x64\fscs."     "%DST_DIR%\imaging\rdeploy\Linux\x64\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Linux\x64\makeimx."  "%DST_DIR%\imaging\rdeploy\Linux\x64\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Linux\x64\partgen."  "%DST_DIR%\imaging\rdeploy\Linux\x64\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Linux\x64\showdisk." "%DST_DIR%\imaging\rdeploy\Linux\x64\" %FIL_OPTS%
xcopy "%RD_DIR%\rd\TechSup\Linux\x64\wipe."     "%DST_DIR%\imaging\rdeploy\Linux\x64\" %FIL_OPTS%

goto :eof
=====================================================================================
REM Gather DAgent config.dll Static file
=====================================================================================
:CONFIG
echo Copying DAgent files from "%DA_DIR%"...
xcopy "%DA_DIR%" "%DST_DIR%\config\config.dll" %FIL_OPTS%

goto :eof
=====================================================================================
REM PCT FILES Current version in build as of 8/14/09 6.8.1054
=====================================================================================
:PCT
echo Copying PCT files from "%PCT_DIR%"...
xcopy "%PCT_DIR%\*.*" "%DST_DIR%\PCT" %DIR_OPTS%

goto :eof
