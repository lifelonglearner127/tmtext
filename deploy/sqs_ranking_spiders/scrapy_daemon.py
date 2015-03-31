#
# This script is a replacement of Scrapyd. It pulls a message from the queue,
# starts the spider, reports progress, and does all the other things.
#

import datetime
import json
import os
import sys
import random
import time
import zipfile
from subprocess import Popen, PIPE

import boto
from boto.s3.key import Key
import unidecode


# TODO:
# * ...


# list of all available incoming SQS with tasks
TASK_QUEUES_LIST = [
    'sqs_ranking_spiders_tasks',  # production one
    'sqs_ranking_spiders_tasks_dev',  # development one
    'sqs_ranking_spiders_tasks_tests',  # test one
]
OUTPUT_QUEUE_NAME = 'sqs_ranking_spiders_output'
PROGRESS_QUEUE_NAME = 'sqs_ranking_spiders_progress'  # progress reports
JOB_OUTPUT_PATH = '~/job_output'  # local dir
CWD = os.path.dirname(os.path.abspath(__file__))
path = os.path.expanduser('~/repo')
# fo local mode
sys.path.insert(1, os.path.join(CWD, '..'))
sys.path.insert(2, os.path.join(CWD, '..', '..', 'special_crawler',
                                'queue_handler'))
# for servers path
sys.path.insert(1, os.path.join(path, '..'))
sys.path.insert(2, os.path.join(path, '..', '..', 'special_crawler',
                                'queue_handler'))
from sqs_ranking_spiders.task_id_generator import \
    generate_hash_datestamp_data, load_data_from_hash_datestamp_data
try:
    # try local mode (we're in the deploy dir)
    from sqs_ranking_spiders.remote_instance_starter import REPO_BASE_PATH,\
        logging, AMAZON_BUCKET_NAME, AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY
except ImportError:
    # we're in /home/spiders/repo
    from repo.remote_instance_starter import REPO_BASE_PATH, logging, \
        AMAZON_BUCKET_NAME, AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY
sys.path.insert(
    3, os.path.join(REPO_BASE_PATH, 'special_crawler', 'queue_handler'))
from sqs_connect import SQS_Queue

TEST_MODE = False  # if we should perform local file tests

logger = logging.getLogger('main_log')


def set_global_variables_from_data_file():
    try:
        json_data = load_data_from_hash_datestamp_data()
        globals()['RANDOM_HASH'] = json_data['random_hash']
        globals()['DATESTAMP'] = json_data['datestamp']
        globals()['FOLDERS_PATH'] = json_data['folders_path']
    except:
        logger.error("Required hash_datestamp_data wasn't created."
                     "Create it now.")
        generate_hash_datestamp_data()
        set_global_variables_from_data_file()

def json_serializer(obj):
    """ JSON serializer for objects not serializable by default json code """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        serial = obj.isoformat()
        return serial


def job_to_fname(metadata):
    searchterms_str = metadata.get('searchterms_str', None)
    site = metadata['site']
    if isinstance(searchterms_str, (str, unicode)):
        searchterms_str = searchterms_str.decode('utf8')
    # job_name = datetime.datetime.utcnow().strftime('%d-%m-%Y')
    job_name = DATESTAMP + '____' + RANDOM_HASH
    if searchterms_str:
        additional_part = unidecode.unidecode(
            searchterms_str).replace(' ', '-')
    else:
        # maybe should be changed to product_url
        additional_part = 'single-product-url-request'
    job_name += '____' + additional_part + '____' + site
    # job_name += '____' + site + '____' + get_random_hash()
    return job_name


def read_msg_from_sqs(queue_name_or_instance):
    if isinstance(queue_name_or_instance, (str, unicode)):
        sqs_queue = SQS_Queue(queue_name_or_instance)
    else:
        sqs_queue = queue_name_or_instance
    if not sqs_queue.q:
        logger.error("Task queue '%s' not exist at all",
                     queue_name_or_instance)
        return
    if sqs_queue.count() == 0:
        logger.warning("No any task messages were found at the queue '%s'.",
                       sqs_queue.q.name)
        return  # the queue is empty
    try:
        # Get message from SQS
        message = sqs_queue.get()
    except IndexError as e:
        logger.warning("Failed to get message from queue. Maybe it's empty.")
        # This exception will most likely be triggered because you were
        #  grabbing off an empty queue
        return
    except Exception as e:
        logger.error("Failed to get message from queue. %s.", str(e))
        # Catch all other exceptions to prevent the whole thing from crashing
        # TODO : Consider testing that sqs_scrape is still live, and restart
        #  it if needed
        return
    try:
        message = json.loads(message)
    except Exception, e:
        logger.error("Message was provided not in json format. %s.", str(e))
        return
    return message, sqs_queue  # we will need sqs_queue later


def test_get_fs_name_from_queue_name(queue_name):
    return '/tmp/%s' % queue_name


def test_read_msg_from_fs(queue_name):
    fake_class = SQS_Queue(queue_name)
    with open(test_get_fs_name_from_queue_name(queue_name), 'r') as fh:
        return json.loads(fh.read()), fake_class


def test_write_msg_to_fs(queue_name_or_instance, msg):
    if not isinstance(msg, (str, unicode)):
        msg = json.dumps(msg, default=json_serializer)
    if isinstance(queue_name_or_instance, (str, unicode)):
        sqs_queue = SQS_Queue(queue_name_or_instance)
    else:
        sqs_queue = queue_name_or_instance
    with open(
            test_get_fs_name_from_queue_name(queue_name_or_instance), 'a'
    ) as fh:
        fh.write(msg+'\n')


def _create_sqs_queue(queue_or_connection, queue_name, visib_timeout=30):
    if isinstance(queue_or_connection, SQS_Queue):
        queue_or_connection = queue_or_connection.conn
    queue_or_connection.create_queue(queue_name, visib_timeout)


def write_msg_to_sqs(queue_name_or_instance, msg):
    if not isinstance(msg, (str, unicode)):
        msg = json.dumps(msg, default=json_serializer)
    if isinstance(queue_name_or_instance, (str, unicode)):
        sqs_queue = SQS_Queue(queue_name_or_instance)
    else:
        sqs_queue = queue_name_or_instance
    if getattr(sqs_queue, 'q', '') is None:
        logger.warning("Queue '%s' does not exist. Will be created new one.",
                        queue_name_or_instance)
        _create_sqs_queue(sqs_queue.conn, queue_name_or_instance)
        sqs_queue = SQS_Queue(queue_name_or_instance)
    time.sleep(5)  # let the queue get up
    try:
        sqs_queue.put(msg)
    except Exception, e:
        logger.error("Failed to put message to queue %s:\n%s",
                      queue_name_or_instance, str(e))


def dump_result_data_into_sqs(data_key, logs_key, queue_name, metadata):
    instance_log_filename = DATESTAMP + '____' + RANDOM_HASH + '____' + \
        'remote_instance_starter2.log'
    s3_key_instance_starter_logs = (FOLDERS_PATH + instance_log_filename)
    msg = {
        '_msg_id': metadata.get('task_id', metadata.get('task', None)),
        'type': 'ranking_spiders',
        's3_key_data': data_key.key,
        's3_key_logs': logs_key.key,
        'bucket_name': data_key.bucket.name,
        'utc_datetime': datetime.datetime.utcnow(),
        's3_key_instance_starter_logs': s3_key_instance_starter_logs,
    }
    logger.info("Provide result msg %s to queue '%s'", msg, queue_name)
    if TEST_MODE:
        test_write_msg_to_fs(queue_name, msg)
    else:
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
    # folders = ("/" + datetime.datetime.utcnow().strftime('%Y/%m/%d')
    #            + "/" + filename)
    folders = (FOLDERS_PATH + filename)
    if compress:
        try:
            import zlib
            mode = zipfile.ZIP_DEFLATED
        except ImportError:
            mode = zipfile.ZIP_STORED
        archive_name = filename + '.zip'
        zf = zipfile.ZipFile(archive_name, 'w', mode)
        try:
            zf.write(fname)
            logger.info("Adding %s to archive", filename)
        finally:
            zf.close()

        filename = archive_name
        # folders = ("/" + datetime.datetime.utcnow().strftime('%Y/%m/%d')
        #            + "/" + archive_name)
        folders = (FOLDERS_PATH + archive_name)

    logger.info("Uploading %s to Amazon S3 bucket %s", filename, bucket_name)
    k = Key(bucket)
    #Set path to file on S3
    k.key = folders
    try:
        # Upload file to S3
        k.set_contents_from_filename(fname)
        # Download file from S3
        #k.get_contents_to_filename('bar.csv')
        # key will be used to provide path at S3 for UI side
        return k
    except Exception:
        logger.warning("Failed to load files to S3. "
                "Check file path and amazon keys/permissions.")


def _check_if_log_file_contains_end_marker(log_file, data_bs_file):
    if not os.path.exists(log_file):
        return
    lines = get_lines_from_file(log_file)
    if lines:
        if 'INFO: Spider closed (finished)' in lines[-1]:
            if data_bs_file:
                lines = get_lines_from_file(data_bs_file[:-3] + ".log")
                if not 'INFO: Spider closed (finished)' in lines[-1]:
                    return
                temp_file = '%s/%s' % (
                    os.path.expanduser(JOB_OUTPUT_PATH),
                    "temp_file.jl"
                )
                os.system(
                    REPO_BASE_PATH + "/product-ranking/add-best-seller.py " +
                    log_file[:-4] + ".jl " + data_bs_file + " >" + temp_file
                )
                with open(temp_file) as bs_file:
                    lines = bs_file.readlines()
                    with open(log_file[:-4]+".jl", "w") as main_file:
                        main_file.writelines(lines)
                os.remove(temp_file)
            return True

def get_lines_from_file(get_file):
    try:
        f = open(get_file,'r')
    except IOError:
        logger.error("Failed to open log file %s", get_file)
        return  # error - can't open the log file
    else:
        f.seek(0, 2)
        fsize = f.tell()
        f.seek(max(fsize-1024, 0), 0)
        lines = f.readlines()
        f.close()
        return lines
    return False

def _check_num_of_products(data_file):
    if not os.path.exists(data_file):
        return
    fh = open(data_file, 'r')
    products = 0
    for _ in fh:
        products += 1
    fh.close()
    return products

def generate_msg(metadata, progress):
    _msg = {
        '_msg_id': metadata.get('task_id', metadata.get('task', None)),
        'utc_datetime': datetime.datetime.utcnow(),
        'progress': progress
    }
    return _msg

def report_progress_and_wait(data_file, log_file, data_bs_file, metadata,
                             initial_sleep_time=15, sleep_time=15):
    time.sleep(initial_sleep_time)
    # if the data file does not exist - try to wait a bit longer
    _max_initial_attempts = 10
    for i in xrange(_max_initial_attempts):
        if i >= _max_initial_attempts - 2:
            logger.error("Spider failed to start.")
            _msg = generate_msg(metadata, 'failed')
            if TEST_MODE:
                test_write_msg_to_fs(
                    metadata['server_name']+PROGRESS_QUEUE_NAME, _msg)
            else:
                write_msg_to_sqs(
                    metadata['server_name']+PROGRESS_QUEUE_NAME, _msg)
            sys.exit()
            return  # error - the data file still does not exist
        if os.path.exists(data_file) and os.path.exists(log_file):
            logger.info("Spider was started")
            break  # the files exist, that means the spider has been started
        time.sleep(initial_sleep_time)
    _msg = generate_msg(metadata, 0)
    if TEST_MODE:
        test_write_msg_to_fs(
            metadata['server_name']+PROGRESS_QUEUE_NAME, _msg)
    else:
        write_msg_to_sqs(
            metadata['server_name']+PROGRESS_QUEUE_NAME, _msg)
    while 1:
        _msg = generate_msg(metadata, _check_num_of_products(data_file))
        if TEST_MODE:
            test_write_msg_to_fs(
                metadata['server_name']+PROGRESS_QUEUE_NAME, _msg)
        else:
            write_msg_to_sqs(
                metadata['server_name']+PROGRESS_QUEUE_NAME, _msg)

        if _check_if_log_file_contains_end_marker(log_file, data_bs_file):
            logger.info("Spider task was completed.")
            _msg = generate_msg(metadata, 'finished')
            if TEST_MODE:
                test_write_msg_to_fs(
                    metadata['server_name']+PROGRESS_QUEUE_NAME, _msg)
            else:
                write_msg_to_sqs(
                    metadata['server_name']+PROGRESS_QUEUE_NAME, _msg)
            return
        time.sleep(sleep_time)

def execute_task_from_sqs():
    set_global_variables_from_data_file()
    while 1:  # try to read from the queue until a new message arrives
        TASK_QUEUE_NAME = random.choice(TASK_QUEUES_LIST)
        logger.info("Try to get task message from queue %s.",
                    TASK_QUEUE_NAME)
        if TEST_MODE:
            msg = test_read_msg_from_fs(TASK_QUEUE_NAME)
        else:
            msg = read_msg_from_sqs(TASK_QUEUE_NAME)
        if msg is None:
            time.sleep(3)
            continue
        metadata, task_queue = msg  # store task_queue to re-use this instance
                                    #  later
        break
    # due to task performance may take more than 12 hrs remove task immediately
    #task_queue.task_done()
    logger.info("Task message was successfully received and "
                "removed form queue.")
    task_id = metadata.get('task_id', metadata.get('task', None))
    searchterms_str = metadata.get('searchterms_str', None)
    url = metadata.get('url', None)
    site = metadata['site']
    server_name = metadata['server_name']
    cmd_line_args = metadata.get('cmd_args', {})  # dict of extra command-line
                                                  # args, such as ordering

    # make sure the job output dir exists
    if not os.path.exists(os.path.expanduser(JOB_OUTPUT_PATH)):
        logger.debug("Create job output dir %s",
                      os.path.expanduser(JOB_OUTPUT_PATH))
        os.makedirs(os.path.expanduser(JOB_OUTPUT_PATH))

    local_job_id = job_to_fname(metadata)
    output_path = '%s/%s' % (os.path.expanduser(JOB_OUTPUT_PATH), local_job_id)
    cmd = ('cd %s/product-ranking'
           ' && scrapy crawl %s -a %s="%s" %s'
           ' -s LOG_FILE=%s -o %s &')
    # prepare command-line arguments
    options = ' '

    for key, value in cmd_line_args.items():
        options += ' -a %s=%s' % (key, value)
    if searchterms_str:
        arg_name = 'searchterms_str'
        arg_value = searchterms_str
    if url:
        arg_name = 'product_url'
        arg_value = url
    cmd = cmd % (
        REPO_BASE_PATH, site+'_products', arg_name, arg_value,
        options, output_path+'.log', output_path+'.jl'
    )
    logger.info("Runing %s", cmd)

    data_bs_file = None
    if "with_best_seller_ranking" in metadata \
            and metadata["with_best_seller_ranking"]:
        data_bs_file = output_path + '_bs.jl'
        cmdbs = ('cd %s/product-ranking'
                 ' && scrapy crawl %s -a %s="%s" %s'
                 ' -a search_sort=%s -s LOG_FILE=%s -o %s &') % (
            REPO_BASE_PATH, site + '_products', arg_name, arg_value,
            options, "best_sellers", output_path + '_bs.log', data_bs_file
        )

        pbs = Popen(cmdbs, shell=True, stdout=PIPE, stderr=PIPE)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)

    # report progress and wait until the task is done
    report_progress_and_wait(output_path+'.jl', output_path+'.log', data_bs_file, metadata)
    # upload the files to SQS and S3
    data_key = put_file_into_s3(AMAZON_BUCKET_NAME, output_path+'.jl')
    logs_key = put_file_into_s3(AMAZON_BUCKET_NAME, output_path+'.log')

    if data_key and logs_key:
        dump_result_data_into_sqs(data_key, logs_key,
            server_name+OUTPUT_QUEUE_NAME, metadata)
    else:
        logger.error("Failed to load info to results sqs. Amazon keys "
                     "wasn't received")
    logger.info("Spider default output:\n%s%s",
                p.stderr.read(),
                p.stdout.read().strip())


def prepare_test_data():
    # only for local-filesystem tests!
    # prepare incoming tasks
    with open('/tmp/sqs_ranking_spiders_tasks', 'w') as fh:
        msg = {
            'task_id': 4444, 'site': 'walmart', 'searchterms_str': 'iphone',
            'server_name': 'test_server_name',
            # "url": "http://www.walmart.com/ip/42211446?productRedirect=true",
            'with_best_seller_ranking': True,
            'cmd_args':
                {
                    'quantity': 20,
                }
        }
        fh.write(json.dumps(msg, default=json_serializer))


if __name__ == '__main__':
    if 'test' in [a.lower().strip() for a in sys.argv]:
        TEST_MODE = True
        prepare_test_data()
        try:
            # local mode
            from sqs_ranking_spiders.fake_sqs_queue_class import SQS_Queue
        except ImportError:
            from repo.fake_sqs_queue_class import SQS_Queue
        logger.debug('TEST MODE ON')
        logger.debug('Faking the SQS_Queue class')
    execute_task_from_sqs()