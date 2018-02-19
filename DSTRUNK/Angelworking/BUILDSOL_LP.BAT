REM Build LP batch file for any solution

REM this script requires 2 parameters to run

REM %1 = TOP
REM %2 = buildnumber IE 7.1.1250
REM %3 = Path to BuildLP
REM %4 = SLN file
REM %5 ProjectName

REM Example Call: BuildLP.bat %WORKSPACE%\trunk 1250 %WORKSPACE%\CM\BuildLP

REM ===============================================================
%3\BuildLP.exe %1\%4 %5 Release false E

"C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\IDE\devenv.exe" %1\%4 /build Release /project %5 /buildversion %2