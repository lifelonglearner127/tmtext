import os
import sys
import random
import time
import logging
import logging.config

from boto.ec2.autoscale import AutoScaleConnection
from boto.utils import get_instance_metadata
import boto
from boto.s3.key import Key

"""This script will try to stop instance by itself.

Instance will not be deleted if task still performed or
file /tmp/remote_instance_starter2.log is blank.
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
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': log_file_path,
            'maxBytes': 1024*1024*1024, # 1GB
            'backupCount': 1,
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
    flag, reason = check_logs_status(log_file)
    if flag and reason:
        os.system('rm %s' % log_file)
        s3_conn = boto.connect_s3()
        bucket = s3_conn.get_bucket(BUCKET_NAME)
        k = Key(bucket)
        k.key = BUCKET_KEY
        global log_file_path
        time.sleep(70)
        # Try to upload logs prior to stop server
        os.system('python upload_logs_to_s3.py')
        k.get_contents_to_filename(log_file_path)
        logger.warning("Instance with id=%s was terminated"
                   " due to reason='%s'. "
                   "Instance was killed by itself.", instance_id, reason)
        k.set_contents_from_filename(log_file_path)
        conn.terminate_instance(instance_id, decrement_capacity=True)

if __name__ == '__main__':
    main()