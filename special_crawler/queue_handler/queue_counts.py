#!usr/bin/env python3

"""
A super simple script for checking up on the queues and clearing them out if need be
"""

from sqs_connect import SQS_Queue



# The queues you would like to check
queues = ['test_scrape', 'test_process', 'test2_process']
for q in queues:
	print('processing: ', q),

	sqs_scrape = SQS_Queue(q)
	#sqs_scrape.clear()

	print('... done')
	print(q, "count : ", sqs_scrape.count())




