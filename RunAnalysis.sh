#!/bin/bash
    for i in ./data/production_31p2GeV_fixedTarget_2020/ReversedFullField/dev/2020/028/*.root; do
        root -q -l -b "RunAnalysis.C("\""$i"\"")"
    done &
    for i in ./data/production_31p2GeV_fixedTarget_2020/ReversedFullField/dev/2020/029/*.root; do
        root -q -l -b "RunAnalysis.C("\""$i"\"")"
    done &

    wait
# for (( j = 28; j < 30; j++ )); do
#     hadd -f Day$j.root ./Day$j/*.root # hadd same days ADC vs counts files
# done

# Don't forget to: chmod +x RunAnalysis.sh.
# If macros won't run in Linux, try the following:
# dos2unix RunAnalysis.sh
