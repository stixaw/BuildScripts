REM Calls SIMPLER TOOL

REM this script requires 2 parameters to run

REM %1 = TOP
REM %2 = BLD NUMBER

REM Example command:

REM Simpler.bat c:\ds\trunk 1018

REM========================================
REM CALL SIMPLER


"%1\build\Simpler\Simpler.exe" /pl "%1\build\Simpler\1250\Altiris Deployment Solution x64.pl.xml" /saveas "C:\Solution7.1\Altiris Deployment Solution x64.pl.xml" /product "Altiris Deployment Solution x64" /product "Altiris Deployment Solution Core" /product "Altiris Deployment Solution Linux Support" /product "Altiris Deployment Solution WinPE Support" /product "Altiris Deployment Solution Complete Suite" /product "Altiris Deployment Solution Languages" /product "Altiris Deployment Solution with Winpe Support" /prodver 7.1.%2 /plver 7.1.%2 /updatemsi /local "C:\Solution7.1" /repos "C:\Solution7.1" /checkprodcodes "*.msi"

"%1\build\Simpler\Simpler.exe" /pl "%1\build\Simpler\ITMSPL\ITMS_SP1.pl.xml" /saveas "C:\Solution7.1\ITMS_SP1.pl.xml" /product "Altiris Deployment Solution" /product "Altiris Deployment Solution Core" /product "Altiris Deployment Solution Linux Support" /product "Altiris Deployment Solution WinPE Support" /product "Altiris Deployment Solution Complete Suite" /product "Altiris Deployment Solution Languages" /product "Altiris Deployment Solution with Winpe Support" /prodver 7.1.%2 /plver 7.1.%2 /updatemsi /local "C:\Solution7.1" /repos "C:\Solution7.1" /checkprodcodes "*.msi"