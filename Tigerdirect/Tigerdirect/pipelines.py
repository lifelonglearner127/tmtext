# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import json

class TigerdirectPipeline(object):
	def __init__(self):
		self.file = open('tigerdirect_categories.jl', 'wb')

		# pairs of catgory urls and parent urls (to identify a unique category)
		self.cats = []

	def process_item(self, item, spider):
		line = json.dumps(dict(item)) + "\n"
		if 'parent_url' not in item or\
		(item['url'], item['parent_url']) not in self.cats:
			self.file.write(line)
			if 'parent_url' in item:
				self.cats.append((item['url'], item['parent_url']))
			return item