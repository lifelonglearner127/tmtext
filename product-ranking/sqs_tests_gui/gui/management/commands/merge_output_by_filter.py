"""
Merges downloaded output CSV files in one, for jobs filtered by given template
"""

import os
import sys
import datetime
import json
import zipfile

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils.timezone import now
from dateutil.parser import parse as parse_date

CWD = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(CWD, '..', '..', '..', '..'))

from settings import MEDIA_ROOT
from gui.models import Job, get_data_filename, get_log_filename,\
    get_progress_filename


sys.path.append(os.path.join(CWD,  '..', '..', '..', '..', '..',
                             'deploy', 'sqs_ranking_spiders'))
import scrapy_daemon
from test_sqs_flow import download_s3_file, AMAZON_BUCKET_NAME, unzip_file
from list_all_files_in_s3_bucket import list_files_in_bucket, \
        AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        jobs_template = raw_input("Enter the name of the jobs to search for: ")

        # get random jobs
        jobs = Job.objects.filter(
            status='finished', name__icontains=jobs_template)

        confirm = raw_input("Found %i jobs, continue? Y/N: " % jobs.count())
        if confirm.lower() not in ('y', 'yes'):
            print('You did not confirm - exit')
            sys.exit(1)

        output_fname = raw_input("Enter output (merged) file name: ")
        if os.path.exists(output_fname):
            if raw_input("Output file %s already exists, overwrite? Y/N: ").lower()\
                    not in ('y', 'yes'):
                print("Will not overwrite - exit...")

        for job in jobs:
            import pdb; pdb.set_trace()