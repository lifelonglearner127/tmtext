import time
import random
import string
import json
import os
import sys
import pickle
from collections import Counter

import redis


CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(CWD, '..'))

from cache_layer import REDIS_HOST, REDIS_PORT, HANDLED_TASKS_SORTED_SET


class Simmetrica(object):

    """
    ok - Total # items in cache - len of all keys in responses
    ok - Age of newest item - provide through additional entry to redis?
    ok - Age of oldest item - just add first entry to database if it not exists?

    ok - % and # Items Served From Cache,
    last 1 hour, last 24 hours, last 7 days, last 30 days
    provide two database entries - total received requests and quantity of 
    sent back responses ( increment key)

    ok - Top 5 Items Served From Cache and # of Times Served,
    Last 1 hour, last 24 hours, last 7 days, last 30 days
    Provide database entry - response - how often it was requested and when.
    """

    def __init__(self, *args, **kwargs):
        self.db = redis.StrictRedis(
            host=REDIS_HOST,
            port=REDIS_PORT
        )
        # self.db = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.CWD = os.path.dirname(os.path.abspath(__file__))

    def total_resp_in_cache(self):
        return self.db.hlen('responses')

    def set_time_of_newest_resp(self, time=time.time()):
        self.db.set('simmetrica_newest_resp', time)

    def get_time_of_newest_resp(self):
        return self.db.get('simmetrica_newest_resp')

    def set_time_of_oldest_resp(self, time=time.time()):
        self.db.setnx('simmetrica_oldest_resp', time)

    def get_time_of_oldest_resp(self):
        return self.db.get('simmetrica_oldest_resp')

    def increment_received_req_set(self):
        self.db.zadd('total_received_req', time.time(), time.time())

    def increment_returned_resp_set(self, task_stamp):
        item = self.random_generator() + '-' + task_stamp
        self.db.zadd('total_returned_resp', time.time(), item)

    def get_range_of_received_req(self, hours_range):
        max_limit = time.time()
        min_limit = max_limit - hours_range*3600
        return self.db.zrangebyscore('total_received_req',
                                     min_limit, max_limit)

    def get_range_of_returned_resp(self, hours_range):
        max_limit = time.time()
        min_limit = max_limit - hours_range*3600
        return self.db.zrangebyscore('total_returned_resp',
                                     min_limit, max_limit)

    def perc_and_quan_of_served_items(self, hours_range):
        total_req = len(
            self.get_range_of_received_req(hours_range))
        total_resp = len(
            self.get_range_of_returned_resp(hours_range))
        percents = total_resp * 100.0 / total_req
        # (21.1244, 78)
        return percents, total_resp

    def remove_old_req_and_resp(self, hours_limit=12):
        """This method will clear metrics, not responses from cache"""
        max_limit = time.time() - 3600*int(hours_limit)
        self.db.zremrangebyscore('total_returned_resp', 0, max_limit)
        self.db.zremrangebyscore('total_received_req', 0, max_limit)

    def get_most_recent_resp(self, hours_range, quantity=5):
        resp_set = self.get_range_of_returned_resp(hours_range)
        resp = [r.split('-', 1)[1] for r in resp_set]
        # [('walmart:st:water:quantity:5', 2)]
        return Counter(resp).most_common(quantity)

    def get_used_memory(self):
        info = self.db.info()
        return info.get('used_memory_human')

    def get_settings(self):
        try:
            path = os.path.join(self.CWD, 'settings')
            settings_file = open(path, 'r')
            settings_data = json.load(settings_file)
            settings_file.close()
            return settings_data
        except Exception as e:
            return("Failed to load settings file, %s" % e)

    def update_settings(self, data):
        try:
            path = os.path.join(self.CWD, 'settings')
            settings_file = open(path, 'w')
            settings_data = json.dumps(data)
            settings_file.write(settings_data)
            settings_file.close()
            msg = "Settings were successfully updated"
            return msg
        except Exception as e:
            return("Failed to update settings file, %s" % e)

    def delete_old_responses(self, time_limit=12):
        """This method will remove old responses from cache"""
        responses = self.db.hgetall('responses')
        all_time_stamps = []
        for key in responses.keys():
            item = responses[key]
            item_time = pickle.loads(item)[0]
            if time.time() - float(item_time) > (time_limit*3600):
                self.db.hdel('responses', key)
            else:
                all_time_stamps.append(item_time)
        if all_time_stamps:
            self.set_time_of_newest_resp(max(all_time_stamps))
            self.db.set('simmetrica_oldest_resp', min(all_time_stamps))
        else:
            self.db.delete('simmetrica_newest_resp')
            self.db.delete('simmetrica_oldest_resp')

    def clear_cache(self):
        self.db.delete('responses')
        self.db.delete('simmetrica_newest_resp')
        self.db.delete('simmetrica_oldest_resp')

    def remove_sqs_metrics(self, hours_limit):
        max_limit = time.time() - 3600*int(hours_limit)
        self.db.zremrangebyscore(HANDLED_TASKS_SORTED_SET, 0, max_limit)

    @staticmethod
    def random_generator(length=12):
        return ''.join(
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(length)
        )

if (__name__ == '__main__'):
    s = Simmetrica()
    hours_limit = 12
    try:
        settings = s.get_settings()
        hours_limit = int(settings['hours_limit'])
    except Exception as e:
        print(e)
    # s.remove_old_req_and_resp(hours_limit)
    s.delete_old_responses(hours_limit)
    s.remove_sqs_metrics(hours_limit)