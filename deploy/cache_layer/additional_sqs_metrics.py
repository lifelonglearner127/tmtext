import json

import boto
import boto.sqs
from boto.s3.key import Key
from boto.ec2.autoscale import AutoScaleConnection


def check_instance_quantity():
    conn = AutoScaleConnection()
    group = conn.get_all_groups(names=['SCCluster1'])[0]
    return len(group.instances)


def get_sqs_metrics(purge=False):
    """
    This function will count sqs metrics and return them in json format
    {"daily_sqs_instance_counter": int,
     "total_tasks_quantity": int}
    """
    AMAZON_BUCKET_NAME = 'spyder-bucket'  # Amazon S3 bucket name
    conn = boto.connect_s3()
    bucket = conn.get_bucket(AMAZON_BUCKET_NAME, validate=False)
    k = Key(bucket)
    result = {}
    keys_names = [
        'daily_sqs_instance_counter',
        'daily_sqs_executed_tasks'
    ]

    # get daily_sqs_instance_counter
    k.key = keys_names[0]
    result[keys_names[0]] = int(k.get_contents_as_string())
    if purge:
        k.set_contents_from_string('0')

    # get daily_sqs_executed_tasks
    k.key = keys_names[1]
    executed_task = k.get_contents_as_string()
    if purge:
        k.set_contents_from_string('0')
    waiting_task = 0
    sqs_conn = boto.sqs.connect_to_region('us-east-1')
    # TODO: import this from sqs_ranking_spiders/__init__.py
    queues_list = {
        'production': 'sqs_ranking_spiders_tasks',
        'dev': 'sqs_ranking_spiders_tasks_dev',
        'test': 'sqs_ranking_spiders_tasks_tests'
    }
    for queue in queues_list.values():
        try:
            q = sqs_conn.get_queue(queue)
            waiting_task += int(q.count())
        except Exception as e:
            print e
    total_tasks_quantity = int(executed_task) + waiting_task
    result['total_tasks_quantity'] = total_tasks_quantity
    return json.dumps(result)

if __name__ == '__main__':
    print get_sqs_metrics()
    print check_instance_quantity()