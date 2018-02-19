REM PCA Copy script

REM PCA Copy script
REM  %1  = BuildNumber
REM %2 = branch
REM %3 =top

set TOP=%3%
set  branch=%2%
set  BUILD_NUMBER=%1%

cd %TOP%
echo %TOP%
echo %branch%
echo %BUILD_NUMBER%

xcopy /Y /e /k /h /q "%TOP%\source\Release\*.dll" "C:\2 Sign\"
xcopy /Y /e /k /h /q "%TOP%\source\Release\*.exe" "C:\2 Sign\"

cd "C:\2 Sign"
call sign.bat

cd %TOP%

net use \\ali-netapp1.linus.sen.symantec.com\Build /user:linus\ITMSBUILD 1TMS8uild
set NETDIR=\\ali-netapp1.linus.sen.symantec.com\Build\Lindon\pcanywhere\Builds
mkdir %NETDIR%\%branch%\%BUILD_NUMBER%\Symbols\
mkdir %NETDIR%\%branch%\%BUILD_NUMBER%\output_win\

xcopy /Y /e /k /h /q "%TOP%\source\Release\*.pdb" %NETDIR%\%branch%\%BUILD_NUMBER%\Symbols\
xcopy /Y /e /k /h /q "C:\2 Sign\*.dll" %NETDIR%\%branch%\%BUILD_NUMBER%\output_win\
xcopy /Y /e /k /h /q "C:\2 Sign\*.exe" %NETDIR%\%branch%\%BUILD_NUMBER%\output_win\