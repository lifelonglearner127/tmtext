import os
import sys
import random

import boto
import boto.ec2
from boto.ec2.autoscale import AutoScaleConnection


"""This script will stop all remote instances where spider finish
it's task, failed to start scrapy or still wait for tasks.

Instance will not be deleted if task still performed or
file /tmp/remote_instance_starter2.log is blank.

Script should be provided with SSH key so that it can connect to remote
servers.

And should be stored on instance that hace access to amazon
EC2 and autoscale.
"""

def get_all_group_instances_and_conn():
    conn = AutoScaleConnection()
    ec2 = boto.ec2.connect_to_region('us-east-1')
    group = conn.get_all_groups(names=['SCCluster1'])[0]
    instance_ids = [i.instance_id for i in group.instances]
    instances = ec2.get_only_instances(instance_ids)
    return instances, conn


def check_logs_status(file_path):
    flag = False
    if os.path.getsize(file_path) > 3072:
        try:
            f = open(file_path,'r')
        except IOError:
            return  # error - can't open the log file
        else:
            f.seek(0, 2)
            fsize = f.tell()
            f.seek(max(fsize-3072, 0), 0)
            lines = f.readlines()
            f.close()
            for line in lines:
                if 'Spider default output:' in line:
                    print("Task was finished")
                    flag = True
                elif 'Spider failed to start.' in line:
                    print("Spider failed to start")
                    flag = True
            l = ' '.join(lines[-4:])
            if l.count('No any task messages were found at the queue') > 1:
                print("No any tasks were received")
                flag = True 
    return flag

def main():
    instances, conn = get_all_group_instances_and_conn()
    tmp_file = '/tmp/tmp_file'
    cmd = 'scp -o "StrictHostKeyChecking no" -i /tmp/ubuntu_id_rsa '\
          'ubuntu@%s:/tmp/remote_instance_starter2.log %s'
    for instance in instances:
        ip = instance.ip_address
        run_cmd = cmd % (ip, tmp_file)
        res = os.system(run_cmd)
        # in case of no log file exists
        if res > 0:
            continue
        flag = check_logs_status(tmp_file)
        print(instance, ip, flag)
        if flag:
            conn.terminate_instance(instance.id)
            print("WARNING:Instance with ip=%s and id=%s was terminated" % 
                  (instance.ip_address, instance.id))
            print('\n------------')

if __name__ == '__main__':
    if random.randrange(10) != 0:
        sys.exit()
    main()