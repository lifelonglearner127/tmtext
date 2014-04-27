import pygraphviz as pgv
import networkx as nx
import re

categories = set()
categories_urls = {}
# this file contains only categories not split by /
with open("categories-target-urls-firstlev.txt") as catfile:
	for l in catfile:
		# extract just category name
		cat = re.match("/c/([^/]+)/.*", l.strip()).group(1)
		categories.add(cat)
		# add category's url to dictionary
		# try to add the url with least / (no subcategories delimited by / if possible) - purest form
		# and from among these, the one that is shortest: part after /-/N... can have some extra letters that change the page content a bit?
		potential_url = "http://www.target.com" + l.strip()
		if (cat not in categories_urls) or (potential_url.count('/') < categories_urls[cat].count('/')) or (len(potential_url) < len(categories_urls[cat])):
			categories_urls[cat] = potential_url

categories_items = []

for category in categories:
	item = {}
	item['name'] = category
	item['url'] = categories_urls[category]
	parent = ""
	for potential_parent in categories:
		# find longest category that is prefix or suffix to current category
		if (category.startswith(potential_parent) or category.endswith(potential_parent)) \
		and potential_parent!=category and len(potential_parent) > len(parent):
			parent = potential_parent
	item['parent'] = parent

	categories_items.append(item)

# # print all categories items
# for c in categories_items:
# 	print c
#print len(categories_with_parents)

# filter only categories with parents
categories_with_parents = filter(lambda x: x['parent'] != '', categories_items)

# categories without parents
categories_without_parents = filter(lambda x: x['parent'] == '', categories_items)
# # print their urls
# for cwp in categories_without_parents:
# 	print categories_urls[cwp['name']]

# build categories graph
G = nx.Graph()
for category in categories_with_parents:
	G.add_edge(category['name'], category['parent'])

# extract connected components
connected_components = nx.connected_component_subgraphs(G)

#print len(connected_components)

graph_nr=0

# draw each connected component to a graphviz file
for concomp in connected_components:
	filename = "graphs/graph" + str(graph_nr) + ".png"
	graph_nr += 1
	D = pgv.AGraph()
	D.edge_attr.update(color="blue", len="5.0", width="2.0")
	for (child, parent) in concomp.edges():
		D.add_edge(child, parent)
	D.layout()
	D.draw(filename)