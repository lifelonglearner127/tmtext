__author__ = 'root'

import re
import os
import time
import csv
import requests
import HTMLParser
import ast
import xml.etree.ElementTree as ET
from lxml import html, etree
import sys
import json

shelf_urls_list = ["http://www1.macys.com/shop/mens-clothing/mens-pants/Pageindex,Productsperpage/{0},40?id=89&edge=hybrid&cm_sp=c2_1111US_catsplash_men-_-row7-_-icon_pants&cm_kws_path=tasso+elba+quarter+zip",
                   "http://www1.macys.com/shop/mens-clothing/mens-jeans/Pageindex,Productsperpage/{0},40?id=11221&edge=hybrid&cm_sp=c2_1111US_catsplash_men-_-row7-_-icon_jeans&cm_kws_path=tasso+elba+quarter+zip",
                   "http://www1.macys.com/shop/mens-clothing/mens-casual-shirts/Pageindex,Productsperpage/{0},40?id=20627&edge=hybrid&cm_sp=c2_1111US_catsplash_men-_-row7-_-icon_casual-shirts&cm_kws_path=tasso+elba+quarter+zip",
                   "http://www1.macys.com/shop/mens-clothing/mens-dress-shirts/Pageindex,Productsperpage/{0},40?id=20635&edge=hybrid&cm_sp=c2_1111US_catsplash_men-_-row8-_-icon_dress-shirts&cm_kws_path=tasso+elba+quarter+zip",
                   "http://www1.macys.com/shop/mens-clothing/mens-sweaters/Pageindex,Productsperpage/{0},40?id=4286&edge=hybrid&cm_sp=c2_1111US_catsplash_men-_-row9-_-icon_sweaters&cm_kws_path=tasso+elba+quarter+zip"]

url_list = []

for shelf_url in shelf_urls_list:
    try:
        print shelf_url
        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)

        for index in range(1, 100000):
            page_html = html.fromstring(s.get(shelf_url.format(index), headers=h, timeout=5).text)

            if not page_html.xpath("//span[@id='productCount']/text()"):
                break

            urls = page_html.xpath("//div[@class='shortDescription']/a/@href")

            if not urls:
                break

            print len(url)

            urls = ["http://www1.macys.com" + url for url in urls]
            url_list.extend(urls)
        print "success"
    except:
        print "fail"

url_list = list(set(url_list))

output_dir_path = "/home/mufasa/Documents/Workspace/Content Analytics/Misc/Macys from Shelf/"

try:
    if os.path.isfile(output_dir_path + "urls.csv"):
        csv_file = open(output_dir_path + "urls.csv", 'a+')
    else:
        csv_file = open(output_dir_path + "urls.csv", 'w')

    csv_writer = csv.writer(csv_file)

    for product_url in url_list:
        row = [product_url]
        csv_writer.writerow(row)

    csv_file.close()
except:
    print "Error occurred"


print "success"
