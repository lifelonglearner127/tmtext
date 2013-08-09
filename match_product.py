#!/usr/bin/python
import codecs
import re
import json
import sys
from pprint import pprint
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import numpy
from numpy import dot
from nltk.corpus import wordnet

# given two sites and categories/departments, check if there are any common products
# usage:
#		python match_product.py site1 category1 site2 category2


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

# normalize text to list of lowercase words (no punctuation except for inches or feet sign (",') or /)
def normalize(text):
	# other preprocessing: -Inch = "
	text = re.sub("\-Inch", "\"", text)
	text = re.sub("([^\w\"'/])|(u')", " ", text)
	stopset = set(stopwords.words('english'))#["and", "the", "&", "for", "of", "on", "as", "to", "in"]
	#tokens = nltk.WordPunctTokenizer().tokenize(text)
	# we need to keep 19" as one word for ex

	#TODO: maybe keep numbers like "50 1/2" together too somehow
	#TODO: test how all of this works more
	tokens = text.split()
	clean = [token.lower() for token in tokens if token.lower() not in stopset and len(token) > 0]
	#print text, clean

	return clean

# for a product products1[nrproduct] check if the number of words in common for each of the products in products2
# exceeds a cerain threshold
# weigh non-dictionary words with double weight
# use param to calculate the threshold (0-1) (0.7 or 0.6 is good)
def match(products1, products2, nrproduct, param):
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

		weights_common = []
		for word in common_words:
			if not wordnet.synsets(word):
				weights_common.append(2)
			else:
				weights_common.append(1)
		#print common_words, weights_common

		weights1 = []
		for word in words1:
			if not wordnet.synsets(word):
				weights1.append(2)
			else:
				weights1.append(1)

		weights2 = []
		for word in words2:
			if not wordnet.synsets(word):
				weights2.append(2)
			else:
				weights2.append(1)

		#threshold = 0.5*(len(words1) + len(words2))/2

		threshold = param*(sum(weights1) + sum(weights2))/2

		if sum(weights_common) >= threshold:
			products_found.append(product2)
			# product_name += " ".join(list(words1))
			# product_name2 += " ".join(list(words2))
			# print product_name, product_name2

	return product, products_found

results = 0
site1 = sys.argv[1]
category1 = sys.argv[2]
site2 = sys.argv[3]
category2 = sys.argv[4]

products1 = get_products("sample_output/" + site1 + "_bestsellers_dept.jl", category1)
products2 = get_products("sample_output/" + site2 + "_bestsellers_dept.jl", category2)

for nrprod in range(len(products1)):
	(prod, res) = match(products1, products2, nrprod, 0.6)
	if res:
		print prod['product_name']
		for product in res:
			print '-', product['product_name']
		for product in res:
			print product
		print '--------------------------------'
		results += 1

print "results: ", results