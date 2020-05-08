#!/bin/bash
root -q -l -b "FindNmip.C(160)" &
root -q -l -b "FindNmip.C(161)" &

wait
# Don't forget to chmod +x FindNmip.sh.
# If macros won't run in Linux, try the following:
# dos2unix FindNmip.sh