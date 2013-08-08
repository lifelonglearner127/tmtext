#!/usr/bin/python
import codecs
import re
from pprint import pprint

def match(filename1, filename2, nrproduct):
	file1 = open(filename1, "r")
	file2 = open(filename2, "r")

	product = ''

	for i in range(nrproduct):
		product = file1.readline().strip()
	products_found = []

	for line in file2:
		product = re.sub("([^\w\"])|(u')", " ", product)
		product2 = re.sub("([^\w\"])|(u')", " ", line.strip())
		words1 = set(filter(None, re.split("\s", product2)))
		words2 = set(filter(None, re.split("\s", product)))
		common_words = words1.intersection(words2)
		threshold = 0.5*(len(words1) + len(words2))/2
		if len(common_words) >= threshold:
			# print product
			# print product2
			# print "words1: ", words1
			# print "words2: ", words2
			# print "common words: ", common_words
			products_found.append(product2)
			#break

	file1.close()
	file2.close()

	return product, products_found

results = 0

for nrprod in range(50):
	(prod, res) = match("walmart_apparel.txt", "overstock_clothing.txt", nrprod)
	print prod
	pprint(res)
	print ''
	if res:
		results += 1

print "results: ", results