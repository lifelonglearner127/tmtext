# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import json

class BloomingdalesPipeline(object):
	def __init__(self):
		self.file = open('bloomingdales_categories.jl', 'wb')

		self.items = []

	def process_item(self, item, spider):
		# line = json.dumps(dict(item)) + "\n"
		# self.file.write(line)
		self.items.append(item)
		return item

	def close_spider(self, spider):
		l = [dict(x) for x in self.items]
		o = {"data" : l}
		self.file.write(json.dumps(o))

		self.file.close()
