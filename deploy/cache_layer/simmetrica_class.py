import time
import random
import string
from collections import Counter

import redis

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
        self.db = redis.StrictRedis(host='localhost', port=6379, db=0)

    def total_resp_in_cache(self):
        return self.db.hlen('responses')

    def set_time_of_newest_resp(self):
        self.db.set('simmetrica_newest_resp', time.time())

    def get_time_of_newest_resp(self):
        return self.db.get('simmetrica_newest_resp')

    def set_time_of_oldest_resp(self):
        self.db.setnx('simmetrica_oldest_resp', time.time())

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
        return percents, total_resp

    def remove_old_req_and_resp(self):
        max_limit = time.time() - 3600*24*31  # older than 31 day
        self.db.zremrangebyscore('total_returned_resp', 0, max_limit)
        self.db.zremrangebyscore('total_received_req', 0, max_limit)

    def get_most_recent_resp(self, hours_range, quantity=5):
        resp_set = self.get_range_of_returned_resp(hours_range)
        resp = [r.split('-', 1)[1] for r in resp_set]
        return Counter(resp).most_common(quantity)

    @staticmethod
    def random_generator(length=12):
        return ''.join(
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(length)
        )

if (__name__ == '__main__'):
    s = Simmetrica()
    s.remove_old_req_and_resp()