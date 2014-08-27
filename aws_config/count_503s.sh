#!/bin/bash
FILE=$1

echo "503"
echo "-----------"

for NR in {1..10}
do
	LOGFILE=shared_sshfs/search_log_"$FILE"_"$NR".txt
	if [ -f "$LOGFILE" ]
		then
		printf "$NR "; cat $LOGFILE | grep "503 Service Unavailable" | wc -l
	fi
done

