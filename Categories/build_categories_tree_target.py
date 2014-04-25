import pygraphviz as pgv
import networkx as nx
import re

categories = set()
categories_urls = {}
with open("categories-target-urls.txt") as catfile:
	for l in catfile:
		# extract just category name
		cat = re.match("/c/([^/]+)/.*", l.strip()).group(1)
		categories.add(cat)
		# add category's url to dictionary
		# try to add the url with least / (no subcategories delimited by / if possible) - purest form
		if cat not in categories_urls or l.strip().count('/') < categories_urls[cat].count('/'):
			categories_urls[cat] = "http://www.target.com" + l.strip()

print len(categories)
categories_items = []

for category in categories:
	item = {}
	item['name'] = category
	parent = ""
	for potential_parent in categories:
		# find longest category that is prefix or suffix to current category
		if (category.startswith(potential_parent) or category.endswith(potential_parent)) \
		and potential_parent!=category and len(potential_parent) > len(parent):
			parent = potential_parent
	item['parent'] = parent

	categories_items.append(item)

# filter only categories with parents0
categories_with_parents = filter(lambda x: x['parent'] != '', categories_items)
#print len(categories_with_parents)

# categories without parents
categories_without_parents = filter(lambda x: x['parent'] == '', categories_items)
# print their urls
for cwp in categories_without_parents:
	print categories_urls[cwp['name']]

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