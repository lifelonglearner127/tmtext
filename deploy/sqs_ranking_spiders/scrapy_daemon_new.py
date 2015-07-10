import os
from datetime import datetime
from multiprocessing.connection import Listener, AuthenticationError
from .fake_sqs_queue_class import SQS_Queue

# settings
MAX_CONCURRENT_TASKS = 5  # tasks per instance, all with same git branch
MAX_TRIES_TO_GET_TASK = 50  # tries to get max tasks for same branch
LISTENER_ADDRESS = ('localhost', 6000)  # address to listen for signals
SCRAPY_LOGS_DIR = ''  # where to put log files
SCRAPY_DATA_DIR = ''  # where to put scraped data files
S3_UPLOAD_DIR = ''  # folder path on the s3 server, where to save logs/data

# required signals
REQUIRED_SIGNALS = [
    # [signal_name, wait_in_seconds]
    ['script_started', 5 * 60],  # wait for signal after script started
    ['spider_started', 15 * 60],
    ['spider_closed', 24 * 60 * 60],  # wait for spider to scrape all data
    ['script_closed', 15 * 60]
]

# optional extension signals
EXTENSION_SIGNALS = [
    ['cache_downloading', 30 * 60],  # cache load FROM s3
    ['cache_uploading', 30 * 60]  # cache load TO s3,
    # ['logs_uploading', 15 * 60],  # logs load TO s3
    # ['data_uploading', 30 * 60]  # data load TO s3
]


# TODO: this is done for scrapy side, move it there
# TODO: call scrapy with additional parameter, which indicates,
#       that signals should be reported
def report_stats(signal_name, connection=None):
    """
    Decorator, which sends signal to the connection
    with the signal_name as name parameter two times.
    One before method execution with status 'started'.
    Second after method execution with status 'closed'
    :param signal_name: name of the signal
    :param connection: where to send data
    """
    def wrapper(f):

        def send_signal(name, status):
            data = dict(name=name, status=status)
            if connection:
                connection.send(data)
            else:
                print 'sending', data

        def wrapped(*args, **kwargs):
            # 1) report signal start
            send_signal(signal_name, 'started')
            # 2) execute method
            res = f(*args, **kwargs)
            # 3) report signal finish
            send_signal(signal_name, 'closed')
            # 4) return result
            return res

        return wrapped

    return wrapper


def connect_redis(host, port):
    # get from daemon
    pass


def read_glob_variables():
    # get from daemon
    pass


def get_task_from_sqs():
    # get from daemon
    mock = ''
    return mock


def delete_task_from_sqs(queue):
    # get from daemon
    pass


def get_branch_for_task(task_data):
    return task_data.get('branch_name')


def set_working_branch(branch):
    # get from daemon
    pass


def is_same_branch(b1, b2):
    return b1 == b2


def datetime_difference(d1, d2):
    res = d1 - d2
    return 86400 * res.days + res.seconds


def create_dir(path):
    try:
        os.makedirs(path)
    except OSError:  # no access to create folder
        os.makedirs(os.path.expanduser('~/' + os.path.basename(path)))


def check_required_folders():
    # create logs & data folders if needed
    if not os.path.exists(SCRAPY_LOGS_DIR):
        create_dir(SCRAPY_LOGS_DIR)
    if not os.path.exists(SCRAPY_DATA_DIR):
        create_dir(SCRAPY_DATA_DIR)


class ScrapyTask(object):

    def __init__(self, task_data):
        self.task_data = task_data
        self.items_scraped = 0
        self.errors = 0
        self.total_time_taken = 0
        self.finished = False
        self.successfully_finished = False
        self.stop_signal = False  # to break main loop if needed
        self.extension_signals = self.parse_optional_signals()

    def get_unique_name(self):
        # convert task data into unique name
        # TODO: get from daemon job_to_fname ?
        return ''

    def parse_optional_signals(self):
        return [
            dict(name=s[0], wait=s[1], started=None, finished=None)
            for s in EXTENSION_SIGNALS
        ]

    def item_scraped_signal(self, item, response, spider):
        self.items_scraped += 1

    def spider_error_signal(self, failure, response, spider):
        self.errors += 1

    def get_next_signal(self):
        # must return tuple of signal name and time to wait in seconds
        # if none, then all steps are finished
        return '', 0

    def is_data_for_extension(self, data):
        # check if received signal is for extension and not for main flow item
        return True

    def update_ext_duration(self, date_time):
        # update all extension signals with the duration of running
        # return all extension signals, which last more then allowed time
        pass

    def process_signal_data(self, data):
        # get data from scrapy
        is_ext = self.is_data_for_extension(data)
        return is_ext

    def finish(self):
        # run this task for both successfully or failed finish
        # upload logs/data to s3
        self.finished = True

    def success_finish(self):
        # run this task after scrapy process successfully finished
        self.successfully_finished = True

    def establish_connection(self):
        try:
            l = Listener(LISTENER_ADDRESS)
        except AuthenticationError:
            return
        conn = l.accept()
        return conn

    def listen(self, conn):
        start_time = datetime.now()
        while not self.stop_signal:  # run through all signals
            next_signal = self.get_next_signal()
            if not next_signal:
                # all steps are finished
                self.success_finish()
                break
            max_step_time = next_signal[1]
            step_time_passed = 0
            step_time_start = datetime.now()
            while not self.stop_signal and step_time_passed <= max_step_time:
                has_data = conn.poll(max_step_time - step_time_passed)
                sub_step_time = datetime.now()
                step_time_passed += datetime_difference(sub_step_time,
                                                        step_time_start)
                if has_data:
                    data = conn.recv()
                    is_ext = self.process_signal_data(data)
                    self.update_ext_duration(sub_step_time)
                    if not is_ext:  # move to next signal
                        break
        finish_time = datetime.now()
        self.total_time_taken = datetime_difference(finish_time, start_time)
        self.finish()


def main():
    connect_redis('', '')
    read_glob_variables()
    check_required_folders()

    max_tries = MAX_TRIES_TO_GET_TASK
    tasks_taken = []
    branch = None

    queue = SQS_Queue('some queue')

    while len(tasks_taken) < MAX_CONCURRENT_TASKS or not max_tries:
        max_tries -= 1
        task_data = get_task_from_sqs()
        # get branch from first task
        if not tasks_taken:
            branch = get_branch_for_task(task_data)
        elif not is_same_branch(get_branch_for_task(task_data), branch):
            # tasks have different branches, skip
            continue
        delete_task_from_sqs(queue)
        task = ScrapyTask(task_data)
        tasks_taken.append(task)

    # run multiprocess connection to listen for signals on some port
    # in separate thread
    # tasks_taken[N].listen