#!/usr/bin/python

# find which URLs are found in one file but not another

import sys
from pprint import pprint

filename1 = sys.argv[1]
filename2 = sys.argv[2]

f1 = open(filename1, "r")
f2 = open(filename2, "r")

lines1 = []
lines2 = []

for line in f1:
	lines1.append(line.strip())

for line in f2:
	lines2.append(line.strip())

f1.close()
f2.close()

#pprint(set(lines1).symmetric_difference(set(lines2)))
pprint(set(lines1).difference(set(lines2)))
