#!/bin/bash
root -q -l -b "FindNmip.C(67)" &
root -q -l -b "FindNmip.C(68)" &
root -q -l -b "FindNmip.C(69)" &
root -q -l -b "FindNmip.C(70)" &
root -q -l -b "FindNmip.C(71)" &
root -q -l -b "FindNmip.C(72)" &

wait
# Don't forget to chmod +x FindNmip.sh.
# If macros won't run in Linux, try the following:
# dos2unix FindNmip.sh
