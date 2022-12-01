#!/bin/bash
date
root -b -q -l DayFitsHistos.C'("NmipConstantsDays344_365.txt")'
root -b -q -l DayHistos.C'("NmipConstantsDays344_365.txt")'
date

