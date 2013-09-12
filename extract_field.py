#!/usr/bin/python

# extract specific field from each item from spider output
# usage: python extract_field <output_filename> <field>

import json
import sys
import codecs
from pprint import pprint

filename = sys.argv[1]
field = sys.argv[2]

f = codecs.open(filename, "rb", "utf-8")
fields = []

for line in f:
	item = json.loads(line.strip())

	if field in item:
		fields.append(item[field])

for el in sorted(fields):
	print el

print len(fields), len(set(fields))

f.close()
