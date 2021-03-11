#!/bin/bash
# root -q -l -b "FindNmip.C(22038)" &
root -q -l -b "FindNmip.C(22039)" &
root -q -l -b "FindNmip.C(22040)" &
root -q -l -b "FindNmip.C(22041)" &
root -q -l -b "FindNmip.C(22042)" &
root -q -l -b "FindNmip.C(22043)" &
root -q -l -b "FindNmip.C(22044)" &

wait
# Don't forget to chmod +x FindNmip.sh.
# If macros won't run in Linux, try the following:
# dos2unix FindNmip.sh
