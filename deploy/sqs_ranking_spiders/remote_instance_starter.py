#
# This script is intended to be in the AMI image used to spin up new instances
# on SQS call. It pulls the repo, prepares all the things then pulls message(s)
# from SQS and performs parsing.
#

import os
import sys
import random
import string
import json
import datetime
import zipfile
import time
import hashlib

import boto
from boto.s3.key import Key

from sqs_connect import SQS_Queue


REPO_BASE_PATH = '~/repo/'
REPO_URL = 'git@bitbucket.org:dfeinleib/tmtext.git'
TASK_QUEUE_NAME = 'sqs_ranking_spiders_tasks'  # incoming queue for tasks
DATA_QUEUE_NAME = 'sqs_ranking_spiders_data'  # output data
LOGS_QUEUE_NAME = 'sqs_ranking_spiders_logs'  # output logs
PROGRESS_QUEUE_NAME = 'sqs_ranking_spiders_progress'  # progress reports
JOB_OUTPUT_PATH = '~/job_output'  # local dir
AMAZON_BUCKET_NAME = 'spyder-bucket'  # Amazon S3 bucket name
AMAZON_ACCESS_KEY = 'AKIAIKTYYIQIZF3RWNRA'
AMAZON_SECRET_KEY = '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'
CWD = os.path.dirname(os.path.abspath(__file__))

# TODO:
# * pull message from sqs
# * separate the initial starter script and the daemon (coz we may want to update the daemon in the future)
# * push data to sqs (split into parts!)
# * push logs into sqs (split into parts!)
# * push compressed data & log files to Amazon S3 (for future processing)
# * progress tracking ([wc -l / num_of_results], [wc -l / quantity])
# * ...


def get_random_hash(length=28):
    return ''.join(
        random.choice(string.ascii_lowercase + string.digits)
        for _ in range(length)
    )


def is_first_run():
    """ Checks if it's the first run on this machine """
    return not os.path.exists(os.path.join(CWD, 'starter_already_executed'))


def mark_as_running():
    """ Mark this machine as the one that has already executed this script """
    with open(os.path.join(CWD, 'starter_already_executed'), 'w') as fh:
        fh.write('1')


def pull_repo():
    """ Clones or pulls the repo """
    if os.path.exists('%s/tmtext' % os.path.expanduser(REPO_BASE_PATH)):
        os.system('cd tmtext; git pull')
    else:
        os.system('cd %s && git clone %s' % (REPO_BASE_PATH, REPO_URL))


def read_file_by_parts(fname, part_size=1024*128):
    """ Reads the file and returns iterator of its content """
    fh = open(fname, 'rb')
    while True:
        part = fh.read(part_size)
        if not part:
            break
        yield part


def read_msg_from_sqs(queue_name_or_instance):
    if isinstance(queue_name_or_instance, (str, unicode)):
        sqs_queue = SQS_Queue(queue_name_or_instance)
    else:
        sqs_queue = queue_name_or_instance
    if sqs_queue.count() == 0:
        return  # the queue is empty
    try:
        # Get message from SQS
        message = sqs_queue.get()
    except IndexError as e:
        # This exception will most likely be triggered because you were
        #  grabbing off an empty queue
        return
    except Exception as e:
        # Catch all other exceptions to prevent the whole thing from crashing
        # TODO : Consider testing that sqs_scrape is still live, and restart
        #  it if needed
        return
    try:
        message = json.loads(message)
    except Exception, e:
        return
    return message, sqs_queue  # we will need sqs_queue later


def write_msg_to_sqs(queue_name_or_instance, msg):
    if not isinstance(msg, (str, unicode)):
        msg = json.dumps(msg)
    if isinstance(queue_name_or_instance, (str, unicode)):
        sqs_queue = SQS_Queue(queue_name_or_instance)
    else:
        sqs_queue = queue_name_or_instance
    sqs_queue.put(msg)


def put_file_into_sqs(fname, queue_name, metadata):
    for part_num, part_data in enumerate(read_file_by_parts(fname)):
        msg = {
            'type': 'ranking_spiders',
            'filename': fname,
            'utc_datetime': datetime.datetime.utcnow(),
            'part_num': part_num,
            'part_data': part_data
        }
        msg.update(metadata)
        write_msg_to_sqs(queue_name, msg)


def put_file_into_s3(bucket_name, fname,
                     amazon_public_key=AMAZON_ACCESS_KEY,
                     amazon_secret_key=AMAZON_SECRET_KEY,
                     compress=True):
    # Connect to S3
    conn = boto.connect_s3(
        aws_access_key_id=amazon_public_key,
        aws_secret_access_key=amazon_secret_key,
        is_secure=False,  # uncomment if you are not using ssl
    )
    # Get current bucket
    bucket = conn.get_bucket(bucket_name, validate=False)
    # Cut out file name
    filename = os.path.basename(fname)
    # Generate file path for S3
    folders = ("/" + datetime.datetime.utcnow().strftime('%Y/%m/%d')
               + "/" + filename)
    if compress:
        archive_name = os.path.splitext(filename)[0] + '.zip'
        #print 'Creating archive: ' + archive_name
        zf = zipfile.ZipFile(archive_name, mode='w')
        try:
            print 'Adding ' + filename + " to archive"
            zf.write(fname)
        finally:
            zf.close()

        filename = archive_name
        folders = ("/" + datetime.datetime.utcnow().strftime('%Y/%m/%d')
                   + "/" + archive_name)

    #print 'Uploading %s to Amazon S3 bucket %s' % \
    #   (filename, bucket_name)
    k = Key(bucket)
    #Set path to file on S3
    k.key = folders
    try:
        # Upload file to S3
        k.set_contents_from_filename(fname)
        # Download file from S3
        #k.get_contents_to_filename('bar.csv')
    except Exception:
        print "Check file path..."


def report_progress_and_wait(data_file, log_file, metadata,
                             initial_sleep_time=15, sleep_time=3):
    time.sleep(initial_sleep_time)
    # if the data file does not exist - try to wait a bit longer
    _max_initial_attempts = 10
    for i in xrange(_max_initial_attempts):
        if i >= _max_initial_attempts - 2:
            return  # error - the data file still does not exist
        if os.path.exists(data_file) and os.path.exists(log_file):
            break  # the files exist, that means the spider has been started
        time.sleep(initial_sleep_time)
    write_msg_to_sqs(
        metadata['server_name']+PROGRESS_QUEUE_NAME,
        {
            '_msg_id': metadata.get('task_id', metadata.get('task', None)),
            'utc_datetime': datetime.datetime.utcnow(),
            'progress': 0
        }
    )
    while 1:  # main loop
        raise NotImplementedError


def execute_task_from_sqs():
    #TODO: code for pulling the SQS message from the queue
    while 1:  # try to read from the queue until a new message arrives
        msg = read_msg_from_sqs(TASK_QUEUE_NAME)
        if msg is None:
            time.sleep(3)
            continue
        metadata, task_queue = msg  # store task_queue to re-use this instance
                                    #  later

    task_id = metadata.get('task_id', metadata.get('task', None))
    searchterms_str = metadata.get('searchterms_str', None)
    url = metadata.get('url', None)
    site = metadata['site']
    server_name = metadata['server_name']
    cmd_line_args = metadata.get('cmd_args', {})  # dict of extra command-line
                                                  # args, such as ordering

    # TODO: remove me! it's only for tests
    spider_name = 'walmart_products'
    searchterms_str = 'guitar'
    cmd_line_args = {'quantity': 100}

    # make sure the job output dir exists
    if not os.path.exists(os.path.expanduser(JOB_OUTPUT_PATH)):
        os.makedirs(os.path.expanduser(JOB_OUTPUT_PATH))

    local_job_id = get_random_hash()
    output_path = '%s/%s' % (os.path.expanduser(JOB_OUTPUT_PATH), local_job_id)
    cmd = ('cd %s/tmtext/product-ranking/product_ranking'
           ' && scrapy crawl %s -a searchterms_str="%s" %s'
           ' -s LOG_FILE=%s -o %s &')
    # prepare command-line arguments
    options = ' '
    for key, value in cmd_line_args:
        options += ' -a %s=%s' % (key, value)
    os.system(
        cmd % (
            REPO_BASE_PATH, spider_name, searchterms_str,
            options, output_path+'.log', output_path+'.jl')
    )
    # report progress and wait until the task is done
    report_progress_and_wait(output_path+'.jl', output_path+'.log', metadata)
    # upload the files to SQS and S3
    put_file_into_sqs(output_path+'.jl', server_name+DATA_QUEUE_NAME, metadata)
    put_file_into_sqs(output_path+'.log', server_name+LOGS_QUEUE_NAME,
                      metadata)
    put_file_into_s3(AMAZON_BUCKET_NAME, output_path+'.jl')
    put_file_into_s3(AMAZON_BUCKET_NAME, output_path+'.log')


if __name__ == '__main__':
    if not is_first_run():
        sys.exit()  # we don't want to re-use this machine
    mark_as_running()
    pull_repo()
    execute_task_from_sqs()

