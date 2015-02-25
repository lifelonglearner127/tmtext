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

import boto
from boto.s3.key import Key


REPO_BASE_PATH = '~/repo/'
REPO_URL = 'git@bitbucket.org:dfeinleib/tmtext.git'
TASK_QUEUE_NAME = 'TEST_sqs_ranking_spiders_tasks'  # incoming queue for tasks
DATA_QUEUE_NAME = 'TEST_sqs_ranking_spiders_data'  # output data
LOGS_QUEUE_NAME = 'TEST_sqs_ranking_spiders_logs'  # output logs
JOB_OUTPUT_PATH = '~/job_output'  # local dir
AMAZON_BUCKET_NAME = 'spyder-bucket'  # Amazon S3 bucket name
AMAZON_ACCESS_KEY = 'AKIAIKTYYIQIZF3RWNRA'
AMAZON_SECRET_KEY = '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'
CWD = os.path.dirname(os.path.abspath(__file__))

# TODO:
# * pull message from sqs
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


def read_msg_from_sqs(queue_name):
    raise NotImplementedError


def write_msg_to_sqs(queue_name, msg):
    if not isinstance(msg, (str, unicode)):
        msg = json.dumps(msg)
    raise NotImplementedError


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


def execute_task_from_sqs():
    #TODO: code for pulling the SQS message from the queue
    spider_name = 'walmart_products'
    quantity = 100
    searchterms_str = 'guitar'
    metadata = read_msg_from_sqs(TASK_QUEUE_NAME)


    # make sure the job output dir exists
    if not os.path.exists(os.path.expanduser(JOB_OUTPUT_PATH)):
        os.makedirs(os.path.expanduser(JOB_OUTPUT_PATH))

    local_job_id = get_random_hash()
    output_path = '%s/%s' % (os.path.expanduser(JOB_OUTPUT_PATH), local_job_id)
    cmd = ('cd %s/tmtext/product-ranking/product_ranking '
           '&& scrapy crawl %s -a searchterms_str="%s" %s -s LOG_FILE=%s -o %s')
    options = ' '
    if 'quantity' in locals():
        options += '-a quantity=%s' % quantity
    os.system(
        cmd % (
            REPO_BASE_PATH, spider_name, searchterms_str,
            options, output_path+'.log', output_path+'.jl')
    )
    put_file_into_sqs(output_path+'.jl', DATA_QUEUE_NAME, metadata)
    put_file_into_sqs(output_path+'.log', LOGS_QUEUE_NAME, metadata)
    put_file_into_s3(output_path+'.jl')
    put_file_into_s3(output_path+'.log')


if __name__ == '__main__':
    if not is_first_run():
        sys.exit()  # we don't want to re-use this machine
    mark_as_running()
    pull_repo()
    execute_task_from_sqs()

