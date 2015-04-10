import os
import sys
import json
import time
import pickle
import logging
import logging.config

import redis

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(2, os.path.join(CWD, '..', '..', 'special_crawler',
                                'queue_handler'))
from sqs_connect import SQS_Queue

from cache_starter import log_settings

CACHE_TASKS_SQS = 'cache_sqs_ranking_spiders_tasks' # received_requests
CACHE_OUTPUT_QUEUE_NAME = 'cache_sqs_ranking_spiders_output'

SPIDERS_TASKS_SQS = 'sqs_ranking_spiders_tasks_tests'  # tasks to spiders
SPIDERS_PROGRESS_QUEUE_NAME = 'sqs_ranking_spiders_progress'  # rcvd progress report from spiders 
SPIDERS_OUTPUT_QUEUE_NAME = 'sqs_ranking_spiders_output'

# we will redefine it's in set_logger funcion after task will be received
logger = None

def connect_to_redis_database():
    # db = redis.StrictRedis(
    #     host='mycachecluster.6zn94d.0001.usw2.cache.amazonaws.com',
    #     port=6379
    # )
    db = redis.StrictRedis(host='localhost', port=6379, db=0)
    return db


def receive_task_from_server(queue_name=CACHE_TASKS_SQS):
    input_queue = SQS_Queue(queue_name)
    if not input_queue.conn or not input_queue.q:
        print("Task queue not exist or cannot connect to amazon SQS.")
        return
    if not input_queue.empty():
        try:
            message = input_queue.get()
            input_queue.task_done()  #### Uncomment this for production
            message = json.loads(message)
            return message
        except:
            pass
    return


def get_data_from_cache_hash(hash_name, key, database):
    # responses_store = {
    #    'term/url:site:arguments': '(time:response)'}
    return database.hget(hash_name, key)


def get_requests_from_cache(task_stamp, database):
    # requests_store = {
    #    'term/url:site:arguments': '[(time:server), (time:server)]'}
    return database.hget('requests', task_stamp)


def put_requests_into_cache(task_stamp, requests, database):
    database.hmset('requests', {task_stamp: requests})


def put_message_into_sqs(message, sqs_name):
    if not isinstance(message, (str, unicode)):
        message = json.dumps(message)
    sqs_queue = SQS_Queue(sqs_name)
    if getattr(sqs_queue, 'q', '') is None:  # SQS with this name don't exist
        logger.warning(
            "Queue {name} not exist. Create new one".format(name=sqs_name))
        sqs_queue.conn.create_queue(sqs_name)
        time.sleep(5)
        sqs_queue = SQS_Queue(sqs_name)
    try:
        sqs_queue.put(message)
    except Exception, e:
        logger.error("Failed to put message to queue %s:\n%s",
            sqs_name, str(e))


def check_task_status(sqs_name):
    sqs_queue = SQS_Queue(sqs_name)
    status = None
    if sqs_queue.q is None or sqs_queue.empty():
        # There is no results yet
        return status
    try:
        status = sqs_queue.get()
        sqs_queue.task_done()
    except IndexError:
        pass
    return status


def get_spiders_results(sqs_name):
    logger.info("Get spiders results from {sqs}".format(sqs=sqs_name))
    output = None
    sqs_queue = SQS_Queue(sqs_name)
    attemps = 0
    while attemps < 6:
        if sqs_queue.q is None:
            logger.error("Queue %s doesn't exist" % sqs_name)
            time.sleep(5)
            continue
        try:
            output = sqs_queue.get()
            sqs_queue.task_done()
        except Exception as e:
            logger.info(str(e))
            attemps += 1
            time.sleep(5)
            continue
        else:
            break
    return output


def pickle_results(data):
    logger.info("Pickle data")
    pickled_data = pickle.dumps((time.time(), data))
    return pickled_data


def unpickle_data(data):
    logger.info("Unpickle data")
    timestamp, decompressed_data = pickle.loads(data)
    return timestamp, decompressed_data


def put_results_into_cache(task_stamp, data, hash_name, database):
    database.hmset(hash_name, {task_stamp: data})


def load_cache_response_to_sqs(data, sqs_name):
    for part in data:
        put_message_into_sqs(part, sqs_name)


def generate_task_stamp(task_message):
    # TODO: handle single urls // If they are required
    # TODO: store additional arguments
    logger.info("Generate task stamp for task")
    searchterms_str = task_message['searchterms_str']
    site = task_message['site']
    cmd_args = task_message.get('cmd_args', {})
    stamp = "{term}:{site}".format(term=searchterms_str,
                                   site=site)
    for key, value in cmd_args.items():
        stamp += ':{key}:{value}'.format(key=key, value=value)
    return stamp


def generate_and_handle_new_request(task_stamp, task_message, cache_db):
    logger.info("Generate and handle new request")
    response_will_be_provided_by_another_daemon = False
    server_name = task_message['server_name']
    request_item = (time.time(), server_name)
    requests = get_requests_from_cache(task_stamp, cache_db)
    if requests:  # request hash entry existing in database
        requests = pickle.loads(requests)
        if requests:  # request hash not blank
            logger.info("Previous requests were found")
            last_request_time = requests[-1][0]
            # last Request is older than 1 hour
            # we need check only added to spider TASKS SQS request time, not just last
            if time.time() - last_request_time > 3600:
                logger.info("Last request is very old")
                logger.info("Provide new task to spiders SQS")
                put_message_into_sqs(task_message, SPIDERS_TASKS_SQS)
            else:
                logger.info("Last request fresh enough")
                response_will_be_provided_by_another_daemon = True
    else:
        logger.info("No requests were found in cache. Create new one.")
        requests = []
        put_message_into_sqs(task_message, SPIDERS_TASKS_SQS)
    requests.append(request_item)
    pickled_requests = pickle.dumps(requests)
    put_requests_into_cache(task_stamp, pickled_requests, cache_db)
    if response_will_be_provided_by_another_daemon:
        sys.exit()

    spiders_progress_queue = server_name + SPIDERS_PROGRESS_QUEUE_NAME
    spiders_output_queue = server_name + SPIDERS_OUTPUT_QUEUE_NAME

    counter = 0
    logger.info("Check for spider status")
    while True:
        status = check_task_status(spiders_progress_queue)
        if status and 'failed' in status:
            counter += 1
            if counter <= 3:
                logger.warning("Receive failed status. Restart spider.")
                put_request_into_sqs(task_message, SPIDERS_TASKS_SQS)
                continue
            else:
                logger.error("Spider still not working. Exit.")
                sys.exit()
        if status and 'finished' in status:
            break

    output = get_spiders_results(spiders_output_queue)
    if not output:
        logger.error("Don't receive output from spider")
        sys.exit()

    pickled_output = pickle_results(output)
    logger.info("Pickled output: %s", pickled_output) ##########
    logger.info("Update response object for this search term in cache")
    put_results_into_cache(
        task_stamp, pickled_output, 'responses', cache_db)

    logger.info("Renew requests list")
    requests = get_requests_from_cache(task_stamp, cache_db)
    requests = pickle.loads(requests)
    logger.info("Return data to all requests/servers")
    while requests:
        item = requests.pop()
        logger.info("Request: %s", item)
        server_name = item[1]
        cache_output_queue = server_name + CACHE_OUTPUT_QUEUE_NAME
        logger.info("Uploading response data to server queue")
        put_message_into_sqs(output, cache_output_queue)
        
    logger.info("Update requests database entry with blank requests list")
    requests = pickle.dumps(requests)
    cache_db.hmset('requests', {task_stamp: requests})


def set_logger(task_message):
    global logger
    task_id = task_message['task_id']
    log_file_path = '/tmp/cache_logs/%s_sqs_cache' % task_id
    log_settings['handlers']['to_log_file']['filename'] = log_file_path
    logging.config.dictConfig(log_settings)
    logger = logging.getLogger('cache_log')


def main(queue_name):
    cache_db = connect_to_redis_database()
    attemps = 0
    while attemps < 3:
        task_message = receive_task_from_server(queue_name)   
        if not task_message:
            attemps += 1
            time.sleep(1)
            continue
        break
    else:
        # no any messages was found - this is duplicated instance
        sys.exit()
    set_logger(task_message)
    logger.info("Task was succesfully received:\n%s", task_message)
    task_stamp = generate_task_stamp(task_message)
    logger.debug("Task stamp:     %s", task_stamp)
    response = get_data_from_cache_hash('responses', task_stamp, cache_db)
    server_name = task_message['server_name']
    # freshness = task_message['freshness']
    freshness = 30*60 # 12*60*60 // 3.5*12*60*60

    if response:
        logger.info("Use existing response")
        timestamp, output = unpickle_data(response)
        if time.time() - timestamp < freshness:
            logger.info("Existing response fresh enough")
            # change _msg_id for output msg
            json_output = json.loads(output)
            json_output['_msg_id'] = task_message.get('task_id', None)
            cache_output_queue = server_name + CACHE_OUTPUT_QUEUE_NAME
            logger.info("Uploading response data to servers queue")
            put_message_into_sqs(json_output, cache_output_queue)
        # Response exist but it's too old
        else:
            logger.info("Existing response not satisfy freshness")
            generate_and_handle_new_request(task_stamp, task_message, cache_db)
    # Response not exist at all
    else:
        logger.info("Existing response wasn't found for this task")
        generate_and_handle_new_request(task_stamp, task_message, cache_db)


if (__name__ == '__main__'):
    if len(sys.argv) > 1:
        queue_name = sys.argv[1].strip()
    else:
        queue_name = CACHE_TASKS_SQS
    main(queue_name)
