import os, sys, json, requests
import xml.etree.ElementTree as ET

tags_map = {
	'Product_Description' : 'description',
	'Search_Terms_-_General' : 'keywords',
	'Brand' : 'brand',
	'Category' : 'category_name',
	'Directions' : 'directions',
	'Warnings' : 'warnings',
	'Barcode' : 'upc',
}

def parse(filename, dest):
	f = open(filename, 'r')
	content = f.read()
	f.close()

	products_json = []

	products = ET.fromstring(content)

	for product in products:
		if product.tag == 'header':
			continue

		product_json = {}

		for field in product:
			if field.tag in tags_map:
				field_name = tags_map[field.tag]

				if field.text == 'Not Available':
					continue

				product_json[field_name] = field.text

			if field.tag == 'Product_Title_Long':
				product_json['product_title'] = field.text
				product_json['product_name'] = field.text
				product_json['title_seo'] = field.text

			if field.tag == 'images':
				product_json['image_count'] = int(field.get('count'))
				product_json['images'] = []

				for image in field:
					product_json['images'].append(image.find('url').text)

			if field.tag == 'ingredients':
				product_json['ingredients'] = field.text.split(', ')

			if 'Features_and_Benefits' in field.tag:
				if not 'features' in product_json:
					product_json['features'] = []

				product_json['features'].append(field.text)

		products_json.append(product_json)

	#requests.post(dest, data=products_json, headers={'Content-Type': 'application/json'})
	print 'successfully parsed %s and sent results to %s' % (filename, dest)

	os.remove(filename)

if __name__ == '__main__':
	parse(sys.argv[1], sys.argv[2])
