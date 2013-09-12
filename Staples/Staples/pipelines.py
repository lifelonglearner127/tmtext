# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import json

class StaplesPipeline(object):
	def __init__(self):
		self.file = open('staples_categories.jl', 'wb')
		self.items = []
	
	def process_item(self, item, spider):
		if item['url'] not in self.items:
			self.items.append(item['url'])
			line = json.dumps(dict(item)) + "\n"
			self.file.write(line)
			return item
