import os
import smtplib
from os.path import basename
import glob
import unittest
import json
import re
import copy
import psycopg2
import psycopg2.extras
import requests
import sys
import urllib
import time
import csv
from datetime import date
import xml.etree.ElementTree as ET
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

con = None
con = psycopg2.connect(database='scraper_test', user='root', password='QdYoAAIMV46Kg2qB', host='scraper-test.cmuq9py90auz.us-east-1.rds.amazonaws.com', port='5432')
cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

today = date.today()

website = "walmart"

if len(sys.argv) > 1:
    website = sys.argv[1]

sql_sample_products = "select id, url, website, json, not_a_product from console_urlsample where website='{0}'".format(website)

cur.execute(sql_sample_products)
rows = cur.fetchall()

invalid_products_list = []
upc_missing_product_list = []
review_issue_product_list = []
price_issue_product_list = []
marketplace_issue_product_list = []
walmart_v1_product_list = []

number_of_reported_products = len(rows)
#> 80% of product titles are < 2 characters long
count_product_titles_are_less_than_2_character_long = 0
#> 80% of review counts are 0
count_review_counts_are_0 = 0
#> 80% of product descriptions are < 2 words long
count_product_descriptions_are_less_than_2_character_long = 0
#> 80% of image counts are 0
count_image_counts_are_0 = 0
#> 80% of products are out of stock
count_products_are_out_of_stock = 0

for row in rows:
    try:
        sample_json = json.loads(row["json"])

        if "sellers" not in sample_json.keys():
            raise Exception("Invalid product")

        #> 80% of product titles are < 2 characters long
        if not sample_json["product_info"]["product_title"] or len(sample_json["product_info"]["product_title"]) < 2:
            count_product_titles_are_less_than_2_character_long = count_product_titles_are_less_than_2_character_long  + 1

        #> 80% of review counts are 0
        if not sample_json["reviews"]["review_count"] or sample_json["reviews"]["review_count"] == 0:
            count_review_counts_are_0 = count_review_counts_are_0  + 1

        #> 80% of product descriptions are < 2 words long
        if not sample_json["product_info"]["description"] or len(sample_json["product_info"]["description"]) < 2:
            count_product_descriptions_are_less_than_2_character_long = count_product_descriptions_are_less_than_2_character_long  + 1

        #> 80% of image counts are 0
        if not sample_json["page_attributes"]["image_count"] or sample_json["page_attributes"]["image_count"] == 0:
            count_image_counts_are_0 = count_image_counts_are_0  + 1

        #> 80% of products are out of stock
        if sample_json["sellers"]["owned_out_of_stock"] and sample_json["sellers"]["owned_out_of_stock"] == 1:
            count_products_are_out_of_stock = count_products_are_out_of_stock  + 1

        #UPC missing products
        if not sample_json["product_info"]["upc"]:
            upc_missing_product_list.append({"store url": sample_json["url"], "regression report url": "http://regression.contentanalyticsinc.com:8080/regression/console/urlsample/" + str(row["id"])})

        #Review issue products
        if sample_json["reviews"]["review_count"] > 0 and \
                (sample_json["reviews"]["average_review"] is None or sample_json["reviews"]["max_review"] is None or sample_json["reviews"]["min_review"] is None or sample_json["reviews"]["reviews"] is None):
            review_issue_product_list.append({"store url": sample_json["url"], "regression report url": "http://regression.contentanalyticsinc.com:8080/regression/console/urlsample/" + str(row["id"])})

        #Price issue products
        if sample_json["sellers"]["price"] and (sample_json["sellers"]["price_amount"] is None or sample_json["sellers"]["price_currency"] is None):
            price_issue_product_list.append({"store url": sample_json["url"], "regression report url": "http://regression.contentanalyticsinc.com:8080/regression/console/urlsample/" + str(row["id"])})

        #Marketplace issue products
        if ((sample_json["marketplace_sellers"] and not sample_json["marketplace_prices"]) or (not sample_json["marketplace_sellers"] and sample_json["marketplace_prices"])) \
                or ((sample_json["marketplace_sellers"] and sample_json["marketplace_prices"]) and len(sample_json["marketplace_sellers"]) != len(sample_json["marketplace_prices"])):
            marketplace_issue_product_list.append({"store url": sample_json["url"], "regression report url": "http://regression.contentanalyticsinc.com:8080/regression/console/urlsample/" + str(row["id"])})

        #Walmart v1 products
        if website == "walmart" and sample_json["scraper"] == "Walmart v1":
            walmart_v1_product_list.append({"store url": sample_json["url"], "regression report url": "http://regression.contentanalyticsinc.com:8080/regression/console/urlsample/" + str(row["id"])})
    except:
        invalid_products_list.append(row["url"])


sql_changed_products = "select id, sample_url, website, changes_in_structure, sample_json, current_json from console_reportresult where report_date = '{0}' and website='{1}'".format(today.isoformat(), website)

cur.execute(sql_changed_products)
rows = cur.fetchall()
rows = sorted(rows, key=lambda k: k['changes_in_structure'], reverse=True)
email_content = ""

#UPC missing issue
csv_file_name_upc_missed = "/home/ubuntu/tmtext/special_crawler/jenkins/{0}_upc_missed_{1}.csv".format(website, time.strftime("%Y_%m_%d"))

if upc_missing_product_list:
    field_names = ["store url", "regression report url"]
    csv_file = open(csv_file_name_upc_missed, "w")
    csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
    csv_writer.writeheader()

    for product in upc_missing_product_list:
        csv_writer.writerow(product)

    csv_file.close()

#Review issue
csv_file_name_review_issue = "/home/ubuntu/tmtext/special_crawler/jenkins/{0}_review_issue_{1}.csv".format(website, time.strftime("%Y_%m_%d"))

if review_issue_product_list:
    field_names = ["store url", "regression report url"]
    csv_file = open(csv_file_name_review_issue, "w")
    csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
    csv_writer.writeheader()

    for product in review_issue_product_list:
        csv_writer.writerow(product)

    csv_file.close()

#Price issue
csv_file_name_price_issue = "/home/ubuntu/tmtext/special_crawler/jenkins/{0}_price_issue_{1}.csv".format(website, time.strftime("%Y_%m_%d"))

if price_issue_product_list:
    field_names = ["store url", "regression report url"]
    csv_file = open(csv_file_name_price_issue, "w")
    csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
    csv_writer.writeheader()

    for product in price_issue_product_list:
        csv_writer.writerow(product)

    csv_file.close()

#Marketplace issue
csv_file_name_marketplace_issue = "/home/ubuntu/tmtext/special_crawler/jenkins/{0}_marketplace_issue_{1}.csv".format(website, time.strftime("%Y_%m_%d"))

if marketplace_issue_product_list:
    field_names = ["store url", "regression report url"]
    csv_file = open(csv_file_name_marketplace_issue, "w")
    csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
    csv_writer.writeheader()

    for product in marketplace_issue_product_list:
        csv_writer.writerow(product)

    csv_file.close()

#Walmart v1 products
csv_file_name_walmart_v1 = "/home/ubuntu/tmtext/special_crawler/jenkins/{0}_walmart_v1_products_{1}.csv".format(website, time.strftime("%Y_%m_%d"))

if walmart_v1_product_list:
    field_names = ["store url", "regression report url"]
    csv_file = open(csv_file_name_walmart_v1, "w")
    csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
    csv_writer.writeheader()

    for product in walmart_v1_product_list:
        csv_writer.writerow(product)

    csv_file.close()

field_names = ["store url", "number of changed parts", "version changed(Yes/No)", "regression report url"]
csv_file_name_product_changes = "/home/ubuntu/tmtext/special_crawler/jenkins/{0}_product_changes_{1}.csv".format(website, time.strftime("%Y_%m_%d"))
csv_file = open(csv_file_name_product_changes, "w")
csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
csv_writer.writeheader()

number_of_changed_products = 0
number_of_version_changed_products = 0

for row in rows:
    sample_json = json.loads(row["sample_json"])
    current_json = json.loads(row["current_json"])

    if row["changes_in_structure"] > 0:
        number_of_changed_products = number_of_changed_products + 1
        version_changed = "No"

        if sample_json["scraper"] != current_json["scraper"]:
            number_of_version_changed_products = number_of_version_changed_products + 1
            version_changed = "Yes"

        csv_writer.writerow({"store url": row["sample_url"], "number of changed parts": str(row["changes_in_structure"]), "version changed(Yes/No)": version_changed, "regression report url": "http://regression.contentanalyticsinc.com:8080/regression/console/reportresult/" + str(row["id"])})

csv_file.close()

percentage_of_changed_products = (float(number_of_changed_products) / float(number_of_reported_products)) * float(100)
possibility_of_overall_website_changes = "No"

if percentage_of_changed_products > 80:
    possibility_of_overall_website_changes = "Yes"

possibility_of_80_percent_product_titles_are_less_than_2_character_long = "No"
possibility_of_80_percent_review_counts_are_0 = "No"
possibility_of_80_percent_product_descriptions_are_less_than_2_character_long = "No"
possibility_of_80_percent_image_counts_are_0 = "No"
possibility_of_80_percent_products_are_out_of_stock = "No"

#> 80% of product titles are < 2 characters long
if float(float(count_product_titles_are_less_than_2_character_long) / float(number_of_reported_products)) > 0.8:
    possibility_of_80_percent_product_titles_are_less_than_2_character_long = "Yes"
#> 80% of review counts are 0
if float(float(count_review_counts_are_0) / float(number_of_reported_products)) > 0.8:
    possibility_of_80_percent_review_counts_are_0 = "Yes"
#> 80% of product descriptions are < 2 words long
if float(float(count_product_descriptions_are_less_than_2_character_long) / float(number_of_reported_products)) > 0.8:
    possibility_of_80_percent_product_descriptions_are_less_than_2_character_long = "Yes"
#> 80% of image counts are 0
if float(float(count_image_counts_are_0) / float(number_of_reported_products)) > 0.8:
    possibility_of_80_percent_image_counts_are_0 = "Yes"
#> 80% of products are out of stock
if float(float(count_products_are_out_of_stock) / float(number_of_reported_products)) > 0.8:
    possibility_of_80_percent_products_are_out_of_stock = "Yes"

website_header = "- " + website + "\n" + "Total tested product numbers: %d\n" \
                                         "Product numbers of content structure changed: %d\n" \
                                         "Product numbers of version changed: %d\n" \
                                         "Percentage of changed products: %f\n" \
                                         "80 percent of product titles are < 2 characters long: %s\n" \
                                         "80 percent of review counts are 0: %s\n" \
                                         "80 percent of product descriptions are < 2 words long: %s\n" \
                                         "80 percent of image counts are 0: %s\n" \
                                         "80 percent of products are out of stock: %s\n" \
                                         "Possibility of overall website changes: %s\n" \
                                         "Web console: %s\n" % (
                                             number_of_reported_products,
                                             number_of_changed_products,
                                             number_of_version_changed_products,
                                             percentage_of_changed_products,
                                             possibility_of_80_percent_product_titles_are_less_than_2_character_long,
                                             possibility_of_80_percent_review_counts_are_0,
                                             possibility_of_80_percent_product_descriptions_are_less_than_2_character_long,
                                             possibility_of_80_percent_image_counts_are_0,
                                             possibility_of_80_percent_products_are_out_of_stock,
                                             possibility_of_overall_website_changes,
                                             "http://regression.contentanalyticsinc.com:8080/regression/\nlogin: tester\npassword: password\n")
email_content += (website_header)



fromaddr = "jenkins@contentanalyticsinc.com"
toaddrs = ["jacob.cats426@gmail.com", "diogo.medeiros1115@gmail.com", "adriana@contentanalyticsinc.com", "support@contentanalyticsinc.com"] # must be a list
#toaddrs = ["jacob.cats426@gmail.com"] # must be a list
subject = "{0} Daily Notification from Regression Service : {1}".format(website.upper(), today.isoformat())

print "Message length is " + repr(len(email_content))

#Change according to your settings
smtp_server = 'email-smtp.us-east-1.amazonaws.com'
smtp_username = 'AKIAI2XV5DZO5VTJ6LXQ'
smtp_password = 'AgWhl58LTqq36BpcFmKPs++24oz6DuS/J1k2GrAmp1T6'
smtp_port = '587'
smtp_do_tls = True

msg = MIMEMultipart(
        From=fromaddr,
        To=COMMASPACE.join(toaddrs),
        Date=formatdate(localtime=True)
        )
msg['Subject'] = subject
msg.preamble = subject

if os.path.isfile(csv_file_name_product_changes):
    csv_file = MIMEApplication(open(csv_file_name_product_changes, "rb").read())
    csv_file.add_header('Content-Disposition', 'attachment', filename=basename(csv_file_name_product_changes))
    msg.attach(csv_file)

if os.path.isfile(csv_file_name_upc_missed):
    csv_file1 = MIMEApplication(open(csv_file_name_upc_missed, "rb").read())
    csv_file1.add_header('Content-Disposition', 'attachment', filename=basename(csv_file_name_upc_missed))
    msg.attach(csv_file1)

if os.path.isfile(csv_file_name_review_issue):
    csv_file1 = MIMEApplication(open(csv_file_name_review_issue, "rb").read())
    csv_file1.add_header('Content-Disposition', 'attachment', filename=basename(csv_file_name_review_issue))
    msg.attach(csv_file1)

if os.path.isfile(csv_file_name_price_issue):
    csv_file1 = MIMEApplication(open(csv_file_name_price_issue, "rb").read())
    csv_file1.add_header('Content-Disposition', 'attachment', filename=basename(csv_file_name_price_issue))
    msg.attach(csv_file1)

if os.path.isfile(csv_file_name_marketplace_issue):
    csv_file1 = MIMEApplication(open(csv_file_name_marketplace_issue, "rb").read())
    csv_file1.add_header('Content-Disposition', 'attachment', filename=basename(csv_file_name_marketplace_issue))
    msg.attach(csv_file1)

if os.path.isfile(csv_file_name_walmart_v1):
    csv_file1 = MIMEApplication(open(csv_file_name_walmart_v1, "rb").read())
    csv_file1.add_header('Content-Disposition', 'attachment', filename=basename(csv_file_name_walmart_v1))
    msg.attach(csv_file1)

msg.attach(MIMEText(email_content))

server = smtplib.SMTP(
    host = smtp_server,
    port = smtp_port,
    timeout = 10
)

server.set_debuglevel(10)
server.starttls()
server.ehlo()
server.login(smtp_username, smtp_password)
server.sendmail(fromaddr, toaddrs, msg.as_string())

print server.quit()
