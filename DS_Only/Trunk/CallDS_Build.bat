SET TOP=%CD%
SET PATH=%TOP%\build\scons;%TOP%\build\python;%TOP%\build\python\Lib\site-packages\pywin32_system32;c:\windows;C:\windows\system32;C:\Program Files\Perforce;%TOP%\build\windows\system32
SET PYTHONPATH=%TOP%\build\python;%TOP%\build\scons

python build\scripts\ECbuild.py --top=%WORKSPACE%\trunk --workspace=%P4CLIENT% --tools=%DSTOOLS% --buildnum=%ITMSBUILDNUM%