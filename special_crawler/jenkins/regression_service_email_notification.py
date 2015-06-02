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

sql_changed_products = "select sample_url from console_reportresult where changes_in_structure > 0 and report_date = '%s'" % today.isoformat()

cur.execute(sql_changed_products)
rows = cur.fetchall()
urls = []

for row in rows:
    urls.append(row["sample_url"])

urls = list(set(urls))
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
not_product_urls = "\n" .join(urls)

not_product_urls = "\n\nFollowing product urls are invalid.\n" + not_product_urls
print not_product_urls

fromaddr = "jenkins@contentanalyticsinc.com"
toaddrs = ["jacob.cats426@gmail.com", "diogo.medeiros1115@gmail.com", "adriana@contentanalyticsinc.com"] # must be a list
subject = "Daily Notification from Regression Service : %s" % today.isoformat()
msg = """\
From: %s
To: %s
Subject: %s

%s
""" % (fromaddr, ", ".join(toaddrs), subject, changed_product_urls + not_product_urls)

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
