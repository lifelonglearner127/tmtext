# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import json
import re

class MacysPipeline(object):
	def __init__(self):
		self.file = open('macys_categories.jl', 'wb')
		self.items = []
		self.ids = {}

	def process_item(self, item, spider):
		# ignore duplicates: consider categories as distinct if they have different urls
		# also ignore element if there was another with the same id
		# extract id from url
		catid = ""
		m = re.match(".*[^_][iI][dD]=([0-9]+).*", item['url'])
		if m:
			catid = m.group(1)
		# else:
		# 	print "NO MATCH ", item['url']
		# if catid in self.ids and self.ids[catid]!=item['url']:
		# 	print "MATCH: ", item['url'], self.ids[catid]

		if item['url'] not in self.items and catid and catid not in self.ids:
			self.items.append(item['url'])
			self.ids[catid] = item['url']
			line = json.dumps(dict(item)) + "\n"
			self.file.write(line)
			return item