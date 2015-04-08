import os
import sys
import datetime
import json
import time
import multiprocessing as mp
import logging
import logging.config


import boto
import boto.ec2
from boto.s3.key import Key
from boto.ec2.autoscale import AutoScaleConnection


"""This script will stop all remote instances where spider finish
it's task, failed to start scrapy or still wait for tasks.

Instance will not be deleted if task still performed or
file /tmp/remote_instance_starter2.log is blank.

Script should be provided with SSH key so that it can connect to remote
servers.

And should be stored on instance that hace access to amazon
EC2 and autoscale.

After performing tasks script will upload logs to S3 bucket.
"""

# log settings
log_file_path = '/tmp/instances_killer_logs.log'
log_settings = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s:%(message)s'
        }
    },
    'handlers': {
        'to_log_file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': log_file_path
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'default'
        },
    },
    'loggers': {
        'killer_log': {
            'level': 'DEBUG',
            'handlers': ['to_log_file', 'console']
        }
    },
}
logging.config.dictConfig(log_settings)
logger = logging.getLogger('killer_log')
BUCKET_NAME = 'spyder-bucket'
BUCKET_KEY = 'instances_killer_logs'
TOTAL_WAS_TERMINATED = 0

def get_all_group_instances_and_conn():
    conn = AutoScaleConnection()
    globals()['conn'] = conn
    ec2 = boto.ec2.connect_to_region('us-east-1')
    group = conn.get_all_groups(names=['SCCluster1'])[0]
    instance_ids = [i.instance_id for i in group.instances]
    instances = ec2.get_only_instances(instance_ids)
    return instances, conn


def check_logs_status(file_path):
    flag = False
    reason = ''
    if os.path.getsize(file_path) > 3072:
        try:
            f = open(file_path,'r')
        except IOError:
            return flag, reason # error - can't open the log file
        else:
            f.seek(0, 2)
            fsize = f.tell()
            f.seek(max(fsize-3072, 0), 0)
            lines = f.readlines()
            f.close()
            for line in lines:
                if 'Spider default output:' in line or \
                        'Simmetrica events have been pushed...' in line:
                    reason = "Task was finished"
                    flag = True
                elif 'Spider failed to start.' in line:
                    reason = "Spider failed to start"
                    flag = True
            if fsize > 8000:
                m1 = 'No any task messages were found at the queue'
                m2 = 'Try to get task message from queue'
                if m1 in lines[-1] and m2 in lines[-2]:
                    reason = "No any tasks were received for long time"
                    flag = True
    return flag, reason


def teminate_instance_and_log_it(inst_ip, inst_id, reason):
    conn.terminate_instance(inst_id, decrement_capacity=True)
    logger.warning("Instance with ip=%s and id=%s was terminated"
                   " due to reason='%s'.", inst_ip, inst_id, reason)
    globals()['TOTAL_WAS_TERMINATED'] += 1


def stop_if_required(inst_ip, inst_id):
    tmp_file = '/tmp/tmp_file'
    # purge previous entry
    open(tmp_file, 'w').close()
    ssh_key = '/home/ubuntu/.ssh/ubuntu_id_rsa'
    cmd = 'scp -o "StrictHostKeyChecking no" -i %s '\
          'ubuntu@%s:/tmp/remote_instance_starter2.log %s'
    run_cmd = cmd % (ssh_key, inst_ip, tmp_file)
    proc = mp.Process(target=os.system, args=(run_cmd,))
    proc.start()
    checker = 0
    # it will give 30 second to downloads logs.
    while checker < 30:
        if proc.is_alive():
            checker += 1
            time.sleep(1)
        else:
            break
    else:
        proc.terminate()
        return True
    try:
        flag, reason = check_logs_status(tmp_file)
    except:
        return True
    print(inst_id, inst_ip, flag, reason)
    if flag:
        teminate_instance_and_log_it(inst_ip, inst_id, reason)


def update_unresponded_dict_or_terminate_instance(inst_ip, inst_id,
                                                  unresponded):
    if inst_id in unresponded.keys():
        last_time = unresponded[inst_id][1]
        # if instance not responded for 15 minutes already
        if time.time() - int(last_time) > 15*60:
            teminate_instance_and_log_it(
                inst_ip,
                inst_id,
                reason="Instance not respond for 15 minutes"
            )
            del unresponded[inst_id]
    else:
        unresponded[inst_id] = [inst_ip, time.time()]


def upload_logs_to_s3():
    conn = boto.connect_s3()
    bucket = conn.get_bucket(BUCKET_NAME)
    k = Key(bucket)
    k.key = BUCKET_KEY
    k.set_contents_from_filename(log_file_path)


def main():
    instances, conn = get_all_group_instances_and_conn()
    total_instances = len(instances)
    not_responded_hosts = '/tmp/not_responded_hosts'
    if not os.path.exists(not_responded_hosts):
        f = open(not_responded_hosts, 'w')
        f.close()
    with open(not_responded_hosts, 'r') as f:
        try:
            unresponded = json.load(f)
        except:
            unresponded = {}
    for instance in instances:
        print('\n------------')
        # instance is not running
        if instance.state_code != 16:
            update_unresponded_dict_or_terminate_instance(
                instance.ip_address,
                instance.id,
                unresponded
            )
        else:
            inst_ip = instance.ip_address
            inst_id = instance.id
            failed_to_downoad_logs = stop_if_required(inst_ip, inst_id)
            if failed_to_downoad_logs:
                update_unresponded_dict_or_terminate_instance(
                    inst_ip,
                    inst_id,
                    unresponded
                )
    with open(not_responded_hosts, 'w') as f:
        f.write(json.dumps(unresponded))
    logger.info("Were terminated %s instances from %s total.",
                TOTAL_WAS_TERMINATED, total_instances)
    upload_logs_to_s3()

if __name__ == '__main__':
    main()