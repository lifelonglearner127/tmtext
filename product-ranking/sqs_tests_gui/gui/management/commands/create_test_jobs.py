# Creates many test jobs

import os
import sys
import random

from django.core.management.base import BaseCommand, CommandError

CWD = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(CWD, '..', '..', '..', '..'))

from gui.models import Job, generate_spider_choices


sys.path.append(os.path.join(CWD,  '..', '..', '..', '..', '..',
                             'deploy', 'sqs_ranking_spiders'))
from add_task_to_sqs import put_msg_to_sqs


def _create_job(i, all_spiders=False):
    search_terms = [
        'laptop',
        'water',
        'iphone',
        'galaxy tab',
        'dresses',
        'black shoes',
        'green shoes',
        'cokies',
        'harry potter',
        'nice',
        'red',
        'black',
    ]
    sites = ['amazon_products',
            'walmart_products',
            'topshop_products',
            'amazonca_products',
            'amazoncouk_products',
            'amazonde_products'
    ]
    if all_spiders:
        choices = generate_spider_choices()
        sites = [choice[0] for choice in choices]
    Job.objects.create(
        name='bulk created task ' + str(i),
        spider=random.choice(sites),
        search_term=random.choice(search_terms),
        quantity=random.randrange(300,400),
        task_id=random.randrange(100000, 900000),
        mode='no cache',
        branch_name='tor_proxies'
    )


class Command(BaseCommand):
    help = 'Creates many test jobs'

    def handle(self, *args, **options):
        # TODO: command-line args for num of jobs and branch name
        N = 300
        for i in xrange(N):
            _create_job(i)