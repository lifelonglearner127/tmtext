import unittest
import random
import json
import time
import copy
import pickle
import os
import sys

from boto.sqs.message import Message
import boto.sqs

import sqs_cache
import cache_starter


"""
To use this script you need:
1. Start redis database like:
$ /etc/init.d/redis_6379 start
2. Start cache_starter:
$ python cache_starter.py
"""

class TestSQSCache(unittest.TestCase):
    """Tests for SQS cache.
    Note: this test assume that:
    1. Walmart spider working correctly.
    2. Product-ranking sqs working correctly
    3. You have connect to amazon database or run your local one
    """

    @classmethod
    def setUpClass(cls):
        cls.db = sqs_cache.connect_to_redis_database()
        cls.sqs_conn = boto.sqs.connect_to_region("us-east-1")
        cls.start_cache_queues_list = cache_starter.CACHE_QUEUES_LIST
        cls.cache_task_queue = cls.start_cache_queues_list.values()[2]  # test queue
        cls.cache_progress_queue = sqs_cache.CACHE_PROGRESS_QUEUE

    @staticmethod
    def generate_message(url=None, server_name=None, site=None, quantity=None):
        task_id = random.randint(100000, 200000)
        msg = {
            "searchterms_str": "water",
            "server_name": "cache_test_server_name",
            "cmd_args": {"quantity": 5},
            "site": "walmart",
            "task_id": task_id,
        }
        if url:
            del msg['searchterms_str']
            msg['url'] = url
        if server_name:
            msg['server_name'] = server_name
        if site:
            msg['site'] = site
        if quantity:
            msg["cmd_args"]["quantity"] = quantity
        return msg

    def provide_msg_to_queue(self, msg, queue_name):
        m = Message()
        m.set_body(json.dumps(msg))
        q = self.sqs_conn.get_queue(queue_name)
        if not q:
            self.sqs_conn.create_queue(queue_name)
            time.sleep(5)
            q = self.sqs_conn.get_queue(queue_name)
        q.write(m)

    def check_status(self, queue_name):
        attemps = 0
        status = None
        while attemps < 50:
            try:
                q = self.sqs_conn.get_queue(queue_name)
                m = q.get_messages()
                string = m[0].get_body()
                m[0].delete()
                message = json.loads(string)
                status = message['progress']
                if isinstance(status, int):
                    continue
                break
            except Exception as e:
                print e
                attemps += 1
                time.sleep(1)
        return status

    def check_cache_results(self, task_message, cached=False):
        server_name = task_message['server_name']
        queue_name = server_name + sqs_cache.CACHE_OUTPUT_QUEUE_NAME
        q = None
        while not q:
            q = self.sqs_conn.get_queue(queue_name)
            time.sleep(5)
        # self.assertEqual(q.count(), 1)
        for i in range(10):
            if q.count() > 0:
                break
            time.sleep(1)
        m = q.get_messages()
        msg_body = m[0].get_body()
        m[0].delete()
        message = json.loads(msg_body)
        self.assertEqual(message['_msg_id'], task_message['task_id'])
        if cached:
            self.assertEqual(message['cached'], cached)

    def test_non_existed_response_and_request_and_send_same_task_again(self):
        print(
            "\nThree cases at one time:"
            "\n\t1. Response not exist, request not exist."
            "\n\t2. Response not exist, request exist and fresh enough."
            "\n\t3. Response exist at database and fresh enough."
        )
        # response not exist, request not exist
        print("Send non existing task to cache")
        msg = self.generate_message()
        print(msg["task_id"])
        self.provide_msg_to_queue(msg, self.cache_task_queue)
        queue_name = msg['server_name'] + self.cache_progress_queue
        status_list = [
            'Ok. Task was received.',
            'Redirect request to spiders sqs.',
        ]
        status = self.check_status(queue_name)
        print ("Rcvd status: '%s'" % status)
        self.assertTrue(status in status_list)
        status2 = self.check_status(queue_name)
        print ("Rcvd status: '%s'" % status2)
        self.assertTrue(status2 in status_list)

        # response not exist, request exist and fresh enough
        print("Send the same task again(but change server_name)."
              "Response not exist but request already was generated")
        another_server_msg = copy.deepcopy(msg)
        second_server = 'cache_test_server_name2'
        another_server_msg['server_name'] = second_server
        self.provide_msg_to_queue(another_server_msg, self.cache_task_queue)
        second_server_q = second_server + self.cache_progress_queue
        status_list_for_second_server = [
            'Ok. Task was received.',
            'Wait for request from other instance.',
        ]
        status = self.check_status(second_server_q)
        print ("Rcvd status: '%s'" % status)
        self.assertTrue(status in status_list_for_second_server)
        status2 = self.check_status(second_server_q)
        print ("Rcvd status: '%s'" % status2)
        self.assertTrue(status2 in status_list_for_second_server)

        print("Now wait until scrapy_daemon/cache will finish their work")
        print("It may take about 20-30 minutes")
        while True:
            status = self.check_status(queue_name)
            if status:
                self.assertEqual(status, 'finished')
                break
        self.check_cache_results(msg)
        self.check_cache_results(another_server_msg)

        # response exist at database and fresh enough(request not required)
        print("Send again the same task to cache. Response should exists")
        msg['task_id'] = random.randint(100000, 200000)
        print(msg["task_id"])
        self.provide_msg_to_queue(msg, self.cache_task_queue)
        status_list = [
            'Ok. Task was received.',
            'finished',
        ]
        status = self.check_status(queue_name)
        print ("Rcvd status: '%s'" % status)
        self.assertTrue(status in status_list)
        status2 = self.check_status(queue_name)
        print ("Rcvd status: '%s'" % status2)
        self.assertTrue(status2 in status_list)

        self.check_cache_results(msg, cached=True)
        task_stamp = sqs_cache.generate_task_stamp(msg)
        print("Delete collected responses for this task")
        self.db.hdel('responses', task_stamp)
        self.db.hdel('last_request', task_stamp)

    def test_not_fresh_request(self):
        print("\nCase: Response not exist,"
              " request exist but not fresh enough")
        msg = self.generate_message()
        print("First simulate that request for the same task was already"
              " sent but more than 1 hour ago")
        print(msg["task_id"])
        task_stamp = sqs_cache.generate_task_stamp(msg)
        request_item = (time.time() + 3601, msg['server_name'])
        self.db.hset('last_request', task_stamp, time.time()-3601)
        print("Now send task to cache.")
        self.provide_msg_to_queue(msg, self.cache_task_queue)
        queue_name = msg['server_name'] + self.cache_progress_queue
        status_list = [
            'Ok. Task was received.',
            'Request for this task was found but '\
            'it was sent more than 1 hour ago.',
            'Redirect request to spiders sqs.',
        ]
        for i in range(3):
            status = self.check_status(queue_name)
            print ("Rcvd status: '%s'" % status)
            self.assertTrue(status in status_list)
        print("Now wait until scrapy_daemon/cache will finish their work")
        print("It may take about 20-30 minutes")
        while True:
            status = self.check_status(queue_name)
            print(status)
            if status:
                if isinstance(status, int):
                    continue
                else:
                    self.assertEqual(status, 'finished')
                    break
        self.check_cache_results(msg)
        self.db.hdel('responses', task_stamp)
        self.db.hdel('last_request', task_stamp)

    def test_response_not_satisfy_freshness(self):
        print("\nCase: Response exist but not satisfy freshness")
        print("First generate some fake response")
        msg = self.generate_message()
        print(msg["task_id"])
        msg['freshness'] = 1 # 1 hour
        task_stamp = sqs_cache.generate_task_stamp(msg)
        fake_response = pickle.dumps((time.time()- 3601, {}))
        self.db.hset('responses', task_stamp, fake_response)
        print("Send task to cache")
        self.provide_msg_to_queue(msg, self.cache_task_queue)
        queue_name = msg['server_name'] + self.cache_progress_queue
        status_list = [
            'Ok. Task was received.',
            'Redirect request to spiders sqs.',
        ]
        status = self.check_status(queue_name)
        print ("Rcvd status: '%s'" % status)
        self.assertTrue(status in status_list)
        status2 = self.check_status(queue_name)
        print ("Rcvd status: '%s'" % status2)
        self.assertTrue(status2 in status_list)

        print("Now wait until scrapy_daemon/cache will finish their work")
        print("It may take about 20-30 minutes")
        while True:
            status = self.check_status(queue_name)
            if status:
                if isinstance(status, int):
                    continue
                else:
                    self.assertEqual(status, 'finished')
                    break
        self.check_cache_results(msg)
        self.db.hdel('responses', task_stamp)
        self.db.hdel('last_request', task_stamp)

    def test_forced_message(self):
        print("\nTest forced task message")
        msg = self.generate_message()
        msg["forced_task"] = True
        print("First create fake response for the same task.")
        task_stamp = sqs_cache.generate_task_stamp(msg)
        fake_response = pickle.dumps((time.time(), {}))
        self.db.hset('responses', task_stamp, fake_response)
        print("Send task to cache")
        print(msg["task_id"])
        self.provide_msg_to_queue(msg, self.cache_task_queue)

        queue_name = msg['server_name'] + self.cache_progress_queue
        status_list = [
            'Ok. Task was received.',
            'Redirect request to spiders sqs.',
        ]
        for i in range(2):
            status = self.check_status(queue_name)
            print ("Rcvd status: '%s'" % status)
            self.assertTrue(status in status_list)
        print("Now wait until scrapy_daemon/cache will finish their work")
        print("It may take about 20-30 minutes")
        while True:
            status = self.check_status(queue_name)
            if status:
                if isinstance(status, int):
                    continue
                else:
                    self.assertEqual(status, 'finished')
                    break
        self.check_cache_results(msg)
        self.db.hdel('responses', task_stamp)
        self.db.hdel('last_request', task_stamp)

    @classmethod
    def tearDownClass(cls):
        # delete all possible test queues
        name1 = 'cache_test_server_name'
        name2 = 'cache_test_server_name2'
        names = [
            name1+sqs_cache.CACHE_OUTPUT_QUEUE_NAME,
            name1+sqs_cache.CACHE_PROGRESS_QUEUE,
            name1+'sqs_ranking_spiders_output',
            name1+'sqs_ranking_spiders_progress',
            name2+sqs_cache.CACHE_OUTPUT_QUEUE_NAME,
            name2+sqs_cache.CACHE_PROGRESS_QUEUE,
        ]
        for name in names:
            try:
                q = cls.sqs_conn.get_queue(name)
                q.delete()
                print("'%s' queue was deleted." % name)
            except Exception as e:
                print(e)
                pass


if (__name__ == '__main__'):
    unittest.main()
