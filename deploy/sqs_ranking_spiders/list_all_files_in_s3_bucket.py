#
# This script lists all the files in the spiders' S3 bucket
#

import os
import sys

import boto
from boto.s3.connection import S3Connection


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..'))

try:
    # try local mode (we're in the deploy dir)
    from sqs_ranking_spiders.scrapy_daemon import (
        AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_BUCKET_NAME)
except ImportError:
    # we're in /home/spiders/repo
    from repo.remote_instance_starter import (
        AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_BUCKET_NAME)


def list_files_in_bucket(access_key, secret_key, bucket_name):
    conn = S3Connection(access_key, secret_key)
    bucket = conn.get_bucket(bucket_name)
    return bucket.list()


if __name__ == '__main__':
    for f in list_files_in_bucket(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_BUCKET_NAME):
        print f
#        if 'job_output' in f.name: 
#            f.get_contents_to_filename(os.path.basename(f.name))
