
# This file takes the given spider and performs its check.
# If no spidername given, it'll check a random spider
#

#assert False, 'read todo!'
# TODO:
# 1) alerts (special page + emails?)
# 2) better admin (list_fields, filters, status colors, all that stuff)
# 3) cron jobs file
# 4) removing old test runs and their files!
# 5) overall reports - just a page with list of spiders with status 'ok' and 'not ok'
#       (basically, testers will need to review the whole spider)
# 6) redirect page to go to #5 - like /spider-checks/costco_products/

import sys
import os
import re
import shutil
import time
import subprocess
import shlex
import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..', '..', '..'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from tests_app.models import Spider, TestRun, Report
from utils import test_run_to_dirname


ENABLE_CACHE = False


def run(command, shell=None):
    """ Runs the given command and returns its output """
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


def _create_proj_dir(test_run):
    dirname = test_run_to_dirname(test_run)
    if not dirname.endswith('/'):
        dirname += '/'
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return dirname


def _get_branches_dirs(test_run):
    base_dir = _create_proj_dir(test_run)
    dir1 = os.path.join(base_dir, test_run.branch1)
    dir2 = os.path.join(base_dir, test_run.branch2)
    return dir1, dir2


def prepare_git_branches(test_run, copy_files=True):
    """ Creates 2 dirs under base path; each dir contains complete project
        with the specific branches """
    dir1, dir2 = _get_branches_dirs(test_run)
    if not os.path.exists(dir1):
        os.makedirs(dir1)
    if not os.path.exists(dir2):
        os.makedirs(dir2)
    # clone & checkout first dir
    this_repo_dir = os.path.abspath(os.path.join(CWD, '..', '..', '..', '..'))
    cmd_copy = 'cp -r "%s/." "%s"'
    cmd_fetch = 'cd %s; git fetch --all && git checkout %s && git pull origin %s'
    if copy_files:
        os.system(cmd_copy % (this_repo_dir, dir1))
        os.system(cmd_copy % (this_repo_dir, dir2))
    os.system(cmd_fetch % (dir1, test_run.branch1, test_run.branch1))
    os.system(cmd_fetch % (dir2, test_run.branch2, test_run.branch2))


def test_match(test_run):
    prepare_git_branches(test_run, copy_files=False)
    # TODO: git fetch --all
    # TODO: git checkout test_run.branch1
    # TODO: run crawl  scrapy crawl myspider -s LOG_FILE=scrapy.log   (override settings: request_delay=0.01; local_cache=enabled; local_cache_path=...;)
    # TODO: git checkout test_run.branch2
    # TODO: run crawl
    # TODO: match output files


class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        # get a test run to check
        test_runs = TestRun.objects.filter(status='stopped').order_by('when_started')[0:10]
        for tr in test_runs:
            print 'Going to check test run %s' % tr
            test_match(tr)
        if not test_runs:
            print 'No test runs to check'