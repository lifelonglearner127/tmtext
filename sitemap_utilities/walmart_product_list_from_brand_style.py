__author__ = 'diogo'

import re
import os
import time
import csv
import requests
import HTMLParser
import ast
import xml.etree.ElementTree as ET
import urllib
from lxml import html, etree
import sys

walmart_site_url = "http://www.walmart.com"
walmart_search_url = "http://www.walmart.com/search/?query="
output_file_path = "/home/mufasa/Documents/Workspace/Content Analytics/Misc/Brand & Style/walmart_product_list_by_brand_style.csv"

f = open('/home/mufasa/Documents/Workspace/Content Analytics/Misc/Brand & Style/walmart_brand_style (copy).csv')
csv_f = csv.reader(f)

brand_style_list = list(csv_f)
search_url_list = [[row[0], row[1], walmart_search_url + urllib.quote(row[0] + " " + row[1])] for row in brand_style_list]

product_url_list_by_category = {}

for row in search_url_list:
    item_count = 0
    category_name = row[0] + "-----" + row[1]
    search_url = row[2]

    if category_name not in product_url_list_by_category:
        product_url_list_by_category[category_name] = []
        
    print search_url

    try:
        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        category_html = html.fromstring(s.get(search_url, headers=h, timeout=5).text)
    except:
        print "fail"
        continue

    url_list = category_html.xpath("//div[@id='tile-container']//div[@class='js-tile js-tile-landscape tile-landscape']//a[@class='js-product-title']/@href")

    for index, url in enumerate(url_list):
        if not url.startswith(walmart_site_url):
            url_list[index] = walmart_site_url + url

    product_url_list_by_category[category_name].extend(url_list)

    try:
        item_count = int(re.findall(r'\d+', category_html.xpath("//div[@class='result-summary-container']/text()")[0].replace(",", ""))[1])
    except:
        item_count = -1

    if item_count == 0:
        continue

    if item_count > 50:
        continue
        min_price = 0
        max_price = 1

        while True:
            print "price range: {0} - {1}".format(min_price, max_price)

            for index in range(1, 10000):
                if "?" not in search_url:
                    url = search_url + "?page=" + str(index)
                else:
                    url = search_url + "&page=" + str(index)

                if max_price > 0:
                    url = url + "&min_price={0}&max_price={1}".format(min_price, max_price)
                else:
                    url = url + "&min_price={0}".format(min_price)

                h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
                s = requests.Session()
                a = requests.adapters.HTTPAdapter(max_retries=3)
                b = requests.adapters.HTTPAdapter(max_retries=3)
                s.mount('http://', a)
                s.mount('https://', b)
                category_html = html.fromstring(s.get(url, headers=h, timeout=5).text)

                try:
                    item_count = int(re.findall(r'\d+', category_html.xpath("//div[@class='result-summary-container']/text()")[0].replace(",", ""))[1])
                except:
                    item_count = -1

                print item_count

                if item_count > 1000:
                    print "Over 1000"

                try:
                    if int(category_html.xpath("//ul[@class='paginator-list']/li/a[@class='active']")[0].text_content().strip()) != index:
                        break
                except:
                    break

                url_list = category_html.xpath("//div[@id='tile-container']//div[@class='js-tile js-tile-landscape tile-landscape']//a[@class='js-product-title']/@href")

                for index, url in enumerate(url_list):
                    if not url.startswith(walmart_site_url):
                        url_list[index] = walmart_site_url + url

                product_url_list_by_category[category_name].extend(url_list)

            if max_price < 0:
                break

            if "?" not in search_url:
                url = search_url + "?page=" + str(index)
            else:
                url = search_url + "&page=" + str(index)

            url = url + "&min_price={0}".format(max_price)

            h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            b = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('http://', a)
            s.mount('https://', b)
            category_html = html.fromstring(s.get(url, headers=h, timeout=5).text)
            item_count = int(re.findall(r'\d+', category_html.xpath("//div[@class='result-summary-container']/text()")[0].replace(",", ""))[1])

            min_price = max_price

            if item_count > 1000:
                max_price = max_price + 1
            else:
                max_price = -1
    else:
        for index in range(2, 10000):
            if "?" not in search_url:
                url = search_url + "?page=" + str(index)
            else:
                url = search_url + "&page=" + str(index)

            h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            b = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('http://', a)
            s.mount('https://', b)
            category_html = html.fromstring(s.get(url, headers=h, timeout=5).text)
            url_list = category_html.xpath("//div[@id='tile-container']//div[@class='js-tile js-tile-landscape tile-landscape']//a[@class='js-product-title']/@href")

            try:
                if int(category_html.xpath("//ul[@class='paginator-list']/li/a[@class='active']")[0].text_content().strip()) != index:
                    break
            except:
                break

            for index, url in enumerate(url_list):
                if not url.startswith(walmart_site_url):
                    url_list[index] = walmart_site_url + url

            product_url_list_by_category[category_name].extend(url_list)

if os.path.isfile(output_file_path):
    csv_file = open(output_file_path, 'a+')
else:
    csv_file = open(output_file_path, 'w')

csv_writer = csv.writer(csv_file)

for category in product_url_list_by_category:
    try:
        product_url_list_by_category[category] = list(set(product_url_list_by_category[category]))

        brand = category.split("-----")[0]
        style = category.split("-----")[1]

        if (len(product_url_list_by_category[category]) == 0):
            print brand + " " + style

        for product_url in product_url_list_by_category[category]:
            row = [brand, style, product_url]
            csv_writer.writerow(row)
    
        csv_file.close()
    except:
        print "Error occurred"
