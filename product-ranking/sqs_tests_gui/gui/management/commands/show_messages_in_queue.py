import os
import sys
import random

from django.core.management.base import BaseCommand, CommandError

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

from update_jobs import _get_queue


def read_messages_from_queue_iterator(
        queue_name, region="us-east-1", timeout=5, num_messages=5555):
    q = _get_queue(queue_name, region=region)
    num_iterations = num_messages / 10 + 1
    for i in range(0, num_iterations):
        for m in q.get_messages(num_messages=10, visibility_timeout=timeout):
            yield m


class Command(BaseCommand):
    help = 'Shows messages in the specified queue'

    def add_arguments(self, parser):
        parser.add_argument('--queue_name', dest='queue_name')
        parser.add_argument('--num_messages', dest='num_messages')
        parser.add_argument('--visibility_timeout', dest='visibility_timeout')

    def handle(self, *args, **options):
        queue_name = options['queue_name']
        num_messages = int(options['num_messages'])
        visibility_timeout = int(options['visibility_timeout'])
        print 'Showing messages for queue %s' % queue_name
        for m in read_messages_from_queue_iterator(
                queue_name=queue_name, num_messages=num_messages,
                timeout=visibility_timeout):
            print m._body
            if random.randint(0, 100) == 0:
                sys.stdout.flush()