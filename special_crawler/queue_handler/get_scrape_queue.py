#!/usr/bin/env python

'''
Gist : Scrape Queue -> Scrape -> Process Queue

'''

from sqs_connect import SQS_Queue
import logging
import sys
import time
import json
import requests
import threading
import urllib
from datetime import datetime

import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection

import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import crawler_service

# initialize the logger
logger = logging.getLogger('basic_logger')
logger.setLevel(logging.DEBUG)
fh = logging.StreamHandler()
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

queue_names = {
    "Development": "dev_scrape", 
    "UnitTest": "unit_test_scrape", 
    "IntegrationTest": "integration_test_scrape", 
    "RegressionTest": "test_scrape",
    "Demo": "demo_scrape", 
    "Production": "production_scrape",
    "Walmartfullsite": "walmart-fullsite_scrape",
    "Walmartondemand": "walmart-ondemand_scrape",
    "WalmartMPHome": "walmart-mp_home_scrape",
    "WalmartScrapeTO": "walmart-mp_scrapeto",
    "Productioncustomer": "production_customer_scrape",
    "wm_production_scrape": "wm_production_scrape"
}

INDEX_ERROR = "IndexError : The queue was really out of items, but the count was lagging so it tried to run again."

FETCH_FREQUENCY = 60

def main( environment, scrape_queue_name, thread_id):
    logger.info( "Starting thread %d" % thread_id)
    # establish the scrape queue
    sqs_scrape = SQS_Queue( scrape_queue_name)

    last_fetch = datetime.min

    proxy = None
    walmart_proxy_crawlera = None
    walmart_proxy_proxyrain = None
    walmart_proxy_shaderio = None
    walmart_proxy_luminati = None
    api_key = None
    walmart_api_key = None

    # Continually pull off the SQS Scrape Queue
    while True:
        go_to_sleep = False
        
        if sqs_scrape.count() == 0:
            go_to_sleep = True

        if not go_to_sleep:
            try:
                # Get message from SQS
                message = sqs_scrape.get()
            except IndexError as e:
                # This exception will most likely be triggered because you were grabbing off an empty queue
                go_to_sleep = True
            except Exception as e:
                # Catch all other exceptions to prevent the whole thing from crashing
                # TODO : Consider testing that sqs_scrape is still live, and restart it if need be
                go_to_sleep = True
                logger.warn(e)

        if not go_to_sleep:
            try:
                # De-serialize to a json object
                message_json = json.loads(message)

                # Vars from the json object
                url = message_json['url']
                site = message_json['site']
                site_id = message_json['site_id']
                server_name = message_json['server_name']
                product_id = message_json['product_id']
                event = message_json['event']

                additional_requests = message_json.get('additional_requests')

                LogHistory.start_log()

                LogHistory.add_log('url', url)
                LogHistory.add_log('server_hostname', message_json.get('server_hostname'))
                LogHistory.add_log('pl_name', message_json.get('pl_name'))

                logger.info("Received: thread %d server %s url %s" % ( thread_id, server_name, url))

                if (datetime.now() - last_fetch).seconds > FETCH_FREQUENCY:
                    amazon_bucket_name = 'ch-settings'
                    key_file = 'proxy_settings.cfg'

                    try:
                        S3_CONN = boto.connect_s3(is_secure=False)
                        S3_BUCKET = S3_CONN.get_bucket(amazon_bucket_name, validate=False)
                        k = Key(S3_BUCKET)
                        k.key = key_file
                        key_dict = json.loads(k.get_contents_as_string())

                        proxy = key_dict['default']
                        walmart_proxy_crawlera = int(key_dict['walmart']['crawlera'])
                        walmart_proxy_proxyrain = int(key_dict['walmart']['proxyrain'])
                        walmart_proxy_shaderio = int(key_dict['walmart']['shaderio'])
                        walmart_proxy_luminati = int(key_dict['walmart']['luminati'])
                        api_key = key_dict['crawlera']['api_keys']['default']
                        walmart_api_key = key_dict['crawlera']['api_keys']['walmart']

                        logger.info('FETCHED PROXY CONFIG')
                        last_fetch = datetime.now()

                    except Exception as e:
                        logger.warn(e)
                        logger.warn('FAILED TO FETCH PROXY CONFIG')

                max_retries = 3

                for i in range(1, max_retries):
                    # Scrape the page using the scraper running on localhost
                    get_start = time.time()

                    try:
                        site = crawler_service.extract_domain(url)
                        LogHistory.add_log('scraper_type', site)

                        # create scraper class for requested site
                        site_scraper = crawler_service.SUPPORTED_SITES[site](url=url,
                            bot = None,
                            additional_requests = additional_requests,
                            api_key = api_key,
                            walmart_api_key = walmart_api_key,
                            proxy = proxy,
                            walmart_proxy_crawlera = walmart_proxy_crawlera,
                            walmart_proxy_proxyrain = walmart_proxy_proxyrain,
                            walmart_proxy_shaderio = walmart_proxy_shaderio,
                            walmart_proxy_luminati = walmart_proxy_luminati)

                        output_json = site_scraper.product_info()
                        LogHistory.add_log('failure_type', output_json.get('failure_type'))

                    except Exception as e:
                        get_end = time.time()

                        print 'Error extracting output json', type(e), e
                        logger.warn(e)

                        output_json = {
                            "error":str(e),
                            "date":datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'),
                            "status":"failure",
                            "page_attributes":{"loaded_in_seconds":round(get_end-get_start,2)}}

                    output_json['attempt'] = i

                    # If scraper response was successful, we're done
                    if not output_json.get('status') == 'failure':
                        break

                    # If failure was due to proxies
                    if output_json.get('failure_type') in ['max_retries', 'proxy']:
                        logger.info('GOT FAILURE TYPE %s for %s - RETRY %s' % (output_json.get('failure_type'), url, i))
                        max_retries = 10
                        # back off incrementally
                        time.sleep(60*i)
                    else:
                        max_retries = 3
                        time.sleep(1)

                output_json['url'] = url
                output_json['site_id'] = site_id
                output_json['product_id'] = product_id
                output_json['event'] = event

                output_message = json.dumps(output_json)
                #print(output_message)

                # Add the scraped page to the processing queue ...
                sqs_process = SQS_Queue('%s_process'%server_name)
                sqs_process.put( output_message, url)
                # ... and remove it from the scrape queue
                sqs_scrape.task_done()
                
                logger.info("Sent: thread %d server %s url %s" % ( thread_id, server_name, url))

                # Send Log History
                LogHistory.send_log()

            except Exception as e:
                logger.warn(e)
                sqs_scrape.reset_message()

        time.sleep(1)

if __name__ == "__main__":
    from log_history import LogHistory

    if len(sys.argv) > 1:
        environment = sys.argv[1] # e.g., UnitTest, see dictionary of queue names
        queue_name = "no queue"
        
        for k in queue_names:
            if environment == k:
                queue_name = queue_names[k]

        if queue_name != "no queue":
            logger.info( "environment: %s" % environment)
            logger.info( "using scrape queue %s" % queue_name)
            if environment != "UnitTest":
                threads = []
                for i in range(5):
                    logger.info( "Creating thread %d" % i)
                    t = threading.Thread( target=main, args=( environment, queue_name, i))
                    threads.append( t)
                    t.start()
            else:
                main( environment, queue_name, -1)
        else:
            print "Environment not recognized: %s" % environment
    else:
        print "######################################################################################################"
        print "This script receives URLs via SQS and sends back the scraper response."
        print "Please input correct argument for the environment.\nfor ex: python get_scrape_queue.py 'UnitTest' "
        print "######################################################################################################"
