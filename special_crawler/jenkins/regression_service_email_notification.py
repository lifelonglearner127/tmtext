import smtplib
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
from datetime import date
import xml.etree.ElementTree as ET



con = None
con = psycopg2.connect(database='scraper_test', user='root', password='QdYoAAIMV46Kg2qB', host='scraper-test.cmuq9py90auz.us-east-1.rds.amazonaws.com', port='5432')
cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

today = date.today()

sql_changed_products = "select id, sample_url, website, changes_in_structure, sample_json, current_json from console_reportresult where report_date = '%s'" % today.isoformat()

cur.execute(sql_changed_products)
rows = cur.fetchall()
email_content = ""

urls = []
website_list = []

for row in rows:
    if row["website"] not in website_list:
        website_list.append(row["website"])

urls_version_changed = []

for website in website_list:
    number_of_reported_products = 0

    for row in rows:
        if row["website"] == website:
            number_of_reported_products = number_of_reported_products + 1

        if row["website"] == website and row["changes_in_structure"] > 0:
            sample_json = json.loads(row["sample_json"])
            current_json = json.loads(row["current_json"])

            if sample_json["scraper"] != current_json["scraper"]:
                urls_version_changed.append(row["sample_url"])
                urls.append(row["sample_url"] +
                            "\n    - number of changed parts: " + str(row["changes_in_structure"]) +
                            "\n    - version changed(Yes/No): Yes" +
                            "\n    - detail view: http://regression.contentanalyticsinc.com:8080/regression/console/reportresult/" + str(row["id"]))
            else:
                urls.append(row["sample_url"] +
                            "\n    - number of changed parts: " + str(row["changes_in_structure"]) +
                            "\n    - version changed(Yes/No): No" +
                            "\n    - detail view: http://regression.contentanalyticsinc.com:8080/regression/console/reportresult/" + str(row["id"]))

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

    website_header = "- " + website + "\n" + "Total tested product numbers: %d\n" \
                                             "Product numbers of content structure changed: %d\n" \
                                             "Product numbers of version changed: %d\n" \
                                             "Invalid product numbers: %d\n" \
                                             "Web console: %s\n" % (number_of_reported_products + number_of_invalid_products, number_of_changed_products, number_of_version_changed_products, number_of_invalid_products, "http://regression.contentanalyticsinc.com:8080/regression/\nlogin: tester\npassword: password\n")
    email_content += (website_header + changed_product_urls + not_product_urls)


fromaddr = "jenkins@contentanalyticsinc.com"
toaddrs = ["jacob.cats426@gmail.com", "diogo.medeiros1115@gmail.com", "adriana@contentanalyticsinc.com", "support@contentanalyticsinc.com"] # must be a list
subject = "Daily Notification from Regression Service : %s" % today.isoformat()
msg = """\
From: %s
To: %s
Subject: %s

%s
""" % (fromaddr, ", ".join(toaddrs), subject, email_content)

print "Message length is " + repr(len(msg))

#Change according to your settings
smtp_server = 'email-smtp.us-east-1.amazonaws.com'
smtp_username = 'AKIAI2XV5DZO5VTJ6LXQ'
smtp_password = 'AgWhl58LTqq36BpcFmKPs++24oz6DuS/J1k2GrAmp1T6'
smtp_port = '587'
smtp_do_tls = True

server = smtplib.SMTP(
    host = smtp_server,
    port = smtp_port,
    timeout = 10
)
server.set_debuglevel(10)
server.starttls()
server.ehlo()
server.login(smtp_username, smtp_password)
server.sendmail(fromaddr, toaddrs, msg)
print server.quit()
