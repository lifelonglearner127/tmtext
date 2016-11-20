import os
import sys
from collections import OrderedDict

import boto
import boto.ec2.autoscale


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..', '..', '..'))

sys.path.append(os.path.join(CWD,  '..', '..', '..',
                             'deploy', 'sqs_ranking_spiders'))

from add_task_to_sqs import QUEUES_LIST
from libs import get_autoscale_groups


def get_number_of_messages_in_queues():
    result = OrderedDict()
    conn = boto.sqs.connect_to_region("us-east-1")
    for _, queue_name in QUEUES_LIST.items():
        q = conn.get_queue(queue_name)
        result[queue_name] = q.count()
    return result


def get_number_of_instances_in_autoscale_groups():
    result = OrderedDict()
    conn = boto.ec2.autoscale.connect_to_region("us-east-1")
    for group_name in get_autoscale_groups()['groups']:
        group = conn.get_all_groups([group_name])[0]
        result[group_name] = {
            'group': group,
            'current_size': len([i.instance_id for i in group.instances]),
        }
    return result


def get_max_instances_in_groups():
    result = OrderedDict()
    conn = boto.ec2.autoscale.connect_to_region("us-east-1")
    for group_name in get_autoscale_groups()['groups']:
        group = conn.get_all_groups([group_name])[0]
        result[group_name] = {
            'group': group,
            'max_size': group.max_size,
        }
    return result


def set_autoscale_group_capacity(group, num_instances,
                                 attributes=('min_size', 'max_size', 'desired_capacity')):
    """ Changes "min_size", "max_size", and/or "desired_capacity"
        attributes of the autoscale group """
    conn = boto.ec2.autoscale.connect_to_region("us-east-1")
    group = conn.get_all_groups(names=[group])[0]
    for attrib in attributes:
        setattr(group, attrib, num_instances)
    if attributes:
        group.update()


if __name__ == '__main__':
    print get_number_of_instances_in_autoscale_groups()
