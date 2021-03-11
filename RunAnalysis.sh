#!/bin/bash
	day=58
	
	#Fix day for output
	Day=$day
	if [ $day -gt 100 ]
	then Day=$day
	else Day=0$day
	fi
	
	#Make directories if they don't exist already
	mkdir -p Day$day/{data09,data10,data11,data12}
	
	wait

    for i in /star/data09/reco/production_7p7GeV_2021/ReversedFullField/dev/2021/$Day/*; do
		for j in $i/st_physics*.picoDst.root; do
			root -q -l -b "RunAnalysis.C("\""$j"\"")"
		done
    done
	
    mv Day$day/st_physics*.picoDst.root Day$day/data09/
	
	for i in /star/data10/reco/production_7p7GeV_2021/ReversedFullField/dev/2021/$Day/*; do
		for j in $i/st_physics*.picoDst.root; do
			root -q -l -b "RunAnalysis.C("\""$j"\"")"
		done
    done
	
    mv Day$day/st_physics*.picoDst.root Day$day/data10/
	
	for i in /star/data11/reco/production_7p7GeV_2021/ReversedFullField/dev/2021/$Day/*; do
		for j in $i/st_physics*.picoDst.root; do
			root -q -l -b "RunAnalysis.C("\""$j"\"")"
		done
    done
	
    mv Day$day/st_physics*.picoDst.root Day$day/data11/
	
	for i in /star/data12/reco/production_7p7GeV_2021/ReversedFullField/dev/2021/$Day/*; do
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


#    wait
# for (( j = 28; j < 30; j++ )); do
#     hadd -f Day$j.root ./Day$j/*.root # hadd same days ADC vs counts files
# done

# Don't forget to: chmod +x RunAnalysis.sh.
# If macros won't run in Linux, try the following:
# dos2unix RunAnalysis.sh
