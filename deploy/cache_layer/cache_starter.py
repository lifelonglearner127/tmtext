import os
import sys
import time
import random
import logging
import logging.config

import boto.sqs


TASK_QUEUES_LIST = [
    'cache_sqs_ranking_spiders_tasks',  # production one
    'cache_sqs_ranking_spiders_tasks_dev',  # development one
    'cache_sqs_ranking_spiders_tasks_tests',  # test one
]

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
    return not os.path.exists(os.path.join(os.getcwd(), __file__+'.running'))


def mark_as_running():
    with open(os.path.join(os.getcwd(), __file__+'.running'), 'w') as fh:
        fh.write('1')


def main_starter(TASK_QUEUES_LIST):
    conn = boto.sqs.connect_to_region("us-east-1")  #should be us-east-1
    cmd = 'python sqs_cache.py %s &'
    while True:
        for queue_name in TASK_QUEUES_LIST:
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


if (__name__ == '__main__'):
    time.sleep(random.randrange(10))
    if not can_run():
        sys.exit()
    mark_as_running()
    logging.config.dictConfig(log_settings)
    logger = logging.getLogger('cache_log')
    main_starter(TASK_QUEUES_LIST)
