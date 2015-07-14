import os
import time
from collections import OrderedDict
from datetime import datetime
from threading import Thread
from multiprocessing.connection import Listener, AuthenticationError, Client
from subprocess import Popen, PIPE
from fake_sqs_queue_class import SQS_Queue

# settings
MAX_CONCURRENT_TASKS = 5  # tasks per instance, all with same git branch
MAX_TRIES_TO_GET_TASK = 50  # tries to get max tasks for same branch
LISTENER_ADDRESS = ('localhost', 6000)  # address to listen for signals
SCRAPY_LOGS_DIR = ''  # where to put log files
SCRAPY_DATA_DIR = ''  # where to put scraped data files
S3_UPLOAD_DIR = ''  # folder path on the s3 server, where to save logs/data
STATUS_STARTED = 'opened'
STATUS_FINISHED = 'closed'
SIGNAL_SCRIPT_OPENED = 'script_opened'
SIGNAL_SCRIPT_CLOSED = 'script_closed'
SIGNAL_SPIDER_OPENED = 'spider_opened'
SIGNAL_SPIDER_CLOSED = 'spider_closed'

# required signals
REQUIRED_SIGNALS = [
    # [signal_name, wait_in_seconds]
    [SIGNAL_SCRIPT_OPENED, 5 * 60],  # wait for signal that script started
    [SIGNAL_SPIDER_OPENED, 15 * 60],
    # [SIGNAL_SPIDER_CLOSED, 24 * 60 * 60],
    [SIGNAL_SPIDER_CLOSED, 30],
    [SIGNAL_SCRIPT_CLOSED, 15 * 60]  # take into account extensions
]

# optional extension signals
EXTENSION_SIGNALS = [
    # ['cache_downloading', 30 * 60],  # cache load FROM s3
    # ['cache_uploading', 30 * 60]  # cache load TO s3,
    # ['logs_uploading', 15 * 60],  # logs load TO s3
    # ['data_uploading', 30 * 60]  # data load TO s3
]


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
    pass


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
        path = os.path.expanduser('~/' + os.path.basename(path))
        os.makedirs(path)
    return path


def check_required_folders():
    # create logs & data folders if needed
    global SCRAPY_LOGS_DIR, SCRAPY_DATA_DIR
    if not os.path.exists(SCRAPY_LOGS_DIR):
        SCRAPY_LOGS_DIR = create_dir(SCRAPY_LOGS_DIR)
    if not os.path.exists(SCRAPY_DATA_DIR):
        SCRAPY_DATA_DIR = create_dir(SCRAPY_DATA_DIR)


class ScrapyTask(object):

    def __init__(self, task_data, listener, cmd=None):
        self.task_data = task_data
        self.listener = listener  # common listener to accept connections
        self.process = None  # instance of Popen for scrapy
        self.conn = None  # individual connection for each task
        self.return_code = None  # result of scrapy run
        self.finished = False  # is task finished
        self.finished_ok = False  # is task finished good
        self._stop_signal = False  # to break loop if needed
        self.start_date = None
        self.finish_date = None
        self.required_signals = self._parse_signal_settings(REQUIRED_SIGNALS)
        self.extension_signals = self._parse_signal_settings(EXTENSION_SIGNALS)
        self.current_signal = None  # tuple of key, value for current signal
        self.required_signals_done = OrderedDict()
        self.require_signal_failed = None  # signal, where failed
        # todo: remove
        self.cmd = cmd

    def get_unique_name(self):
        # convert task data into unique name
        # TODO: get from daemon job_to_fname ?
        return ''

    def _parse_signal_settings(self, signal_settings):
        d = OrderedDict()
        wait = 'wait'
        # dict with signal name as key and dict as value
        for s in signal_settings:
            d[s[0]] = {wait: s[1], STATUS_STARTED: None, STATUS_FINISHED: None}
        return d

    def _dispose(self):
        """kill process if running, drop connection if opened"""
        if self.process and self.process.poll() is None:
            try:
                os.killpg(os.getpgid(self.process.pid), 9)
            except OSError as e:
                print 'OSError', e
        if self.conn:
            self.conn.close()

    def get_next_signal(self, date_time):
        """get and remove next signal from the main queue"""
        try:
            k = self.required_signals.iterkeys().next()
        except StopIteration:
            return None
        v = self.required_signals.pop(k)
        v[STATUS_STARTED] = date_time
        return k, v

    def get_signal_by_data(self, data):
        """
        return current main signal or
        one of the extension signals, for which data is sent
        """
        is_ext = False
        if self.current_signal and self.current_signal[0] == data['name']:
            signal = self.current_signal
        else:
            is_ext = True
            signal = (data['name'], self.extension_signals.get(data['name']))
        return is_ext, signal

    def process_signal_data(self, signal, data, date_time, is_ext):
        new_status = data['status']  # opened/closed
        if signal[1][new_status]:  # if value is already set
            res = False
        else:
            res = True
        self.signal_succeeded(signal, date_time, is_ext)
        return res

    def signal_failed(self, signal, date_time, ex):
        """
        set signal as failed
        :param signal: signal itself
        :param date_time: when signal failed
        :param ex: exception that caused fail
        """
        signal[1]['failed'] = True
        signal[1][STATUS_FINISHED] = date_time
        signal[1]['reason'] = ex.__class__.__name__

        self.require_signal_failed = signal

    def signal_succeeded(self, signal, date_time, is_ext):
        """set finish time for signal and save in finished signals if needed"""
        signal[1][STATUS_FINISHED] = date_time
        if not is_ext:
            self.required_signals_done[signal[0]] = signal[1]

    def finish(self):
        # run this task for both successfully or failed finish
        # upload logs/data to s3, etc
        print 'finish'
        self._dispose()
        self.finished = True
        self.finish_date = datetime.now()

    def success_finish(self):
        # run this task after scrapy process successfully finished
        print 'success finish'
        self.finished_ok = True

    def _start_scrapy_process(self, cmd=None):
        if not cmd:
            cmd = self.cmd
        self.process = Popen(cmd, shell=True, stdout=PIPE,
                             stderr=PIPE, preexec_fn=os.setsid)
        print 'process started'

    def _establish_connection(self):
        self.conn = self.listener.accept()

    def _dummy_client(self):
        """used to interrupt waiting for the connection from client"""
        Client(LISTENER_ADDRESS).close()

    def try_connect(self, wait):
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
        self.conn.close()
        self.conn = None
        return False

    def try_finish(self, wait):
        """
        runs as last signal, checks if process finished and  has return code
        """
        counter = 0
        while not self._stop_signal and counter < wait:
            time.sleep(1)
            counter += 1
            res = self.process.poll()
            if res is not None:  # don't check for "not res", can be 0
                self.return_code = res
                return True
        # kill process group, if not finished in allowed time
        try:
            self.process.terminate()
            self.return_code = self.process.poll()
            if not self.return_code:
                return False
        except OSError as e:
            print 'Kill process error:', e
        return False

    def run_signal(self, next_signal, step_time_start):
        max_step_time = next_signal[1]['wait']
        if next_signal[0] == SIGNAL_SCRIPT_OPENED:  # first signal
            res = self.try_connect(max_step_time)
            if not res:
                raise ConnectError
            self.signal_succeeded(next_signal, datetime.now(), False)
            return True
        elif next_signal[0] == SIGNAL_SCRIPT_CLOSED:  # last signal
            res = self.try_finish(max_step_time)
            if not res:
                raise FinishError
            self.signal_succeeded(next_signal, datetime.now(), False)
            return True
        step_time_passed = 0
        while not self._stop_signal and step_time_passed < max_step_time:
            has_data = self.conn.poll(max_step_time - step_time_passed)
            sub_step_time = datetime.now()
            step_time_passed += datetime_difference(sub_step_time,
                                                    step_time_start)
            if has_data:
                data = self.conn.recv()
                is_ext, signal = self.get_signal_by_data(data)
                res = self.process_signal_data(signal, data,
                                               sub_step_time, is_ext)
                if not res:
                    raise SignalSentTwiceError
                if not is_ext:
                    return True
        else:
            raise SignalTimeoutError

    def run(self):
        t = Thread(target=self.listen)
        t.start()

    def listen(self):
        start_time = datetime.now()
        while not self._stop_signal:  # run through all signals
            step_time_start = datetime.now()
            next_signal = self.get_next_signal(step_time_start)
            if not next_signal:
                # all steps are finished
                self.success_finish()
                break
            self.current_signal = next_signal
            try:
                self.run_signal(next_signal, step_time_start)
            except FlowError as e:
                self.signal_failed(next_signal, datetime.now(), e)
                break
        finish_time = datetime.now()
        self.finish_date = datetime_difference(finish_time, start_time)
        self.finish()
        print self.report()

    def start(self):
        """start the scrapy process and wait for first signal"""
        start_time = datetime.now()
        self.start_date = start_time
        self._start_scrapy_process()
        first_signal = self.get_next_signal(start_time)
        try:
            self.run_signal(first_signal, start_time)
        except FlowError as e:
            self.signal_failed(first_signal, datetime.now(), e)
            self.finish()
            return False
        return True

    def stop(self):
        """send stop signal, doesn't guaranties to stop immediately"""
        self._stop_signal = True

    def report(self):
        """returns string with the task running stats"""
        # s = ''
        s = self.cmd + '\n'  # todo: remove
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


def main():
    connect_redis('', '')
    read_glob_variables()
    check_required_folders()

    max_tries = MAX_TRIES_TO_GET_TASK
    tasks_taken = []
    branch = None

    try:
        listener = Listener(LISTENER_ADDRESS)
    except AuthenticationError:
        listener = None

    if not listener:
        print 'Socket auth failed!'
        return
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
        task = ScrapyTask(task_data, listener)
        tasks_taken.append(task)


def main_test():
    cmd = ('cd /home/user/projects/tmtext/product-ranking && '
           '. ../../venv-tm/bin/activate && '
           'scrapy crawl amazon_products -a quantity=1 '
           '-a searchterms_str="iphone" -o ~/22.csv '
           '-s LOG_FILE=/tmp/tmp.log -s WITH_SIGNALS=1')
    cmd2 = ('cd /home/user/projects/tmtext/product-ranking && '
           '. ../../venv-tm/bin/activate && '
           'scrapy crawl walmart_products -a quantity=1 '
           '-a searchterms_str="iphone" -o ~/23.csv '
           '-s LOG_FILE=/tmp/tmp.log -s WITH_SIGNALS=1')
    cmd3 = ('cd /home/user/projects/tmtext/product-ranking && '
           '. ../../venv-tm/bin/activate && '
           'scrapy crawl target_products -a quantity=1 '
           '-a searchterms_str="iphone" -o ~/24.csv '
           '-s LOG_FILE=/tmp/tmp.log -s WITH_SIGNALS=1')

    addr = 'localhost', 9080
    l = Listener(addr)
    t1 = ScrapyTask({}, l, cmd)
    t2 = ScrapyTask({}, l, cmd2)
    t3 = ScrapyTask({}, l, cmd3)
    if t1.start():
        print 'run t1'
        t1.run()
    if t2.start():
        print 'run t2'
        t2.run()
    if t3.start():
        print 'run t3'
        t3.run()
    l.close()

main_test()