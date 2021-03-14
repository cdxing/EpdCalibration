#!/bin/bash
# This script runs calibrations for the EPD.
# This looks through the directories containing
# data in production and finds all relevant files
# from across the runs. This program takes two arguments:
# Argument 1 is the day to run analysis on, or the first day in a range of days;
# Argument 2, if supplied, is the last day in a range of days to do analysis on.

	#This is where the data is within /star/dataXX/
	Directory="reco/production_7p7GeV_2021/ReversedFullField/dev/2021/"

    #This is argument 1, if supplied
	daystart=52 #default
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
		Day=$day

		#Fix day for output
		if [ "$day" -lt 100 ]
		then
			Day=0$day
		fi


		#Make directories if they don't exist already
		mkdir -p Day$day/{data09,data10,data11,data12}

		wait

		for i in /star/data09/$Directory$Day/*; do
			for j in $i/st_physics*.picoDst.root; do
				root -q -l -b "RunAnalysis.C("\""$j"\"")"
			done
		done

		mv Day$day/st_physics*.picoDst.root Day$day/data09/

		for i in /star/data10/$Directory$Day/*; do
			for j in $i/st_physics*.picoDst.root; do
				root -q -l -b "RunAnalysis.C("\""$j"\"")"
			done
		done

		mv Day$day/st_physics*.picoDst.root Day$day/data10/

		for i in /star/data11/$Directory$Day/*; do
			for j in $i/st_physics*.picoDst.root; do
				root -q -l -b "RunAnalysis.C("\""$j"\"")"
			done
		done

		mv Day$day/st_physics*.picoDst.root Day$day/data11/

		for i in /star/data12/$Directory$Day/*; do
			for j in $i/st_physics*.picoDst.root; do
				root -q -l -b "RunAnalysis.C("\""$j"\"")"
			done
		done

		mv Day$day/st_physics*.picoDst.root Day$day/data12/

		wait

		hadd -f ./Day$day/Day$day.data09.root ./Day$day/data09/*.root
		hadd -f ./Day$day/Day$day.data10.root ./Day$day/data10/*.root
		hadd -f ./Day$day/Day$day.data11.root ./Day$day/data11/*.root
		hadd -f ./Day$day/Day$day.data12.root ./Day$day/data12/*.root

		wait

		hadd -f Day$day.root ./Day$day/Day$day.data*.root # Combine seperate data files

	done


# Don't forget to: chmod +x RunAnalysis.sh.
# If macros won't run in Linux, try the following:
# dos2unix RunAnalysis.sh
