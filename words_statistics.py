#!/usr/bin/python

import codecs
import json
from pprint import pprint
import nltk
import networkx as nx

class Utils:

	# static variable that holds a dictionary of stems and their full words
	# is built in normalize() function, using words from its parameters
	stems = {}

	# static variable that holds a dictionary of lowercased words and their original corresponding words
	# is built in normalize() function, using words from its parameters
	upper = {}

	# normalizes a text: tokenizing, lowercasing, eliminating stopwords, stemming
	# (add synonyms?)
	# returns list of tokens
	@classmethod
	def normalize(cls, text):
		stopset = ["and", "the", "&", "for", "of"]#set(stopwords.words('english'))
		stemmer = nltk.PorterStemmer()
		tokens = nltk.WordPunctTokenizer().tokenize(text)
		clean = [token.lower() for token in tokens if token.lower() not in stopset and len(token) > 2]
		final = [stemmer.stem(word) for word in clean]

		for token in tokens:
			cls.upper[token.lower()] = token

		for index in range(len(final)):
			if final[index] not in cls.stems:
				cls.stems[final[index]] = cls.upper[clean[index]]

		return final

	# merge 2 lists of dictionaries without duplicates
	# where a duplicate is an item with the same value for every key in keys
	# assuming dictionary values are lists, and they both have all the keys in key
	@staticmethod
	def merge_dictionaries(list1, list2, keys):
		final_list = []

		for element1 in list1 + list2:
			# if element in conjoined lists is different from all the elements in final list (it hasn't been added yet)
			# if final list is empty add the element
			if not final_list:
				final_list.append(element1)
			# the element is not found in final list
			notfound = True
			for element2 in final_list:
				# if they are different in values for every key in keys list
				different = False
				for key in keys:
					if element1[key]!=element2[key]:
						different = True
						break
				if not different:
					notfound = False
					break
			if (notfound):
				final_list.append(element1)
		return final_list


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
			for word in Utils.normalize(item['text']):
				# add word to dictionary
				# value of dictionary is item and site name

				item["site"] = site
				# newitem = {}
				# newitem["site"] = site
				# newitem["text"] = item["text"]
				if word not in words:
					words[word] = [item]
				else:
					words[word] = words[word] + [item]
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
				category_words = Utils.normalize(item['text'])
				for word in category_words[1:]:
					words.add_edge(category_words[0], word)
		f.close()

	# return connected components of the graph
	return nx.connected_components(words)

# groups categories by following criteria:
# all categories in a group contain a word that is found in another category in that group
# creates graph of words with edges between words that appear in one category name
# and uses it to group categories that contain that word
# returns list of dictionaries of groups containing items as in the spiders' outputs
def group_by_common_words(sites,level):
	# list containing final category groups
	cat_groups = []
	# connected components of word graph
	word_groups = words_graph(sites, level)
	# list of categories indexed by words found in them
	sites_words = dict(words_in_sites(sites, level))
	for word_list in word_groups:
		new_group = {"Group_name":"", "Short_name" : "", "Level":level, "Group_members":[]}

		# build short name from the full version of the stemmed words in the group's list of words
		#TODO: they shouldn't always be concatenated by "," or "&" (ex: "Home Theater")
		short_name = "".join(Utils.stems[word_list[0]])

		# keep adding words to it until it's above 40 characters
		for word in word_list[1:]:
			short_name += ", " + Utils.stems[word].decode("utf-8")

			# if it's over 40 characters remove the last element and exit loop
			if len(short_name) > 40:
				short_name = ",".join(short_name.split(",")[:-1])
				break

		new_group["Short_name"] = short_name

		# build group members list
		names = []
		for word in word_list:
			new_group["Group_members"] = Utils.merge_dictionaries(new_group["Group_members"], sites_words[word], ["site", "text"])

			# construct category name by concatenating all unique category names in the group
			for site_item in sites_words[word]:
				names.append(site_item["text"])
		cat_name = "; ".join(set(names))
		new_group["Group_name"] = cat_name
		cat_groups.append(new_group)
	return cat_groups


# group categories and store output in json file
def serialize(sites, level):
	sites = ["amazon", "bestbuy", "bjs", "bloomingdales", "overstock", "walmart", "wayfair"]
	groups = group_by_common_words(sites, 1)
	f = open('groups.jl', 'wb')
	for group in groups:
		line = json.dumps(group)
		f.write(line+"\n\n")
	f.close()

if __name__=="__main__":
	sites = ["amazon", "bestbuy", "bjs", "bloomingdales", "overstock", "walmart", "wayfair"]
	groups = group_by_common_words(sites, 1)
	pprint(groups)

	#pprint(Utils.stems)

	serialize(sites,1)
