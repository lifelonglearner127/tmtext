#!/bin/bash

INPUT="walmart_urls_topm1"
SITE="target"

for node in "$@"
do
vagrant ssh  node$node -c "screen -dm /bin/bash /home/ubuntu/tmtext/aws_config/run_crawler.sh $node $INPUT $SITE; sleep 5";
done
