#!/usr/bin/python

# extract only departments from output with all categories in toysrus,
# and write their respective category ids to a file

import json
import codecs
import re
from pprint import pprint

output_all = codecs.open("sample_output/amazon_bestsellers_dept.jl", "r", "utf-8")
departments = []
for line in output_all:
	# print line
	if line.strip():
		item = json.loads(line.strip())

	# if it's a department put it in the output file
	#if item['level'] == -1:
	#if 'department' not in item:
		#print item['product_name'], item['bspage_url']
	#	departments.append(item['bspage_url'])
	#if 'department' in item:
	departments.append(item['department'])


# close all opened files
output_all.close()

dept = set(departments)
pprint(dept)
