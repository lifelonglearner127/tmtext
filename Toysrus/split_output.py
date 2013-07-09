#!/usr/bin/python

# split output into separate files by page

import json
import codecs

output_all = codecs.open("toysrus_categories.jl", "r", "utf-8")

# dictionary of files for each page
pages = {}

for line in output_all:
	# print line
	if line.strip():
		items = json.loads(line.strip())

	# get parameter of page as text after "=" symbol in "page" field of each item
	page_param = items['page'].split("=")[1]

	# get corresponding file from dictionary
	if page_param in pages:
		page_file = pages[page_param]
	else:
		page_file = codecs.open(page_param + "_toysrus_categories.jl", "w+", "utf-8")
		pages[page_param] = page_file

	# output the line to corresponding file
	page_file.write(line + "\n")


# close all opened files
output_all.close()
for page_param in pages:
	pages[page_param].close()
