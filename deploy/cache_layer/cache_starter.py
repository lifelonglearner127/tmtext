import os
import sys
import time
import random
import logging
import logging.config
import subprocess


import boto.sqs

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..'))

from cache_layer import CACHE_QUEUES_LIST

log_file_path = '/tmp/cache_logs/main_instance.log'
if not os.path.exists(os.path.dirname(log_file_path)):
    os.makedirs(os.path.dirname(log_file_path))
log_settings = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s [%(module)s] %(levelname)s:%(message)s'
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
        'cache_log': {
            'level': 'DEBUG',
            'handlers': ['to_log_file', 'console']
        }
    },
}


def can_run():
    cmd = 'ps aux'
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    counter = 0
    for line in out.splitlines():
        if 'cache_starter.py' in line:
            counter += 1
    if counter >= 3:
        return False
    return True


def main_starter(CACHE_QUEUES_LIST):
    conn = boto.sqs.connect_to_region("us-east-1")  #should be us-east-1
    cmd = 'python sqs_cache.py %s &'
    while True:
        for queue_name in CACHE_QUEUES_LIST.values():
            queue = conn.get_queue(queue_name)
            try:
                if queue.count() > 0:
                    logger.info("Start cache service for sqs '%s'", queue_name)
                    run_cmd = cmd % queue_name
                    os.system(run_cmd)
            except Exception as e:
                logger.info("Queue '%s' does not exists", queue_name)
                logger.info("Exception: %s", e)
                try:
                    conn.create_queue(queue_name)
                except:
                    pass
                continue
        time.sleep(3)


if __name__ == '__main__':
    time.sleep(random.randrange(10))
    if not can_run():
        sys.exit()
    logging.config.dictConfig(log_settings)
    logger = logging.getLogger('cache_log')
    main_starter(CACHE_QUEUES_LIST)
