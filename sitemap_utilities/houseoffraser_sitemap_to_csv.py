__author__ = 'diogo'

import re
import os
import time
import csv
import requests
import ast
import xml.etree.ElementTree as ET
from lxml import html, etree
import sys

category_url_list = ["http://www.houseoffraser.co.uk/Women%27s+Designer+Clothing/03,default,sc.html",
                     "http://www.houseoffraser.co.uk/Menswear/02,default,sc.html,",
                     "http://www.houseoffraser.co.uk/shoes+boots/15,default,sc.html",
                     "http://www.houseoffraser.co.uk/Bags+Luggage/17,default,sc.html",
                     "http://www.houseoffraser.co.uk/Beauty+cosmetic+skincare+products/01,default,sc.html",
                     "http://www.houseoffraser.co.uk/Kids+and+Baby+Clothing/04,default,sc.html",
                     "http://www.houseoffraser.co.uk/house+accessory/05,default,sc.html",
                     "http://www.houseoffraser.co.uk/Furniture/514,default,sc.html",
                     "http://www.houseoffraser.co.uk/Electricals/10,default,sc.html",
                     "http://www.houseoffraser.co.uk/Gifts+Hub/Giftshub,default,pg.html"]

output_dir_path = "/home/mufasa/Documents/Workspace/Content Analytics/Misc/Houseoffraser"
all_product_url_list = []

for category_url in category_url_list:
    print "Category: " + category_url

    category_html = html.fromstring(requests.get(category_url).text)
    sub_category_url_list = category_html.xpath("//div[@id='categoryQuickLinks']//ul/li/a/@href")

    if not sub_category_url_list:
        continue

    for sub_category_url in sub_category_url_list:
        print "Sub category: " + sub_category_url

        for page_index in range(0, 10000):
            offset_url = "start={0}&sz=30&spcl&ajaxsearchrefinement".format(page_index * 30)

            if "?" in sub_category_url:
                sub_category_html = html.fromstring(requests.get(sub_category_url + "&" + offset_url).text)
            else:
                sub_category_html = html.fromstring(requests.get(sub_category_url + "?" + offset_url).text)

            product_list = sub_category_html.xpath("//div[@class='product-description']/a/@href")

            if not product_list:
                break

            print "    Page number: {0}".format(page_index + 1)

            all_product_url_list.extend(product_list)

all_product_url_list = list(set(all_product_url_list))

try:
    if len(sys.argv) > 1:
        file_name = sys.argv[1] + ".csv"
    else:
        file_name = "products.csv"

    if os.path.isfile(output_dir_path + file_name):
        csv_file = open(output_dir_path + file_name, 'a+')
    else:
        csv_file = open(output_dir_path + file_name, 'w')

    csv_writer = csv.writer(csv_file)

    for product_url in all_product_url_list:
        row = [product_url]
        csv_writer.writerow(row)

    csv_file.close()
except:
    print "Error occurred"
