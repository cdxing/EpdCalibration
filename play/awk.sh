#!/bin/bash
awk -v a='2,4,5,7' -v b='1,2,5,8' '
BEGIN { split(a, ax, ","); split(b, bx, ",");
        for(n in ax) mapping[ bx[n] ] =ax[n];
};
NR==FNR { if (FNR in mapping) hold[ mapping[FNR] ]=$0; next; };
{ print (FNR in hold)? hold[FNR]: $0; }' fileB.txt fileA.txt
