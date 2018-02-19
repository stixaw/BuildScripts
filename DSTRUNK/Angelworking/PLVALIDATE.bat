@echo on
REM ============================================================================================================================================
REM PL Validation tool .com object caller
REM Tests RUN XML Is Well-Formed,Required Product Attributes Are Present,No Duplicate ProductInstallGuids, No Duplicate MSI Package Code, Dependencies Exist, No Circular Dependencies, Supersedes Exist, No Circular Supersedes, Updates Exist, No REM Circular Updates,Hotfix Releases Update and Depend On a Product
REM %1 = top
REM %2 = PLDIR (where the itms pl was created by plautomate process)
REM ============================================================================================================================================

%1\CM\PLValidator\Symantec.PLValidator.exe -pl "%2\itms_7_1_sp2.pl.xml" -tests "XML Is Well-Formed,Required Product Attributes Are Present,No Duplicate ProductInstallGuids, No Duplicate MSI Package Code, Dependencies Exist, No Circular Dependencies, Supersedes Exist, No Circular Supersedes, Updates Exist, No Circular Updates,Hotfix Releases Update and Depend On a Product"
set err=%errorlevel%
echo %err% 1>&2
