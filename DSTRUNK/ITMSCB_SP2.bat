@echo off
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
%4 = top
%5 = BUILDNUM

=======================================================================================================================================
:comment1
@echo on


"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" -directory:"%1" -synchronize -version -wait:60

@ECHO Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Activity Center 7.1 SP2;First Time Setup Portal 7.1 SP2;Activity Center Languages 7.1 SP2" "-Version:%2" > ModifyPL_AC_FTSP_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Asset Management Suite 7.1 SP2;Altiris Asset Management Languages 7.1 SP2;Altiris Asset Management Solution 7.1 SP2;" "-Version:%2" > ModifyPL_AM_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris CMDB Languages 7.1 SP2;Altiris CMDB Solution 7.1 SP2" "-Version:%2" > ModifyPL_CMDB_Version.txt

@Echo Please wait...
REM sleep 3

REM "%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Deployment Solution Complete Suite 7.1 SP2;Altiris Deployment Solution Linux Support 7.1 SP2;Altiris Deployment Solution WinPE Support 7.1 SP2;Altiris Deployment Solution Core 7.1 SP2" "-Version:%2" > ModifyPL_DS_Version.txt

REM @ECHO Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Event Console 7.1 SP2;Altiris Event Console Languages 7.1 SP2" "-Version:%2" > ModifyPL_EC_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Inventory for Network Devices 7.1 SP2;Altiris Inventory for Network Devices Languages 7.1 SP2" "-Version:%2" > ModifyPL_ISND_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Inventory Pack for Servers 7.1 SP2;Altiris Inventory Pack for Servers Languages 7.1 SP2" "-Version:%2" > ModifyPL_IPS_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Inventory Solution 7.1 SP2;Altiris Inventory Solution Languages 7.1 SP2" "-Version:%2" > ModifyPL_IPS_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Monitor Pack for Servers Languages 7.1 SP2;Altiris Monitor Pack for Servers 7.1 SP2" "-Version:%2" > ModifyPL_MP_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Monitor Solution for Servers Languages 7.1 SP2;Altiris Monitor Solution for Servers 7.1 SP2" "-Version:%2" > ModifyPL_MC_Version.txt

@Echo Please wait...
REM sleep 3

REM "%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Network Topology Viewer 7.1 SP2;Altiris Network Topology Viewer Languages 7.1 SP2" "-Version:%2" > ModifyPL_TOP_Version.txt

REM @Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Out-of-Band Management 7.1 SP2;Altiris Out-of-Band Management Languages 7.1 SP2" "-Version:%2" > ModifyPL_OOB_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Patch Management Solution 7.1 SP2;Altiris Patch Management Solution for Windows 7.1 SP2;Altiris Patch Management Solution for Linux 7.1 SP2;Altiris Patch Management Solution for Mac 7.1 SP2" "-Version:%2" > ModifyPL_PM_Version.txt

@ECHO Please wait...
REM sleep 3

REM "%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Power Scheme Task 7.1 SP2;Altiris Power Scheme Task Languages 7.1 SP2" "-Version:%2" > ModifyPL_PS_Version.txt

REM @Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Real-Time Console Infrastructure Languages 7.1 SP2;Altiris Real-Time System Manager Languages 7.1 SP2;Altiris Real-Time Console Infrastructure 7.1 SP2;Altiris Real-Time System Manager 7.1 SP2" "-Version:%2" > ModifyPL_RTSM_Version.txt

@Echo Please wait...
REM sleep 3

REM "%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Server Management Suite 7.1 SP2;Altiris Server Management Suite Languages 7.1 SP2;Altiris Server Management Suite Portal Page 7.1 SP2" "-Version:%2" > ModifyPL_SMSP_Version.txt

REM @Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Software Catalog Data Provider 7.1 SP2;Altiris Software Catalog Data Provider Languages 7.1 SP2;" "-Version:%2" > ModifyPL_ISSC_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Software Management Solution 7.1 SP2;Altiris Software Management Solution Languages 7.1 SP2" "-Version:%2" > ModifyPL_SM_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Altiris Virtual Machine Management 7.1 SP2;Altiris Virtual Machine Management Languages 7.1 SP2" "-Version:%2" > ModifyPL_VMM_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Symantec pcAnywhere 7.1 SP2;Symantec pcAnywhere Languages 7.1 SP2" "-Version:12.6.%5" > ModifyPL_PCA_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Symantec ServiceDesk Solution Languages 7.1 SP2;Symantec ServiceDesk Solution 7.1 SP2" "-Version:%2" > ModifyPL_SD_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" "-action:ProductFixVersion" "-ProductNames:Wise Connector 7.1 SP2;Wise Connector Languages 7.1 SP2" "-Version:%2" > ModifyPL_WC_Version.txt

@Echo Please wait...
REM sleep 3

"%4\CM\PLXML\ModifyPL.exe" -pl:"%4\CM\PLXML\ITMS_7_1_sp2.pl.xml" -action:PackagesChangeRepository "-OldRepository:%1" "-NewRepository:%3" > ModfyPL_Repos.txt

@ECHO Operation Complete!