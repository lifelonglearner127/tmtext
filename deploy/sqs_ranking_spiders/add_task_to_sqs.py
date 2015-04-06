import sys
import json
import random

from boto.sqs.message import Message
import boto.sqs


TASK_QUEUES_LIST = {
    'production': 'sqs_ranking_spiders_tasks',
    'dev': 'sqs_ranking_spiders_tasks_dev',
    'test': 'sqs_ranking_spiders_tasks_tests'
}

### Script can be run with 'manual' argument to provide manual edditing
# of task message

def put_msg_to_sqs(message, queue_name=TASK_QUEUES_LIST['test']):
    conn = boto.sqs.connect_to_region("us-east-1")
    q = conn.get_queue(queue_name)
    m = Message()
    m.set_body(json.dumps(message))
    q.write(m)
    print("Task was provided to sqs %s" % queue_name)
    print("Task:\n%s" % message)


def edit_message(msg):
    keys = ['task_id', 'site', 'searchterms_str', 'server_name']
    for key in keys:
        data = raw_input("Provide '%s' for task message.\n"
                         "If you left field blunk default value will be used.\n"
                         ">>> " % key)
        if data:
            msg[key] = data
    additional_args = raw_input("Provide additional arguments if required "
                                "in format arg=value;arg2=value2\n>>> ")
    args_dict = {}
    for i in additional_args.split(';'):
        splited = i.split('=')
        args_dict[splited[0]] = splited[1]
    if 'quantity' not in args_dict.keys():
        args_dict['quantity'] = 100
    msg['cmd_args'] = args_dict


if __name__ == '__main__':
    msg = {
            'task_id': 4444,
            'site': 'amazon',
            'searchterms_str': random.choice(['water', 'cola', 'wine']),
            'server_name': 'test_server_name',
            # "url": "http://www.walmart.com/ip/42211446?productRedirect=true",
            'cmd_args': {'quantity': 30}
        }
    if 'manual' in [a.lower().strip() for a in sys.argv]:
        edit_message(msg)
    put_msg_to_sqs(msg)