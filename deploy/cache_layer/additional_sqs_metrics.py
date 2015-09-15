import json
import os
import sys
import time

import boto
import boto.sqs
from boto.s3.key import Key
from boto.ec2.autoscale import AutoScaleConnection
import redis

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..'))

from cache_layer import REDIS_HOST, REDIS_PORT, INSTANCES_COUNTER_REDIS_KEY, \
    TASKS_COUNTER_REDIS_KEY, HANDLED_TASKS_SORTED_SET
try:
    from sqs_ranking_spiders import QUEUES_LIST
except ImportError:
    QUEUES_LIST = {
        'urgent': 'sqs_ranking_spiders_tasks_urgent',
        'production': 'sqs_ranking_spiders_tasks',
        'dev': 'sqs_ranking_spiders_tasks_dev',
        'test': 'sqs_ranking_spiders_tasks_tests'
    }


def check_instance_quantity():
    conn = AutoScaleConnection()
    group = conn.get_all_groups(names=['SCCluster1'])[0]
    return len(group.instances)


def get_key_value(key_name, bucket, purge=False, next_value=False):
    k = Key(bucket)
    k.key = key_name
    try:
        result = int(k.get_contents_as_string())
    except:
        k.set_contents_from_string('0')
        result = 0
    # in case get_contets_as_string return blank string ''
    if not result:
        result = 0
    if purge:
        k.set_contents_from_string('0')
    if next_value:
        if not isinstance(next_value, str):
            next_value = str(next_value)
        k.set_contents_from_string(next_value)
    return result

def get_key_or_return_zero(key, redis_db, purge):
    try:
        result = int(redis_db.get(key))
        if purge:
            redis_db.set(key, 0)
    except Exception as e:
        print e
        result = 0
    return result

def get_tasks_for_time_limit(redis_db, hours_limit=1):
    max_limit = time.time()
    min_limit = max_limit - 3600*hours_limit
    try:
        tasks = len(redis_db.zrangebyscore(HANDLED_TASKS_SORTED_SET,
                                           min_limit, max_limit))
    except:
        tasks = 0
    return tasks

def get_average_tasks(redis_db, hours_limit=1):
    """Counts how many tasks per hour were performed
    during required hours_limit"""
    tasks = get_tasks_for_time_limit(redis_db, hours_limit)
    average = tasks/float(hours_limit)
    return average


def get_sqs_metrics(purge=False, hours_limit=1):
    """
    This function will count sqs metrics and return them in json format
    {
    "daily_sqs_instances_counter": int,
    "executed_tasks_during_the_day": int,
    "waiting_task": int,
     }
    """
    redis_db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


    daily_sqs_instances_counter = get_key_or_return_zero(
        INSTANCES_COUNTER_REDIS_KEY, redis_db, purge=purge)

    executed_tasks_during_the_day = get_key_or_return_zero(
        TASKS_COUNTER_REDIS_KEY, redis_db, purge=purge)


    waiting_task = 0
    sqs_conn = boto.sqs.connect_to_region('us-east-1')
    for queue in QUEUES_LIST.values():
        try:
            q = sqs_conn.get_queue(queue)
            waiting_task += int(q.count())
        except Exception as e:
            print e

    task_during_last_hour = get_tasks_for_time_limit(redis_db, 1)
    average_tasks = get_average_tasks(redis_db, hours_limit)

    result = {
        'daily_sqs_instances_counter': daily_sqs_instances_counter,
        'executed_tasks_during_the_day': executed_tasks_during_the_day,
        'waiting_task': waiting_task,
        'task_during_last_hour': task_during_last_hour,
        'average_tasks': average_tasks
    }
    return json.dumps(result)

if __name__ == '__main__':
    print get_sqs_metrics()
    print check_instance_quantity()