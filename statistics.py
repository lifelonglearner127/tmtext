#!/usr/bin/python

import codecs
import json
from pprint import pprint

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
			for word in item['text'].split():
				# add word to dictionary
				# value of dictionary is item and site name
				item["site"] = site
				if word not in words:
					words[word] = [item]
				else:
					words[word] = words[word] + [item]
	f.close()
	return words

# returns dictionary with number of levels and number of categories on each level for a site
def number_of_levels(site):
	# filename is of form "Site/site_categories.jl"
	filename = site[0].upper() + site[1:] + "/" + site + "_categories.jl"
	# separate handling for BJs
	if site.strip() == "bjs":
		filename = "BJs/bjs_categories.jl"
	f = codecs.open(filename, "r", "utf-8")

	levels = {}
	for line in f:
		item = json.loads(line.strip())
		level = item['level']
		if level not in levels:
			levels[level] = 1
		else:
			levels[level] += 1
	levels["nrlevels"] = len(levels.keys())
	levels["site"] = site
	return levels

# prints table with number of levels and of categories on each level for a list of sites
def levels_table(sites):
	levels = {}

	# print it
	#TODO: levels up to 2? how do you handle it?
	print "%20s%20s%20s%20s%20s" % ("site", "nr_levels", "departments", "categories", "subcategories")
	print "-------------------------------------------------------------------------------------------------------"
	for site in sites:
		levels = number_of_levels(site)
		print "%20s%20d%20d%20d%20d" % (site, levels['nrlevels'], levels.get(1,0), levels.get(0,0), levels.get(-1,0))

sites = ["amazon", "bestbuy", "bjs", "bloomingdales", "overstock", "walmart", "wayfair"]
levels_table(sites)