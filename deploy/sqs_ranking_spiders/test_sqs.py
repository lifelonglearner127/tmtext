import json
from boto.sqs.message import Message
from boto.sqs import connect_to_region as connect_sqs
from boto.s3 import connect_to_region as connect_s3


def generate_tasks():
    """
    returns dictionaries with tasks to be pushed to sqs
    keys of dictionary are ids for the task
    """
    # TODO
    # query term of one word
    # query term as phrase
    # query term with non ascii characters
    # walmart with best sellers
    # few product urls
    # additional cmd args
    tasks = []
    tasks_dict = {}
    return tasks_dict


def add_additional_task_params(tasks, add_to_cmd_args=False, **params):
    """add some parameters to the tasks"""
    for task in tasks.itervalues():
        if add_to_cmd_args:
            task.update(params)
        else:
            if 'cmd_args' not in task:
                task['cmd_args'] = {}
            task['cmd_args'].update(params)


def get_or_create_sqs_queue(conn, queue_name):
    """create and return sqs queue"""
    try:
        queue = conn.get_queue(queue_name)
    except Exception as e:
        queue = conn.create_queue(queue_name)
    return queue


def push_tasks_to_sqs(tasks, queue):
    """put tasks to sqs queue"""
    for task in tasks:
        data = json.dumps(task)
        m = Message()
        m.set_body(data)
        queue.write(m)


def get_message_from_queue(queue, wait_time):
    """read and delete one message from given queue (if any)"""
    msg = queue.read(wait_time)
    if msg:
        data = json.loads(msg.get_body())
        queue.delete_message(msg)
        return data


def check_s3_key(bucket, key):
    """returns True if key exists and not empty, else False"""
    item = bucket.lookup(key)
    if item and item.size:
        return True
    return False


def check_tasks_completed(tasks, wait_minutes, output_queue, s3_bucket):
    """check all pushed tasks to be completed"""
    max_wait_time = wait_minutes * 60
    step_time = 10
    for _ in xrange(0, max_wait_time, step_time):
        message = get_message_from_queue(output_queue, step_time)
        if not message:
            continue
        task_id = message['_msg_id']
        res = check_s3_key(s3_bucket, message['s3_key_data'])
        if res:
            tasks.pop(task_id, None)
        if not tasks:
            return True  # return True only when all tasks finished working
    return False


def log_failed_tasks(tasks):
    pass


def main():
    sqs_conn = connect_sqs('us-east-1')
    s3_conn = connect_s3('us-east-1')
    bucket = s3_conn.get_bucket('spyder-bucket')
    max_wait_minutes = 30
    server_name = 'sqs_test'
    output_queue_name = '%ssqs_ranking_spiders_output' % (server_name,)
    progress_queue_name = '%ssqs_ranking_spiders_progress' % (server_name,)
    output_queue = get_or_create_sqs_queue(sqs_conn, output_queue_name)
    progress_queue = get_or_create_sqs_queue(sqs_conn, progress_queue_name)
    tasks_queue = get_or_create_sqs_queue(sqs_conn, 'sqs_ranking_spiders_tasks_tests')

    tasks = generate_tasks()

    # we never store and retrieve data to/from cache
    add_additional_task_params(
        tasks, sqs_cache_save_ignore=True, sqs_cache_get_ignore=True,
        server_name=server_name)

    push_tasks_to_sqs(tasks, tasks_queue)
    res = check_tasks_completed(tasks, max_wait_minutes, output_queue, bucket)
    if res:
        # everything is ok
        pass
    else:
        log_failed_tasks(tasks)


