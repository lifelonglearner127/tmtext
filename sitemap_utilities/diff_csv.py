__author__ = 'root'

import csv

f1 = open('/home/mufasa/Documents/Workspace/Content Analytics/Misc/Walmart CSV by Categories/results 9 - 4/urls.csv')
csv_f = csv.reader(f1)
product_list1 = list(csv_f)
product_list1 = [row[0] for row in product_list1]

f2 = open('/home/mufasa/Documents/Workspace/Content Analytics/Misc/Walmart CSV by Categories/results 9 - 9/site_owned_only.csv')
csv_f = csv.reader(f2)
product_list2 = list(csv_f)
product_list2 = [row[0] for row in product_list2]

diff_list = list(set(product_list2) - set(product_list1))

for url in diff_list:
    print url

pass