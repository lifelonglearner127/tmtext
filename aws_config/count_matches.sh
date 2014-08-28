#!/bin/bash

echo "MATCHES"
echo "----------"

FILE=$1

for NR in {1..10}
do
	RES=shared_sshfs/"$FILE"_"$NR"_matches.csv
	if [ -f "$RES" ]
		then
		printf "$NR "; cat $RES | grep ",h" | wc -l
	fi
done

echo "-------------------------"
printf "ALL "; cat shared_sshfs/"$FILE"_* | grep ",h" | wc -l