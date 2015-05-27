import os
import sys
import random

from boto.ec2.autoscale import AutoScaleConnection
from boto.utils import get_instance_metadata

"""This script will try to stop instance by itself.

Instance will not be deleted if task still performed or
file /tmp/remote_instance_starter2.log is blank.
"""

def check_logs_status(file_path):
    flag = False
    reason = ''
    if os.path.getsize(file_path) > 1024:
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
    return flag, reason

def main():
    conn = AutoScaleConnection()
    instance_id = get_instance_metadata()['instance-id']
    log_file = '/tmp/remote_instance_starter2.log'
    flag = check_logs_status(log_file)
    if flag:
        conn.terminate_instance(instance_id, decrement_capacity=True)
        print("WARNING:Instance id=%s was terminated" % instance_id)

if __name__ == '__main__':
    main()