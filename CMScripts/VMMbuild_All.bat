@echo off
echo Starting VMM build %date% %time%

::What build do you want to do?
REM set buildTODO=debug
set buildTODO="release"

REM verify if version is specified
if "" == "%ITMSVERSION%" goto MissedVersion

REM start job
goto Start

:MissedVersion

REM version is missed
echo ERROR: Environment variable ITMSVERSION is not specified.
exit /b 1

REM okay, proceed
:Start

set LOGFILE=VMM_build.log
if EXIST %LOGFILE% del %LOGFILE%
"C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\IDE\devenv.exe" vman.sln /build %buildTODO% /BuildVersion %ITMSVERSION% /out %LOGFILE%

REM Dump log file to Std out so will show up in the Hudson log
if ERRORLEVEL 1 (
    echo Error: %0 failed
	type %LOGFILE%
	exit /b 1
    set ERROR=1
  )
  
echo Copying .msi files
del c:\output_msi\*.msi
xcopy /y vMan\Release\VMM_x64.msi c:\output_msi\
xcopy /y VMMLP\Release\VMMLanguages_x64.msi c:\output_msi\

echo "Build Complete" %date% %time%