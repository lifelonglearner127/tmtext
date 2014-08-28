#!/bin/bash

echo "RESULTS"
echo "---------"

FILE=$1

for NR in {1..10}
do
	RES=shared_sshfs/"$FILE"_"$NR"_matches.csv
	if [ -f "$RES" ]
		then
		printf "$NR "; cat $RES | wc -l
	fi
done

echo "-------------------------"
printf "ALL "; cat shared_sshfs/"$FILE"_* | wc -l