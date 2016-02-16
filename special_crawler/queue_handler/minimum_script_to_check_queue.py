__author__ = 'root'

import csv
import json

with open('/home/mufasa/Downloads/items url.csv', 'rb') as f:
    reader = csv.reader(f)
    urls = list(reader)
    urls = [row[0] for row in urls]

#s3 = S3Connection('AKIAJPOFQWU54DCMDKLQ', '/aebM4IZ97NEwVnfS6Jys6sKVvDXa6eDZsB2X7gP')

conf = {
    "sqs-access-key": "AKIAJPOFQWU54DCMDKLQ",
    "sqs-secret-key": "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",
    "sqs-input-queue-name": "search_queue",
    "sqs-output-queue-name": "92bc860b-e3eb-4a69-9870-47c0c00834f4_process",
    "sqs-region": "us-east-1",
    "sqs-path": "sqssend"
}

import boto.sqs
conn = boto.sqs.connect_to_region(
    conf.get('sqs-region'),
    aws_access_key_id=conf.get('sqs-access-key'),
    aws_secret_access_key=conf.get('sqs-secret-key')
)

input_q = conn.create_queue(conf.get('sqs-input-queue-name'))
output_q = conn.create_queue(conf.get('sqs-output-queue-name'))

from boto.sqs.message import RawMessage

for url in urls:
    m = RawMessage()
    m.set_body('{"server_name":"92bc860b-e3eb-4a69-9870-47c0c00834f4", "url": "' + url + '"}')
    retval = input_q.write(m)
    print 'added message, got retval: %s' % retval

import time

unique_list = []
duplicate_list = []

while(True):
    for m in output_q.get_messages():
        result = json.loads(m.get_body())

        if result["message"] == "Unique content.":
            unique_list.append(result["url"])

        if result["message"] == "Found duplicate content from other links.":
            duplicate_list.append(result["url"])

        print '%s: %s' % (m, m.get_body())
        output_q.delete_message(m)

    time.sleep(1)

print unique_list
print duplicate_list