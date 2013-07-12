#!/usr/bin/python

import codecs
import json
from pprint import pprint
import nltk
import networkx as nx

# normalizes a text: tokenizing, lowercasing, eliminating stopwords, stemming
# (add synonyms?)
# returns list of tokens
def normalize(text):
	stopset = ["and", "the", "&"]#set(stopwords.words('english'))
	stemmer = nltk.PorterStemmer()
	tokens = nltk.WordPunctTokenizer().tokenize(text)
	clean = [token.lower() for token in tokens if token.lower() not in stopset and len(token) > 2]
	final = [stemmer.stem(word) for word in clean]
	return final

# gets a dictionary of words that appear in categories of a certain sitemap, on a certain level of nesting
# excluding special categories
#
# input: site - sitename as a string 
#		 level - level as an int
# returns: dictionary indexed by word, with values consisting of the item of that category (from the spider's outputs)
def words_in_site(site, level):
	# filename is of form "Site/site_categories.jl"
	filename = site[0].upper() + site[1:] + "/" + site + "_categories.jl"
	# separate handling for BJs
	if site.strip() == "bjs":
		filename = "BJs/bjs_categories.jl"
	f = codecs.open(filename, "r", "utf-8")

	words = {}
	for line in f:
		item = json.loads(line.strip())
		if int(item['level']) == level and 'special' not in item:
			for word in normalize(item['text']):
				# add word to dictionary
				# value of dictionary is item and site name

				#item["site"] = site
				newitem = {}
				newitem["site"] = site
				newitem["text"] = item["text"]
				if word not in words:
					words[word] = [newitem]
				else:
					words[word] = words[word] + [newitem]
	f.close()
	return words

# aggregates result of words_in_site to a list of sites, and returns ordered output by the words' frequency
def words_in_sites(sites,level):
	words = {}
	for site in sites:
		site_words = words_in_site(site, level)
		for word in site_words:
			if word not in words:
				words[word] = site_words[word]
			else:
				words[word] = words[word] + site_words[word]
	
	return sorted(words.items(), key=lambda x: len(x[1]), reverse=True)

# creates graph that connects words that are both found in a category name
# to use in grouping function
# returns connected components of the graph
def words_graph(sites, level):
	words = nx.Graph()
	for site in sites:
		# filename is of form "Site/site_categories.jl"
		filename = site[0].upper() + site[1:] + "/" + site + "_categories.jl"
		# separate handling for BJs
		if site.strip() == "bjs":
			filename = "BJs/bjs_categories.jl"
		f = codecs.open(filename, "r", "utf-8")

		for line in f:
			item = json.loads(line.strip())
			if int(item['level']) == level and 'special' not in item:
				category_words = normalize(item['text'])
				for word in category_words[1:]:
					words.add_edge(category_words[0], word)
		f.close()
	# return connected components of the graph
	return nx.connected_components(words)

# groups categories by following criteria:
# all categories in a group contain a word that is found in another category in that group
# creates graph of words with edges between words that appear in one category name
# and uses it to group categories that contain that word
# returns dictionary of groups containing items as in the spiders' outputs
def group_by_common_words(sites,level):
	words = nx.Graph()


sites = ["amazon", "bestbuy", "bjs", "bloomingdales", "overstock", "walmart", "wayfair"]
pprint(words_in_sites(sites, 1))