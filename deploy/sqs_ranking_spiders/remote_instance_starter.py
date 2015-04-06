#
# This script is intended to be in the AMI image used to spin up new instances
# on SQS call. It pulls the repo, prepares all the things then executes another
# script that pulls the SQS queue and performs all the parsing
#

import os
import sys
import time
import urllib
import logging
import logging.config
from subprocess import Popen, PIPE

import boto
from boto.s3.key import Key


REPO_URL = 'git@bitbucket.org:dfeinleib/tmtext.git'
SCRAPY_DAEMON = 'scrapy_daemon.py'
CWD = os.path.dirname(os.path.abspath(__file__))
REPO_BASE_PATH = os.path.realpath(os.path.join(CWD, '..', '..'))  # local mode
if os.path.dirname(os.path.abspath(__file__)) == '/home/spiders/repo':  # remote
    REPO_BASE_PATH = '/home/spiders/repo/tmtext'

# for stop flag settings
FLAG_URL = "stop-sc-spiders.contentanalyticsinc.com"
FLAG_S3_KEY = "scrapy_daemon_stop_flag"
AMAZON_BUCKET_NAME = 'spyder-bucket'  # Amazon S3 bucket name
AMAZON_ACCESS_KEY = 'AKIAIKTYYIQIZF3RWNRA'
AMAZON_SECRET_KEY = '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'

log_file_path = '/tmp/remote_instance_starter2.log'
log_settings = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s [%(module)s] %(levelname)s:%(message)s'
        }
    },
    'handlers': {
        'to_log_file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': log_file_path
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'default'
        },
    },
    'loggers': {
        'main_log': {
            'level': 'DEBUG',
            'handlers': ['to_log_file', 'console']
        }
    },
}

logging.config.dictConfig(log_settings)
logger = logging.getLogger('main_log')


def is_first_run():
    """ Checks if it's the first run on this machine """
    return not os.path.exists(os.path.join(CWD, __file__+'.marker'))


def mark_as_running():
    """ Mark this machine as the one that has already executed this script """
    with open(os.path.join(CWD, __file__+'.marker'), 'w') as fh:
        fh.write('1')


def pull_repo():
    """ Clones or pulls the repo """
    if os.path.exists('%s' % os.path.expanduser(REPO_BASE_PATH)):
        cmd = 'cd %s; git pull 2>&1' % os.path.expanduser(REPO_BASE_PATH)
        p = Popen(cmd, shell=True, stdout=PIPE)
    else:
        cmd = 'cd %s && git clone %s 2>&1' % (
            os.path.dirname(REPO_BASE_PATH), REPO_URL)
        p = Popen(cmd, shell=True, stdout=PIPE)
    logger.info("Run %s", cmd)
    logger.info("Git:%s", p.stdout.read().strip())


def start_scrapy_daemon():
    # just call an external script that is supposed to do all the parsing magic
    path = os.path.expanduser('~/repo/tmtext/deploy/sqs_ranking_spiders/')
    cmd = 'cd %s; python %s &' % (path, SCRAPY_DAEMON)
    logger.info("Run %s", cmd)
    os.system(cmd)


def wait_until_post_starter_script_executed(script_name):
    if script_name.endswith('.marker'):
        script_name = script_name.replace('.marker', '')
    while 1:
        if not os.path.exists(os.path.join(CWD, script_name+'.marker')):
            time.sleep(5)
            logger.info("       %s is running...", script_name)
        else:
            return


def stop_flag_exists_at_s3(bucket_name, key,
                           amazon_public_key=AMAZON_ACCESS_KEY,
                           amazon_secret_key=AMAZON_SECRET_KEY,):
    conn = boto.connect_s3(
        aws_access_key_id=amazon_public_key,
        aws_secret_access_key=amazon_secret_key,
        is_secure=False,
    )
    bucket = conn.get_bucket(bucket_name, validate=False)
    k = Key(bucket)
    k.key = "scrapy_daemon_stop_flag"
    try:
        if "true" in k.get_contents_as_string().lower():
            return True
        return False
    except:
        return False


# def stop_flag_exists_at_url(url):
#     u = urllib.urlopen(url)
#     if "True" in u.read():
#         return True
#     return False


if __name__ == '__main__':
    if not is_first_run():
        sys.exit()  # we don't want to re-use this machine
    if stop_flag_exists_at_s3(AMAZON_BUCKET_NAME, FLAG_S3_KEY):
    # if stop_flag_exists_at_url(FLAG_URL):
        sys.exit()
    mark_as_running()
    pull_repo()
    wait_until_post_starter_script_executed('post_starter_root.py')
    wait_until_post_starter_script_executed('post_starter_spiders.py')
    start_scrapy_daemon()