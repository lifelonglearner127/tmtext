# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

# Output type 1: output only matches URLs to a file (one column), URLs with no matches to another file
# Output type 2: output all matches to one file, 2 columns (original and matched URL). For manufacturer spider add product_images and product_videos column
# Output type 3: like output type 2, except with additional columns: confidence score, product name, model (for both sites)

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
		if spider.name == "walmart_fullurls":
			if spider.outfile:
				self.file = open(spider.outfile, 'wb')
			else:
				self.file = None
		else:
			self.file = open(spider.outfile, 'wb')
			if int(spider.output)==1:
				self.file2 = open(spider.outfile2, 'wb')

			# write headers row
			titles = []
			if int(spider.output) >= 2:
				titles.append("Original_URL")
			if int(spider.output) == 3:
				titles.append("Original_product_name")
				titles.append("Original_product_model")
			titles.append("Match_URL")
			if int(spider.output) == 3:
				titles.append("Match_product_name")
				titles.append("Match_product_model")

			if (spider.name == 'manufacturer'):
				titles.append("Product_images")
				titles.append("Product_videos")

			if int(spider.output) == 3:
				titles.append("Confidence")

			self.file.write(",".join(titles) + "\n")


	def process_item(self, item, spider):

		# different actions for walmart_fullurls spider
		if spider.name == "walmart_fullurls":
			return self.process_item_fullurl(item, spider)

		if spider.name == "manufacturer":
			return self.process_item_manufacturer(item, spider)

		option = int(spider.output)
		# for option 1, output just found products URLs in one file, and not matched URLs (or ids) in the second file
		if option == 1:
			if 'product_url' in item:
				line = item['product_url'] + "\n"
				self.file.write(line)
			else:
				# if spider.by_id:
				# 	line = item['origin_id'] + "\n"
				# else:
				line = item['origin_url'] + "\n"
				self.file2.write(line)
		# for option 2, output in one file source product URL (or id) and matched product URL (if found), separated by a comma
		else:
			# if 'product_url' in item:
			# 	if spider.by_id:
			# 		line = ",".join([item['origin_id'], item['product_url']]) + "\n"
			# 	else:
			# 	line = ",".join([item['origin_url'], item['product_url']]) + "\n"
			# else:
			# 	if spider.by_id:
			# 		line = item['origin_id'] + "\n"
			# 	else:
			# 	line = item['origin_url'] + "\n"
			fields = [item['origin_url']]

			# if output type is 3, add additional fields
			if option == 3:
				fields.append(item['origin_name'])
				if 'origin_model' in item:
					fields.append(item['origin_model'])
				else:
					# add empty field (corresponding to the origin_model header column)
					fields.append("")

			# if a match was found add it to the fields to be output
			if 'product_url' in item:
				fields.append(item['product_url'])
			else:
				# add empty field (corresponding to the product_url header column)
				fields.append("")
			
			# if output type is 3, add additional fields
			if option == 3:
				fields.append(item['product_name'])
				if 'product_model' in item:
					fields.append(item['product_model'])
				else:
					# add empty field (corresponding to the product_model header column)
					fields.append("")

				fields.append(item['confidence'])

			# construct line from fields list
			line = ",".join(fields) + "\n"

			self.file.write(line)
		return item

	def process_item_fullurl(self, item, spider):
		line = ",".join([item['walmart_short_url'], item['walmart_full_url']])
		if self.file:
			self.file.write(line + "\n")
		else:
			print line

	def process_item_manufacturer(self, item, spider):
		fields = []

		# (Output 3 not supported for manufacturer spider)

		if int(spider.output) == 2:
			fields.append(item['origin_url'])
		if 'product_url' in item:
			fields.append(item['product_url'])
			# write unmatched products to second file
		elif int(spider.output) == 1:
			#self.file2.write(item['origin_url'] + "," + item['product_name'] + "\n")
			self.file2.write(item['origin_url'] + "\n")
		if 'product_images' in item:
			fields.append(str(item['product_images']))
		if 'product_videos' in item:
			fields.append(str(item['product_videos']))

		line = ",".join(fields) + "\n"

		self.file.write(line)

		return item


	def close_spider(self, spider):
		if self.file:
			self.file.close()
