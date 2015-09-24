import json
from time import time, mktime
from redis import StrictRedis
from zlib import compress, decompress
from datetime import date

from cache_layer import REDIS_HOST, REDIS_PORT


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


class SqsCache(object):
    """
    interact with redis DB in terms of cache (put/get item to/from cache)
    """
    CACHE_SETTINGS_PATH = 'settings'  # location of file with settings
    REDIS_CACHE_TIMESTAMP = 'cached_timestamps'  # zset, expiry for items
    REDIS_CACHE_KEY = 'cached_responses'  # hash, cached items
    REDIS_CACHE_STATS = 'cached_count'  # zset, to get most popular items
    REDIS_COMPLETED_TASKS = 'completed_tasks'  # zset, count completed tasks
    REDIS_INSTANCES_COUNTER = 'daily_sqs_instances_counter'

    def __init__(self, db=None):
        self.db = db if db else StrictRedis(REDIS_HOST, REDIS_PORT)
        # self.db = db if db else StrictRedis()  # for local

    def _task_to_key(self, task):
        """
        generate unique key-string for the task, from server_name and task_id
        task should be dict
        """
        if not isinstance(task, dict):
            return None
        res = []
        keys_to_check = {'site': 'site', 'url': 'url', 'urls': 'urls',
                         'searchterms_str': 'term',
                         'with_best_seller_ranking': 'bsr',
                         'branch_name': 'branch'}
        for key in sorted(keys_to_check.keys()):
            val = task.get(key)
            if val is not None:
                res.append('%s-%s' % (keys_to_check[key], val))
        for key in sorted(task.get('cmd_args', {}).keys()):
            res.append('%s-%s' % (key, task['cmd_args'][key]))
        res = ':'.join(res)
        return res

    def get_result(self, task_str):
        """
        retrieve cached result
        freshness in minutes
        returns tuple (is_item_found_in_cache, item_or_None)
        """
        task = json.loads(task_str)
        uniq_key = self._task_to_key(task)
        if not uniq_key:
            return False, None
        score = self.db.zscore(self.REDIS_CACHE_TIMESTAMP, uniq_key)
        if not score:  # if not found item in cache
            return False, None
        # take only results, saved today
        today = date.today()
        freshness = int(mktime(today.timetuple()))
        if score < freshness:  # if item is too old
            return True, None
        item = self.db.hget(self.REDIS_CACHE_KEY, uniq_key)
        if not item:
            return False, None
        self.db.zincrby(self.REDIS_CACHE_STATS, uniq_key, 1)
        item = decompress(item)
        return True, item

    def put_result(self, task_str, result):
        """
        put task response into cache
        returns True if success
        """
        task = json.loads(task_str)
        uniq_key = self._task_to_key(task)
        if not uniq_key:
            return False
        # save some space using compress
        self.db.hset(self.REDIS_CACHE_KEY, uniq_key, compress(result))
        self.db.zadd(self.REDIS_CACHE_TIMESTAMP, int(time()), uniq_key)
        return True

    def delete_old_tasks(self, freshness):
        """
        :param freshness: value in minutes
        clears cache from old data
        data is considered old, if time, when it was added
        is less then (now - freshness)
        :return number of rows affected
        """
        time_offset = int(time()) - (freshness * 60)
        old_keys = self.db.zrangebyscore(
            self.REDIS_CACHE_TIMESTAMP, 0, time_offset)
        # delete old keys from redis, 100 items at once
        for sub_keys in chunks(old_keys, 100):
            self.db.hdel(self.REDIS_CACHE_KEY, *sub_keys)
        return self.db.zremrangebyscore(
            self.REDIS_CACHE_TIMESTAMP, 0, time_offset)

    def clear_stats(self):
        """
        return tuple of count of deleted items from cache and from tasks
        """
        self.db.delete(self.REDIS_INSTANCES_COUNTER)
        return \
            (self.db.zremrangebyrank(self.REDIS_CACHE_STATS, 0, -1),
             self.db.zremrangebyrank(self.REDIS_COMPLETED_TASKS, 0, -1))

    def purge_cache(self):
        """
        removes all data, related to cache
        """
        self.db.delete(self.REDIS_CACHE_TIMESTAMP,
                       self.REDIS_CACHE_KEY, self.REDIS_CACHE_STATS)

    def complete_task(self, task_str):
        task = json.loads(task_str)
        key = '%s_%s' % (task.get('task_id'), task.get('server_name'))
        return self.db.zadd(self.REDIS_COMPLETED_TASKS, int(time()), key)

    def get_cached_tasks_count(self):
        """
        get count of cached tasks
        """
        return self.db.zcard(self.REDIS_CACHE_TIMESTAMP)

    def get_today_instances(self):
        """
        get count of started instances for current day
        """
        return self.db.get('daily_sqs_instances_counter')

    def get_executed_tasks_count(self, hours_from=None, hours_to=None,
                                 for_last_hour=False):
        """
        get count of executed tasks for
        hours time period or for today, if not set
        """
        if hours_from is None and not for_last_hour:
            return self.db.zcard(self.REDIS_COMPLETED_TASKS)
        else:
            today = list(date.today().timetuple())
            if for_last_hour:
                time_from = int(time()) - 60 * 60
            else:
                today[3] = hours_from
                time_from = mktime(today)
            if hours_to:
                today[3] = hours_to
                time_to = mktime(today)
            else:
                time_to = int(time())
            return self.db.zcount(
                self.REDIS_COMPLETED_TASKS, time_from, time_to)

    def get_most_popular_cached_items(self, cnt=10):
        """
        gets 10 most popular items in cache
        """
        return self.db.zrevrangebyscore(self.REDIS_CACHE_STATS,
                                        9999, 0, 0, cnt, True, int)

    def get_used_memory(self):
        return self.db.info().get('used_memory_human')

    def get_total_cached_responses(self):
        """
        returns tuple of 2 elements: unique elements, requested from cache and
        total number of elements requested from cache
        """
        data = self.db.zrange(self.REDIS_CACHE_STATS, 0, -1,
                              withscores=True, score_cast_func=int)
        return len(data), sum([_[1] for _ in data])

    def get_cache_settings(self):
        """
        returns dict with current settings
        """
        with open(self.CACHE_SETTINGS_PATH, 'r') as f:
            s = f.read()
        data = json.load(s or '""')
        return data

    def save_cache_settings(self, data):
        """
        saves settings dict to file
        """
        if not data:
            return
        with open(self.CACHE_SETTINGS_PATH, 'w') as f:
            s = json.dumps(data)
            f.write(s)