goto comment1
========================================================================================================================================
Purpose:
The purpose of this batch file is to automate the creation of the ITMS 7.1 SP2 PL. There is only one utility involved in the process: modifypl.exe. The first command below runs modfiypl.exe and updates all MSI files to the version found in the path specified by the 
'-directory' switch which must be a mapped drive or unc path. It will aslo update the repository information for each MSI to point to that same path. If the MSI in the path is not found in the PL or if the file is not an MSI it will be skipped (or you may see an error which can be ignored). This command will also update product versions as long as there is a package in that product. In the second and third commands the product version for the DS Complete Suite and Patch Management Soluion are updated using the ProductFixVersion action. In this case you will have to know the version to insert (see variables). The fourth command below changes each repository to point to the 'http' path.
 
Setup:
All utilities that are used in the process are found under the 'C:\Tools' folder.The first step in this process is to copy a 'template' PL file to the c:\Tools\Template folder. This 'template' is nothing more than a normal PL that is configured appropriately with all applicable products and dependencies and such. If this template ever needs to be updated with additional products, or any of the tabs (in SPLE) describing the various aspects of the product need to be changed, it will have be done by manually updating the pl.xml directly or by using SPLE.
 
%1 = Daily builds folder
%2 = Version (e.g., 7.1.6004)
%3 = New repository


=======================================================================================================================================
:comment1


"C:\Tools\ModifyPL\ModifyPL.exe" -pl:"c:\Tools\ModifyPL\ITMS_smp_7_1_sp2.pl.xml" -directory:"z:\itms\combinedbuild\daily_builds\7.1.6004.0\20110712162925\pl" -synchronize -version -wait:60 > ModifyPL_test1.txt

@ECHO Please wait...
REM sleep 3

"C:\Tools\ModifyPL\ModifyPL.exe" -pl:"c:\Tools\ModifyPL\ITMS_smp_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Deployment Solution Complete Suite 7.1 SP2;Altiris Deployment Solution Linux Support 7.1 SP2;Altiris Deployment Solution WinPE Support 7.1 SP2;Altiris Deployment Solution Core 7.1 SP2" "-Version:7.1.6004" > ModifyPL_DS_Version_test1.txt

@ECHO Please wait...
REM sleep 3

"C:\Tools\ModifyPL\ModifyPL.exe" -pl:"c:\Tools\ModifyPL\ITMS_smp_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Patch Management Solution 7.1 SP2;Altiris Patch Management Solution for Windows 7.1 SP2;Altiris Patch Management Solution for Linux 7.1 SP2;Altiris Patch Management Solution for Mac 7.1 SP2" "-Version:7.1.6004" > ModifyPL_PM_Version_test1.txt

@ECHO Please wait...
REM sleep 3

"C:\Tools\ModifyPL\ModifyPL.exe" -pl:"c:\Tools\ModifyPL\ITMS_smp_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Activity Center 7.1 SP2;First Time Setup Portal 7.1 SP2" "-Version:7.1.6004" > ModifyPL_AC_FTSP_Version_test1.txt

@Echo Please wait...
REM sleep 3

"C:\Tools\ModifyPL\ModifyPL.exe" -pl:"c:\Tools\ModifyPL\ITMS_smp_7_1_sp2.pl.xml" -action:PackagesChangeRepository "-OldRepository:z:\itms\combinedbuild\daily_builds\7.1.6004.0\20110712162925\pl" "-NewRepository:http://install.altiris.com/itms/combinedbuild/daily_builds/7.1.6004.0/20110712162925/pl" > ModfyPL_Repos_test1.txt

@ECHO Operation Complete!