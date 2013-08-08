#!/usr/bin/python
import codecs
import re
import json
import sys
from pprint import pprint
import nltk
from nltk.corpus import stopwords

def get_products(filename, category):
	output_all = codecs.open(filename, "r", "utf-8")

	products = []

	for line in output_all:
		# print line
		if line.strip():
			item = json.loads(line.strip())
			if 'department' in item:
				if item['department'] == category:
					products.append(item)
			if 'category' in item:
				if item['category'] == category:
					products.append(item)

	# close all opened files
	output_all.close()
	return products

def normalize(text):
	text = re.sub("([^\w\"])|(u')", " ", text)
	stopset = set(stopwords.words('english'))#["and", "the", "&", "for", "of", "on", "as", "to", "in"]
	stemmer = nltk.PorterStemmer()
	tokens = nltk.WordPunctTokenizer().tokenize(text)
	clean = [token.lower() for token in tokens if token.lower() not in stopset and len(token) > 0]

	return clean


def match(products1, products2, nrproduct):
	product = ''

	product = products1[nrproduct]
	products_found = []

	for product2 in products2:
		product_name = product['product_name']
		product_name2 = product2['product_name']
		# words1 = set(filter(None, re.split("\s", product_name2)))
		# words2 = set(filter(None, re.split("\s", product_name)))
		words1 = set(normalize(product_name))
		words2 = set(normalize(product_name2))
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

	return product, products_found

results = 0
site1 = sys.argv[1]
category1 = sys.argv[2]
site2 = sys.argv[3]
category2 = sys.argv[4]

products1 = get_products("sample_output/" + site1 + "_bestsellers_dept.jl", category1)
products2 = get_products("sample_output/" + site2 + "_bestsellers_dept.jl", category2)

for nrprod in range(len(products1)):
	(prod, res) = match(products1, products2, nrprod)
	print prod['product_name']
	print 'res:'
	for product in res:
		print '-', product['product_name']
	print ''
	if res:
		for product in res:
			print product
		results += 1

print "results: ", results