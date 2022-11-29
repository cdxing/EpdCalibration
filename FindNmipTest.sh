#!/bin/bash
#This is argument 1, if supplied
daystart=178 #default
if [ $# -ge 1 ]
then
        daystart=$1
fi

#This is argument 2, if supplied
dayend=daystart
if [ $# -ge 2 ]
then
        dayend=$2
fi

for (( day = daystart; day <= dayend; day++ )); do
        root -q -l -b "FindNmipTest.C($day)" &

done

wait
# Don't forget to chmod +x FindNmip.sh.
# If macros won't run in Linux, try the following:
# dos2unix FindNmipTest.sh
