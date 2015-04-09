import random

from django.db import models

# Create your models here.
# TODO:
# 1) push into SQS
# 2) monitor progress queue
# 3) monitor output data queue
# 4) pull data file if needed


def get_data_filename(job):
    """ Returns local job filename relative to STATIC """
    try:
        job = int(job)
    except TypeError:
        pass
    if not isinstance(job, int):
        job = job.pk
    return '/%s/data_file.csv' % job


def get_log_filename(job):
    """ Returns local job logs relative to STATIC """
    try:
        job = int(job)
    except TypeError:
        pass
    if not isinstance(job, int):
        job = job.pk
    return '/%s/log.log' % job


class Job(models.Model):
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
        help_text='Enter this OR product URL below'
    )
    product_url = models.URLField(
        max_length=500, blank=True, null=True,
        help_text='Enter this OR search term above'
    )
    quantity = models.IntegerField(
        blank=True, null=True, default=20,
        help_text='Leave blank for unlimited results (slow!)'
    )
    task_id = models.IntegerField(default=100000)
    server_name = models.CharField(max_length=100, default='test_server')

    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=100, choices=_status_choices,
                              default='created')