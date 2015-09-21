# import boto
# import boto.sqs
# import boto.ec2
# from boto.ec2.autoscale import AutoScaleConnection
#
#
# def check_qunatity_of_waiting_tasks():
#     sqs_conn = boto.sqs.connect_to_region('us-east-1')
#     queues_list = [
#         'sqs_ranking_spiders_tasks_tests',
#         'sqs_ranking_spiders_tasks',
#         'sqs_ranking_spiders_tasks_dev',
#     ]
#     total_waiting_tasks = 0
#     for queue_name in queues_list:
#         try:
#             queue = sqs_conn.get_queue(queue_name)
#             total_waiting_tasks += int(queue.count())
#         except Exception as e:
#             print e
#     return total_waiting_tasks
#
#
# def scale_autoscale_group():
#     waiting_tasks = check_qunatity_of_waiting_tasks()
#     print "waiting_tasks %s" % waiting_tasks
#     autoscale_conn = AutoScaleConnection()
#     group = autoscale_conn.get_all_groups(names=['SCCluster1'])[0]
#
#     exist_capacity = int(group.desired_capacity)
#
#     if waiting_tasks in range(20,100):
#         waiting_tasks = 20
#     if waiting_tasks in range(100,201):
#         waiting_tasks = 50
#     if waiting_tasks >= 201:
#         waiting_tasks = 100
#     new_instances_quantity = min((waiting_tasks + exist_capacity),
#                                  (int(group.max_size) - 30))
#     group.set_capacity(new_instances_quantity)
#     group.desired_capacity = new_instances_quantity
#     group.update()
#     print "Group was ajdusted to %s instances from %s instances" % \
#           (new_instances_quantity, exist_capacity)
#
# if __name__ == '__main__':
#     scale_autoscale_group()
#

from math import ceil
import boto.sqs
from boto.ec2.autoscale import AutoScaleConnection


def get_sqs_tasks_count():
    q_prefix = 'sqs_ranking_spiders'
    tasks_count = 0
    try:
        conn = boto.sqs.connect_to_region('us-east-1')
        queues = conn.get_all_queues(prefx=q_prefix)
        tasks_count = sum(q.count() for q in queues)
    except Exception as e:
        print e
    return tasks_count


def scale_instances(tasks_per_instance):
    conn = AutoScaleConnection()
    group = conn.get_all_groups('SCCluster1')[0]

    if group.desired_capacity == group.max_size:
        print 'Maximum number of instances reached'
        return
    tasks_count = get_sqs_tasks_count()
    if not tasks_count:
        print 'No tasks left in queues'
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
    group.update()
    print 'Done'
