__author__ = 'root'

import csv
import os
import itertools

f = open('/home/mufasa/Documents/Workspace/Content Analytics/Misc/Brand & Style/Kohls Brand & Style(duplicated).csv')
csv_f = csv.reader(f)
brand_style = list(csv_f)
brand_style = set(map(tuple, brand_style))
brand_style = map(list, brand_style)

try:
    if os.path.isfile('/home/mufasa/Documents/Workspace/Content Analytics/Misc/Brand & Style/kohls_brand_style.csv'):
        csv_file = open('/home/mufasa/Documents/Workspace/Content Analytics/Misc/Brand & Style/kohls_brand_style.csv', 'a+')
    else:
        csv_file = open('/home/mufasa/Documents/Workspace/Content Analytics/Misc/Brand & Style/kohls_brand_style.csv', 'w')

    csv_writer = csv.writer(csv_file)

    for row in brand_style:
        csv_writer.writerow(row)

    csv_file.close()
except:
    print "Error occurred"

pass