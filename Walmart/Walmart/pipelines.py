# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import json

class WalmartPipeline(object):
	def __init__(self):
		self.file = open('walmart_categories.jl', 'wb')

		# keep crawled items represented by (url, parent_url) pairs
		# to eliminate duplicates
		self.crawled = []
	
	def process_item(self, item, spider):
		if 'parent_url' not in item or (item['url'], item['parent_url']) not in self.crawled:
			line = json.dumps(dict(item)) + "\n"
			self.file.write(line)
			if 'parent_url' in item:
				self.crawled.append((item['url'], item['parent_url']))
			return item
		else:
			print 'already been here: ', (item['url'], item['parent_url'])
