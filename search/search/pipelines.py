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
	def open_spider(self, spider):
		self.file = open(spider.outfile, 'wb')
		if int(spider.output)==1:
			self.file2 = open(spider.outfile2, 'wb')


	def process_item(self, item, spider):
		option = int(spider.output)
		# for option 1, output just found products URLs in one file, and not matched URLs (or ids) in the second file
		if option == 1:
			if 'product_url' in item:
				line = item['product_url'] + "\n"
				self.file.write(line)
			else:
				if spider.by_id:
					line = item['origin_id'] + "\n"
				else:
					line = item['origin_url'] + "\n"
				self.file2.write(line)
		# for option 2, output in one file source product URL (or id) and matched product URL (if found), separated by a comma
		else:
			if 'product_url' in item:
				if spider.by_id:
					line = ",".join([item['origin_id'], item['product_url']]) + "\n"
				else:
					line = ",".join([item['origin_url'], item['product_url']]) + "\n"
			else:
				if spider.by_id:
					line = item['origin_id'] + "\n"
				else:
					line = item['origin_url'] + "\n"
			self.file.write(line)
		return item

	def close_spider(self, spider):
		self.file.close()