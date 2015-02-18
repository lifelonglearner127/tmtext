'''
For testing new versions of scraper before deployment

Sends message to an SQS scrape queue and awaits and validates response from process queue

author: Quinn Stearns

'''

from sqs_connect import Scrape_Queue

def runTests(scrape_queue_name, process_queue_name, batch_csv=None):
    print("RUNNING SQS TESTS")

    sqs_scrape = SQS_Queue(scrape_queue_name)

    message = {'url':'http://www.pgshop.com/home/kitchen/dishwasher-detergent/cascade-complete-powder-dishwasher-detergent-fresh-scent-75-oz/PG_00037000338369.html', 
                                         'site_id':5, 
                                         'server_name':'unit_test', 
                                         'product_id':384, 
                                         'site':'walmart.com', 
                                         'event':1}

    sqs_scrape.put( json.dumps( message ))

    print("SENT MESSAGE. WAITING FOR RESPONSE")

    sqs_process = SQS_Queue(process_queue_name)

    # while sqs_process.count() > 0:
    try:
        message = sqs_process.get()
        print("RECEIVED MESSAGE")
        sqs_process.task_done()

    except Exception as e:
        sqs_process.reset_message()
        print('error: ', e)
        continue

    print("SUCCESS. SENT AND RECEIVED MESSAGE.")

if (__name__ == '__main__'):
    runTests('unit_test_scrape', 'unit_test_process')
