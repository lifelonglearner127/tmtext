import os
import sys
import time
import json
import zipfile
import codecs
import csv
import unidecode
import string
import redis
import boto
import random
from boto.utils import get_instance_metadata
from boto.s3.key import Key
from collections import OrderedDict
import datetime
from threading import Thread
from multiprocessing.connection import Listener, AuthenticationError, Client
from subprocess import Popen, PIPE

# list of all available incoming SQS with tasks
OUTPUT_QUEUE_NAME = 'sqs_ranking_spiders_output'
PROGRESS_QUEUE_NAME = 'sqs_ranking_spiders_progress'  # progress reports
JOB_OUTPUT_PATH = '~/job_output'  # local dir
CWD = os.path.dirname(os.path.abspath(__file__))
path = os.path.expanduser('~/repo')
# for local mode
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
    from sqs_ranking_spiders import QUEUES_LIST
except ImportError:
    # we're in /home/spiders/repo
    from repo.remote_instance_starter import REPO_BASE_PATH, logging, \
        AMAZON_BUCKET_NAME, AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY
    from repo.remote_instance_starter import QUEUES_LIST
sys.path.insert(
    3, os.path.join(REPO_BASE_PATH, 'special_crawler', 'queue_handler'))
from sqs_connect import SQS_Queue
from cache_layer import REDIS_HOST, REDIS_PORT, INSTANCES_COUNTER_REDIS_KEY, \
    TASKS_COUNTER_REDIS_KEY, HANDLED_TASKS_SORTED_SET


TEST_MODE = False  # if we should perform local file tests

logger = logging.getLogger('main_log')

RANDOM_HASH = None
DATESTAMP = None
FOLDERS_PATH = None

CONVERT_TO_CSV = True

# Connect to S3
S3_CONN = boto.connect_s3(
    aws_access_key_id=AMAZON_ACCESS_KEY,
    aws_secret_access_key=AMAZON_SECRET_KEY,
    is_secure=False,  # uncomment if you are not using ssl
)
# Get current bucket
S3_BUCKET = S3_CONN.get_bucket(AMAZON_BUCKET_NAME, validate=False)

# settings
MAX_CONCURRENT_TASKS = 3  # tasks per instance, all with same git branch
MAX_TRIES_TO_GET_TASK = 50  # tries to get max tasks for same branch
LISTENER_ADDRESS = ('localhost', 9070)  # address to listen for signals
# SCRAPY_LOGS_DIR = ''  # where to put log files
# SCRAPY_DATA_DIR = ''  # where to put scraped data files
# S3_UPLOAD_DIR = ''  # folder path on the s3 server, where to save logs/data
STATUS_STARTED = 'opened'
STATUS_FINISHED = 'closed'
SIGNAL_SCRIPT_OPENED = 'script_opened'
SIGNAL_SCRIPT_CLOSED = 'script_closed'
SIGNAL_SPIDER_OPENED = 'spider_opened'
SIGNAL_SPIDER_CLOSED = 'spider_closed'

# required signals
REQUIRED_SIGNALS = [
    # [signal_name, wait_in_seconds]
    [SIGNAL_SCRIPT_OPENED, 2 * 60],  # wait for signal that script started
    [SIGNAL_SPIDER_OPENED, 1 * 60],
    [SIGNAL_SPIDER_CLOSED, 24 * 60 * 60],
    [SIGNAL_SCRIPT_CLOSED, 1 * 60]
]

# optional extension signals
EXTENSION_SIGNALS = {
    'cache_downloading': 30 * 60,  # cache load FROM s3
    'cache_uploading': 30 * 60  # cache load TO s3,
}


# custom exceptions
class FlowError(Exception):
    """base class for new custom exceptions"""
    pass


class ConnectError(FlowError):
    """failed to connect to scrapy process in allowed time"""
    pass


class FinishError(FlowError):
    """scrapy process didn't finished in allowed time"""
    pass


class SignalSentTwiceError(FlowError):
    """same signal came twice"""
    pass


class SignalTimeoutError(FlowError):
    """signal didn't finished in allowed time"""
    pass


def get_branch_for_task(task_data):
    return task_data.get('branch_name')


def switch_branch_if_required(metadata):
    branch_name = metadata.get('branch_name')
    if branch_name:
        logger.info("Checkout to branch %s", branch_name)
        cmd = 'git checkout -f {branch} && git pull origin {branch} && '\
              'git checkout master -- task_id_generator.py && '\
              'git checkout master -- remote_instance_starter.py && '\
              'git checkout master -- upload_logs_to_s3.py'
        cmd = cmd.format(branch=branch_name)
        logger.info("Run '%s'", cmd)
        os.system(cmd)


def update_handled_tasks_set(set_name, redis_db):
    """Will add new score:value pair to some redis sorted set.
    Score and value will be current time."""
    if redis_db:
        try:
            redis_db.zadd(set_name, time.time(), time.time())
        except Exception as e:
            logger.warning("Failed to add info to set '%s' with exception"
                           " '%s'", set_name, e)


def is_same_branch(b1, b2):
    return b1 == b2


def slugify(s):
    output = ''
    for symbol in s:
        if symbol.lower() not in string.lowercase and not \
                symbol.lower() in string.digits:
            output += '-'
        else:
            output += symbol
    output = output.replace(' ', '-')
    while '--' in output:
        # to avoid reserved double-minus chars
        output = output.replace('--', '-')
    return output


def connect_to_redis_database(redis_host, redis_port):
    if TEST_MODE:
        print 'Simulating connect to redis'
        return
    try:
        db = redis.StrictRedis(host=redis_host, port=redis_port)
    except Exception as e:
        logger.warning("Failed connect to redis database with exception %s", e)
        db = None
    return db


def increment_metric_counter(metric_name, redis_db):
    """This method will just increment reuired key in redis database
    if connecntion to the database exist."""
    if TEST_MODE:
        print 'Simulate redis incremet, key is %s' % metric_name
        return
    if redis_db:
        try:
            redis_db.incr(metric_name)
        except Exception as e:
            logger.warning("Failed to increment redis metric '%s' "
                           "with exception '%s'", metric_name, e)


def read_msg_from_sqs(queue_name_or_instance, timeout=None):
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
        message = sqs_queue.get(timeout)
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


def test_read_msg_from_fs(queue_name):
    global task_number
    try:
        task_number
    except NameError:
        task_number = -1
    task_number += 1
    fake_class = SQS_Queue(queue_name)
    with open('/tmp/%s' % queue_name, 'r') as fh:
        cur_line = 0
        while cur_line < task_number:
            fh.readline()
            cur_line += 1
        try:
            return json.loads(fh.readline()), fake_class
        except ValueError:
            return None


def set_global_variables_from_data_file():
    try:
        json_data = load_data_from_hash_datestamp_data()
        global RANDOM_HASH, DATESTAMP, FOLDERS_PATH
        RANDOM_HASH = json_data['random_hash']
        DATESTAMP = json_data['datestamp']
        FOLDERS_PATH = json_data['folders_path']
    except:
        logger.error("Required hash_datestamp_data wasn't created."
                     "Create it now.")
        generate_hash_datestamp_data()
        set_global_variables_from_data_file()


def _create_sqs_queue(queue_or_connection, queue_name, visib_timeout=30):
    if isinstance(queue_or_connection, SQS_Queue):
        queue_or_connection = queue_or_connection.conn
    queue_or_connection.create_queue(queue_name, visib_timeout)


def _get_server_ip():
    ip_fname = '/tmp/_server_ip'
    if os.path.exists(ip_fname):
        with open(ip_fname) as fh:
            return fh.read().strip()


def generate_msg(metadata, progress):
    _msg = {
        '_msg_id': metadata.get('task_id', metadata.get('task', None)),
        'utc_datetime': datetime.datetime.utcnow(),
        'progress': progress,
        'server_ip': _get_server_ip()
    }
    return _msg


def json_serializer(obj):
    """ JSON serializer for objects not serializable by default json code """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        serial = obj.isoformat()
        return serial


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


def test_write_msg_to_fs(queue_name_or_instance, msg):
    print 'Simulate msg to sqs: %s' % msg
    return
    # if not isinstance(msg, (str, unicode)):
    #     msg = json.dumps(msg, default=json_serializer)
    # if isinstance(queue_name_or_instance, (str, unicode)):
    #     sqs_queue = SQS_Queue(queue_name_or_instance)
    # else:
    #     sqs_queue = queue_name_or_instance
    # with open(
    #         test_get_fs_name_from_queue_name(queue_name_or_instance), 'a'
    # ) as fh:
    #     fh.write(msg+'\n')


def put_msg_to_sqs(queue_name_or_instance, msg):
    if TEST_MODE:
        test_write_msg_to_fs(queue_name_or_instance, msg)
    else:
        write_msg_to_sqs(queue_name_or_instance, msg)


def put_file_into_s3(bucket_name, fname,
                     amazon_public_key=AMAZON_ACCESS_KEY,
                     amazon_secret_key=AMAZON_SECRET_KEY,
                     compress=True):
    if TEST_MODE:
        print 'Simulate put file to s3, %s' % fname
        return True

    global S3_CONN, S3_BUCKET
    # Cut out file name
    filename = os.path.basename(fname)
    if compress:
        try:
            import zlib
            mode = zipfile.ZIP_DEFLATED
        except ImportError:
            mode = zipfile.ZIP_STORED
        archive_name = filename + '.zip'
        archive_path = fname + '.zip'
        zf = zipfile.ZipFile(archive_path, 'w', mode)
        try:
            zf.write(filename=fname, arcname=filename)
            logger.info("Adding %s to archive", filename)
        finally:
            zf.close()

        filename = archive_name
        fname = archive_path
        # folders = ("/" + datetime.datetime.utcnow().strftime('%Y/%m/%d')
        #            + "/" + archive_name)

    # Generate file path for S3
    # folders = ("/" + datetime.datetime.utcnow().strftime('%Y/%m/%d')
    #            + "/" + filename)
    global FOLDERS_PATH
    folders = (FOLDERS_PATH + filename)
    logger.info("Uploading %s to Amazon S3 bucket %s", filename, bucket_name)
    k = Key(S3_BUCKET)
    # Set path to file on S3
    k.key = folders
    try:
        # Upload file to S3
        k.set_contents_from_filename(fname)
        # Download file from S3
        # k.get_contents_to_filename('bar.csv')
        # key will be used to provide path at S3 for UI side
        return k
    except Exception:
        logger.warning("Failed to load files to S3. "
                       "Check file path and amazon keys/permissions.")


def convert_json_to_csv(filepath):
    json_filepath = filepath + '.jl'
    logger.info("Convert %s to .csv", json_filepath)
    field_names = set()
    items = []
    with codecs.open(json_filepath, "r", "utf-8") as jsonfile:
        for line in jsonfile:
            item = json.loads(line.strip())
            items.append(item)
            fields = [name for name, val in item.items()]
            field_names = field_names | set(fields)

    csv.register_dialect(
        'json',
        delimiter=',',
        doublequote=True,
        quoting=csv.QUOTE_ALL)

    csv_filepath = filepath + '.csv'

    with open(csv_filepath, "w") as csv_out_file:
        csv_out_file.write(codecs.BOM_UTF8)
        writer = csv.writer(csv_out_file, 'json')
        writer.writerow(list(field_names))
        for item in items:
            vals = []
            for name in field_names:
                val = item.get(name, '')
                if name == 'description':
                    val = val.replace("\n", '\\n')
                if type(val) == type(unicode("")):
                    val = val.encode('utf-8')
                vals.append(val)
            writer.writerow(vals)
    return csv_filepath


def dump_result_data_into_sqs(data_key, logs_key, csv_data_key,
                              queue_name, metadata):
    if TEST_MODE:
        print 'Simulate dump data into sqs'
        return
    global RANDOM_HASH, DATESTAMP, FOLDERS_PATH
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
        'server_ip': _get_server_ip()
    }
    if csv_data_key:
        msg['csv_data_key'] = csv_data_key.key
    logger.info("Provide result msg %s to queue '%s'", msg, queue_name)
    if TEST_MODE:
        test_write_msg_to_fs(queue_name, msg)
    else:
        write_msg_to_sqs(queue_name, msg)


def datetime_difference(d1, d2):
    res = d1 - d2
    return 86400 * res.days + res.seconds


def create_dir(p):
    try:
        os.makedirs(p)
    except OSError:  # no access to create folder
        p = os.path.expanduser('~/' + os.path.basename(p))
        os.makedirs(p)
    return p


def check_required_folders():
    # create logs & data folders if needed
    global SCRAPY_LOGS_DIR, SCRAPY_DATA_DIR
    if not os.path.exists(SCRAPY_LOGS_DIR):
        SCRAPY_LOGS_DIR = create_dir(SCRAPY_LOGS_DIR)
    if not os.path.exists(SCRAPY_DATA_DIR):
        SCRAPY_DATA_DIR = create_dir(SCRAPY_DATA_DIR)


class ScrapyTask(object):

    def __init__(self, task_data, listener):
        self.task_data = task_data
        self.listener = listener  # common listener to accept connections
        self.process = None  # instance of Popen for scrapy
        self.process_bsr = None  # process for best seller ranking
        self.conn = None  # individual connection for each task
        self.return_code = None  # result of scrapy run
        self.finished = False  # is task finished
        self.finished_ok = False  # is task finished good
        self._stop_signal = False  # to break loop if needed
        self.start_date = None
        self.finish_date = None
        self.required_signals = self._parse_signal_settings(REQUIRED_SIGNALS)
        self._add_extensions()
        # self.extension_signals=self._parse_signal_settings(EXTENSION_SIGNALS)
        self.extension_signals = []
        self.current_signal = None  # tuple of key, value for current signal
        self.required_signals_done = OrderedDict()
        self.require_signal_failed = None  # signal, where failed
        self.items_scraped = 0
        self.spider_errors = 0

    def get_unique_name(self):
        # convert task data into unique name
        global RANDOM_HASH, DATESTAMP
        searchterms_str = self.task_data.get('searchterms_str', None)
        site = self.task_data['site']
        if isinstance(searchterms_str, (str, unicode)):
            searchterms_str = searchterms_str.decode('utf8')
        # job_name = datetime.datetime.utcnow().strftime('%d-%m-%Y')
        server_name = self.task_data['server_name']
        server_name = slugify(server_name)
        job_name = DATESTAMP + '____' + RANDOM_HASH + '____' + server_name+'--'
        task_id = self.task_data.get('task_id',
                                     self.task_data.get('task', None))
        if task_id:
            job_name += str(task_id)
        if searchterms_str:
            additional_part = unidecode.unidecode(
                searchterms_str).replace(
                    ' ', '-').replace('/', '').replace('\\', '')
        else:
            # maybe should be changed to product_url
            additional_part = 'single-product-url-request'
        job_name += '____' + additional_part + '____' + site
        # job_name += '____' + site + '____' + get_random_hash()
        return job_name

    def _parse_signal_settings(self, signal_settings):
        d = OrderedDict()
        wait = 'wait'
        # dict with signal name as key and dict as value
        for s in signal_settings:
            d[s[0]] = {wait: s[1], STATUS_STARTED: None, STATUS_FINISHED: None}
        return d

    def _add_extensions(self):
        ext_cache_down = 'cache_downloading'
        ext_cache_up = 'cache_uploading'
        cmd_args = self.task_data.get('cmd_args', {})
        if cmd_args.get('save_s3_cache', False):
            self.required_signals[SIGNAL_SPIDER_OPENED]['wait'] += \
                EXTENSION_SIGNALS[ext_cache_up]
        if cmd_args.get('load_s3_cache'):
            self.required_signals[SIGNAL_SCRIPT_CLOSED]['wait'] += \
                EXTENSION_SIGNALS[ext_cache_down]

    def get_total_wait_time(self):
        return sum([r['wait'] for r in self.required_signals.itervalues()])

    def _dispose(self):
        """kill process if running, drop connection if opened"""
        if self.process_bsr and self.process_bsr.poll() is None:
            try:
                os.killpg(os.getpgid(self.process_bsr.pid), 9)
            except OSError as e:
                logger.error('OSError: %s', e)
        if self.process and self.process.poll() is None:
            try:
                os.killpg(os.getpgid(self.process.pid), 9)
            except OSError as e:
                logger.error('OSError: %s', e)
        if self.conn:
            self.conn.close()

    def _get_next_signal(self, date_time):
        """get and remove next signal from the main queue"""
        try:
            k = self.required_signals.iterkeys().next()
        except StopIteration:
            return None
        v = self.required_signals.pop(k)
        v[STATUS_STARTED] = date_time
        return k, v

    def _get_signal_by_data(self, data):
        """
        return current main signal or
        one of the extension signals, for which data is sent
        """
        if data['name'] == 'item_scraped':
            self.items_scraped += 1
            return None
        elif data['name'] == 'spider_error':
            self.spider_errors += 1
            return None
        is_ext = False
        if self.current_signal and self.current_signal[0] == data['name']:
            signal = self.current_signal
        else:
            is_ext = True
            signal = (data['name'], self.extension_signals.get(data['name']))
        return is_ext, signal

    def _process_signal_data(self, signal, data, date_time, is_ext):
        new_status = data['status']  # opened/closed
        if signal[1][new_status]:  # if value is already set
            res = False
        else:
            res = True
        self._signal_succeeded(signal, date_time, is_ext)
        return res

    def _signal_failed(self, signal, date_time, ex):
        """
        set signal as failed
        :param signal: signal itself
        :param date_time: when signal failed
        :param ex: exception that caused fail
        """
        signal[1]['failed'] = True
        signal[1][STATUS_FINISHED] = date_time
        signal[1]['reason'] = ex.__class__.__name__

        logger.error('Task #%s failed. %s',
                     self.task_data.get('task_id', 0), signal)

        self.require_signal_failed = signal

        _msg = generate_msg(self.task_data, 'failed')
        put_msg_to_sqs(self.task_data['server_name']+PROGRESS_QUEUE_NAME, _msg)

    def _signal_succeeded(self, signal, date_time, is_ext):
        """set finish time for signal and save in finished signals if needed"""
        signal[1][STATUS_FINISHED] = date_time
        if not is_ext:
            self.required_signals_done[signal[0]] = signal[1]

    def _finish(self):
        # runs for both successfully or failed finish
        # upload logs/data to s3, etc
        self._stop_signal = True
        self._dispose()
        output_path = self.get_output_path()
        if self.process_bsr:
            temp_file = output_path + 'temp_file.jl'
            os.system('%s/product-ranking/add-best-seller.py %s %s > %s' % (
                REPO_BASE_PATH, output_path+'.jl',
                output_path+'_bs.jl', temp_file))
            with open(temp_file) as bs_file:
                lines = bs_file.readlines()
                with open(output_path+'.jl', 'w') as main_file:
                    main_file.writelines(lines)
            os.remove(temp_file)
        try:
            data_key = put_file_into_s3(
                AMAZON_BUCKET_NAME, output_path+'.jl')
        except Exception:
            data_key = None
        logs_key = put_file_into_s3(
            AMAZON_BUCKET_NAME, output_path+'.log')

        csv_data_key = None
        global CONVERT_TO_CSV
        if CONVERT_TO_CSV:
            try:
                csv_filepath = convert_json_to_csv(output_path)
                csv_data_key = put_file_into_s3(
                    AMAZON_BUCKET_NAME, csv_filepath)
            except Exception as e:
                logger.warning(
                    "CSV converter failed with exception: %s", str(e))

        if data_key and logs_key:
            dump_result_data_into_sqs(
                data_key, logs_key, csv_data_key,
                self.task_data['server_name']+OUTPUT_QUEUE_NAME, self.task_data)
        else:
            logger.error("Failed to load info to results sqs. Amazon keys "
                         "wasn't received")

        logger.info("Spider default output:\n%s%s",
                    self.process.stderr.read(),
                    self.process.stdout.read().strip())
        logger.info('Finish task #%s.', self.task_data.get('task_id', 0))
        self.finished = True
        self.finish_date = datetime.datetime.utcnow()

    def _success_finish(self):
        # run this task after scrapy process successfully finished
        logger.info('Success finish task #%s', self.task_data.get('task_id', 0))
        self.finished_ok = True

    def get_output_path(self):
        output_path = '%s/%s' % (
            os.path.expanduser(JOB_OUTPUT_PATH), self.get_unique_name())
        return output_path

    def _parse_task_and_get_cmd(self, is_bsr=False):
        """get search string from the task"""
        searchterms_str = self.task_data.get('searchterms_str', None)
        url = self.task_data.get('url', None)
        urls = self.task_data.get('urls', None)
        site = self.task_data['site']
        cmd_line_args = self.task_data.get('cmd_args', {})
        output_path = self.get_output_path()
        options = ' '
        arg_name = arg_value = None
        for key, value in cmd_line_args.items():
            options += ' -a %s=%s' % (key, value)
        if searchterms_str:
            arg_name = 'searchterms_str'
            arg_value = searchterms_str
        if url:
            arg_name = 'product_url'
            arg_value = url
        if urls:
            arg_name = 'products_url'
            arg_value = urls
        if not is_bsr:
            cmd = ('cd %s/product-ranking'
                   ' && scrapy crawl %s -a %s="%s" %s'
                   ' -s LOG_FILE=%s -s WITH_SIGNALS=1 -o %s &') % (
                REPO_BASE_PATH, site + '_products', arg_name, arg_value,
                options, output_path+'.log', output_path+'.jl'
            )
        else:
            cmd = ('cd %s/product-ranking'
                   ' && scrapy crawl %s -a %s="%s" %s'
                   ' -a search_sort=%s -s LOG_FILE=%s -o %s &') % (
                REPO_BASE_PATH, site+'_products', arg_name, arg_value,
                options, "best_sellers", output_path+'_bs.log',
                output_path+'_bs.jl')
        return cmd

    def _start_scrapy_process(self):
        cmd = self._parse_task_and_get_cmd()
        self.process = Popen(cmd, shell=True, stdout=PIPE,
                             stderr=PIPE, preexec_fn=os.setsid)
        if self.task_data.get('with_best_seller_ranking', False):
            cmd = self._parse_task_and_get_cmd(True)
            self.process_bsr = Popen(cmd, shell=True, stdout=PIPE,
                                     stderr=PIPE, preexec_fn=os.setsid)
        logger.info('Scrapy process started for task #%s',
                    self.task_data.get('task_id', 0))

    def _establish_connection(self):
        self.conn = self.listener.accept()

    def _dummy_client(self):
        """used to interrupt waiting for the connection from client"""
        logger.warning('Running dummy client for task #%s',
                       self.task_data.get('task_id', 0))
        Client(LISTENER_ADDRESS).close()

    def _try_connect(self, wait):
        """
        tries to accept new client in the given time
        checks status of connection each second
        if no connection was done in the given time, simulate it and close
        :param wait: time in seconds to wait
        :return: success of connection
        """
        t = Thread(target=self._establish_connection)
        counter = 0
        t.start()
        while not self._stop_signal and counter < wait:
            time.sleep(1)
            counter += 1
            if self.conn:  # connected successfully
                return True
        # if connection failed
        self._dummy_client()
        if self.conn:
            self.conn.close()
            self.conn = None
        return False

    def _try_finish(self, wait):
        """
        runs as last signal, checks if process finished and  has return code
        """
        counter = 0
        while not self._stop_signal and counter < wait:
            time.sleep(1)
            counter += 1
            res = self.process.poll()
            res_bsr = self.process_bsr.poll() if self.process_bsr else True
            if res is not None and res_bsr is not None:
                logger.info('Finish try succeeded')
                self.return_code = res
                time.sleep(5)
                return True
        else:
            logger.warning('Killing scrapy process manually, task id is %s',
                           self.task_data.get('task_id', 0))
        # kill process group, if not finished in allowed time
        if self.process_bsr:
            try:
                self.process_bsr.terminate()
            except OSError as e:
                logger.error('Kill process bsr error in task #%s: %s',
                             self.task_data.get('task_id', 0), e)
        try:
            self.process.terminate()
        except OSError as e:
            logger.error('Kill process error in task #%s: %s',
                         self.task_data.get('task_id', 0), e)
        return False

    def _run_signal(self, next_signal, step_time_start):
        max_step_time = next_signal[1]['wait']
        if next_signal[0] == SIGNAL_SCRIPT_OPENED:  # first signal
            res = self._try_connect(max_step_time)
            if not res:
                raise ConnectError
            self._signal_succeeded(next_signal,
                                   datetime.datetime.utcnow(), False)
            msg = generate_msg(self.task_data, 0)
            put_msg_to_sqs(
                self.task_data['server_name']+PROGRESS_QUEUE_NAME, msg)
            return True
        elif next_signal[0] == SIGNAL_SCRIPT_CLOSED:  # last signal
            res = self._try_finish(max_step_time)
            if not res:
                raise FinishError
            self._signal_succeeded(next_signal,
                                   datetime.datetime.utcnow(), False)
            msg = generate_msg(self.task_data, 'finished')
            put_msg_to_sqs(
                self.task_data['server_name']+PROGRESS_QUEUE_NAME, msg)
            return True
        step_time_passed = 0
        while not self._stop_signal and step_time_passed < max_step_time:
            has_data = self.conn.poll(max_step_time - step_time_passed)
            sub_step_time = datetime.datetime.utcnow()
            step_time_passed = datetime_difference(sub_step_time,
                                                   step_time_start)
            if has_data:
                try:
                    data = self.conn.recv()
                except EOFError as ex:
                    logger.error('eof error: %s', ex)
                    self._signal_failed(next_signal,
                                        datetime.datetime.utcnow(), False)
                    self._finish()
                    return
                s_d = self._get_signal_by_data(data)
                if not s_d:  # item_scraped or spider_error signals
                    continue
                is_ext, signal = s_d
                res = self._process_signal_data(signal, data,
                                                sub_step_time, is_ext)
                if not res:
                    raise SignalSentTwiceError
                if not is_ext:
                    return True
        else:
            raise SignalTimeoutError

    def _listen(self):
        start_time = datetime.datetime.utcnow()
        while not self._stop_signal:  # run through all signals
            step_time_start = datetime.datetime.utcnow()
            next_signal = self._get_next_signal(step_time_start)
            if not next_signal:
                # all steps are finished
                self._success_finish()
                break
            self.current_signal = next_signal
            try:
                self._run_signal(next_signal, step_time_start)
            except FlowError as ex:
                self._signal_failed(next_signal, datetime.datetime.utcnow(), ex)
                break
        finish_time = datetime.datetime.utcnow()
        self.finish_date = datetime_difference(finish_time, start_time)
        self._finish()

    def start(self):
        """start the scrapy process and wait for first signal"""
        start_time = datetime.datetime.utcnow()
        self.start_date = start_time
        self._start_scrapy_process()
        first_signal = self._get_next_signal(start_time)
        try:
            self._run_signal(first_signal, start_time)
            return True
        except FlowError as ex:
            self._signal_failed(first_signal, datetime.datetime.utcnow(), ex)
            self._finish()
            return False

    def run(self):
        t = Thread(target=self._listen)
        t.start()

    def stop(self):
        """send stop signal, doesn't guaranties to stop immediately"""
        self._stop_signal = True

    def is_finished(self):
        return self.finished

    def is_finised_ok(self):
        return self.finished_ok

    def report(self):
        """returns string with the task running stats"""
        s = 'Task #%s, command %r.\n' % (self.task_data.get('task_id', 0),
                                         self._parse_task_and_get_cmd())
        if self.start_date:
            s += 'Task started at %s.\n' % str(self.start_date.time())
        if self.finish_date:
            s += 'Finished %s at %s, duration %s.\n' % (
                'successfully' if self.finished_ok else 'with error',
                str(self.finish_date.time()),
                str(self.finish_date - self.start_date))
        if self.require_signal_failed:
            sig = self.require_signal_failed
            s += 'Failed signal is: %r, reason %r, started at %s, ' \
                 'finished at %s, duration %s.\n' % (
                     sig[0], sig[1]['reason'],
                     str(sig[1][STATUS_STARTED].time()),
                     str(sig[1][STATUS_FINISHED].time()),
                     str(sig[1][STATUS_FINISHED] - sig[1][STATUS_STARTED]))
        s += 'Items scrapped: %s, spider errors: %s.\n' % (
            self.items_scraped, self.spider_errors)
        if self.required_signals_done:
            s += 'Succeeded required signals:\n'
            for sig in self.required_signals_done.iteritems():
                s += '\t%r, started at %s, finished at %s, duration %s;\n' % (
                    sig[0], str(sig[1][STATUS_STARTED].time()),
                    str(sig[1][STATUS_FINISHED].time()),
                    str(sig[1][STATUS_FINISHED] - sig[1][STATUS_STARTED]))
        else:
            s += 'None of the signals are finished.\n'
        return s

    def send_current_status_to_sqs(self):
        msg = generate_msg(self.task_data, self.items_scraped)
        put_msg_to_sqs(
            self.task_data['server_name']+PROGRESS_QUEUE_NAME, msg)


def main():
    if not TEST_MODE:
        instance_meta = get_instance_metadata()
        inst_ip = instance_meta.get('public-ipv4')
        inst_id = instance_meta.get('instance-id')
        logger.info("IMPORTANT: ip: %s, instance id: %s", inst_ip, inst_id)
    # increment quantity of instances spinned up during the day.
    redis_db = connect_to_redis_database(redis_host=REDIS_HOST,
                                         redis_port=REDIS_PORT)
    increment_metric_counter(INSTANCES_COUNTER_REDIS_KEY, redis_db)
    set_global_variables_from_data_file()

    max_tries = MAX_TRIES_TO_GET_TASK
    tasks_taken = []
    branch = None

    try:
        listener = Listener(LISTENER_ADDRESS)
    except AuthenticationError:
        listener = None

    if not listener:
        logger.error('Socket auth failed!')
        return

    # get tasks
    while len(tasks_taken) < MAX_CONCURRENT_TASKS and max_tries:
        TASK_QUEUE_NAME = random.choice([q for q in QUEUES_LIST.values()])
        if TEST_MODE:
            msg = test_read_msg_from_fs(TASK_QUEUE_NAME)
        else:
            # set short wait time, so if task has different branch,
            # this task must appear on another instance asap
            msg = read_msg_from_sqs(TASK_QUEUE_NAME, max_tries)
        if msg is None:
            time.sleep(3)
            continue
        logger.info('Trying to get task from %s, try #%s',
                    TASK_QUEUE_NAME, MAX_TRIES_TO_GET_TASK - max_tries)
        max_tries -= 1
        task_data, queue = msg
        # get branch from first task
        if not tasks_taken:
            branch = get_branch_for_task(task_data)
        elif not is_same_branch(get_branch_for_task(task_data), branch):
            queue.reset_message()
            # tasks have different branches, skip
            continue
        queue.task_done()
        logger.info("Task message was successfully received and "
                    "removed form queue.")
        logger.info("Whole tasks msg: %s", str(task_data))
        increment_metric_counter(TASKS_COUNTER_REDIS_KEY, redis_db)
        update_handled_tasks_set(HANDLED_TASKS_SORTED_SET, redis_db)
        task = ScrapyTask(task_data, listener)
        tasks_taken.append(task)

    # prepare to execute tasks
    switch_branch_if_required(tasks_taken[0].task_data)
    if not os.path.exists(os.path.expanduser(JOB_OUTPUT_PATH)):
        logger.debug("Create job output dir %s",
                     os.path.expanduser(JOB_OUTPUT_PATH))
        os.makedirs(os.path.expanduser(JOB_OUTPUT_PATH))

    max_wait_time = max([t.get_total_wait_time() for t in tasks_taken])
    # start and run tasks
    logger.info('Starting to execute tasks, total %s.', len(tasks_taken))
    for task in tasks_taken:
        if task.start():
            task.run()
            logger.info('Task #%s (%r) started successfully.',
                        task.task_data.get('task_id', 0),
                        task.get_output_path())
        else:
            logger.error('Task #%s (%r) failed to start.',
                         task.task_data.get('task_id', 0),
                         task.get_output_path())

    def is_all_tasks_finished(tasks):
        return all([_.is_finished() for _ in tasks])

    logger.info('Max allowed running time is %ss', max_wait_time)
    step_time = 15
    cur_wait_time = 0
    try:
        while cur_wait_time < max_wait_time:
            if is_all_tasks_finished(tasks_taken):
                logger.info('All tasks finished.')
                break
            # update sqs with running statuses
            [t.send_current_status_to_sqs()
             for t in tasks_taken
             if not t.is_finished()]
            cur_wait_time += step_time
            time.sleep(step_time)
        else:
            logger.error('Some of the tasks not finished in allowed time.')
    except KeyboardInterrupt:
        [t.stop() for t in tasks_taken]
        raise Exception
    listener.close()
    for task in tasks_taken:
        logger.info(task.report())

    # write finish marker
    logger.info('Scrapy daemon finished.')


def prepare_test_data():
    # only for local-filesystem tests!
    # prepare incoming tasks
    tasks = [dict(
        task_id=4443, site='walmart', searchterms_str='iphone',
        server_name='test_server_name', with_best_seller_ranking=True,
        cmd_args={'quantity': 50}
    ), dict(
        task_id=4444, site='amazon', searchterms_str='iphone',
        server_name='test_server_name', with_best_seller_ranking=True,
        cmd_args={'quantity': 1}
    ), dict(
        task_id=4445, site='target', searchterms_str='iphone',
        server_name='test_server_name', with_best_seller_ranking=True,
        cmd_args={'quantity': 50}
    )]
    files = [open('/tmp/sqs_ranking_spiders_tasks_tests', 'w'),
             open('/tmp/sqs_ranking_spiders_tasks_dev', 'w'),
             open('/tmp/sqs_ranking_spiders_tasks', 'w')]
    for fh in files:
        for msg in tasks:
            fh.write(json.dumps(msg, default=json_serializer)+'\n')
        fh.close()


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

    try:
        main()
    except Exception as e:
        logger.error(e)
        logger.error('Finished with error.')
        try:
            os.killpg(os.getpgid(os.getpid()), 9)
        except:
            pass