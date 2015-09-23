#!/bin/bash

INPUT="hanes_amazon_manual"
SITE="kohls"

# separate argument list one on each line
echo $@ | sed -e 's/[ ]/\n/g' | \
	xargs -P10 -I% vagrant ssh node% -c "screen -dm /bin/bash /home/ubuntu/shared_sshfs/run_crawler.sh % $INPUT $SITE; sleep 5"
