#!/usr/bin/python

# given two sites and categories/departments, check if there are any common products
# usage:
#		python match_product.py site1 category1 site2 category2

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

# normalize text to list of lowercase words (no punctuation except for inches sign (") or /)
def normalize(orig_text):
	text = orig_text
	# other preprocessing: -Inch = "
	text = re.sub("\-Inch", "\"", text)
	#! including ' as an exception keeps things like women's a single word. also doesn't find it as a word in wordnet -> too high a priority
	# excluding it leads to women's->women (s is a stopword)
	text = re.sub("([^\w\"/])|(u')", " ", text)
	stopset = set(stopwords.words('english'))#["and", "the", "&", "for", "of", "on", "as", "to", "in"]
	#tokens = nltk.WordPunctTokenizer().tokenize(text)
	# we need to keep 19" as one word for ex

	#TODO: maybe keep numbers like "50 1/2" together too somehow (originally they're "50-1/2")
	tokens = text.split()
	clean = [token.lower() for token in tokens if token.lower() not in stopset and len(token) > 0]
	#print "clean", orig_text, clean

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

		#print "common words, weight:", common_words, sum(weights_common)

		threshold = param*(sum(weights1) + sum(weights2))/2

		if sum(weights_common) >= threshold:
			products_found.append((product2, sum(weights_common)))
			# product_name += " ".join(list(words1))
			# product_name2 += " ".join(list(words2))
			# print product_name, product_name2
		products_found = sorted(products_found, key = lambda x: x[1], reverse = True)

	return product, products_found

# second approach: rank them with tf-idf, bag of words


# third approach: check common ngrams (is order important?)

results = 0
site1 = sys.argv[1]
category1 = sys.argv[2]
site2 = sys.argv[3]
category2 = sys.argv[4]

products1 = get_products("sample_output/" + site1 + "_bestsellers_dept.jl", category1)
products2 = get_products("sample_output/" + site2 + "_bestsellers_dept.jl", category2)

for nrprod in range(len(products1)):
	(prod, res) = match(products1, products2, nrprod, 0.65)
	if res:
		print prod['product_name']
		for product in res:
			print '-', product[0]['product_name'], "SCORE:", product[1]
		for product in res:
			print product[0]
		print '--------------------------------'
		results += 1

print "results: ", results