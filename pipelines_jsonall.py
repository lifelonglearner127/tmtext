# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import json
from scrapy import spider

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
