#!/bin/bash
root -q -l -b "FindNmip.C(94)" &
root -q -l -b "FindNmip.C(95)" &
root -q -l -b "FindNmip.C(96)" &
root -q -l -b "FindNmip.C(97)" &
root -q -l -b "FindNmip.C(98)" &
# root -q -l -b "FindNmip.C(99)" &
# root -q -l -b "FindNmip.C(100)" &

wait
# Don't forget to chmod +x FindNmip.sh.
# If macros won't run in Linux, try the following:
# dos2unix FindNmip.sh
