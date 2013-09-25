# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import json

class NeweggPipeline(object):
	def __init__(self):
		self.file = open('newegg_categories.jl', 'wb')
		self.urls = []
	
	def process_item(self, item, spider):
		line = json.dumps(dict(item)) + "\n"
		if item['url'] not in self.urls:
			self.urls.append(item['url'])
			self.file.write(line)
			return item
