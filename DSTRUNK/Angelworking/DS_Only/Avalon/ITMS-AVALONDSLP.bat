REM==== BUILD LP USING BuildLP.exe =======

REM this script requires 1 parameter to run

REM %1 = TOP
REM %2 = BuildNumber

REM Example command:

REM BuildDSLP.bat c:\ds\trunk 1250

REM=======================================
rem initiate the retry number
set retryNumber=0

:BUILDLP
%1\build\BuildLP\BuildLP.exe %1\build\LP-2008\Deployment\Deployment\Deployment.sln DeploymentSolution_LanguagePack Release false EU

IF ERRORLEVEL 1 GOTO :RETRY
REM re-set the retry number if success
set retryNumber=0
GOTO :BUILDMSI

:BUILDMSI
"C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\IDE\devenv.exe" %1\build\LP-2008\Deployment\Deployment\Deployment.sln /build Release /project DeploymentSolution_LanguagePack /buildversion %2

if ERRORLEVEL 1 (
@echo (%date% %time%) Msi Creation Failed
type LPMSI.log
Exit 1)

GOTO :EXIT

:RETRY
set /a retryNumber=%retryNumber%+1
@echo (%date% %time%) There was an error with BuildLP.exe retrying the Extract and Update process
IF %retryNumber% LSS 4 (GOTO :BUILDLP)
IF %retryNumber% EQU 4 (GOTO :ERR)

:ERR
echo (%date% %time%)BuildLP Extraction Failed Check Your Solution
type LP.log
Exit

:EXIT
Exit