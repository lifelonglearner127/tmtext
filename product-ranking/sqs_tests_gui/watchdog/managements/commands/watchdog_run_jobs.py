import os
import sys
import datetime
import json
import zipfile
import subprocess
import random
import tempfile

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils.timezone import now
import boto
from dateutil.parser import parse as parse_date

CWD = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(CWD, '..', '..', '..', '..'))

from settings import MEDIA_ROOT
from watchdog.models import WatchDogJob, WatchDogJobTestRuns
from gui.models import Job, get_data_filename


sys.path.append(os.path.join(CWD,  '..', '..', '..', '..', '..',
                             'deploy', 'sqs_ranking_spiders'))


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
    help = 'Runs a watchdog job and checks if it fails'

    def handle(self, *args, **options):
        if num_of_running_instances('watchdog_run_jobs') > 1:
            print 'an instance of the script is already running...'
            sys.exit()

        from jsonpath_rw import jsonpath, parse as jsonparse

        # get all active jobs
        active_jobs = [j for j in WatchDogJob.objects.all() if j.is_active()]
        for active_job in active_jobs:
            print("Creating test jobs for WatchDogJob #" + str(active_job.pk))
            for url in [u.strip() for u in active_job.urls.split('\n') if u.strip()]:
                spider_job = Job.objects.create(
                    name='WatchDog Job #%i' % active_job.pk,
                    spider=active_job.spider,
                    product_url=url,
                    task_id=random.randint(999999, 99999999),
                    branch_name=active_job.branch)
                screenshot_job = Job.objects.create(
                    name='WatchDog Job #%i' % active_job.pk,
                    spider='url2screenshot_products',
                    product_url=url,
                    task_id=random.randint(999999, 99999999))
                wd_test_run = WatchDogJobTestRuns.objects.create(
                    wd_job=active_job,
                    spider_job=spider_job,
                    screenshot_job=screenshot_job)
                print('    created test run %i' % wd_test_run.pk)

        # check all finished jobs
        jobs = Job.objects.filter(status='finished', name__icontains="WatchDog Job")\
            .exclude(spider='url2screenshot_products')\
            .filter(wd_test_run_jobs__status='finished').distinct()
        # get only active jobs
        _exclude_jobs = []
        for j in jobs:
            wd_job = j.wd_test_run_jobs.all()[0].wd_job
            if not wd_job.is_active():
                _exclude_jobs.append(j.pk)
        jobs = jobs.exclude(pk__in=_exclude_jobs).distinct()
        for job in jobs:
            wd_job = job.wd_test_run_jobs.all()[0].wd_job
            wd_job.last_checked = now()
            wd_job.save()

            wd_test_run = WatchDogJobTestRuns.objects.get(spider_job=job)
            wd_test_run.status = 'finished'
            wd_test_run.finished = now()
            wd_test_run.save()

            print('Checking results of SQS Job %i' % job.pk)

            job_output_file = MEDIA_ROOT + get_data_filename(job)
            with open(job_output_file, 'r') as fh:
                job_results = fh.read().strip()
            if job_results:
                job_results = json.loads(job_results)
            else:
                print('    error: empty results for SQS Job %i' % job.pk)
                continue
            result_value = jsonparse(wd_job.response_path).find(job_results)
            if str(result_value) != str(wd_job.desired_value):
                print('    error: values differ for WD Job %i' % job.pk)
                wd_job.status = 'failed'
                if not wd_test_run in list(wd_job.failed_test_runs.all()):
                    wd_job.failed_test_runs.add(wd_test_run)
                wd_job.save
            else:
                print('    ok: values are the same for WD Job %i' % job.pk)
