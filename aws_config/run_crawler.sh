#!/bin/bash
cd /home/ubuntu/tmtext/search;
BATCH=$1
OUT=/home/ubuntu/shared_sshfs/walmart_amazon_40000_"$BATCH"_matches.csv
time scrapy crawl amazon -a product_urls_file=/home/ubuntu/shared_sshfs/walmart_urls_40000_$BATCH.csv -s LOG_ENABLED=1 -s LOG_LEVEL="INFO" -s HTTPCACHE_ENABLED=1 \
-a outfile=$OUT 2>/home/ubuntu/shared_sshfs/search_log_walmart_amazon_40000_$BATCH.txt;
sleep 10;
fi