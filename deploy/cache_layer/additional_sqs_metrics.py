import json
import os
import sys

import boto
import boto.sqs
from boto.s3.key import Key
from boto.ec2.autoscale import AutoScaleConnection

sys.path.insert(1, os.path.join(CWD, '..'))

from cache_layer import REDIS_HOST, REDIS_PORT, INSTANCES_COUNTER_REDIS_KEY, \
    TASKS_COUNTER_REDIS_KEY, HANDLED_TASKS_SORTED_SET
from sqs_ranking_spiders import QUEUES_LIST


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

def get_sqs_metrics(purge=False):
    """
    This function will count sqs metrics and return them in json format
    {"daily_sqs_instance_counter": int,
     "total_tasks_quantity": int}
    """
    redis_db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


    daily_sqs_instances_counter = get_key_or_return_zero(
        INSTANCES_COUNTER_REDIS_KEY, redis_db, purge=purge)

    executed_tasks_during_the_day = get_key_or_return_zero(
        TASKS_COUNTER_REDIS_KEY, redis_db, purge=purge)


    waiting_task = 0
    for queue in QUEUES_LIST.values():
        try:
            q = sqs_conn.get_queue(queue)
            waiting_task += int(q.count())
        except Exception as e:
            print e

    result = {
        'daily_sqs_instances_counter': daily_sqs_instances_counter,
        'executed_tasks_during_the_day': executed_tasks_during_the_day,
        'waiting_task': waiting_task,
    }
    return json.dumps(result)

if __name__ == '__main__':
    print get_sqs_metrics()
    print check_instance_quantity()