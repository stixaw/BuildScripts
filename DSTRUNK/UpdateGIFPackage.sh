#!/bin/sh

GIF_BNUM=$1;
TOP=$2;

echo $TOP;
p4pswd=$TOP/build/scripts/p4psswd.txt;

mkdir -p /mnt/GIFPackages
sudo mount -t cifs //10.217.13.199/GIFPackages /mnt/GIFPackages -o username=user,password=user

GIFDIR=/mnt/GIFPackages/Build_$GIF_BNUM/
DSDIR=$TOP/distrib/imaging/ghost/
echo $DSDIR;
echo $P4CLIENT;
p4 login < $p4pswd;
p4 revert //$P4CLIENT/...
p4 edit $DSDIR...
echo " ********************************************  Start copying the files ************************************";
#cp -f $GIFDIR/BDC/x64/autoinst.exe  $DSDIR/bootwiz/Platforms/Windows/x64/Installer/  
#cp -f $GIFDIR/BDC/x64/autoutil.exe  $DSDIR/bootwiz/Platforms/Windows/x64/Installer/
#cp -f $GIFDIR/BDC/x86/autoinst.exe  $DSDIR/bootwiz/Platforms/Windows/x86/Installer/
#cp -f $GIFDIR/BDC/x86/autoutil.exe  $DSDIR/bootwiz/Platforms/Windows/x86/Installer/  
#cp -f $GIFDIR/BDC/x86/apackapi.dll  $DSDIR/bootwiz/
#cp -f $GIFDIR/BDC/x86/BDC_Engine.dll  $DSDIR/bootwiz/
#cp -f $GIFDIR/BDC/x86/BootWiz.exe  $DSDIR/bootwiz/
#cp -f $GIFDIR/BDC/x86/BootWiz_EN.dll  $DSDIR/bootwiz/
cp -f $GIFDIR/gdisk  $DSDIR/Linux/x86/
cp -f $GIFDIR/ghconfig  $DSDIR/Linux/x86/  
cp -f $GIFDIR/ghost  $DSDIR/Linux/x86/
cp -f $GIFDIR/ghregedit  $DSDIR/Linux/x86/
cp -f $GIFDIR/SBS/x64/SbsInterface.dll  $DSDIR/SBS/x64/
cp -f $GIFDIR/SBS/x64/SbsMtftp.exe  $DSDIR/SBS/x64/
cp -f $GIFDIR/SBS/x64/SbsServer.exe  $DSDIR/SBS/x64/  
cp -f $GIFDIR/SBS/x86/SbsInterface.dll  $DSDIR/SBS/x86/
cp -f $GIFDIR/SBS/x86/SbsMtftp.exe  $DSDIR/SBS/x86/  
cp -f $GIFDIR/SBS/x86/SbsServer.exe  $DSDIR/SBS/x86/  
cp -f $GIFDIR/DeployAnywhere64.exe  $DSDIR/x64/
cp -f $GIFDIR/DriverDBMgr64.exe  $DSDIR/x64/
cp -f $GIFDIR/DriverManager64.exe  $DSDIR/x64/
cp -f $GIFDIR/Gdisk64.exe  $DSDIR/x64/  
cp -f $GIFDIR/GhConfig64.exe  $DSDIR/x64/  
cp -f $GIFDIR/Ghost64.exe  $DSDIR/x64/  
cp -f $GIFDIR/GhostExp64.exe  $DSDIR/x64/  
cp -f $GIFDIR/Ghostexp.chm  $DSDIR/x64/  
cp -f $GIFDIR/GhostImageFile64.dll  $DSDIR/x64/  
cp -f $GIFDIR/GhRegEdit64.exe  $DSDIR/x64/  
cp -f $GIFDIR/V2iDiskLib.dll  $DSDIR/x64/  
cp -f $GIFDIR/DeployAnywhere.exe  $DSDIR/x86/
cp -f $GIFDIR/DriverDBMgr.exe  $DSDIR/x86/
cp -f $GIFDIR/DriverManager.exe  $DSDIR/x86/
cp -f $GIFDIR/Gdisk32.exe  $DSDIR/x86/  
cp -f $GIFDIR/GhConfig32.exe  $DSDIR/x86/  
cp -f $GIFDIR/Ghost32.exe  $DSDIR/x86/  
cp -f $GIFDIR/GhostExp.exe  $DSDIR/x86/  
cp -f $GIFDIR/Ghostexp.chm  $DSDIR/x86/  
cp -f $GIFDIR/GhostImageFile.dll  $DSDIR/x86/  
cp -f $GIFDIR/GhRegEdit32.exe  $DSDIR/x86/  
cp -f $GIFDIR/V2iDiskLib.dll  $DSDIR/x86/
cp -f $GIFDIR/OmniFs32.exe $DSDIR/x86/
cp -f $GIFDIR/OmniFs64.exe $DSDIR/x64/
cp -f $GIFDIR/omnifs $DSDIR/Linux/x86/


echo "p4 submit -d "Updating GIF Imaging Tools with version $GIF_BNUM" $DSDIR..."
p4 submit -d "Updating GIF Imaging Tools with version $GIF_BNUM" $DSDIR...


