import os
import sys

from django.db import models


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD,  '..', '..', '..',
                             'deploy'))
from sqs_ranking_spiders import QUEUES_LIST

import settings


def get_data_filename(job):
    """ Returns local job filename relative to MEDIA """
    try:
        job = int(job)
    except TypeError:
        pass
    if not isinstance(job, int):
        job = job.pk
    return '/%s/data_file.csv' % job


def get_log_filename(job):
    """ Returns local job logs relative to MEDIA """
    try:
        job = int(job)
    except TypeError:
        pass
    if not isinstance(job, int):
        job = job.pk
    return '/%s/log.log' % job


class Job(models.Model):
    cache_choices = (
        ('no cache', 'no cache'), ('cache', 'cache')
    )

    _status_choices = [
        ('created', 'created'),
        ('pushed into sqs', 'pushed into sqs'),
        ('in progress', 'in progress'),
        ('finished', 'finished'),
        ('failed', 'failed')
    ]

    name = models.CharField(max_length=100, blank=True, null=True,
                            help_text='Optional, just for convenience')
    spider = models.CharField(max_length=100, choices=[])

    search_term = models.CharField(
        max_length=255, blank=True, null=True,
        help_text='Enter this OR product(s) URL below'
    )
    product_url = models.URLField(
        max_length=500, blank=True, null=True,
        help_text='Enter this OR search term above OR products URL below'
    )
    products_urls = models.CharField(
        max_length=1500, blank=True, null=True,
        help_text=('Enter this OR search term above OR product_url.'
                   ' Only for the CH+SC mode!')
    )
    quantity = models.IntegerField(
        blank=True, null=True, default=20,
        help_text='Leave blank for unlimited results (slow!)'
    )
    extra_cmd_args = models.TextField(
        max_length=300, blank=True, null=True,
        help_text="Extra command-line arguments, 1 per line. Example: enable_cache=1"
    )
    with_best_seller_ranking = models.BooleanField(
        default=False, help_text='For Walmart bestsellers matching')
    task_id = models.IntegerField(default=100000)
    server_name = models.CharField(max_length=100, default='test_server')
    branch_name = models.CharField(
        max_length=100, blank=True, null=True,
        help_text='Branch to use at the instance(s); leave blank for master'
    )

    mode = models.CharField(
        max_length=100, choices=cache_choices, default=cache_choices[0])

    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=100, choices=_status_choices,
                              default='created')

    def searchterm_or_url(self):
        return ('SearchTerm [%s]' % self.search_term if self.search_term
                else 'URL')
    searchterm_or_url.short_description = 'Type'

    def get_input_queue(self):
        if self.mode == 'no cache':
            return settings.TEST_QUEUE
        elif self.mode == 'cache':
            return settings.TEST_CACHE_QUEUE

