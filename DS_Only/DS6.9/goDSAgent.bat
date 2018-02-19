@echo off
cls
SET TOP=%CD%
SET TOPRULES=%TOP%\build\jam\jamrules
SET DOS32A=%TOP%\build\dos32a
::SET PATH=%TOP%\build\python;%PATH%;%TOP%\build\scons;%TOP%\build\python;%TOP%\build\cxxunit
SET PATH=%TOP%\build\scons;%TOP%\build\python;%TOP%\build\cxxunit;C:\Program Files\Perforce;
SET PYTHONPATH=%TOP%\build\scons
SET P4CLIENT=SCM_DSTEST
SET GRADE=dev_rc
::echo %BRANCH% environment is now set up
echo %TOP% environment is now set up
cd %TOP%
if "%1" == "" goto nocompiler
call %1
:nocompiler
if "%1" == "" title %TOP% (no compiler)
if "%1" == "" goto end
title %TOP% (%1)
goto end
:syntax
echo.
echo          syntax: go [compiler]
echo where compiler is: wat, ms, ce, etc.               (optional)
echo        examples: go ms
echo                  go
:end
