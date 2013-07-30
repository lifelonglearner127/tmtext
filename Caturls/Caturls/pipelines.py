# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

class CaturlsPipeline(object):
	def __init__(self):
		self.file = open('product_urls.txt', 'wb')
	
	def process_item(self, item, spider):
		line = item['product_url'] + "\n"
		self.file.write(line)
		return item
