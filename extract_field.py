#!/usr/bin/python

# extract specific field from each item from spider output
# usage: python extract_field <output_filename> <field>

import json
import sys
import codecs
from pprint import pprint

filename = sys.argv[1]
field = sys.argv[2]

if len(sys.argv) > 3:
	filter_field = sys.argv[3]
	value = sys.argv[4]

f = codecs.open(filename, "rb", "utf-8")
fields = []

for line in f:
	item = json.loads(line.strip())

	if field in item:
		if len(sys.argv) > 3:
			if filter_field in item and item[filter_field] == value:
				fields.append(item[field])
		else:
			fields.append(item[field])

for el in sorted(fields):
	print el

print len(fields), len(set(fields))

f.close()
