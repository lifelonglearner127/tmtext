#!/usr/bin/env python3

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
#from models import select_site_by_id


INDEX_ERROR = "IndexError : The queue was really out of items, but the count was lagging so it tried to run again."

def main():
    # establish the scrape queue
    sqs_scrape = SQS_Queue('test_scrape')


    # Continually pull off the SQS Scrape Queue
    while True:
        try:
            # Get message from SQS and de-serialize to a json object
            message = sqs_scrape.get()
            message_json = json.loads(message)

            # Vars from the json object
            url = message_json['url']
            site = message_json['site']
            site_id = message_json['site_id']
            server_name = message_json['server_name']
            product_id = message_json['product_id']
            event = message_json['event']

            # Connect to the proccess queue responsible for the current batch
            sqs_process = SQS_Queue('%s_process'%server_name)

            # Scrape the page using the scraper running on localhost
            base = "http://localhost/get_data?url=%s"
            output = requests.get(base%(urllib.quote(url))).text

            # Add the processing fields to the return object and re-serialize it
            output = json.loads(output)
            output['url'] = url
            output['site_id'] = site_id
            output['product_id'] = product_id
            output['event'] = event
            output = json.dumps(output)
            print(output)

            # Add the scraped page to the processing queue and remove it from the scrape queue
            sqs_process.put(output)
            sqs_scrape.task_done()

        except IndexError as e:
            # This exception will most likely be triggered because you were grabbing off an empty queue
            time.sleep(1)

        except Exception as e:
            # Catch all other exceptions to prevent the whole thing from crashing
            # TODO : Consider testing that sqs_scrape is still live, and restart it if need be
            logging.warning('Error: ', e)
            sqs_scrape.reset_message()


if __name__ == "__main__":
    threads = []
    for i in range(5):
        t = threading.Thread(target=main)
        threads.append(t)
        t.start()
