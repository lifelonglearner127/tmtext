#!/bin/bash

echo "EXCEPTIONS"
echo "--------------"

FILE=$1

for NR in {1..10}
do
	LOGFILE=shared_sshfs/search_log_"$FILE"_"$NR".txt
	if [ -f "$LOGFILE" ]
		then
		printf "$NR "; ack "<exception" $LOGFILE |  wc -l
	fi
done
