# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import json

# write each JSON object on one line
class LinesPipeline(object):
	def open_spider(self, spider):
		filename = spider.name + "_categories.jl"
		self.file = open(filename, 'wb')

	def process_item(self, item, spider):
		line = json.dumps(dict(item)) + "\n"
		self.file.write(line)
		return item

# write each JSON object on one line, lines separated by commas
class CommaSeparatedLinesPipeline(object):

    # categories tree - tree of entire sitemap structured as dictionary with keys being URLs of categories, and values being a dictionary containing a list of its subcategories URLs
    # if has_tree flag is on in spider, this tree will be built and used to aggregate number of products for each category where it's not explicitly specified on the site
    categories_tree = {}

	def __init__(self):
		# flag indicating if the first item has been written to output
		self.started = False

	def open_spider(self, spider):
		filename = spider.name + "_categories.jl"
		self.file = open(filename, 'wb')

	# process item in spider for which we build the sitemap tree
	def process_item_fortree(self, item):
		pass

	def process_item(self, item, spider):
		if spider.has_tree:
			self.process_item_fortree(item)
		else:
			# if we're not aggregating number of products, just return the item
			line = json.dumps(dict(item))
			if self.started:
				self.file.write(",\n" + line)
			else:
				self.file.write(line)
				self.started = True
			return item

	def close_spider(self, spider):
		self.file.close()


# write entire content as a JSON object in the output file
class JSONObjectPipeline(object):
	def __init__(self):
		self.items = []

	def open_spider(self, spider):
		filename = spider.name + "_categories.jl"
		self.file = open(filename, 'wb')

	def process_item(self, item, spider):
		self.items.append(item)
		return item

	def close_spider(self, spider):
		l = [dict(x) for x in self.items]
		o = {"data" : l}
		self.file.write(json.dumps(o))

		self.file.close()

