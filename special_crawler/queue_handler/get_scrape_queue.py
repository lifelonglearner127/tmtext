#!/usr/bin/env python

'''
Gist : Scrape Queue -> Scrape -> Process Queue

'''

from sqs_connect import SQS_Queue
import logging
import time
import json
import requests
import threading
import urllib

from config import scrape_queue_name

INDEX_ERROR = "IndexError : The queue was really out of items, but the count was lagging so it tried to run again."

def main( thread_id):
    print( "Starting thread %i" % thread_id)
    # establish the scrape queue
    sqs_scrape = SQS_Queue( scrape_queue_name)

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
                logging.warning('Error: ', e)

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
                
                print('Received: thread $i server %s url %s'.format( thread_id, server_name, url))

                # Scrape the page using the scraper running on localhost
                base = "http://localhost/get_data?url=%s"
                output_text = requests.get(base%(urllib.quote(url))).text

                # Add the processing fields to the return object and re-serialize it
                output_json = json.loads(output_text)
                output_json['url'] = url
                output_json['site_id'] = site_id
                output_json['product_id'] = product_id
                output_json['event'] = event
                output_message = json.dumps( output_json)
                #print(output_message)

                # Add the scraped page to the processing queue ...
                sqs_process = SQS_Queue('%s_process'%server_name)
                sqs_process.put( output_message)
                # ... and remove it from the scrape queue
                sqs_scrape.task_done()
                
                print('Sent: thread $i server %s url %s'.format( thread_id, server_name, url))

            except Exception as e:
                logging.warning('Error: ', e)
                sqs_scrape.reset_message()

        sleep( 1)

if __name__ == "__main__":
    threads = []
    for i in range(5):
        print( "Creating thread %i" % i)
        t = threading.Thread( target=main, args=( i))
        threads.append( t)
        t.start()
