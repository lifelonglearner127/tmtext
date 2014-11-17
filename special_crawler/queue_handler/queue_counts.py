#!usr/bin/env python3

"""
A super simple script for checking up on the queues and clearing them out if need be
"""

from sqs_connect import SQS_Queue



# The queues you would like to check
queues = ['test_scrape', 'test_process', 'test2_process']
for q in queues:
    #sqs_scrape.clear()
    sqs_scrape = SQS_Queue(q)
    print(q, "count : ", sqs_scrape.count())




# 51 - 53
# 49 - 55
# 27 - 72
