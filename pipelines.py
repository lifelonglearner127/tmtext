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
	def __init__(self):
		# flag indicating if the first item has been written to output
		self.started = False

	def open_spider(self, spider):
		filename = spider.name + "_categories,jl"
		self.file = open(filename, 'wb')

	def process_item(self, item, spider):
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

