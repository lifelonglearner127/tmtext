import os
import sys

from django.db import models
from django.core.urlresolvers import reverse_lazy


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD,  '..', '..', '..',
                             'deploy'))

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


def get_progress_filename(job):
    """ Returns local progress logs relative to MEDIA """
    try:
        job = int(job)
    except TypeError:
        pass
    if not isinstance(job, int):
        job = job.pk
    return '/%s/progress.progress' % job


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
    spider = models.CharField(max_length=100, choices=[])  # see gui/forms.py

    search_term = models.CharField(
        max_length=255, blank=True, null=True,
        help_text='Enter this OR product(s) URL below'
    )
    product_url = models.URLField(
        max_length=500, blank=True, null=True,
        help_text='Enter this OR search term above OR products URL below'
    )
    product_urls = models.CharField(
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
    sc_ch_mode = models.BooleanField(
        default=False, help_text=('Run the spider in CH mode. Do not forget to'
                                  ' fill the Product UrlS field above.')
    )
    with_best_seller_ranking = models.BooleanField(
        default=False, help_text='For Walmart bestsellers matching')
    task_id = models.IntegerField(default=100000)
    server_name = models.CharField(max_length=100, default='test_server')
    branch_name = models.CharField(
        max_length=100, blank=True, null=True,
        help_text='Branch to use at the instance(s); leave blank for sc_production'
    )

    save_raw_pages = models.BooleanField(
        default=False, help_text='Upload raw cache to S3?')
    #load_raw_pages = models.DateField(  # DISABLED for now!
    #    blank=True, null=True, default=timezone.now().date(),
    #    help_text='Load raw cache from S3'
    #)

    mode = models.CharField(
        max_length=100, choices=cache_choices, default=cache_choices[0])

    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=100, choices=_status_choices,
                              default='created')

    priority_choices = ['test', 'urgent', 'production', 'dev']
    priority = models.CharField(max_length=20, default='urgent', choices=[(c, c) for c in priority_choices])

    def searchterm_or_url(self):
        return ('SearchTerm [%s]' % self.search_term if self.search_term
                else 'URL')
    searchterm_or_url.short_description = 'Type'

    def view_as_image(self):
        # for url2screenshot spider
        if 'url2screenshot' in self.spider:
            return "<a href='%s' target='_blank'>Image</a>" % reverse_lazy(
                'view_base64_image', kwargs={'job': self.pk})
        return ''
    view_as_image.short_description = 'Image'
    view_as_image.allow_tags = True

    def get_input_queue(self):
        if self.priority not in self.priority_choices\
                or self.priority == 'test':  # default, test priority
            if self.mode == 'no cache':
                return settings.TEST_QUEUE
            elif self.mode == 'cache':
                return settings.TEST_CACHE_QUEUE
        if self.mode == 'no cache':
            return settings.QUEUES_LIST[self.priority]
        elif self.mode == 'cache':
            return settings.CACHE_QUEUES_LIST[self.priority]


class JobGrouperCache(models.Model):
    """ Group automatically incoming created jobs in a single piece
        (for products_url only). In other words, groups product_url into
        products_url
    """
    spider = models.CharField(max_length=100, db_index=True)
    product_url = models.URLField(max_length=500)
    extra_args = models.TextField(blank=True, null=True)  # for other args,JSON
    created = models.DateTimeField(auto_now_add=True, db_index=True,
                                   blank=True, null=True)

    def __unicode__(self):
        return u'%s: %s: %s' % (self.spider, self.product_url, self.created)
