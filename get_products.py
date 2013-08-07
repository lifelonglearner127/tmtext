#!/usr/bin/python

# extract products from a certain output file, that belong to a certain category/department
# and write their respective category ids to a file

import json
import codecs
import re
from pprint import pprint

def get_products(filename, category):
	output_all = codecs.open(filename, "r", "utf-8")

	products = []

	for line in output_all:
		# print line
		if line.strip():
			item = json.loads(line.strip())
			if 'department' in item:
				if item['department'] == category:
					products.append(item['product_name'])
			if 'category' in item:
				if item['category'] == category:
					products.append(item['product_name'])

	# close all opened files
	output_all.close()
	return products

filename = "sample_output/walmart_bestsellers_dept.jl"
category = "Baby"
prods = get_products(filename, category)

pprint(prods)
