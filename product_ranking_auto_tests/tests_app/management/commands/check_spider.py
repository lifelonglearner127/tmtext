#
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

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..', '..', '..'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from settings import (SPIDER_ROOT, MEDIA_ROOT, EMAIL_SUBJECT,
                      DEFAULT_FROM_EMAIL, HOST_NAME)
from tests_app.models import (Spider, TestRun, FailedRequest, Alert,
                              ThresholdSettings)


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


def get_spider_to_check(spider_to_get=None):
    """ Select random spider """
    if spider_to_get:
        # spider name arg given - select it
        spiders = Spider.objects.filter(active=True, name=spider_to_get.strip())
        if not spiders:
            print 'Spider %s not found in the DB' % spider_to_get
            sys.exit()
        spider = spiders[0]
    else:
        spiders = Spider.objects.filter(active=True).order_by('?')
        for spider in spiders:
            if spider_is_running(spider.name):
                continue
    # check one more time (there is a chance the test run
    #  was stopped while switching between the requests)
    time.sleep(3)
    if not spider_is_running(spider.name):
        time.sleep(3)
        if not spider_is_running(spider.name):
            return spider


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


def get_scrapy_spider_and_settings(spider):
    """ Returns the Scrapy spider class and the validator class
        for the given Django spider """
    # import the spider module
    module_name = None
    _sn = spider.name if not isinstance(spider, (str, unicode)) else spider
    for fname, spider_name in list_spiders():
        if spider_name == _sn:
            module_name = fname.replace('.py', '')
    if module_name is None:
        return
    sys.path.append(os.path.join(SPIDER_ROOT))
    sys.path.append(os.path.join(SPIDER_ROOT, 'product_ranking'))
    sys.path.append(os.path.join(SPIDER_ROOT, 'product_ranking', 'spiders'))
    module = __import__(module_name)
    # get validator settings class and the spider class itself
    validator = None
    scrapy_spider = None
    for obj in dir(module):
        if type(getattr(module, obj, '')) == type:
            if hasattr(getattr(module, obj), 'test_requests'):
                validator = getattr(module, obj)
            elif (hasattr(getattr(module, obj), 'name')
                    and hasattr(getattr(module, obj), 'start_urls')):
                if not 'Base' in str(getattr(module, obj)):
                    scrapy_spider = getattr(module, obj)
    return scrapy_spider, validator


def create_failed_request(test_run, scrapy_spider, request,
                          error, html_error=None):
    """ Just a convenient wrapper to avoid 'repeating myself' """
    today = timezone.now().strftime('%d_%m_%Y')
    output_dir = os.path.join(MEDIA_ROOT, 'output', test_run.spider.name)
    if not os.path.exists(os.path.join(output_dir, today)):
        os.makedirs(os.path.join(output_dir, today))
    fs_request = slugify(request)  # filesystem-friendly chars only
    output_file = os.path.join(output_dir, today,
                               str(test_run.pk)+'__'+fs_request+'.csv')
    log_file = os.path.join(output_dir, today,
                            str(test_run.pk)+'__'+fs_request+'.txt')
    if os.path.exists(scrapy_spider._validation_filename()):
        shutil.copy(scrapy_spider._validation_filename(), output_file)
    shutil.copy(scrapy_spider._validation_log_filename(), log_file)
    fr = FailedRequest.objects.create(
        test_run=test_run, request=request,
        error=error, error_html=html_error if html_error else "",
        result_file=os.path.relpath(output_file, MEDIA_ROOT),
        log_file=os.path.relpath(log_file, MEDIA_ROOT)
    )
    return fr


def is_test_run_passed(test_run):
    """ Check if the test run has been passed
        (by percentage of allowed failed requests)
    """
    percent_of_failed_requests = test_run.spider\
        .get_percent_of_failed_requests()
    num_failed = test_run.num_of_failed_requests
    num_ok = test_run.num_of_successful_requests
    percent_failed = float(num_failed) / float(num_failed+num_ok) * 100
    return percent_failed < percent_of_failed_requests


def send_alert_if_needed(test_run_or_spider):
    """ Send a notification if the threshold passed """
    if isinstance(test_run_or_spider, TestRun):
        spider = test_run_or_spider.spider
    else:
        spider = test_run_or_spider
    if not spider.is_error():
        return  # everything is okay?
    test_run = spider.get_last_failed_test_run()
    if test_run.test_run_alerts.count():
        return  # the alert has already been sent
    msg = """
The spider {spider_name} has:

1) {failed_requests} failed requests
2) {success_requests} success requests

You can see more info here: {host_name}{failed_run}
    """
    msg.format(
        spider_name=spider.name,
        failed_requests=test_run.num_of_failed_requests,
        success_requests=test_run.num_of_successful_requests,
        host_name=HOST_NAME,
        failed_run=reverse_lazy('tests_app_test_run_review',
                                kwargs={'pk': test_run.pk})
    )
    recipients = [r.strip() for r in spider.get_notify().split(',')]
    send_mail(
        EMAIL_SUBJECT.format(spider_name=spider.name),
        msg, DEFAULT_FROM_EMAIL, recipients,
        fail_silently=False
    )
    Alert.objects.create(test_run=test_run)


def check_spider(spider):
    test_run = TestRun.objects.create(status='running', spider=spider)
    scrapy_spider, spider_settings = get_scrapy_spider_and_settings(spider)
    scrapy_spider = scrapy_spider()  # instantiate class to use its methods
    for req, req_range in spider_settings.test_requests.items():
        run_spider(spider, req)
        errors = scrapy_spider.errors()
        html_errors = scrapy_spider.errors_html()
        output_data = scrapy_spider._validation_data()
        if errors:
            test_run.num_of_failed_requests += 1
            create_failed_request(test_run, scrapy_spider, req,
                                  errors, html_errors)
            print ' '*7, 'request failed:', req
        elif (isinstance(req_range, int)
                and len(output_data) != 0):
            test_run.num_of_failed_requests += 1
            create_failed_request(
                test_run, scrapy_spider, req,
                'must have empty output', '<p>must have empty output</p>')
            print ' '*7, 'request failed:', req
        elif (isinstance(req_range, (list, tuple))
                and not (req_range[0] < len(output_data) < req_range[1])):
            test_run.num_of_failed_requests += 1
            _msg = 'must have output in range %s but got %i results' % (
                        req_range, len(output_data))
            create_failed_request(
                test_run, scrapy_spider, req, _msg, '<p>' + _msg + '</p>'
            )
            print ' '*7, 'request failed:', req
        else:
            test_run.num_of_successful_requests += 1
            print ' '*7, 'request passed:', req

    if is_test_run_passed(test_run):
        test_run.status = 'passed'
        print ' '*3, 'test run PASSED'
    else:
        test_run.status = 'failed'
        print ' '*3, 'test run FAILED'
    test_run.when_finished = timezone.now()
    test_run.save()


def wait_until_spider_finishes(spider):
    if spider_is_running(spider.name):
        time.sleep(1)


def run_spider(spider, search_term):
    global ENABLE_CACHE
    old_cwd = os.getcwd()
    os.chdir(os.path.join(SPIDER_ROOT))
    # add `-a quantity=10 -a enable_cache=1` below for easider debugging
    cmd = 'scrapy crawl %s -a searchterms_str="%s" -a validate=1' % (
        spider.name, search_term)
    if ENABLE_CACHE:
        cmd += ' -a enable_cache=1'
    run(cmd)
    wait_until_spider_finishes(spider)
    os.chdir(old_cwd)


class Command(BaseCommand):
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('spider_name', nargs='?', type=str)
        parser.add_argument('enable_cache', nargs='?', type=str)

    def handle(self, *args, **options):
        global ENABLE_CACHE
        # check ThresholdSettings
        if not ThresholdSettings.objects.count():
            print 'Create at least one ThresholdSettings!'
            sys.exit()
        # get a spider to check
        spider = get_spider_to_check(options.get('spider_name', None))
        if options.get('enable_cache', None):
            ENABLE_CACHE = True
        if spider is None:
            print 'No active spiders in the DB, or all of them are running'
            sys.exit()
        print ' '*3, 'going to check spider %s:' % spider.name
        check_spider(spider)