# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import json

class WalmartPipeline(object):
	def __init__(self):
		self.file = open('walmart_categories.jl', 'wb')

		# flag indicating if the first item has been written to output
		self.started = False

	def process_item(self, item, spider):
		line = json.dumps(dict(item))
		if self.started:
			self.file.write(",\n" + line)
			self.started = True
		else:
			self.file.write(line)
		return item

	def close_spider(self):
		self.file.close()

