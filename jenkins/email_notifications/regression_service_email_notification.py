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

sql_changed_products = "select id, sample_url, website, changes_in_structure, sample_json, current_json from console_reportresult where report_date = '%s'" % today.isoformat()

cur.execute(sql_changed_products)
rows = cur.fetchall()
rows = sorted(rows, key=lambda k: k['changes_in_structure'], reverse=True)
email_content = ""

urls = []
website_list = []

for row in rows:
    if row["website"] not in website_list:
        website_list.append(row["website"])

urls_version_changed = []

field_names = ["url", "number of changed parts", "version changed(Yes/No)", "detail view link"]
csv_file_name_product_changes = "/home/ubuntu/tmtext/special_crawler/jenkins/product_changes_" + time.strftime("%Y_%m_%d") + ".csv"
csv_file_name_upc_missed = "/home/ubuntu/tmtext/special_crawler/jenkins/upc_missed_" + time.strftime("%Y_%m_%d") + ".csv"

if os.path.isfile(csv_file_name_product_changes):
    os.remove(csv_file_name_product_changes)

if os.path.isfile(csv_file_name_upc_missed):
    os.remove(csv_file_name_upc_missed)

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


for website in website_list:
    number_of_reported_products = 0

    for row in rows:
        if row["website"] == website:
            number_of_reported_products = number_of_reported_products + 1

            sample_json = json.loads(row["sample_json"])
            current_json = json.loads(row["current_json"])

            #> 80% of product titles are < 2 characters long
            if not current_json["product_info"]["product_title"] or len(current_json["product_info"]["product_title"]) < 2:
                count_product_titles_are_less_than_2_character_long = count_product_titles_are_less_than_2_character_long  + 1

            #> 80% of review counts are 0
            if not current_json["reviews"]["review_count"] or current_json["reviews"]["review_count"] == 0:
                count_review_counts_are_0 = count_review_counts_are_0  + 1

            #> 80% of product descriptions are < 2 words long
            if not current_json["product_info"]["description"] or len(current_json["product_info"]["description"]) < 2:
                count_product_descriptions_are_less_than_2_character_long = count_product_descriptions_are_less_than_2_character_long  + 1

            #> 80% of image counts are 0
            if not current_json["page_attributes"]["image_count"] or current_json["page_attributes"]["image_count"] == 0:
                count_image_counts_are_0 = count_image_counts_are_0  + 1

            #> 80% of products are out of stock
            if current_json["sellers"]["site_online_out_of_stock"] and current_json["sellers"]["site_online_out_of_stock"] == 1:
                count_products_are_out_of_stock = count_products_are_out_of_stock  + 1

            #UPC missed
            if not current_json["product_info"]["upc"]:
                csv_file = None

                if os.path.isfile(csv_file_name_upc_missed):
                    csv_file = open(csv_file_name_upc_missed, "a+")
                else:
                    csv_file = open(csv_file_name_upc_missed, "w")

                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([row["sample_url"]])

                csv_file.close()

        if row["website"] == website and row["changes_in_structure"] > 0:

            csv_file = None

            if os.path.isfile(csv_file_name_product_changes):
                csv_file = open(csv_file_name_product_changes, "a+")
            else:
                csv_file = open(csv_file_name_product_changes, "w")
                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                writer.writeheader()

            csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)

            if sample_json["scraper"] != current_json["scraper"]:
                urls_version_changed.append(row["sample_url"])
                csv_writer.writerow({"url": row["sample_url"], "number of changed parts": str(row["changes_in_structure"]), "version changed(Yes/No)": "Yes", "detail view link": "http://regression.contentanalyticsinc.com:8080/regression/console/reportresult/" + str(row["id"])})
                urls.append(row["sample_url"] +
                            "\n    - number of changed parts: " + str(row["changes_in_structure"]) +
                            "\n    - version changed(Yes/No): Yes" +
                            "\n    - detail view: http://regression.contentanalyticsinc.com:8080/regression/console/reportresult/" + str(row["id"]))
            else:
                csv_writer.writerow({"url": row["sample_url"], "number of changed parts": str(row["changes_in_structure"]), "version changed(Yes/No)": "No", "detail view link": "http://regression.contentanalyticsinc.com:8080/regression/console/reportresult/" + str(row["id"])})
                urls.append(row["sample_url"] +
                            "\n    - number of changed parts: " + str(row["changes_in_structure"]) +
                            "\n    - version changed(Yes/No): No" +
                            "\n    - detail view: http://regression.contentanalyticsinc.com:8080/regression/console/reportresult/" + str(row["id"]))

            csv_file.close()

    urls = list(set(urls))
    number_of_changed_products = len(urls)
    number_of_version_changed_products = len(urls_version_changed)
    changed_product_urls = "\n" .join(urls)

    changed_product_urls = "Following product urls are needed to check.\n" + changed_product_urls
    print changed_product_urls

    sql_not_products = "select url from console_urlsample where not_a_product = 1 and qualified_date = '%s'" % today.isoformat()

    cur.execute(sql_not_products)
    rows = cur.fetchall()
    urls = []

    for row in rows:
        urls.append(row["url"])

    urls = list(set(urls))
    number_of_invalid_products = len(urls)
    not_product_urls = "\n" .join(urls)

    not_product_urls = "\n\nFollowing product urls are invalid.\n" + not_product_urls
    print not_product_urls

    percentage_of_invalid_products = (float(number_of_invalid_products) / float(number_of_reported_products + number_of_invalid_products)) * float(100)
    percentage_of_changed_products = (float(number_of_changed_products) / float(number_of_reported_products + number_of_invalid_products)) * float(100)
    possibility_of_overall_website_changes = "No"

    if percentage_of_changed_products > 80:
        possibility_of_overall_website_changes = "Yes"

    possibility_of_80_percent_product_titles_are_less_than_2_character_long = "No"
    possibility_of_80_percent_review_counts_are_0 = "No"
    possibility_of_80_percent_product_descriptions_are_less_than_2_character_long = "No"
    possibility_of_80_percent_image_counts_are_0 = "No"
    possibility_of_80_percent_products_are_out_of_stock = "No"

    #> 80% of product titles are < 2 characters long
    if float(float(count_product_titles_are_less_than_2_character_long) / float(number_of_reported_products + number_of_invalid_products)) > 0.8:
        possibility_of_80_percent_product_titles_are_less_than_2_character_long = "Yes"
    #> 80% of review counts are 0
    if float(float(count_review_counts_are_0) / float(number_of_reported_products + number_of_invalid_products)) > 0.8:
        possibility_of_80_percent_review_counts_are_0 = "Yes"
    #> 80% of product descriptions are < 2 words long
    count_product_descriptions_are_less_than_2_character_long = 0
    if float(float(count_product_descriptions_are_less_than_2_character_long) / float(number_of_reported_products + number_of_invalid_products)) > 0.8:
        possibility_of_80_percent_product_descriptions_are_less_than_2_character_long = "Yes"
    #> 80% of image counts are 0
    count_image_counts_are_0 = 0
    if float(float(count_image_counts_are_0) / float(number_of_reported_products + number_of_invalid_products)) > 0.8:
        possibility_of_80_percent_image_counts_are_0 = "Yes"
    #> 80% of products are out of stock
    count_products_are_out_of_stock = 0
    if float(float(count_products_are_out_of_stock) / float(number_of_reported_products + number_of_invalid_products)) > 0.8:
        possibility_of_80_percent_products_are_out_of_stock = "Yes"

    website_header = "- " + website + "\n" + "Total tested product numbers: %d\n" \
                                             "Product numbers of content structure changed: %d\n" \
                                             "Product numbers of version changed: %d\n" \
                                             "Invalid product numbers: %d\n" \
                                             "Percentage of invalid products: %f\n" \
                                             "Percentage of changed products: %f\n" \
                                             "80 percent of product titles are < 2 characters long: %s\n" \
                                             "80 percent of review counts are 0: %s\n" \
                                             "80 percent of product descriptions are < 2 words long: %s\n" \
                                             "80 percent of image counts are 0: %s\n" \
                                             "80 percent of products are out of stock: %s\n" \
                                             "Possibility of overall website changes: %s\n" \
                                             "Web console: %s\n" % (
                                                 number_of_reported_products + number_of_invalid_products,
                                                 number_of_changed_products,
                                                 number_of_version_changed_products,
                                                 number_of_invalid_products,
                                                 percentage_of_invalid_products,
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
subject = "Daily Notification from Regression Service : %s" % today.isoformat()

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
