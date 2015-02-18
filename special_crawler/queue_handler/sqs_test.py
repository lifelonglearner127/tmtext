'''
For testing new versions of scraper before deployment

Sends message to an SQS scrape queue and awaits and validates response from process queue

author: Quinn Stearns

'''

from sqs_connect import Scrape_Queue

def runTests(scrape_queue_name, process_queue_name, url):
    print("RUNNING SQS TESTS")

    sqs_scrape = SQS_Queue(scrape_queue_name)

    message = {'url':url, 
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
        return None

    return message

if (__name__ == '__main__'):
    if len(sys.argv) > 1:
        url = sys.argv[1] # 'localhost/get_data?url=http://www.ozon.ru/context/detail/id/28659614/'
        print runTests('unit_test_scrape', 'unit_test_process', url)

    else:
        print "######################################################################################################"
        print "This script sends a message to an SQS Queue for processing and prints the response.(Author: Quinn Stearns)"
        print "Please input correct argument.\nfor ex: python sqs_test.py 'http://www.ozon.ru/context/detail/id/28659614/'"
        print "######################################################################################################"

    
