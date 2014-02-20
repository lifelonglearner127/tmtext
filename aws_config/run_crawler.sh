#!/bin/bash
cd /home/ubuntu/tmtext/search;
BATCH=$1
OUT=/home/ubuntu/shared_sshfs/walmart_amazon_40000_"$BATCH"_matches.csv
COOKIES=/home/ubuntu/shared_sshfs/cookies_node"$BATCH".jl
time scrapy crawl amazon -a product_urls_file=/home/ubuntu/shared_sshfs/walmart_urls_40000_"$BATCH".csv \
-s LOG_ENABLED=1 -s LOG_LEVEL="INFO" -s HTTPCACHE_ENABLED=0 -a fast=0 -a output=3\
-a outfile=$OUT 2>/home/ubuntu/shared_sshfs/search_log_walmart_amazon_40000_"$BATCH".txt;
sleep 10;

only halt if this is not batch 1 (node 1 hosts shared folder)
if [ "$BATCH" -ne 1 ]
HOST=`hostname`; 
if [ "$HOST" != "node1" ]
	then
	sudo halt;
fi