#!/bin/bash
root -q -l -b "FindNmipTest.C(157)" &
root -q -l -b "FindNmipTest.C(159)" &
root -q -l -b "FindNmipTest.C(160)" &
root -q -l -b "FindNmipTest.C(161)" &
root -q -l -b "FindNmipTest.C(164)" &
root -q -l -b "FindNmipTest.C(165)" &
root -q -l -b "FindNmipTest.C(166)" &
root -q -l -b "FindNmipTest.C(167)" &
root -q -l -b "FindNmipTest.C(172)" &
root -q -l -b "FindNmipTest.C(173)" &

wait
# Don't forget to chmod +x FindNmip.sh.
# If macros won't run in Linux, try the following:
# dos2unix FindNmipTest.sh
