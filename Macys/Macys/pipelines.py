# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import json

class MacysPipeline(object):
	def __init__(self):
		self.file = open('macys_categories.jl', 'wb')
		self.items = []

	def process_item(self, item, spider):
		# ignore duplicates: consider categories as distinct if they have different urls
		if item['url'] not in self.items:
			self.items.append(item['url'])
			line = json.dumps(dict(item)) + "\n"
			self.file.write(line)
			return item