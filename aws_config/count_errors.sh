#!/bin/bash
FILE=$1

echo "ERRORS"
echo "-----------"

for NR in {1..10}
do
	LOGFILE=shared_sshfs/search_log_"$FILE"_"$NR".txt
	if [ -f "$LOGFILE" ]
		then
		printf "$NR "; ack --lines "ERROR" $LOGFILE
	fi
done

