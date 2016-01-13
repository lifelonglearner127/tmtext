import sys
from boto.s3.connection import S3Connection

queue_names_list = ["dev_scrape",
                    "test_scrape",
                    "demo_scrape",
                    "production_scrape",
                    "unit_test_scrape",
                    "integration_test_scrape",
                    "walmart-fullsite_scrape"]

s3 = S3Connection('AKIAJPOFQWU54DCMDKLQ', '/aebM4IZ97NEwVnfS6Jys6sKVvDXa6eDZsB2X7gP')

queue_name = sys.argv[1]

bucket = None
bucket_name = 'contentanalytcis.inc.ch.s3.{0}'.format(queue_name)

if s3.lookup(bucket_name):
    bucket = s3.get_bucket(bucket_name)
else:
    bucket = None

if bucket:
    rs = bucket.list()
    key_list = [key.name for key in rs]

    deleted_key_count = 0
    bucket_length = len(key_list)

    for key in key_list:
        bucket.delete_key(key)
        deleted_key_count += 1

    print "bucket name: " + bucket_name
    print "bucket length: " + bucket_length
    print "deleted key count: " + deleted_key_count
else:
    print "There's no bucket for specified queue."