from math import ceil
import boto.sqs
from boto.ec2.autoscale import AutoScaleConnection


def get_sqs_tasks_count():
    q_prefix = 'sqs_ranking_spiders'
    tasks_count = 0
    try:
        conn = boto.sqs.connect_to_region('us-east-1')
        queues = conn.get_all_queues(prefix=q_prefix)
        tasks_count = sum(q.count() for q in queues)
    except Exception as e:
        print e
    return tasks_count


def scale_instances(tasks_per_instance):
    conn = AutoScaleConnection()
    group = conn.get_all_groups(names=['SCCluster1'])[0]

    if group.desired_capacity == group.max_size:
        print 'Maximum number of instances reached'
        return
    tasks_count = get_sqs_tasks_count()
    if not tasks_count:
        print 'No tasks left in queues'
        return
    print 'Num of tasks in queues', tasks_count
    tasks_per_instance *= 1.0  # convert to float
    additional_instances_count = ceil(tasks_count/tasks_per_instance)
    updated_instances_count = \
        group.desired_capacity + additional_instances_count
    # consider max allowed instances
    if updated_instances_count > group.max_size:
        updated_instances_count = group.max_size
    print 'Updating group from %s to %s instances' % (
        group.desired_capacity, updated_instances_count)
    group.set_capacity(updated_instances_count)
    group.desired_capacity = updated_instances_count
    group.update()
    print 'Done'


if __name__ == '__main__':
    scale_instances(12)
