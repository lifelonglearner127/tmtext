#!/usr/bin/python

# extract specific field from each item from spider output
# usage: python extract_field <output_filename> <field>

import json
import sys
import codecs
from pprint import pprint

from optparse import OptionParser

parser = OptionParser()
parser.add_option("--file", dest="filename",
                  help="extract from file")
parser.add_option("--field", dest="field",
                  help="field to extract")

parser.add_option("--field2", dest="field2",
                  help="second field to extract", default=None)

parser.add_option("--filter_field", dest="filter_field",
                  help="field to filter by", default=None)
parser.add_option("--filter_value", dest="filter_value",
                  help="field value to filter by", default=None)

(options, args) = parser.parse_args()

f = codecs.open(options.filename, "rb", "utf-8")
fields = []

for line in f:
	item = json.loads(line.strip())

	if options.field in item:
		if options.filter_field and options.filter_value:
			if options.filter_field in item and item[options.filter_field] == options.filter_value:
				fields.append(item[options.field])
		else:
			if options.field2 and options.field2 in item:
				fields.append((item[options.field], item[options.field2]))
			else:
				fields.append(item[options.field])

for el in sorted(fields):
	if type(el) is tuple:
		print map(lambda x: x.encode("utf-8"), el)
	else:
		print el.encode("utf-8")

print len(fields), len(set(fields))

f.close()
