
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

from tests_app.models import Spider, TestRun, Report, ReportSearchterm,\
    LocalCache
from utils import test_run_to_dirname, get_output_fname

sys.path.append(os.path.join(CWD, '..', '..', '..', '..', 'product-ranking'))
from debug_match_urls import match


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


def prepare_git_branches(test_run, copy_files=True, force=True):
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
    cmd_fetch = 'cd %s; git fetch --all %s && git checkout %s %s && git pull origin %s %s'
    if copy_files:
        os.system(cmd_copy % (this_repo_dir, dir1))
        os.system(cmd_copy % (this_repo_dir, dir2))
    if force:
        force = ' --force '
    else:
        force = ''
    os.system(cmd_fetch % (dir1, force, test_run.branch1, force, test_run.branch1, force))
    os.system(cmd_fetch % (dir2, force, test_run.branch2, force, test_run.branch2, force))


def get_cache(searchterm, test_run, delete_expired=True):
    """ Returns valid cache for the specified searchterm and spider
    if it exists; None otherwise
    """
    cache = LocalCache.objects.filter(
        searchterm=searchterm, test_run=test_run, spider=test_run.spider
    ).order_by('-when_created')
    if delete_expired:
        for c in cache:
            if not c.is_valid():
                shutil.rmtree(c.get_path())
                print '    removing expired cache %s' % c
                c.delete()
    cache = LocalCache.objects.filter(
        searchterm=searchterm, test_run=test_run, spider=test_run.spider
    ).order_by('-when_created')
    if cache and os.path.exists(cache[0].get_path()):
        print '    returning cache %s' % cache[0]
        return cache[0]
    else:
        # file path does not exist - create new cache
        cache = LocalCache.objects.create(
            searchterm=searchterm, test_run=test_run, spider=test_run.spider)
        print '    created new cache %s' % cache
        return cache


def create_cache_path_if_doesnt_exist(cache):
    if not os.path.exists(cache.get_path()):
        print '    created cache path %s' % cache.get_path()
        os.makedirs(cache.get_path())


def test_match(test_run):
    prepare_git_branches(test_run, copy_files=False, force=True)
    # TODO: add cache management!
    # TODO: run crawl  scrapy crawl myspider -s LOG_FILE=scrapy.log   (override settings: request_delay=0.01; local_cache=enabled; local_cache_path=...;)
    cmd = ('cd "{branch_dir}/product-ranking/"; scrapy crawl {spider_name}'
           ' -a searchterms_str="{searchterm}" -a quantity={quantity}'
           ' -a enable_cache=True -s HTTPCACHE_DIR="{cache_dir}"'
           ' -s DOWNLOAD_DELAY=0.05 -o {output_path}')
    report = Report.objects.create(testrun=test_run)
    for searchterm in test_run.spider.searchterms.all():
        cache = get_cache(searchterm, test_run)
        create_cache_path_if_doesnt_exist(cache)
        print '    executing spider %s for ST %s' % (
            test_run.spider.name, searchterm.searchterm)
        output1 = get_output_fname(searchterm, test_run, test_run.branch1)
        output2 = get_output_fname(searchterm, test_run, test_run.branch2)
        os.system(cmd.format(
            branch_dir=_get_branches_dirs(test_run)[0],
            spider_name=test_run.spider.name,
            searchterm=searchterm.searchterm, quantity=searchterm.quantity,
            cache_dir=cache.get_path(), output_path=output1))
        os.system(cmd.format(
            branch_dir=_get_branches_dirs(test_run)[1],
            spider_name=test_run.spider.name,
            searchterm=searchterm.searchterm, quantity=searchterm.quantity,
            cache_dir=cache.get_path(), output_path=output2))
        if test_run.exclude_fields is None:
            test_run.exclude_fields = []
        diff = match(
            f1=output1, f2=output2,
            fields2exclude=test_run.exclude_fields,
            strip_get_args=test_run.strip_get_args,
            skip_urls=test_run.skip_urls,
            print_output=False
        )
        report_searchterm = ReportSearchterm.objects.create(
            report=report, searchterm=searchterm, total_urls=diff['total_urls'],
            matched_urls=diff['matched_urls'], diffs=diff['diff'])


def cleanup_files(test_run):
    for _dir in _get_branches_dirs(test_run):
        shutil.rmtree(_dir)


class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        # get a test run to check
        test_runs = TestRun.objects.filter(status='stopped').order_by('when_started')[0:10]
        for tr in test_runs:
            print 'Going to check test run %s' % tr
            tr.status = 'running'
            tr.save()
            test_match(tr)
            tr_reports = tr.testrun_reports.all().order_by('-when_created')
            if tr_reports:
                status = 'passed'
                if tr_reports[0].not_enough_matched_urls():
                    status = 'failed'
                if tr_reports[0].diffs_found():
                    status = 'failed'
            else:
                status = 'failed'
            tr.status = status
            tr.save()
            cleanup_files(tr)
        if not test_runs:
            print 'No test runs to check'