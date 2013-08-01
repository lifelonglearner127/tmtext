#!/usr/bin/python

# extract only departments from output with all categories in toysrus,
# and write their respective category ids to a file

import json
import codecs
import re

output_all = codecs.open("toysrus_categories.jl", "r", "utf-8")

# output containing only departments
#output_departments = codecs.open("toysrus_departments.jl", "w+", "utf-8")
output_departments = codecs.open("toysrus_departmentids.jl", "w+", "utf-8")

for line in output_all:
	# print line
	if line.strip():
		item = json.loads(line.strip())

	# get parameter of page as text after "=" symbol in "page" field of each item
	level = item['level']

	# if it's a department put it in the output file
	if level == 1:
		# get category id
		url = item['url']
		print url
		m = re.match("http://www\.toysrus\.com/s[a-z]*/index\.jsp\?categoryId=([0-9]+)&s=A-Description-TRUS&searchSort=TRUE", url)
		cat_id = m.group(1)
		output_departments.write(cat_id + "\n")
		#output_departments.write(line + "\n")


# close all opened files
output_all.close()
output_departments.close()
