import os, sys, xml, json, requests, threading
import xml.etree.ElementTree as ET
from api_lib import *

tags_map = {
    'Product_Description' : 'description',
    'Directions' : 'usage_directions',
    'Warnings' : 'caution_warnings_allergens',
    #'Barcode' : 'id_value',
}

def setup_parse(content, dest, token):
    products = ET.fromstring(content)

    if not (products.tag == 'products' and products[0].tag == 'header'):
        message = 'expected structure &lt;products&gt;&lt;header&gt;'
        raise ValueError(message)

    report_status(token, 2)

    t = threading.Thread(target=parse, args=(products, dest, token))
    t.start()

def parse(products, dest, token):
    products_json = []

    product_count = 0

    for product in products:
        if product.tag == 'header':
            continue

        product_json = {}

        product_json['id_type'] = 'upc'
        #product_json['id_value'] = '381371016761'

        for field in product:
            if field.tag in tags_map:
                field_name = tags_map[field.tag]

                if field.text == 'Not Available':
                    continue

                product_json[field_name] = field.text

            if field.tag == 'Barcode':
                product_json['id_value'] = field.text.zfill(14)

            if field.tag == 'Product_Title_Long':
                product_json['product_name'] = field.text

            if field.tag == 'Categoy':
                product_json['category'] = {'name': field.text}

            if field.tag == 'Ingredients':
                product_json['ingredients'] = field.text.split(', ')

            '''
            if field.tag == 'images':
                product_json['image_count'] = int(field.get('count'))
                product_json['images'] = []

                for image in field:
                    product_json['images'].append(image.find('url').text)

            if 'Features_and_Benefits' in field.tag:
                if not 'features' in product_json:
                    product_json['features'] = []

                product_json['features'].append(field.text)
            '''

        print product_json['id_value']
        products_json.append(product_json)

        product_count += 1

        '''
        # Only parse the first 10 products
        if product_count == 1:
            break
        '''

    print 'PRODUCT_COUNT', product_count
    send_json(token, products_json)
    report_status(token, 3)

if __name__ == '__main__':
    parse(sys.argv[1], sys.argv[2])
