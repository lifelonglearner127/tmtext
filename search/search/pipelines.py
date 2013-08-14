# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import json

class SearchPipeline(object):
	def __init__(self):
		self.file = open('search_results.jl', 'wb')
	
	def process_item(self, item, spider):
		line = json.dumps(dict(item)) + "\n"
		self.file.write(line)
		return item

class URLsPipeline(object):
	def __init__(self):
		self.file = open('search_results.txt', 'wb')
	
	def process_item(self, item, spider):
		option = int(spider.output)
		# depending on the spider's option, either output just the URL of the result product, or the URL of the source product as well
		if option == 1:
			line = item['product_url'] + "\n"
		else:
			line = item['origin_url']
			if 'product_url' in item:
				line += "," + item['product_url']
			line += "\n"
		self.file.write(line)
		return item