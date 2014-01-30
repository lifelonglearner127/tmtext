#!/bin/bash

for node in "$@"
do
	vagrant ssh  node$node -c "screen -dm /bin/bash /home/ubuntu/shared_sshfs/run_crawler.sh $node; sleep 5";
done