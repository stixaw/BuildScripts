#!/bin/bash

echo " Updating the PackageBuild/package.pbs .........."

if [ $# -ne 1 ]
then
    echo " Usage: `basename $0` <version> eg: 7.1.1144"
    exit -1
fi

newrev=$1
REV_STR=product_revision
PBSFILE="PackageBuild/package.pbs"
oldrev=`grep "^$REV_STR"* $PBSFILE | uniq|awk -F\" '{print $2}'`

echo "Old rev is "$oldrev" and new rev is "$newrev
OLD_REV_STR=$REV_STR"=\""$oldrev"\""
NEW_REV_STR=$REV_STR"=\""$newrev"\""
export OLD_REV_STR
export NEW_REV_STR
 
ret=`sed -i 's/'$OLD_REV_STR'/'$NEW_REV_STR'/g' $PBSFILE`

echo " Done updating package.pbs file ............."

echo " Updating the rollout-auto.sh .........."

REV_STR=pb_product_revision
ROLLOUTFILE="OEM/DS/Linux/x86/automation/rollout-auto.sh"

oldrev=`grep "^$REV_STR"* $ROLLOUTFILE | uniq|awk -F\" '{print $2}'`
echo "Old rev is "$oldrev" and new rev is "$newrev
OLD_REV_STR=$REV_STR"=\""$oldrev"\""
NEW_REV_STR=$REV_STR"=\""$newrev"\""
export OLD_REV_STR
export NEW_REV_STR
ret=`sed -i 's/'$OLD_REV_STR'/'$NEW_REV_STR'/g' $ROLLOUTFILE`

REV_STR=pb_product_version_build
oldbldnum=`grep "^$REV_STR"* $ROLLOUTFILE | uniq|awk -F\" '{print $2}'`
echo oldbldnum

newbldnum=`echo $newrev | awk -F\. '{print $3}'`

OLD_REV_STR=$REV_STR"=\""$oldbldnum"\""
NEW_REV_STR=$REV_STR"=\""$newbldnum"\""
export OLD_REV_STR
export NEW_REV_STR
ret=`sed -i 's/'$OLD_REV_STR'/'$NEW_REV_STR'/g' $ROLLOUTFILE`

echo " Updating the Build date in rollout-auto"
DATE_STR=pb_product_builddate
olddate=`grep "^$DATE_STR"* $ROLLOUTFILE | uniq|awk -F\" '{print $2}'`
newdate=`date`

OLD_DATE_STR=$DATE_STR"=\""$olddate"\""
NEW_DATE_STR=$DATE_STR"=\""$newdate"\""
echo " OldDate $OLD_DATE_STR"
echo " New Date $NEW_DATE_STR"
export OLD_DATE_STR
export NEW_DATE_STR
ret=`sed -i "s/'$OLD_DATE_STR'/'$NEW_DATE_STR'/g" $ROLLOUTFILE`

