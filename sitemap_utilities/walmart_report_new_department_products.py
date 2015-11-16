__author__ = 'root'

import os,time

#!/usr/bin/env python

import re
import zlib
import os
import csv
import glob
import operator
import shutil
import smtplib
import sys

def generate_department_product_list(input_file, output_dir):
    with open(input_file) as f:
        fieldnames = ['url', 'department', 'type']
        owned_home_count = marketplace_count = 0
        department_owned_marketplace_total_list = {}

        for line in f:
            try:
                url = re.search('\<url\>(.+?)\</url\>', line).group(1)
                department = re.search('<department>(.+?)</department>', line).group(1)
                type = re.search('<type>(.+?)</type>', line).group(1)
                count_list = [0, 0, 0]

                if department in department_owned_marketplace_total_list:
                    count_list = department_owned_marketplace_total_list[department]

                if type == "owned":
                    owned_home_count = owned_home_count + 1
                    count_list[0] = count_list[0] + 1

                if type == "marketplace":
                    marketplace_count = marketplace_count + 1
                    count_list[1] = count_list[1] + 1

                count_list[2] = count_list[0] + count_list[1]
                department_owned_marketplace_total_list[department] = count_list

                localDate = time.localtime()
                dateString = time.strftime("%m%d%Y", localDate)

#                csv_file_name = ("%s_%s_%s.csv" % (department, type, dateString)).lower()
                csv_file_name = ("%s_%s.csv" % (department, type)).lower()

                if os.path.isfile(output_dir + csv_file_name):
                    csv_file = open(output_dir + csv_file_name, 'a+')
                else:
                    csv_file = open(output_dir + csv_file_name, 'w')
#                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#                    writer.writeheader()
#                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#                csv_writer.writerow({'url': url, 'department': department, 'type': type})

                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([url])

                csv_file.close()
            except:
                continue

path_output = "/home/ubuntu/walmart_departments_output/"
gz_file_list = glob.glob("/home/ubuntu/walmart_departments/*.gz")

for i in range(len(gz_file_list)):
    statinfo = os.stat(gz_file_list[i])
    gz_file_list[i] = gz_file_list[i],statinfo.st_size,statinfo.st_ctime

gz_file_list.sort(key=operator.itemgetter(2))
gz_file_list.reverse()

path_file_most_recent = gz_file_list[0][0]
path_file_prev = gz_file_list[1][0]

print path_file_most_recent
print path_file_prev

try:
    shutil.rmtree(path_output + "prev")
    shutil.rmtree(path_output + "recent")
except:
    pass

date_numbers = re.findall("(\d+)", path_file_most_recent)

if os.path.exists(path_output + ('_' . join(str(x) for x in date_numbers))):
    sys.exit(0)
else:
    os.makedirs(path_output + "prev")
    os.makedirs(path_output + "recent")
    os.makedirs(path_output + ('_' . join(str(x) for x in date_numbers)))

CHUNKSIZE = 1024

d = zlib.decompressobj(16 + zlib.MAX_WBITS)

file_most_recent = open(path_file_most_recent, 'rb')
buffer = file_most_recent.read(CHUNKSIZE)

path_output_file_most_recent = path_output + "recent/recent.xml"
output_file_most_recent = open(path_output_file_most_recent, 'w')

while buffer:
    outstr = d.decompress(buffer)
    output_file_most_recent.write(outstr)
    buffer = file_most_recent.read(CHUNKSIZE)

outstr = d.flush()
output_file_most_recent.write(outstr)

file_most_recent.close()
output_file_most_recent.close()

generate_department_product_list(path_output_file_most_recent, path_output + "recent/")

CHUNKSIZE = 1024

d = zlib.decompressobj(16 + zlib.MAX_WBITS)

file_prev = open(path_file_prev, 'rb')
buffer = file_prev.read(CHUNKSIZE)

path_output_file_prev = path_output + "prev/prev.xml"
output_file_prev = open(path_output_file_prev, 'w')

while buffer:
    outstr = d.decompress(buffer)
    output_file_prev.write(outstr)
    buffer = file_prev.read(CHUNKSIZE)

outstr = d.flush()
output_file_prev.write(outstr)

file_prev.close()
output_file_prev.close()

generate_department_product_list(path_output_file_prev, path_output + "prev/")

recent_csv_files = [f for f in os.listdir(path_output + "recent/") if f.endswith(".csv")]
prev_csv_files = [f for f in os.listdir(path_output + "prev/") if f.endswith(".csv")]
common_csv_files = list(set(recent_csv_files).intersection(prev_csv_files))

for csv_file_name in common_csv_files:
    f1 = open(path_output + "recent/" + csv_file_name)
    csv_f1 = csv.reader(f1)
    recent_product_list = list(csv_f1)
    recent_product_list = [row[0] for row in recent_product_list]
    f1.close()

    f2 = open(path_output + "prev/" + csv_file_name)
    csv_f2 = csv.reader(f2)
    prev_product_list = list(csv_f2)
    prev_product_list = [row[0] for row in prev_product_list]
    f2.close()

    new_product_list = list(set(recent_product_list) - set(prev_product_list))
    all_product_list = list(set(recent_product_list + prev_product_list))

    if new_product_list:
        csv_file = open(path_output + ('_' . join(str(x) for x in date_numbers)) + "/" + csv_file_name.split(".")[0] + "_new.csv", 'w')
        csv_writer = csv.writer(csv_file)

        for product in new_product_list:
            csv_writer.writerow([product])

        csv_file.close()

    if all_product_list:
        csv_file = open(path_output + ('_' . join(str(x) for x in date_numbers)) + "/" + csv_file_name.split(".")[0] + "_all.csv", 'w')
        csv_writer = csv.writer(csv_file)

        for product in all_product_list:
            csv_writer.writerow([product])

        csv_file.close()

try:
    shutil.rmtree(path_output + "prev")
    shutil.rmtree(path_output + "recent")
except:
    pass

report_results = "Reference path: ubuntu@52.7.234.182:" + path_output + ('_' . join(str(x) for x in date_numbers) + "\n\n*Please contact to ITS to register your ssh key to access the results")

fromaddr = "jenkins@contentanalyticsinc.com"
#toaddrs = ["dave@contentanalyticsinc.com", "jacob.cats426@gmail.com", "support@contentanalyticsinc.com"] # must be a list
toaddrs = ["dave@contentanalyticsinc.com", "diogo.medeiros1115@gmail.com", "jacob.cats426@gmail.com", "support@contentanalyticsinc.com"] # must be a list
subject = "Walmart department product list was updated"
msg = """\
From: %s
To: %s
Subject: %s

%s
""" % (fromaddr, ", ".join(toaddrs), subject, report_results)

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