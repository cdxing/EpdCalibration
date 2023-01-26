#!/bin/bash
date
dayStart=41
dayEnd=55
echo "Day Start: $dayStart"
echo "Day End: $dayEnd"
root -b -q -l "DayFitsHistos.C($dayStart,$dayEnd,\"NmipConstantsDays41_55.txt\")"
root -b -q -l "DayHistos.C($dayStart,$dayEnd,\"NmipConstantsDays41_55.txt\")"
#root -b -q -l DayHistos.C\($dayStart,$dayEnd,"NmipConstantsDays344_365.txt"\)
date

