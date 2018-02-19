@echo off
REM Copy the build symbols over using the symstore.exe

set noofArgs=0

for %%i in (%*) do set /A  %noofArgs+=1

if %noofArgs% NEQ 3 (
  goto Usage

)

set PDB_SRC=%1
set BUILD_NUMBER=%2
set SOL=%3

net use \\ali-netapp1.altiris.com\Dev_Store1 /user:linus\ITMSBuild 1TMS8uild

%WORKSPACE%\CM\Scripts\SymStore\symstore.exe add /o /r /f %PDB_SRC%\*.pdb /s  \\ali-netapp1.altiris.com\Dev_Store1\ITMS_Symbols /t "%SOL%"  /v "%BUILD_NUMBER%"

goto EOF

:Usage

  echo [USAGE]: %~1 arg1 arg2 arg3
  echo "arg1 : <path to pdb files>  eg: WORKSPACE\Source\release"
  echo "arg2 : Build_number eg: 7.1.6000.0"
  echo "arg3 : Name of the Solution to be entered in the Symbol Store eg: pcAnywhereSolution"
  goto EOF

:EOF

