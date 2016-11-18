import os
import sys
import time
import json
import random
import zipfile
import unidecode
import string
import redis
import boto
import requests
from re import sub
from boto.utils import get_instance_metadata
from boto.s3.key import Key
from collections import OrderedDict
import datetime
from threading import Thread
from multiprocessing.connection import Listener, AuthenticationError, Client
from subprocess import Popen, PIPE, check_output, CalledProcessError, STDOUT


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
sys.path.insert(2, os.path.join(CWD, '..', '..', 'product-ranking'))

# for servers path
sys.path.insert(1, os.path.join(path, '..'))
sys.path.insert(2, os.path.join(path, '..', '..', 'special_crawler',
                                'queue_handler'))
sys.path.insert(3, os.path.join(path, 'tmtext', 'product-ranking'))


push_simmetrica_event = None
try:
    from monitoring import push_simmetrica_event
except ImportError:
    try:
        from spiders import push_simmetrica_event
    except ImportError:
        try:
            from product_ranking.spiders import push_simmetrica_event
        except ImportError:
            #print 'ERROR: CAN NOT IMPORT MONITORING PACKAGE!'
            pass


from sqs_ranking_spiders.task_id_generator import \
    generate_hash_datestamp_data, load_data_from_hash_datestamp_data
try:
    # try local mode (we're in the deploy dir)
    from sqs_ranking_spiders.remote_instance_starter import REPO_BASE_PATH,\
        logging, AMAZON_BUCKET_NAME
    from sqs_ranking_spiders import QUEUES_LIST
except ImportError:
    # we're in /home/spiders/repo
    from repo.remote_instance_starter import REPO_BASE_PATH, logging, \
        AMAZON_BUCKET_NAME
    from repo.remote_instance_starter import QUEUES_LIST
from product_ranking import statistics
sys.path.insert(
    3, os.path.join(REPO_BASE_PATH, 'deploy', 'sqs_ranking_spiders'))
from sqs_queue import SQS_Queue
from libs import convert_json_to_csv
from cache_layer import REDIS_HOST, REDIS_PORT, INSTANCES_COUNTER_REDIS_KEY, \
    JOBS_STATS_REDIS_KEY, JOBS_COUNTER_REDIS_KEY


TEST_MODE = False  # if we should perform local file tests

logger = logging.getLogger('main_log')

RANDOM_HASH = None
DATESTAMP = None
FOLDERS_PATH = None

CONVERT_TO_CSV = True

# Connect to S3
S3_CONN = boto.connect_s3(is_secure=False)
# uncomment if you are not using ssl

# Get current bucket
S3_BUCKET = S3_CONN.get_bucket(AMAZON_BUCKET_NAME, validate=False)

# settings
MAX_CONCURRENT_TASKS = 16  # tasks per instance, all with same git branch
MAX_TRIES_TO_GET_TASK = 100  # tries to get max tasks for same branch
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

# cache settings
CACHE_HOST = 'http://sqs-metrics.contentanalyticsinc.com/'
CACHE_URL_GET = 'get_cache'  # url to retrieve task cache from
CACHE_URL_SAVE = 'save_cache'  # to save cached result to
CACHE_URL_STATS = 'complete_task'  # to have some stats about completed tasks
CACHE_URL_FAIL = 'fail_task'  # to manage broken tasks
CACHE_AUTH = ('admin', 'SD*/#n\%4c')
CACHE_TIMEOUT = 15  # 15 seconds request timeout
# key in task data to not retrieve cached result
# if True, task will be executed even if there is result for it in cache
CACHE_GET_IGNORE_KEY = 'sqs_cache_get_ignore'
# key in task data to not save cached result
# if True, result will not be saved to cache
CACHE_SAVE_IGNORE_KEY = 'sqs_cache_save_ignore'

# File with required parameters for restarting scrapy daemon.
OPTION_FILE_FOR_RESTART = '/tmp/scrapy_daemon_option_file.json'
# Allow to restart scrapy daemon
ENABLE_TO_RESTART_DAEMON = True


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


class GlobalSettingsFromRedis(object):
    """settings cache"""

    __settings = None

    @classmethod
    def get_global_settings_from_sqs_cache(cls):
        if cls.__settings is None:
            try:
                from cache_layer.cache_service import SqsCache
                sqs = SqsCache()
                logger.info('Getting global settings from redis cache.')
                cls.__settings = sqs.get_settings()
            except Exception as e:
                cls.__settings = {}
                logger.error(
                    'Error while get global settings from redis cache.'
                    ' ERROR: %s', str(e))
        return cls.__settings

    def get(self, key, default=None):
        return self.get_global_settings_from_sqs_cache().get(key, default)
global_settings_from_redis = GlobalSettingsFromRedis()


def get_actual_branch_from_cache():
    logger.info('Get default branch from redis cache.')
    branch = global_settings_from_redis.get('remote_instance_branch',
                                            'sc_production')
    logger.info('Branch is %s', branch)
    return branch or 'sc_production'


def switch_branch_if_required(metadata):
    default_branch = get_actual_branch_from_cache()
    branch_name = metadata.get('branch_name', default_branch)
    if branch_name:
        logger.info("Checkout to branch %s", branch_name)
        cmd = ('git checkout -f {branch} && git pull origin {branch} && '
               'git checkout {default_branch} -- task_id_generator.py && '
               'git checkout {default_branch} -- remote_instance_starter.py &&'
               ' git checkout {default_branch} -- upload_logs_to_s3.py')
        cmd = cmd.format(branch=branch_name, default_branch=default_branch)
        logger.info("Run '%s'", cmd)
        os.system(cmd)


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


def connect_to_redis_database(redis_host, redis_port, timeout=10):
    if TEST_MODE:
        print 'Simulating connect to redis'
        return
    try:
        db = redis.StrictRedis(host=redis_host, port=redis_port,
                               socket_timeout=timeout)
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


def read_msg_from_sqs(queue_name_or_instance, timeout=None, attributes=None):
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
        message = sqs_queue.get(timeout, attributes)
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
        # add attributes data to message, like date when message was sent
        message['attributes'] = sqs_queue.get_attributes()
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
        'server_ip': _get_server_ip(),
        'searchterms_str': metadata.get('searchterms_str', None),
        'site': metadata.get('site', None),
        'server_name': metadata.get('server_name', None),
        'url': metadata.get('url', None),
        'urls': metadata.get('urls', None),
        'statistics': statistics.report_statistics()
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


def compress_multiple_files(output_fname, *filenames):
    """ Creates a single ZIP archive with the given files in it """
    try:
        import zlib
        mode = zipfile.ZIP_DEFLATED
    except ImportError:
        mode = zipfile.ZIP_STORED
    zf = zipfile.ZipFile(output_fname, 'a', mode, allowZip64=True)
    for filename in filenames:
        zf.write(filename=filename, arcname=os.path.basename(filename))
    zf.close()


def put_file_into_s3(bucket_name, fname, compress=True,
                     is_add_file_time=False):
    if TEST_MODE:
        print 'Simulate put file to s3, %s' % fname
        return True

    if not os.path.exists(fname):
        logger.warning('File to upload doesnt exits: %r, aborting.', fname)
        return
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
        zf = zipfile.ZipFile(archive_path, 'w', mode, allowZip64=True)
        try:
            zf.write(filename=fname, arcname=filename)
            logger.info("Adding %s to archive", filename)
        except Exception as ex:
            logger.error('Zipping Error')
            logger.exception(ex)
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
    # Add file creation time to metadata
    if is_add_file_time:
        k.set_metadata('creation_time', get_file_cm_time(filename))
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


def dump_cached_data_into_sqs(cached_key, queue_name, metadata):
    instance_log_filename = DATESTAMP + '____' + RANDOM_HASH + '____' + \
        'remote_instance_starter2.log'
    s3_key_instance_starter_logs = (FOLDERS_PATH + instance_log_filename)
    msg = {
        '_msg_id': metadata.get('task_id', metadata.get('task', None)),
        'type': 'ranking_spiders',
        's3_key_data': cached_key + '.jl.zip',
        's3_key_logs': cached_key + '.log.zip',
        'bucket_name': AMAZON_BUCKET_NAME,
        'utc_datetime': datetime.datetime.utcnow(),
        's3_key_instance_starter_logs': s3_key_instance_starter_logs,
        'server_ip': _get_server_ip()
    }
    if CONVERT_TO_CSV:
        msg['csv_data_key'] = cached_key + '.csv.zip'
    logger.info('Sending cached response to queue %s: %s', queue_name, msg)
    if TEST_MODE:
        test_write_msg_to_fs(queue_name, msg)
    else:
        write_msg_to_sqs(queue_name, msg)


def datetime_difference(d1, d2):
    """helper func to get difference between two dates in seconds"""
    res = d1 - d2
    return 86400 * res.days + res.seconds


class ScrapyTask(object):
    """
    class to control flow of the scrapy process with given task from SQS
    if task wasn't finished in allowed time, it will terminate
    """
    def __init__(self, queue, task_data, listener):
        """
        :param queue: SQS queue instance
        :param task_data: message with task data, taken from the queue
        :param listener: multiprocessing listener to establish connection
                         with the scrapy process
        """
        self.queue = queue
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
            try:
                searchterms_str = searchterms_str.decode('utf8')
            except UnicodeEncodeError:  # special chars may break
                pass
        server_name = self.task_data['server_name']
        server_name = slugify(server_name)
        job_name = DATESTAMP + '____' + RANDOM_HASH + '____' + server_name+'--'
        task_id = self.task_data.get('task_id',
                                     self.task_data.get('task', None))
        if task_id:
            job_name += str(task_id)
        if searchterms_str:
            additional_part = unidecode.unidecode(
                searchterms_str.replace("'", '')).replace(
                    ' ', '-').replace('/', '').replace('\\', '')
        else:
            # maybe should be changed to product_url
            additional_part = 'single-product-url-request'
        job_name += '____' + additional_part + '____' + site
        job_name = sub("\(|\)|&|;|'", "", job_name)
        # truncate resulting string as file name limitation is 256 characters
        return job_name[:200]

    def _parse_signal_settings(self, signal_settings):
        """
        calculate running time for the scrapy process
        based on the signals settings
        """
        d = OrderedDict()
        wait = 'wait'
        # dict with signal name as key and dict as value
        for s in signal_settings:
            d[s[0]] = {wait: s[1], STATUS_STARTED: None, STATUS_FINISHED: None}
        return d

    def _add_extensions(self):
        """
        add time limit to run scrapy process, based on the parameters of task
        currently supports cache downloading/uploading
        """
        ext_cache_down = 'cache_downloading'
        ext_cache_up = 'cache_uploading'
        cmd_args = self.task_data.get('cmd_args', {})
        if not isinstance(cmd_args, dict):
            cmd_args = {}
        if cmd_args.get('save_raw_pages', False):
            self.required_signals[SIGNAL_SPIDER_OPENED]['wait'] += \
                EXTENSION_SIGNALS[ext_cache_up]
        if cmd_args.get('load_raw_pages'):
            self.required_signals[SIGNAL_SCRIPT_CLOSED]['wait'] += \
                EXTENSION_SIGNALS[ext_cache_down]

    def get_total_wait_time(self):
        """
        get max wait time for scrapy process in seconds
        """
        s = sum([r['wait'] for r in self.required_signals.itervalues()])
        if self.current_signal:
            s += self.current_signal[1]['wait']
        return s

    def _dispose(self):
        """
        used to terminate scrapy process, called from finish method
        kill process if running, drop connection if opened
        """
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
        one of the extension signals, for which data is sent,
        depending on the data, received from the scrapy process
        """
        if data['name'] == 'item_scraped':
            self.items_scraped += 1
            return None
        elif data['name'] == 'item_dropped':
            # items dropped - most likely because of "subitems" mode,
            # so calculate the number of really scraped items
            if random.randint(0, 30) == 0:  # do not overload server's filesystem
                self._update_items_scraped()
            return
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
        """
        set signal as finished, collect its duration
        """
        new_status = data['status']  # opened/closed
        if signal[1][new_status]:  # if value is already set
            res = False
        else:
            res = True
        self._signal_succeeded(signal, date_time, is_ext)
        return res

    def _signal_failed(self, signal, date_time, ex):
        """
        set signal as failed, when it takes more then allowed time
        :param signal: signal itself
        :param date_time: when signal failed
        :param ex: exception that caused fail, derived from the FlowError
        """
        signal[1]['failed'] = True
        signal[1][STATUS_FINISHED] = date_time
        signal[1]['reason'] = ex.__class__.__name__

        logger.error('Task #%s failed. %s',
                     self.task_data.get('task_id', 0), signal)

        self.require_signal_failed = signal
        self.send_current_status_to_sqs('failed')

    def _signal_succeeded(self, signal, date_time, is_ext):
        """set finish time for signal and save in finished signals if needed"""
        signal[1][STATUS_FINISHED] = date_time
        if not is_ext:
            self.required_signals_done[signal[0]] = signal[1]

    def _get_daemon_logs_files(self):
        """ Returns logs from the /tmp/ dir """
        for fname in os.listdir('/tmp/'):
            fname = os.path.join('/tmp/', fname)
            if fname.lower().endswith('.log'):
                yield fname

    def _zip_daemon_logs(self, output_fname='/tmp/daemon_logs.zip'):
        """
        zips all log giles, found in the /tmp dir to the output_fname
        """
        log_files = list(self._get_daemon_logs_files())
        if os.path.exists(output_fname):
            os.unlink(output_fname)
        compress_multiple_files(output_fname, *log_files)
        return output_fname

    def _finish(self):
        """
        called after scrapy process finished, or failed for some reason
        sends logs and data files to amazon
        """
        self._stop_signal = True
        self._dispose()

        output_path = self.get_output_path()
        if self.process_bsr and self.finished_ok:
            logger.info('Collecting best sellers data...')
            temp_file = output_path + 'temp_file.jl'
            cmd = '%s/product-ranking/add-best-seller.py %s %s > %s' % (
                REPO_BASE_PATH, output_path+'.jl',
                output_path+'_bs.jl', temp_file)
            try:  # if best seller failed, download data without bsr column
                output = check_output(cmd, shell=True, stderr=STDOUT)
                logger.info('BSR script output: %s', output)
                with open(temp_file) as bs_file:
                    lines = bs_file.readlines()
                    with open(output_path+'.jl', 'w') as main_file:
                        main_file.writelines(lines)
                os.remove(temp_file)
            except CalledProcessError as ex:
                logger.error('Best seller conversion error')
                logger.error(ex.output)
                logger.exception(ex)
        try:
            data_key = put_file_into_s3(
                AMAZON_BUCKET_NAME, output_path+'.jl')
        except Exception as ex:
            logger.error('Data file uploading error')
            logger.exception(ex)
            data_key = None
        logs_key = put_file_into_s3(
            AMAZON_BUCKET_NAME, output_path+'.log')

        if self.is_screenshot_job():
            if not os.path.exists(output_path + '.screenshot.jl'):
                # screenshot task not finished yet? wait 30 seconds
                time.sleep(60)
            if not os.path.exists(output_path + '.screenshot.jl'):
                logger.error('Screenshot output file does not exist: %s' % (
                    output_path + '.screenshot.jl'))
            else:
                try:
                    put_file_into_s3(
                        AMAZON_BUCKET_NAME, output_path+'.screenshot.jl',
                        is_add_file_time=True)
                    logger.info('Screenshot file uploaded: %s' % (output_path + '.screenshot.jl'))
                except Exception as ex:
                    logger.error('Screenshot file uploading error')
                    logger.exception(ex)
                try:
                    put_file_into_s3(
                        AMAZON_BUCKET_NAME, output_path+'_url2screenshot.log',
                        is_add_file_time=True)
                    logger.info('url2screenshot log file uploaded: %s' % (output_path+'_url2screenshot.log'))
                except Exception as ex:
                    logger.error('url2screenshot log file uploading error')
                    logger.exception(ex)

        csv_data_key = None
        global CONVERT_TO_CSV
        if CONVERT_TO_CSV:
            try:
                csv_filepath = convert_json_to_csv(output_path, logger)
                logger.info('Zip created at: %r.', csv_filepath)
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
                         "wasn't received. data_key=%r, logs_key=%r.",
                         data_key, logs_key)

        logger.info("Spider default output:\n%s%s",
                    self.process.stderr.read(),
                    self.process.stdout.read().strip())
        logger.info('Finish task #%s.', self.task_data.get('task_id', 0))

        # upload scrapy_daemon logs
        daemon_logs_zipfile = None
        try:
            daemon_logs_zipfile = self._zip_daemon_logs()
        except Exception as e:
            logger.warning('Could not create daemon ZIP: %s' % str(e))
        if daemon_logs_zipfile and os.path.exists(daemon_logs_zipfile):
            # now move the file into output path folder
            if os.path.exists(output_path+'.daemon.zip'):
                os.unlink(output_path+'.daemon.zip')
            try:
                os.rename(daemon_logs_zipfile, output_path+'.daemon.zip')
            except OSError as e:
                logger.error('File %r to %r rename error: %s.',
                             daemon_logs_zipfile, output_path+'.daemon.zip', e)
            try:
                put_file_into_s3(AMAZON_BUCKET_NAME, daemon_logs_zipfile,
                                 compress=False)
                logger.warning('Daemon logs uploaded')
            except Exception as e:
                logger.warning('Could not upload daemon logs: %s' % str(e))
        self.finished = True
        self.finish_date = datetime.datetime.utcnow()
        self.task_data['finish_time'] = \
            time.mktime(self.finish_date.timetuple())

    def _update_items_scraped(self):
        output_path = self.get_output_path() + '.jl'
        if os.path.exists(output_path):
            cont = None
            try:
                with open(output_path, 'r') as fh:
                    cont = fh.readlines()
            except Exception as ex:
                logger.error('Could not read output file [%s]: %s' % (output_path, str(ex)))
            if cont is not None:
                if isinstance(cont, (list, tuple)):
                    self.items_scraped = len(cont)

    def _success_finish(self):
        """
        used to indicate, that scrapy process finished
        successfully in allowed time
        """
        # run this task after scrapy process successfully finished
        # cache result, if there is at least one scraped item
        time.sleep(2)  # let the data to be dumped into the output file?
        self._update_items_scraped()
        if self.items_scraped:
            self.save_cached_result()
        else:
            logger.warning('Not caching result for task %s (%s) '
                           'due to no scraped items.',
                           self.task_data.get('task_id'),
                           self.task_data.get('server_name'))
        logger.info('Success finish task #%s', self.task_data.get('task_id', 0))
        self.finished_ok = True

    def get_output_path(self):
        """
        get abs path, where to store logs and data files for scrapy task
        """
        output_path = '%s/%s' % (
            os.path.expanduser(JOB_OUTPUT_PATH), self.get_unique_name())
        return output_path

    def _parse_task_and_get_cmd(self, is_bsr=False):
        """
        convert data of the SQS task to the scrapy run command with
        all parameters which are given in task data
        """
        searchterms_str = self.task_data.get('searchterms_str', None)
        url = self.task_data.get('url', None)
        urls = self.task_data.get('urls', None)
        site = self.task_data['site']
        cmd_line_args = self.task_data.get('cmd_args', {})
        if not isinstance(cmd_line_args, dict):
            cmd_line_args = {}
        output_path = self.get_output_path()
        options = ' '
        arg_name = arg_value = None
        for key, value in cmd_line_args.items():
            # exclude raw s3 cache - otherwise 2 spiders will work in parallel
            #  with cache enabled
            if is_bsr and key == 'save_raw_pages':
                continue
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
        """
        starts scrapy process for current SQS task
        also starts second process for best_sellers if required
        """
        cmd = self._parse_task_and_get_cmd()
        self.process = Popen(cmd, shell=True, stdout=PIPE,
                             stderr=PIPE, preexec_fn=os.setsid)
        if self.task_data.get('with_best_seller_ranking', False):
            logger.info('With best seller ranking')
            cmd = self._parse_task_and_get_cmd(True)
            self.process_bsr = Popen(cmd, shell=True, stdout=PIPE,
                                     stderr=PIPE, preexec_fn=os.setsid)
        else:
            logger.info('Skipping best seller')
        logger.info('Scrapy process started for task #%s',
                    self.task_data.get('task_id', 0))

    def _push_simmetrica_events(self):
        if push_simmetrica_event is None:
            logger.error('Error! push_simmetrica_event method not imported!')
            return
        # push global tasks per server
        push_simmetrica_event('monitoring_job_server_name_%s' % (self.task_data['server_name']))
        # push global tasks for site
        push_simmetrica_event('monitoring_job_site_%s' % (self.task_data['site']))
        # push tasks server / site
        push_simmetrica_event('monitoring_job_server_name_and_site_%s_%s' % (
            self.task_data['server_name'], self.task_data['site']))
        # push tasks per server per type
        type = 'unknown'
        if 'url' in self.task_data:
            type = 'product_url'
        elif 'searchterms_str' in self.task_data:
            type = 'searchterm'
        if 'checkout' in self.task_data['site']:
            type = 'checkout'
        if '_shelf' in self.task_data['site']:
            type = 'shelf_page'
        if 'screenshot' in self.task_data['site']:
            type = 'screenshot'
        push_simmetrica_event('monitoring_job_server_name_and_type_%s_%s' % (
            self.task_data['server_name'], type))

    def _establish_connection(self):
        """
        tries to accept connection from the scrapy process to receive
        stats on signals, like spider_error, spider_opened etc
        """
        self.conn = self.listener.accept()

    def _dummy_client(self):
        """used to interrupt waiting for the connection from scrapy process
        with connecting by itself, closes connection immediately"""
        logger.warning('Running dummy client for task #%s',
                       self.task_data.get('task_id', 0))
        Client(LISTENER_ADDRESS).close()

    def _try_connect(self, wait):
        """
        tries to establish connection to scrapy process in the given time
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
                time.sleep(15)
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
        """
        controls the flow of running given signal to scrapy process
        """
        max_step_time = next_signal[1]['wait']
        if next_signal[0] == SIGNAL_SCRIPT_OPENED:  # first signal
            res = self._try_connect(max_step_time)
            if not res:
                raise ConnectError
            self._signal_succeeded(next_signal,
                                   datetime.datetime.utcnow(), False)
            self.send_current_status_to_sqs(0)
            return True
        elif next_signal[0] == SIGNAL_SCRIPT_CLOSED:  # last signal
            res = self._try_finish(max_step_time)
            if not res:
                raise FinishError
            self._signal_succeeded(next_signal,
                                   datetime.datetime.utcnow(), False)
            self.send_current_status_to_sqs('finished')
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
        """
        checks signal to finish in allowed time, otherwise raises error
        and stops scrapy process, logs duration for given signal
        """
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
        """
        start scrapy process, try to establish connection with it,
        terminate if fails
        """
        # it may break during task parsing, for example wrong server name or
        # unsupported characters in the name os spider
        try:
            start_time = datetime.datetime.utcnow()
            self.start_date = start_time
            self.task_data['start_time'] = \
                time.mktime(self.start_date.timetuple())
            self._start_scrapy_process()
            self._push_simmetrica_events()
            first_signal = self._get_next_signal(start_time)
        except Exception as ex:
            logger.warning('Error occurred while starting scrapy: %s', ex)
            return False
        try:
            self._run_signal(first_signal, start_time)
            return True
        except FlowError as ex:
            self._signal_failed(first_signal, datetime.datetime.utcnow(), ex)
            self._finish()
            return False

    def run(self):
        """
        run listening of scrapy process execution in separate thread
        to not block main thread and allow multiple tasks running same time
        """
        t = Thread(target=self._listen)
        t.start()

    def stop(self):
        """send stop signal, doesn't guaranties to stop immediately"""
        self._stop_signal = True

    def is_finished(self):
        return self.finished

    def is_finised_ok(self):
        return self.finished_ok

    def get_cached_result(self, queue_name):
        res = get_task_result_from_cache(self.task_data, queue_name)
        if res:
            self.send_current_status_to_sqs('finished')
            dump_cached_data_into_sqs(
                res, self.task_data['server_name']+OUTPUT_QUEUE_NAME,
                self.task_data)
        return bool(res)

    def save_cached_result(self):
        return save_task_result_to_cache(self.task_data, self.get_output_path())

    def is_screenshot_job(self):
        return self.task_data.get('cmd_args', {}).get('make_screenshot_for_url', False)

    def start_screenshot_job_if_needed(self):
        """ Starts a new url2screenshot local job, if needed """
        url2scrape = None
        if self.task_data.get('product_url', self.task_data.get('url', None)):
            url2scrape = self.task_data.get('product_url', self.task_data.get('url', None))
        # TODO: searchterm jobs? checkout scrapers?
        if url2scrape:
            # scrapy_path = "/home/spiders/virtual_environment/bin/scrapy"
            # python_path = "/home/spiders/virtual_environment/bin/python"
            output_path = self.get_output_path()
            cmd = ('cd {repo_base_path}/product-ranking'
                   ' && scrapy crawl url2screenshot_products'
                   ' -a product_url="{url2scrape}" '
                   ' -a width=1280 -a height=1024 -a timeout=60 '
                   ' -s LOG_FILE={log_file}'
                   ' -o "{output_file}" &').format(
                       repo_base_path=REPO_BASE_PATH,
                       log_file=output_path+'_url2screenshot.log', url2scrape=url2scrape,
                       output_file=output_path+'.screenshot.jl')
            logger.info('Starting a new parallel screenshot job: %s' % cmd)
            os.system(cmd)  # use Popen instead?

    def report(self):
        """returns string with the task running stats"""
        s = 'Task #%s, command %r.\n' % (self.task_data.get('task_id', 0),
                                         self._parse_task_and_get_cmd())
        if self.start_date:
            s += 'Task started at %s.\n' % str(self.start_date.time())
        if self.finish_date:
            s += 'Finished %s at %s, duration %s.\n' % (
                'successfully' if self.finished_ok else 'containing errors',
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

    def send_current_status_to_sqs(self, status=None):
        msg = generate_msg(
            self.task_data, status if status else self.items_scraped)
        put_msg_to_sqs(
            self.task_data['server_name']+PROGRESS_QUEUE_NAME, msg)
        # put current progress to S3 as well, for easier debugging & tracking
        progress_fname = self.get_output_path() + '.progress'
        with open(progress_fname, 'w') as fh:
            fh.write(json.dumps(msg, default=json_serializer))
        put_file_into_s3(AMAZON_BUCKET_NAME, progress_fname)


def get_file_cm_time(file_path):
    """Get unix timestamp of create date of file or last modify date."""
    try:
        create_time = os.path.getctime(file_path)
        if create_time:
            return int(create_time)
        modify_time = os.path.getmtime(file_path)
        if modify_time:
            return int(modify_time)
    except (OSError, ValueError) as e:
        logger.error('Error while get creation time of file. ERROR: %s.',
                     str(e))
    return 0


def get_task_result_from_cache(task, queue_name):
    """try to get cached result for some task"""
    task_id = task.get('task_id', 0)
    server = task.get('server_name', '')
    if task.get(CACHE_GET_IGNORE_KEY, False):
        logger.info('Ignoring cache result for task %s (%s).', task_id, server)
        return None
    url = CACHE_HOST + CACHE_URL_GET
    data = dict(task=json.dumps(task), queue=queue_name)
    try:
        resp = requests.post(url, data=data, timeout=CACHE_TIMEOUT,
                             auth=CACHE_AUTH)
    except Exception as ex:
        logger.warning(ex)
        return None
    if resp.status_code != 200:  # means no cached data was received
        logger.info('No cached result for task %s (%s). '
                    'Status %s, message is: "%s".',
                    task_id, server, resp.status_code, resp.text)
        return None
    else:  # got task
        logger.info('Got cached result for task %s (%s): %s.',
                    task_id, server, resp.text)
        return resp.text


def save_task_result_to_cache(task, output_path):
    """save cached result for task to sqs cache"""
    task_id = task.get('task_id', 0)
    server = task.get('server_name', '')
    if task.get(CACHE_SAVE_IGNORE_KEY, False):
        logger.info('Ignoring save to cache for task %s (%s)', task_id, server)
        return False
    message = FOLDERS_PATH + os.path.basename(output_path)
    url = CACHE_HOST + CACHE_URL_SAVE
    data = dict(task=json.dumps(task), message=message)
    try:
        resp = requests.post(url, data=data, timeout=CACHE_TIMEOUT,
                             auth=CACHE_AUTH)
    except Exception as ex:  # timeout passed but no response received
        logger.warning(ex)
        return False
    if resp.status_code != 200:
        logger.warning('Failed to save cached result for task %s (%s). '
                       'Status %s, message: "%s".',
                       task_id, server, resp.status_code, resp.text)
        return False
    else:
        logger.info('Saved cached result for task %s (%s).', task_id, server)
        return True


def log_failed_task(task):
    """
    log broken task
    if this function returns True, task is considered
    as failed max allowed times and should be removed
    """
    url = CACHE_HOST + CACHE_URL_FAIL
    data = dict(task=json.dumps(task))
    try:
        resp = requests.post(url, data=data, timeout=CACHE_TIMEOUT,
                             auth=CACHE_AUTH)
    except Exception as ex:
        logger.warning(ex)
        return False
    if resp.status_code != 200:
        logger.warning('Mark task as failed wrong response status code: %s, %s',
                       resp.status_code, resp.text)
        return False
    # resp.text contains only 0 or 1 number,
    #  1 indicating that task should be removed
    try:
        return json.loads(resp.text)
    except ValueError as ex:
        logger.warning('JSON conversion error: %s', ex)
        return False


def notify_cache(task, is_from_cache=False):
    """send request to cache (for statistics)"""
    url = CACHE_HOST + CACHE_URL_STATS
    json_task = json.dumps(task)
    logger.info('Notify cache task: %s', json_task)
    data = dict(task=json_task, is_from_cache=json.dumps(is_from_cache))
    if 'start_time' in task and task['start_time']:
        if ('finish_time' in task and not task['finish_time']) or \
                'finish_time' not in task:
            task['finish_time'] = int(time.time())
    data = dict(task=json.dumps(task), is_from_cache=json.dumps(is_from_cache))
    try:
        resp = requests.post(url, data=data, timeout=CACHE_TIMEOUT,
                             auth=CACHE_AUTH)
        logger.info('Cache: updated task (%s), status %s.',
                    task.get('task_id'), resp.status_code)
    except Exception as ex:
        logger.warning('Cache: update completed task error: %s.', ex)


def del_duplicate_tasks(tasks):
    """Checks all tasks (its ids) and removes ones, which ids are repeating"""
    task_ids = []
    for i in xrange(len(tasks) - 1, -1, -1):  # iterate from the end
        t = tasks[i].task_data.get('task_id')
        if t is None:
            continue
        if t in task_ids:
            logger.warning('Found duplicate task for id %s, removing it.', t)
            del tasks[i]
            continue
        task_ids.append(t)


def is_task_taken(new_task, tasks):
    """
    check, if task with such id already taken
    """
    task_ids = [t.task_data.get('task_id') for t in tasks]
    new_task_id = new_task.get('task_id')
    if new_task_id is None:
        return False
    return new_task_id in task_ids


def store_tasks_metrics(task, redis_db):
    """This method will just increment required key in redis database
        if connection to the database exist."""
    if TEST_MODE:
        print 'Simulate redis incremet, key is %s' % JOBS_COUNTER_REDIS_KEY
        print 'Simulate redis incremet, key is %s' % JOBS_STATS_REDIS_KEY
        return
    if not redis_db:
        return
    try:
        # increment quantity of tasks spinned up during the day.
        redis_db.incr(JOBS_COUNTER_REDIS_KEY)
    except Exception as e:
        logger.warning("Failed to increment redis metric '%s' "
                       "with exception '%s'", JOBS_COUNTER_REDIS_KEY,
                       e)
    generated_key = '%s:%s:%s' % (
        task.get('server_name', 'UnknownServer'),
        task.get('site', 'UnknownSite'),
        ('term' if 'searchterms_str' in task and task['searchterms_str']
         else 'url')
    )
    try:
        redis_db.hincrby(JOBS_STATS_REDIS_KEY, generated_key, 1)
    except Exception as e:
        logger.warning("Failed to increment redis key '%s' and"
                       "redis metric '%s' with exception '%s'",
                       JOBS_STATS_REDIS_KEY, generated_key, e)


def get_instance_billing_limit_time():
    try:
        return int(global_settings_from_redis.get('instance_max_billing_time'))
    except Exception as e:
        logger.warning('Error while getting instance billing '
                       'time limit from redis cache. Limitation is disabled.'
                       ' ERROR: %s.', str(e))
    return 0


def shut_down_instance_if_swap_used():
    """ Shuts down the instance of swap file is used heavily
    :return:
    """
    stats = statistics.report_statistics()
    swap_usage_total = stats.get('swap_usage_total', None)
    ram_usage_total = stats.get('ram_usage_total', None)

    logger.info('Checking swap and RAM usage...')

    if swap_usage_total and ram_usage_total:
        try:
            swap_usage_total = float(ram_usage_total)
            ram_usage_total = float(ram_usage_total)
        except:
            logger.error('Swap and RAM usage check failed during float() conversion')
            return

        if ram_usage_total > 70:
            if swap_usage_total > 10:
                # we're swapping very badly!
                logger.error('Swap and RAM usage is too high! Terminating instance')
                try:
                    conn = boto.connect_ec2()
                    instance_id = get_instance_metadata()['instance-id']
                    conn.terminate_instances(instance_id, decrement_capacity=True)
                except Exception as e:
                    logger.error('Failed to terminate instance, exception: %s' % str(e))


def get_uptime():
    """
    Get instance billing time.
    """
    output = Popen('cat /proc/uptime', shell=True, stdout=PIPE)
    return float(output.communicate()[0].split()[0])


def restart_scrapy_daemon():
    """
    Restart this script after update source code.
    """
    global REPO_BASE_PATH
    logger.info('Scrapy daemon restarting...')
    arguments = ['python'] + [REPO_BASE_PATH+'/deploy/sqs_ranking_spiders/scrapy_daemon.py'] + sys.argv[1:]
    if 'restarted' not in arguments:
        arguments += ['restarted']
    else:
        logger.error('Error while restarting scrapy daemon. '
                     'Already restarted.')
        return
    logging.info('Starting %s with args %s' % (sys.executable, arguments))
    os.execv(sys.executable, arguments)


def daemon_is_restarted():
    """
    Check this script is restarted copy or not.
    """
    return 'restarted' in sys.argv


def load_options_after_restart():
    """
    Load previous script options.
    """
    try:
        with open(OPTION_FILE_FOR_RESTART, 'r') as f:
            options = f.read()
            print '\n\n', options, '\n\n'
        os.remove(OPTION_FILE_FOR_RESTART)
        return json.loads(options)
    except Exception as e:
        logger.error('Error while load old options for scrapy daemon. '
                     'ERROR: %s' % str(e))
    return {}


def save_options_for_restart(options):
    """
    Save script options for another copy.
    """
    try:
        options = json.dumps(options)
        with open(OPTION_FILE_FOR_RESTART, 'w') as f:
            f.write(options)
    except Exception as e:
        logger.error('Error while save options for scrapy daemon. '
                     'ERROR: %s' % str(e))


def prepare_queue_after_restart(options):
    """
    Load queue and message from disk after restart.
    """
    if TEST_MODE:
        global task_number
        try:
            task_number
        except NameError:
            task_number = -1
        task_number += 1
        fake_class = SQS_Queue(options['queue']['name'])
        return options['task_data'], fake_class
    # Connection to SQS
    queue = SQS_Queue(
        name=options['queue']['queue_name'],
        region=options['queue']['conn_region']
    )
    # Create a new message
    queue.currentM = queue.q.message_class()
    # Fill message
    queue.currentM.body = options['queue']['body']
    queue.currentM.attributes = options['queue']['attributes']
    queue.currentM.md5_message_attributes = \
        options['queue']['md5_message_attributes']
    queue.currentM.message_attributes = options['queue']['message_attributes']
    queue.currentM.receipt_handle = options['queue']['receipt_handle']
    queue.currentM.id = options['queue']['id']
    queue.currentM.md5 = options['queue']['md5']
    return options['task_data'], queue


def store_queue_for_restart(queue):
    """
    Save queue options and message to disk for load after restart.
    """
    if TEST_MODE:
        return queue.__dict__
    if not queue.currentM:
        logger.error('Message was not found in queue for restart daemon.')
        return None
    return {
        'conn_region': queue.conn.region.name,
        'queue_name': queue.q.name,
        'body': queue.currentM.get_body(),
        'attributes': queue.currentM.attributes,
        'md5_message_attributes': queue.currentM.md5_message_attributes,
        'message_attributes': queue.currentM.message_attributes,
        'receipt_handle': queue.currentM.receipt_handle,
        'id': queue.currentM.id,
        'md5': queue.currentM.md5
    }


def main():
    if not TEST_MODE:
        instance_meta = get_instance_metadata()
        inst_ip = instance_meta.get('public-ipv4')
        inst_id = instance_meta.get('instance-id')
        logger.info("IMPORTANT: ip: %s, instance id: %s", inst_ip, inst_id)
    set_global_variables_from_data_file()
    redis_db = connect_to_redis_database(redis_host=REDIS_HOST,
                                         redis_port=REDIS_PORT)
    global MAX_CONCURRENT_TASKS
    tasks_taken = []
    options = {}
    if not daemon_is_restarted():
        # increment quantity of instances spinned up during the day.
        increment_metric_counter(INSTANCES_COUNTER_REDIS_KEY, redis_db)
        max_tries = MAX_TRIES_TO_GET_TASK
        branch = None
        task_data = None
        queue = None
        skip_first_getting_task = False
    else:
        options = load_options_after_restart()
        try:
            max_tries = int(options.get('max_tries', MAX_TRIES_TO_GET_TASK))
        except Exception as e:
            logger.warning('Error while load `max_tries` from old options. '
                           'ERROR: %s' % str(e))
            max_tries = MAX_TRIES_TO_GET_TASK
        branch = options.get('branch')
        task_data, queue = prepare_queue_after_restart(options)
        MAX_CONCURRENT_TASKS = options.get('MAX_CONCURRENT_TASKS')
        TASK_QUEUE_NAME = options.get('TASK_QUEUE_NAME')
        skip_first_getting_task = True
    try:
        listener = Listener(LISTENER_ADDRESS)
    except AuthenticationError:
        listener = None

    if not listener:
        logger.error('Socket auth failed!')
        raise Exception  # to catch exception and write end marker

    if not os.path.exists(os.path.expanduser(JOB_OUTPUT_PATH)):
        logger.debug("Create job output dir %s",
                     os.path.expanduser(JOB_OUTPUT_PATH))
        os.makedirs(os.path.expanduser(JOB_OUTPUT_PATH))

    def is_end_billing_instance_time():
        if not get_instance_billing_limit_time() or \
                get_uptime() > get_instance_billing_limit_time():
            return False
        logger.info('Instance execution time limit.')
        return True

    def is_all_tasks_finished(tasks):
        return all([_.is_finished() for _ in tasks])

    def send_tasks_status(tasks):
        return [_.send_current_status_to_sqs()
                for _ in tasks if not _.is_finished()]

    def stop_not_finished_tasks(tasks):
        for _ in tasks:
            if not _.is_finished():
                _.stop()
        time.sleep(15)
        logger.info('Reporting stopped tasks')
        for _ in tasks:
            if not _.is_finished():
                try:
                    logger.info(_.process.stdout.read())
                    logger.info(_.process.stderr.read())
                except:
                    logger.warning('Unable to retrieve logs from task')

    def log_tasks_results(tasks):
        logger.info('#'*10 + 'START TASKS REPORT' + '#'*10)
        [logger.info(_.report()) for _ in tasks]
        logger.info('#'*10 + 'FINISH TASKS REPORT' + '#'*10)

    attributes = 'SentTimestamp'  # additional data to get with sqs messages
    add_timeout = 30  # add to visibility timeout
    # names of the queues in SQS, ordered by priority
    q_keys = ['urgent', 'production', 'test', 'dev']
    q_ind = 0  # index of current queue
    # try to get tasks, untill max number of tasks is reached or
    # max number of tries to get tasks is reached
    while len(tasks_taken) < MAX_CONCURRENT_TASKS and max_tries and \
            not is_end_billing_instance_time():
        # Skip if needed getting first task. After restarting task
        # in old options. For work scrapy daemon with a new source code
        # from new branch and with old task.
        if not skip_first_getting_task or \
                not task_data:
            TASK_QUEUE_NAME = QUEUES_LIST[q_keys[q_ind]]
            logger.info('Trying to get task from %s, try #%s',
                        TASK_QUEUE_NAME, MAX_TRIES_TO_GET_TASK - max_tries)
            if TEST_MODE:
                msg = test_read_msg_from_fs(TASK_QUEUE_NAME)
            else:
                msg = read_msg_from_sqs(
                    TASK_QUEUE_NAME, max_tries+add_timeout, attributes)
            max_tries -= 1
            if msg is None:  # no task
                # if failed to get task from current queue,
                # then change it to the following value in a circle
                if q_ind < len(q_keys) - 1:
                    q_ind += 1
                else:
                    q_ind = 0
                time.sleep(3)
                continue
            task_data, queue = msg
        else:
            skip_first_getting_task = False
        if not task_data or not queue:
            continue
        if not tasks_taken and ENABLE_TO_RESTART_DAEMON:
            options['MAX_CONCURRENT_TASKS'] = MAX_CONCURRENT_TASKS
            options['max_tries'] = max_tries
            options['TASK_QUEUE_NAME'] = TASK_QUEUE_NAME
        if 'url' in task_data and 'searchterms_str' not in task_data \
                and not 'checkout' in task_data['site']:
            if MAX_CONCURRENT_TASKS < 70:  # increase num of parallel jobs
                                           # for "light" URL-based jobs
                MAX_CONCURRENT_TASKS += 1

        if task_data['site'] == 'walmart':
            task_quantity = task_data.get('cmd_args', {}).get('quantity', 20)
            with_best_seller_ranking = task_data.get('with_best_seller_ranking', None)
            if task_quantity > 600:
                # decrease num of parallel tasks for "heavy" Walmart jobs
                MAX_CONCURRENT_TASKS -= 6 if MAX_CONCURRENT_TASKS > 0 else 0
                logger.info('Decreasing MAX_CONCURRENT_TASKS to %i'
                            ' (because of big walmart quantity)' % MAX_CONCURRENT_TASKS)
                if with_best_seller_ranking:
                    # decrease max_concurrent_tasks even more if it's BS task
                    #  which actually runs 2x spiders
                    MAX_CONCURRENT_TASKS -= 6 if MAX_CONCURRENT_TASKS > 0 else 0
                    logger.info('Decreasing MAX_CONCURRENT_TASKS to %i'
                                ' (because of big walmart BS)' % MAX_CONCURRENT_TASKS)
            elif 300 < task_quantity < 600:
                # decrease num of parallel tasks for "heavy" Walmart jobs
                MAX_CONCURRENT_TASKS -= 3 if MAX_CONCURRENT_TASKS > 0 else 0
                logger.info('Decreasing MAX_CONCURRENT_TASKS to %i'
                            ' (because of big walmart quantity)' % MAX_CONCURRENT_TASKS)
                if with_best_seller_ranking:
                    # decrease max_concurrent_tasks even more if it's BS task
                    #  which actually runs 2x spiders
                    MAX_CONCURRENT_TASKS -= 3 if MAX_CONCURRENT_TASKS > 0 else 0
                    logger.info('Decreasing MAX_CONCURRENT_TASKS to %i'
                                ' (because of big walmart BS)' % MAX_CONCURRENT_TASKS)
        elif (task_data['site'] in ('dockers', 'nike')) or 'checkout' in task_data['site']:
            MAX_CONCURRENT_TASKS -= 6 if MAX_CONCURRENT_TASKS > 0 else 0
            logger.info('Decreasing MAX_CONCURRENT_TASKS to %i because of Selenium-based spider in use' % MAX_CONCURRENT_TASKS)
        elif task_data.get('cmd_args', {}).get('make_screenshot_for_url', False):
            MAX_CONCURRENT_TASKS -= 6 if MAX_CONCURRENT_TASKS > 0 else 0
            logger.info('Decreasing MAX_CONCURRENT_TASKS to %i because of the parallel url2screenshot job' % MAX_CONCURRENT_TASKS)

        logger.info("Task message was successfully received.")
        logger.info("Whole tasks msg: %s", str(task_data))
        # prepare to run task
        # check if task with such id is already taken,
        # to prevent running same task multiple times
        if is_task_taken(task_data, tasks_taken):
            logger.warning('Duplicate task %s, skipping.',
                           task_data.get('task_id'))
            continue
        if not tasks_taken:
            # get git branch from first task, all tasks should
            # be in the same branch
            if not daemon_is_restarted():
                branch = get_branch_for_task(task_data)
                switch_branch_if_required(task_data)
                options['branch'] = branch
                options['task_data'] = task_data
                options['queue'] = store_queue_for_restart(queue)
                if branch and \
                        get_actual_branch_from_cache() != branch and \
                        ENABLE_TO_RESTART_DAEMON:
                    save_options_for_restart(options)
                    listener.close()
                    restart_scrapy_daemon()
        elif not is_same_branch(get_branch_for_task(task_data), branch):
            # make sure all tasks are in same branch
            queue.reset_message()
            continue
        # Store jobs metrics
        store_tasks_metrics(task_data, redis_db)
        # start task
        # if started, remove from the queue and run
        task = ScrapyTask(queue, task_data, listener)
        # check for cached response
        if task.get_cached_result(TASK_QUEUE_NAME):
            # if found response in cache, upload data, delete task from sqs
            task.queue.task_done()
            notify_cache(task.task_data, is_from_cache=True)
            del task
            continue
        if task.start():
            tasks_taken.append(task)
            task.run()
            logger.info(
                'Task %s started successfully, removing it from the queue',
                task.task_data.get('task_id'))
            if task.is_screenshot_job():
                task.start_screenshot_job_if_needed()
            task.queue.task_done()
            notify_cache(task.task_data, is_from_cache=False)
        else:
            logger.error('Task #%s failed to start. Leaving it in the queue.',
                         task.task_data.get('task_id', 0))
            # remove task from queue, if it failed many times
            if log_failed_task(task.task_data):
                logger.warning('Removing task %s_%s from the queue due to too '
                               'many failed tries.',
                               task_data.get('server_name'),
                               task_data.get('task_id'))
                task.queue.task_done()
            logger.error(task.report())
    if not tasks_taken:
        logger.warning('No any task messages were found.')
        logger.info('Scrapy daemon finished.')
        return
    logger.info('Total tasks received: %s', len(tasks_taken))
    # wait until all tasks are finished or max wait time is reached
    # report each task progress after that and kill all tasks
    #  which are not finished in time
    max_wait_time = max([t.get_total_wait_time() for t in tasks_taken]) or 61
    logger.info('Max allowed running time is %ss', max_wait_time)
    step_time = 30
    # loop where we wait for all the tasks to complete
    try:
        for i in xrange(0, max_wait_time, step_time):
            if is_all_tasks_finished(tasks_taken):
                logger.info('All tasks finished.')
                break
            send_tasks_status(tasks_taken)
            time.sleep(step_time)
            logger.info('Server statistics: ' + str(statistics.report_statistics()))
            shut_down_instance_if_swap_used()
        else:
            logger.error('Some of the tasks not finished in allowed time, '
                         'stopping them.')
            stop_not_finished_tasks(tasks_taken)
        time.sleep(20)
    except KeyboardInterrupt:
        stop_not_finished_tasks(tasks_taken)
        raise Exception
    listener.close()
    log_tasks_results(tasks_taken)

    # write finish marker
    logger.info('Scrapy daemon finished.')


def prepare_test_data():
    # only for local-filesystem tests!
    # prepare incoming tasks
    tasks = [dict(
        task_id=4443, site='walmart', searchterms_str='iphone',
        server_name='test_server_name', with_best_seller_ranking=True,
        cmd_args={'quantity': 50}, attributes={'SentTimestamp': '1443426145373'}
    ), dict(
        task_id=4444, site='amazon', searchterms_str='iphone',
        server_name='test_server_name', with_best_seller_ranking=True,
        cmd_args={'quantity': 1}, attributes={'SentTimestamp': '1443426145373'}
    ), dict(
        task_id=4445, site='target', searchterms_str='iphone',
        server_name='test_server_name', with_best_seller_ranking=True,
        cmd_args={'quantity': 50}, attributes={'SentTimestamp': '1443426145373'}
    )]
    files = [open('/tmp/' + q, 'w') for q in QUEUES_LIST.itervalues()]
    for fh in files:
        for msg in tasks:
            fh.write(json.dumps(msg, default=json_serializer)+'\n')
        fh.close()


def log_free_disk_space():
    """mostly for debugging purposes, shows result of 'df -h' system command"""
    cmd = 'df -h'
    p = Popen(cmd, shell=True, stdout=PIPE)
    res = p.communicate()
    if res[0]:
        res = res[0]
    else:
        res = res[1]
    logger.warning('Disk usage statisticks:')
    logger.warning(res)


if __name__ == '__main__':
    if daemon_is_restarted():
        logger.info('Scrapy daemon is restarted.')
    if 'test' in [a.lower().strip() for a in sys.argv]:
        TEST_MODE = True
        prepare_test_data()
        CACHE_HOST = 'http://127.0.0.1:5000/'
        try:
            # local mode
            from sqs_ranking_spiders.fake_sqs_queue_class import SQS_Queue
        except ImportError:
            from repo.fake_sqs_queue_class import SQS_Queue
        logger.debug('TEST MODE ON')
        logger.debug('Faking the SQS_Queue class')

    try:
        main()
        log_free_disk_space()
    except Exception as e:
        log_free_disk_space()
        logger.exception(e)
        logger.error('Finished with error.')  # write fail finish marker
        try:
            os.killpg(os.getpgid(os.getpid()), 9)
        except:
            pass
