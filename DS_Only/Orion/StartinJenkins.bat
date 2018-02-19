set ITMSMARKET=%1
set ITMSBUILDNUM=%2

echo ******************************************************  Now Building Language Pack *******************************************
CD %WORKSPACE%\trunk
SET TOP=%CD%
SET PATH=%TOP%\build\scons;%TOP%\build\python;%TOP%\build\python\Lib\site-packages\pywin32_system32;c:\windows;C:\windows\system32;C:\Program Files\Perforce;%TOP%\build\windows\system32
SET PYTHONPATH=%TOP%\build\python;%TOP%\build\scons
SET TOP=%WORKSPACE%\trunk
SET PLDIR=C:\output_msi
IF EXIST %PLDIR% ( 
   cd %PLDIR%
   del /F /Q *.*
)

CD %WORKSPACE%\trunk
p4 revert //%P4CLIENT%/...
python build\scripts\LangPack_Copy.py --top=%WORKSPACE%\trunk --version=%ITMSMARKET%. --buildnum=%ITMSBUILDNUM% build


echo ***************************************************    Now Building Trunk *******************************************
CD %WORKSPACE%\trunk
SET TOP=%CD%
SET PATH=%TOP%\build\scons;%TOP%\build\python;%TOP%\build\python\Lib\site-packages\pywin32_system32;c:\windows;C:\windows\system32;C:\Program Files\Perforce;%TOP%\build\windows\system32
SET PYTHONPATH=%TOP%\build\python;%TOP%\build\scons
set DSTOOLS=dsbuilder-pune-tools

python build\scripts\devbuild.py --top=%WORKSPACE%\trunk --workspace=%P4CLIENT% --tools=%DSTOOLS% --buildnum=%ITMSBUILDNUM%


echo ****************************************************    BUILD OVER **********************************************

SET OUTPUTMSI=C:\output_msi
SET TOP=%WORKSPACE%\trunk




echo ***********************************  Now Verifying ALL MSI EXISTS for PL creation ************************************
cd %OUTPUTMSI%
IF NOT EXIST "deploymentsolutionlanguages_x64.msi" goto EXITWITHERROR
IF NOT EXIST "DeploymentSolution_x64.msi" goto EXITWITHERROR
IF NOT EXIST "DeploymentSolutionLINUX_x64.msi" goto EXITWITHERROR
goto CONTINUE

:EXITWITHERROR
  echo ********************************************************************************
  echo "ERROR  : One or more msi are missing for PL creation, So Stopping here .............."
  exit -1

:CONTINUE


