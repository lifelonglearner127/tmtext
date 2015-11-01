
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


def spider_is_running(name, search_term=None):
    """ Checks if the given spider with name `name` is running.
        Optional arg `search_term` will narrow filtering,
        assuming we want to check that the spider with specified
        `name` AND `search_term` is running
    """
    if isinstance(name, unicode):
        name = name.encode('utf8')
    if search_term is None:
        all_processes = run('ps aux | grep scrapy')
    else:
        all_processes = run('ps aux | grep scrapy | grep "%s"' % search_term)
    all_processes = ''.join(all_processes)
    for proc_line in all_processes.split('\n'):
        if ' '+name in proc_line:
            if ' crawl ' in proc_line:
                return True


def list_spiders():
    """ Returns all the spider names and filenames
    :return:
    """
    spiders_dir = os.path.join(SPIDER_ROOT, 'product_ranking', 'spiders')
    for fname in os.listdir(spiders_dir):
        _full_fname = os.path.join(spiders_dir, fname)
        if not os.path.isfile(_full_fname):
            continue
        with open(_full_fname, 'r') as fh:
            spider_content = fh.read()
        spider_content = spider_content.replace(' ', '').replace('"', "'")
        spider_name = re.search("name=\'([\w_]+_products)\'", spider_content)
        if spider_name:
            yield fname, spider_name.group(1)


def wait_until_spider_finishes(spider):
    if spider_is_running(spider.name):
        time.sleep(1)


def run_spider(spider, search_term, time_marker):
    """ Executes spider
    :param spider: DB spider instance
    :param search_term: str, request to search
    :param time_marker: datetime
    :return: str, path to the temporary file
    """
    global ENABLE_CACHE
    old_cwd = os.getcwd()
    os.chdir(os.path.join(SPIDER_ROOT))
    # add `-a quantity=10 -a enable_cache=1` below for easider debugging
    scrapy_path = '/home/web_runner/virtual-environments/web-runner/bin/scrapy'
    if not os.path.exists(scrapy_path):
        scrapy_path = 'scrapy'
    cmd = r'%s crawl %s -a searchterms_str="%s" -a validate=1' % (
        scrapy_path, spider.name, search_term)
    if ENABLE_CACHE:
        cmd += ' -a enable_cache=1'
    if isinstance(time_marker, (datetime.date, datetime.datetime)):
        time_marker = slugify(str(time_marker))
    _log_filename = '/tmp/%s__%s__%s.log' % (
        spider.name, slugify(search_term), time_marker)
    cmd += ' -s LOG_FILE=%s' % _log_filename
    cmd = str(cmd)  # avoid TypeError: must be encoded string without NULL ...
    subprocess.Popen(shlex.split(cmd), stdout=open(os.devnull, 'w')).wait()
    os.chdir(old_cwd)
    return _log_filename


def test_match(test_run):
    pass
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
            test_match(tr)
            print 'Going to check test run %s' % tr
        if not test_runs:
            print 'No test runs to check'