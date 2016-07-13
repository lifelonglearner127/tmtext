# Removes old keys from S3 bucket

import os
import sys
import datetime
import zipfile
import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils.timezone import now
import boto
from dateutil.parser import parse as parse_date

CWD = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(CWD, '..', '..', '..', '..'))

from settings import MEDIA_ROOT
from gui.models import Job, get_data_filename, get_log_filename


sys.path.append(os.path.join(CWD,  '..', '..', '..', '..', '..',
                             'deploy', 'sqs_ranking_spiders'))
import scrapy_daemon
from test_sqs_flow import download_s3_file, AMAZON_BUCKET_NAME, unzip_file
from list_all_files_in_s3_bucket import list_files_in_bucket


def run(command, shell=None):
    """ Run the given command and return its output
    """
    out_stream = subprocess.PIPE
    err_stream = subprocess.PIPE

    if shell is not None:
        p = subprocess.Popen(command, shell=True, stdout=out_stream,
                             stderr=err_stream, executable=shell)
    else:
        p = subprocess.Popen(command, shell=True, stdout=out_stream,
                             stderr=err_stream)
    (stdout, stderr) = p.communicate()

    return stdout, stderr


def num_of_running_instances(file_path):
    """ Check how many instances of the given file are running """
    processes = 0
    output = run('ps aux')
    output = ' '.join(output)
    for line in output.split('\n'):
        line = line.strip()
        line = line.decode('utf-8')
        if file_path in line and not '/bin/sh' in line:
            processes += 1
    return processes


class Command(BaseCommand):
    help = 'Removes S3 keys older than 45 days'

    def handle(self, *args, **options):
        OLDER_THAN = 30  # in days

        if num_of_running_instances('remove_old_s3_files') > 1:
            print 'an instance of the script is already running...'
            sys.exit()
        conn = boto.connect_s3(
            aws_access_key_id=AMAZON_ACCESS_KEY,
            aws_secret_access_key=AMAZON_SECRET_KEY,
            is_secure=False,  # uncomment if you are not using ssl
        )
        # Get current bucket
        bucket = conn.get_bucket(AMAZON_BUCKET_NAME, validate=False)
        for s3_key in bucket.list():
            if not getattr(s3_key, 'date', None):
                continue
            if parse_date(s3_key.date) < now() - datetime.timedelta(days=OLDER_THAN):
                print 'removing file', s3_key
                try:
                    s3_key.delete()
                except Exception as e:
                    print ' '*4, str(e).upper()
            else:
                print 'skipping file', s3_key