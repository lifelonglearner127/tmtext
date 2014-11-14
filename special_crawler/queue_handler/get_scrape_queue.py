from sqs_connect import SQS_Queue
import logging
import time
import json
import requests

#{batchid : x, event : y, url : z, site : w} 

INDEX_ERROR = "IndexError : The queue was really out of items, but the count was lagging so it tried to run again."

def main():
    sqs_scrape = SQS_Queue('test_scrape')



    # TODO: Explanatory comments
    while True: # not sqs_scrape.empty():
        try:
            row = sqs_scrape.get()
            url_to_scrape = json.loads(row)
            sqs_process = SQS_Queue(url_to_scrape['server_name'])
            url = url_to_scrape['url']
            site = url_to_scrape['site_id']
            # print("Scraping url : ", url)

            base = "http://localhost/get_data?site=%s&url=%s"
            output = requests.get(base%(site, url)).text
            # TODO: add necessary data here: Site_id, and event. deser + add + ser if needed, or use jsonmessage to return
            # print(output)
            sqs_process.put(output)
            sqs_scrape.task_done()
        except IndexError as e:
            # logging.warning('queue is empty, and you tried to grab something off of it, sleeping for 1 sec.')
            time.sleep(1)
            pass
        except Exception as e:
            logging.warning('Error: ', e)

if __name__ == "__main__":
    main()