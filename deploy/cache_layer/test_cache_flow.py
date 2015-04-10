from boto.sqs.message import Message
import boto.sqs
import random
import json

from cache_starter import TASK_QUEUES_LIST

"""
To use this script you need:
1. Start redis database like:
$ /etc/init.d/redis_6379 start
2. Start cache_starter:
$ python cache_starter.py
"""

def provide_task_msg_to_sqs(sfas):
    conn = boto.sqs.connect_to_region('us-east-1')
    queue_name = random.choice(TASK_QUEUES_LIST)
    q = conn.get_queue(queue_name)
    m = Message()
    task_id = random.randint(1000000, 2000000)
    msg = {"searchterms_str": "water",
           "server_name": "test_server_name2",
           "cmd_args": {"quantity": 5},
           "site": "walmart",
           "task_id": task_id}
    m.set_body(json.dumps(msg))
    q.write(m)
    print(task_id)


if (__name__ == '__main__'):
    provide_task_msg_to_sqs(TASK_QUEUES_LIST)