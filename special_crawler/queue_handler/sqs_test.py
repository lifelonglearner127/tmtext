#!/usr/bin/env python

'''
For testing new versions of scraper before deployment

Sends message to an SQS scrape queue and awaits and validates response from process queue

author: Quinn Stearns

'''

import sys
import time
import json
from sqs_connect import SQS_Queue
import requests
import urllib

def runTests(scrape_queue_name, process_queue_name, url):
    print("RUNNING SQS TESTS")
    base = "http://localhost/get_data?url=%s"

    sqs_scrape = SQS_Queue(scrape_queue_name)

    message = {'url':url, 
               'site_id':5,
               'server_name':'unit_test', 
               'product_id':384, 
               'site':'walmart.com',
               'event':1}

    output_text = requests.get(base%(urllib.quote(url))).text
    output_json = json.loads(output_text)
    s3_content = json.dumps(output_json)

    sqs_scrape.put( json.dumps( message ), s3_content)

    print("SENT MESSAGE. WAITING FOR RESPONSE")

    sqs_process = SQS_Queue(process_queue_name)

    while sqs_process.count() == 0:
        time.sleep(1)

    try:
        message = sqs_process.get()
        print("RECEIVED MESSAGE")
        sqs_process.task_done()

    except Exception as e:
        sqs_process.reset_message()
        print('error: ', e)
        return None

    return json.loads( message)

if (__name__ == '__main__'):
    if len(sys.argv) > 1:
        url = sys.argv[1] # 'localhost/get_data?url=http://www.ozon.ru/context/detail/id/28659614/'
        scrape_queue_name = 'unit_test_scrape'
        if len(sys.argv) > 2:
            scrape_queue_name = sys.argv[2]
        process_queue_name = 'unit_test_process'
        print json.dumps( runTests(scrape_queue_name, process_queue_name, url), sort_keys=True, indent = 2).decode('unicode_escape')

    else:
        print "######################################################################################################"
        print "This script sends a message to an SQS Queue for processing and prints the response.(Author: Quinn Stearns)"
        print "Please input correct argument.\nfor ex: python sqs_test.py 'http://www.ozon.ru/context/detail/id/28659614/' ['unit_test_scrape']"
        print "######################################################################################################"

    
