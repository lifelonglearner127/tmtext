#!/bin/bash

INPUT="walmart_champion"
SITE="macys"

for node in "$@"
do
vagrant ssh  node$node -c "screen -dm /bin/bash /home/ubuntu/shared_sshfs/run_crawler.sh $node $INPUT $SITE; sleep 5";
done
