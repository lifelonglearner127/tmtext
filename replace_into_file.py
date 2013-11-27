#!/usr/bin/python

# Receive a file with two values separated by comma on each line
# In the second file, replace all occurences of first value with second value
# Output results on stdout

import sys
import re

newlines = []

with open(sys.argv[1], "r") as infile:
	with open(sys.argv[2], "rw") as outfile:

		for line in infile:
			(value1, value2) = line.strip().split(",")
			for lineout in outfile:
				if value1 in line:
					newline = lineout.strip().replace(value1, value2)
					#print newline
					print lineout, newline

