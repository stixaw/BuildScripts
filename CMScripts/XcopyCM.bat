@echo off
echo Copying CM files to slave

xcopy X:\Hudson\CM\Scripts\*.* "%WORKSPACE%\CM\Scripts" /C/I/V/Y/R/K/S/E
xcopy X:\Hudson\CM\Verisign\*.* "%WORKSPACE%\CM\Verisign" /C/I/V/Y/R/K/S/E
