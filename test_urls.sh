#!/bin/bash

# open URLs from file in browser:
# open in chrome each pair of URLs in a file containing a pair of URLs separated by a comma on each line

# take file as first argument
filename=$1

for line in $(cat $filename)
do
	echo "$line" | cut -d',' -f1 | xargs google-chrome
	echo "$line" | cut -d',' -f2 | xargs google-chrome
	# wait for user input before opening next pairs of urls
	read aux
done