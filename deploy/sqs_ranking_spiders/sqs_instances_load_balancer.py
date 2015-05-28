import boto
import boto.sqs
import boto.ec2
from boto.ec2.autoscale import AutoScaleConnection


def check_qunatity_of_waiting_tasks():
    sqs_conn = boto.sqs.connect_to_region('us-east-1')
    queues_list = [
        'sqs_ranking_spiders_tasks_tests',
        'sqs_ranking_spiders_tasks',
        'sqs_ranking_spiders_tasks_dev',
    ]
    total_waiting_tasks = 0
    for queue_name in queues_list:
        try:
            queue = sqs_conn.get_queue(queue_name)
            total_waiting_tasks += int(queue.count())
        except Exception as e:
            print e
    return total_waiting_tasks


def scale_autoscale_group():
    waiting_tasks = check_qunatity_of_waiting_tasks()
    print "waiting_tasks %s" % waiting_tasks
    autoscale_conn = AutoScaleConnection()
    group = autoscale_conn.get_all_groups(names=['SCCluster1'])[0]

    exist_capacity = int(group.desired_capacity)

    if waiting_tasks in range(20,100):
        waiting_tasks = 20
    if waiting_tasks in range(100,201):
        waiting_tasks = 50
    if waiting_tasks >= 201:
        waiting_tasks = 100
    new_instances_quantity = min((waiting_tasks + exist_capacity),
                                 (int(group.max_size) - 30))
    group.set_capacity(new_instances_quantity)
    group.desired_capacity = new_instances_quantity
    group.update()
    print "Group was ajdusted to %s instances from %s instances" % \
          (new_instances_quantity, exist_capacity)

if __name__ == '__main__':
    scale_autoscale_group()