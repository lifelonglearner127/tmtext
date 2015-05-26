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

sql = "select sample_url from console_reportresult where changes_in_structure > 0 and report_date >= '2015-05-25'"

cur.execute(sql)
rows = cur.fetchall()
urls = []

for row in rows:
    urls.append(row["sample_url"])

changed_product_urls = "\n" .join(urls)

print changed_product_urls

fromaddr = "jenkins@contentanalyticsinc.com"
toaddrs = ["jacob.cats426@gmail.com", "diogo.medeiros1115@gmail.com"] # must be a list
subject = "Website changes notification from regression service"
msg = """\
From: %s
To: %s
Subject: %s

%s
""" % (fromaddr, ", ".join(toaddrs), subject, changed_product_urls)

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
