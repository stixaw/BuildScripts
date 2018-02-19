@echo off
REM Copy the build symbols over using the symstore.exe

set noofArgs=0

for %%i in (%*) do set /A  %noofArgs+=1

if %noofArgs% NEQ 6 (
  goto Usage

)

set PDB_SRC=%1
set BUILD_NUMBER=%2
set SOL=%3
set OUTPUTLOCATION=%4
set USERNAME=%5
set PASSWORD=%6

net use "%OUTPUTLOCATION%" /user:%USERNAME% %PASSWORD%

%WORKSPACE%\CM\Scripts\SymStore\symstore.exe add /o /r /f %PDB_SRC%\*.pdb /s  "%OUTPUTLOCATION%" /t "%SOL%"  /v "%BUILD_NUMBER%"

goto EOF

:Usage

  echo [USAGE]: %~1 arg1 arg2 arg3 arg4 arg5 arg6
  echo "arg1 : <path to pdb files>  eg: WORKSPACE\Source\release"
  echo "arg2 : Build_number eg: 7.1.6000.0"
  echo "arg3 : Name of the Solution to be entered in the Symbol Store eg: pcAnywhereSolution"
  echo "arg4 : Output location where symbols would be stored e.g. \\ali-netapp1.linus.sen.symantec.com\Build\Lindon\Symbols"
  echo "arg5 : UserName used to connect to Output location"
  echo "arg6 : Password for username used to connect to Output location"
  goto EOF

:EOF

