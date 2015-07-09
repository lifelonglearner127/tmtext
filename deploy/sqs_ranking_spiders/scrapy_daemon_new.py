# pass imports for now
from multiprocessing.connection import Listener, AuthenticationError
from sqs_ranking_spiders.fake_sqs_queue_class import SQS_Queue


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


def delete_task_from_sqs():
    # get from daemon
    pass


def get_branch_for_task(task_data):
    return task_data.get('branch_name')


def set_working_branch(branch):
    # get from daemon
    pass


def is_same_branch(b1, b2):
    return b1 == b2


class ScrapyTask(object):

    def __init__(self, task_data):
        self.task_data = task_data
        self.items_scraped = 0
        self.errors = 0
        self.is_started = False
        self.is_spider_finished = False
        self.is_fully_finished = False
        self.stop_signal = False

    def get_unique_name(self):
        # convert task data into unique name
        return ''

    def spider_opened_signal(self, spider):
        self.is_started = True

    def spider_closed_signal(self, spider):
        self.is_spider_finished = True

    def item_scraped_signal(self, item, response, spider):
        self.items_scraped += 1

    def spider_error_signal(self, failure, response, spider):
        self.errors += 1

    def get_next_signal(self):
        # must return tuple of signal name and time to wait in seconds
        # if none, then all steps are finished
        return '', 0

    def listen(self):
        step_time = 15
        try:
            # requires sudo
            l = Listener(('localhost', 6000), authkey='123')
        except AuthenticationError:
            # wrong auth key
            return
        conn = l.accept()
        while not self.stop_signal:
            next_signal = self.get_next_signal()
            if not next_signal:
                # all steps are finished
                print 'task is finished'
                break
            max_time = next_signal[1]
            passed_time = 0
            while not self.stop_signal and passed_time < max_time:
                has_data = conn.poll(step_time)

                if has_data:
                    data = conn.recv()
                    # process collected data
                    # move to next signal
                    break
                else:
                    # wait more untill limit of allowed time
                    passed_time += step_time


def main(max_tasks_number):
    connect_redis('', '')
    read_glob_variables()

    max_tries = 50
    tasks_taken = []
    branch = None

    queue = SQS_Queue('some queue')

    while len(tasks_taken) < max_tasks_number or not max_tries:
        max_tries -= 1
        task_data = get_task_from_sqs()
        # get branch from first task
        if not tasks_taken:
            branch = get_branch_for_task(task_data)
        elif not is_same_branch(get_branch_for_task(task_data), branch):
            # tasks have different branches, skip
            continue
        delete_task_from_sqs()
        task = ScrapyTask(task_data)
        tasks_taken.append(task)

    # run multiprocess connection to listen for signals on some port
    # in separate thread
    # tasks_taken[N].listen