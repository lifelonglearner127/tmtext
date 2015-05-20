import json

import boto
import boto.sqs
from boto.s3.key import Key
from boto.ec2.autoscale import AutoScaleConnection


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

def get_sqs_metrics(purge=False):
    """
    This function will count sqs metrics and return them in json format
    {"daily_sqs_instance_counter": int,
     "total_tasks_quantity": int}
    """
    AMAZON_BUCKET_NAME = 'spyder-bucket'  # Amazon S3 bucket name
    conn = boto.connect_s3()
    bucket = conn.get_bucket(AMAZON_BUCKET_NAME, validate=False)
    result = {}
    keys_names = [
        'daily_sqs_instance_counter',
        'daily_sqs_executed_tasks',
        'previous_day_tasks_at_sqs'
    ]

    # get daily_sqs_instance_counter
    result[keys_names[0]] = get_key_value(keys_names[0], bucket, purge=purge)

    # get daily_sqs_executed_tasks
    executed_task = get_key_value(keys_names[1], bucket, purge=purge)
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
    previous_day_tasks_at_sqs = get_key_value(keys_names[2], bucket,
        next_value=waiting_task)
    total_tasks_quantity = int(executed_task) + waiting_task -\
        previous_day_tasks_at_sqs
    result['total_tasks_quantity'] = total_tasks_quantity
    return json.dumps(result)

if __name__ == '__main__':
    print get_sqs_metrics()
    print check_instance_quantity()