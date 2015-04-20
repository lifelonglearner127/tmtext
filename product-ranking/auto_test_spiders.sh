#!/bin/bash

# cd /myfolder/crawlers/
# PATH=$PATH:/usr/local/bin
# export PATH
source /home/web_runner/virtual-environments/scrapyd/bin/activate
scrapy crawl amazon_products -a searchterms_str="MSIA 02"  -a validate=1