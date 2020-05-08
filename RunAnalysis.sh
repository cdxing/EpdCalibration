#!/bin/bash
    for i in /Picos/Day160/*.root; do
        root -q -l -b "PrashRunAnalysis.C("\""$i"\"")"
    done &
    for i in /Picos/Day161/*.root; do
        root -q -l -b "PrashRunAnalysis.C("\""$i"\"")"
    done &

    wait
for (( j = 160; j < 162; j++ )); do
    hadd Day$j.root /Day$j/*.root
done

# Don't forget to: chmod +x RunAnalysis.sh.
# If macros won't run in Linux, try the following:
# dos2unix RunAnalysis.sh