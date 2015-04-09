import os
import sys
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

CWD = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(CWD, '..', '..', '..', '..'))

from settings import STATIC_ROOT
from gui.models import Job, get_data_filename, get_log_filename


sys.path.append(os.path.join(CWD,  '..', '..', '..', '..', '..',
                             'deploy', 'sqs_ranking_spiders'))
import scrapy_daemon
from test_sqs_flow import download_s3_file, AMAZON_BUCKET_NAME
from list_all_files_in_s3_bucket import list_files_in_bucket, \
        AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY

LOCAL_AMAZON_LIST_CACHE = os.path.join(CWD, '_amazon_listing.txt')


def list_amazon_bucket(bucket=AMAZON_BUCKET_NAME,
                       local_fname=LOCAL_AMAZON_LIST_CACHE):
    filez = list_files_in_bucket(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, bucket)
    with open(local_fname, 'w') as fh:
        for f in filez:
            fh.write(str(f)+'\n')


def get_filenames_for_task_id(task_id, local_fname=LOCAL_AMAZON_LIST_CACHE):
    with open(local_fname, 'r') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if '____%s____' % task_id in line:
                if ',' in line:
                    line = line.split(',')[-1]
                line = line.replace('<', '').replace('>', '')
                yield line.strip()


class Command(BaseCommand):
    help = 'Updates 10 random jobs, downloading their files if ready'

    def handle(self, *args, **options):
        jobs = Job.objects.filter(
            Q(status='pushed into sqs') | Q(status='in progress')
        ).order_by('?').distinct()[0:10]
        list_amazon_bucket()  # get list of files from S3
        for job in jobs:
            # try to find the appropriate S3 file by task ID
            amazon_fnames = get_filenames_for_task_id(job.task_id)
            amazon_data_file = [f for f in amazon_fnames if '.csv' in f]
            if not amazon_data_file:
                continue
            amazon_data_file = amazon_data_file[0]
            print 'For job with task ID %s we found amazon fname [%s]' % (
                job.task_id, amazon_data_file)
            #TODO: download the data and log files, put them into an appropriate path, and update the job status