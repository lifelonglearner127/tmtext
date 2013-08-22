# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

class CaturlsPipeline(object):
	def open_spider(self, spider):
		self.file = open(spider.filename, 'wb')
	
	def process_item(self, item, spider):
		line = item['product_url'] + "\n"
		self.file.write(line)
		return item
