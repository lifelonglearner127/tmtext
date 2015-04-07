
# TODO:
# * individual URL mode
# * add-best-seller.py hack
# ...

import os
import sys
import random
import time
import json

import boto
import boto.sqs
from boto.s3.connection import S3Connection


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..'))

try:
    # try local mode (we're in the deploy dir)
    from sqs_ranking_spiders.remote_instance_starter import (
        AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_BUCKET_NAME)
    from sqs_ranking_spiders.add_task_to_sqs import read_access_and_secret_keys

except ImportError:
    # we're in /home/spiders/repo
    from repo.remote_instance_starter import (
        AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_BUCKET_NAME)
    from repo.add_task_to_sqs import read_access_and_secret_keys


MAX_WORKING_TIME = 30  # 30 mins
LOCAL_DUMP_PATH = '/tmp/_test_sqs_messages'
REGION = "us-east-1"
DELETE_MESSAGES = True  # set False to avoid deleting messages in output queues


def _get_conn():
    conf = read_access_and_secret_keys()
    conn = boto.sqs.connect_to_region(
        REGION,
        aws_access_key_id=conf[0],
        aws_secret_access_key=conf[1]
    )
    return conn


def _get_sqs_queue(queue_name):
    conn = _get_conn()
    return conn.get_queue(queue_name)


def _create_sqs_queue(queue_name, visib_timeout=30):
    conn = _get_conn()
    try:
        return conn.create_queue(queue_name, visib_timeout)
    except Exception, e:
        print str(e)


def _read_queue(queue_name):
    """ Returns all the messages in the queue """
    queue = _get_sqs_queue(queue_name)
    if queue is None:
        return []  # the queue has not been created yet (?)
    return queue.get_messages(
        num_messages=10, visibility_timeout=3
    )


def get_sqs_messages(queue_name):
    """ Turns messages into files """
    def dump_message(message):
        if not os.path.exists(LOCAL_DUMP_PATH):
            os.makedirs(LOCAL_DUMP_PATH)
        fname = str(random.randint(1000000, 2000000))
        if not isinstance(message, (str, unicode)):
            message = json.dumps(message.get_body())
        fname = os.path.join(LOCAL_DUMP_PATH, fname)
        with open(fname, 'w') as fh:
            fh.write(message)
        return fname

    queue = _get_sqs_queue(queue_name)
    for message in _read_queue(queue_name):
        fname = dump_message(message)
        if DELETE_MESSAGES:
            queue.delete_message(message)
        yield fname


def read_msgs_until_task_id_appears(task_id, queue_name, max_wait_time=30*60):
    for sec in range(max_wait_time):
        time.sleep(1)
        for fname in list(get_sqs_messages(queue_name)):
            with open(fname, 'r') as fh:
                msg_data = json.loads(fh.read())
            # may still be string due to double json encoding on dumps()
            if isinstance(msg_data, (str, unicode)):
                msg_data = json.loads(msg_data)
            task_id_sqs = msg_data['_msg_id']
            if str(task_id) == str(task_id_sqs):
                return fname, msg_data


def download_s3_file(bucket, s3_path, local_path):
    aws_connection = S3Connection(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY)
    bucket = aws_connection.get_bucket(bucket)
    key = bucket.get_key(s3_path)
    key.get_contents_to_filename(local_path)


def validate_data_file(fname, search_term):
    """ Checks the local data file (downloaded from S3) """
    all_lines_are_jsons = True
    with open(fname, 'r') as fh:
        for line_no, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                line = json.loads(line)
            except Exception, e:
                print 'LINE %i is not JSON!' % line_no
                all_lines_are_jsons = False
                continue
            if line.get('search_term', '') != search_term:
                print 'SEARCH TERMS DO NOT MARCH AT LINE %i' % line_no
                return False
    return all_lines_are_jsons


def is_plain_jsonlist_file(fname):
    with open(fname, 'r') as fh:
        cont = fh.read(1024)
    if not cont:
        return
    return cont[0] == '{'


if __name__ == '__main__':
    test_server_name = 'test_server'
    test_queue_name = 'sqs_ranking_spiders_tasks_tests'
    search_term = 'asus'
    local_data_file = '/tmp/_s3_data_file.zip'

    # create output 'queues' for this server
    _create_sqs_queue(test_server_name+'sqs_ranking_spiders_progress',
                      visib_timeout=30)
    _create_sqs_queue(test_server_name+'sqs_ranking_spiders_output',
                      visib_timeout=30)

    # 0. Generate random marker to identify the test task
    random_id = str(random.randint(100000, 200000))
    print 'RANDOM ID FOR THIS TASK:', random_id

    # 1. Create a new message in the input queue to start crawling
    cmd = ('python add_task_to_sqs.py task_id=%s'
           ' searchterms_str=%s server_name=%s')
    cmd = cmd % (random_id, search_term, test_server_name)
    print '    ...executing:', cmd
    os.system(cmd)

    # 2. Read the progress queue and validate it
    progress_result = read_msgs_until_task_id_appears(
        random_id, test_server_name+'sqs_ranking_spiders_progress')
    if progress_result is None:
        print 'Progress queue failed!'
        sys.exit()
    fname, msg_data = progress_result
    print 'Progress queue first message:', msg_data
    assert 'progress' in msg_data

    # 3. Read the output queue and get the S3 bucket filename
    output_result = read_msgs_until_task_id_appears(
        random_id, test_server_name+'sqs_ranking_spiders_output')
    if output_result is None:
        print 'Data queue failed!'
        sys.exit()
    fname, msg_data = output_result
    print 'Data queue first message:', msg_data
    assert 's3_key_data' in msg_data

    # 4. Read the S3 bucket file and validate its content
    download_s3_file(
        AMAZON_BUCKET_NAME, msg_data['s3_key_data'], local_data_file)
    if not is_plain_jsonlist_file(local_data_file):
        # TODO: unpack files if needed!
        assert False, 'zip extraction is not implemented yet - do it!'
    if validate_data_file(local_data_file, search_term):
        print 'EVERYTHING IS OK'
    else:
        print 'DATA FILE CHECK FAILED'