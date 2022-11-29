#!/bin/bash
# Merge the the results from FindNmip.C and FindNmipTest.C
# Author: Ding Chen
# Date: Nov 26th, 2022

date
Directory1="./production"
Directory2="./production_test"
#This is argument 1, if supplied
daystart=51 #default
if [ $# -ge 1 ]
then
        daystart=$1
fi

#This is argument 2, if supplied
dayend=$daystart
if [ $# -ge 2 ]
then
        dayend=$2
fi

for (( day = daystart; day <= dayend; day++ )); do
	
	grep "<----------" <$Directory1/NmipConstantsDay$day.txt >> FindNmipDay$daystart\_$dayend\_issue.txt
	grep -n "<----------" <$Directory1/NmipConstantsDay$day.txt | cut -d : -f 1 > temp_lineNumbers.txt
        ftemp=temp_lineNumbers.txt	
	ARRAY=()
	while IFS= read -r line
	do
	  #echo "$line"
	  NUMBER=$(echo "$line" | tr -dc '0-9')
          #echo $NUMBER
	  ARRAY+=($NUMBER)
	  #ARRAY+=(,)
          #awk '{print $1}' $line
  	  #number=$line
          #awk '{if(NR==$NUMBER) print $0}' NmipConstantsTestDay$day.txt >> FindNmipTestDay$daystart\_$dayend\_issue.txt
          #awk 'NR==$NUMBER' NmipConstantsTestDay$day.txt >> FindNmipTestDay$daystart\_$dayend\_issue.txt
	  head -n $NUMBER $Directory2/NmipConstantsTestDay$day.txt | tail -1 >> FindNmipTestDay$daystart\_$dayend\_issue.txt
          #sed 'NUMBER!d' NmipConstantsTestDay$day.txt #>> FindNmipTestDay$daystart\_$dayend\_issue.txt
	  #sed -n $line NmipConstantsTestDay$day.txt
	done < "$ftemp"	
        echo ${ARRAY[@]}
	# https://unix.stackexchange.com/questions/633648/replace-lines-in-one-file-with-lines-in-another-by-line-number
	awk -v a="${ARRAY[*]}" -v b="${ARRAY[*]}" '
	BEGIN { split(a, ax); split(b, bx);
	        for(n in ax) mapping[ bx[n] ] =ax[n];
	};
	NR==FNR { if (FNR in mapping) hold[ mapping[FNR] ]=$0; next; };
	{ print (FNR in hold)? hold[FNR]: $0; }' $Directory2/NmipConstantsTestDay$day.txt $Directory1/NmipConstantsDay$day.txt >> NmipConstantsDays$daystart\_$dayend.txt




done
#file1=$1
#file1=$2
#awk '
#    NR == FNR{         #for lines in first file
#        S[NR] = $0     #put line in array `S` with row number as index 
#        next           #starts script from the beginning
#    }
#    /^!!/{             #for line stared with `!!`
#        $0=S[++count]  #replace line by corresponded array element
#    }
#    1                  #alias for `print $0`
#    ' $2 $1
#grep "<----------" <NmipConstantsDay52.txt > fittingissue.txt
#sed 'Ns/.*/replacement-line/' file.txt > new_file.txt

date

