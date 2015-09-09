import json
from time import time
from redis import StrictRedis
from zlib import compress, decompress

from cache_layer import REDIS_HOST, REDIS_PORT


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


class SqsCache(object):
    """
    interact with redis DB in terms of cache (put/get item to/from cache)
    """
    REDIS_CACHE_TIMESTAMP = 'cached_timestamps'  # zset, expiry for items
    REDIS_CACHE_KEY = 'cached_responses'  # hash, cached items
    REDIS_CACHE_STATS = 'cached_count'  # zset, to get most popular items
    REDIS_COMPLETED_TASKS = 'completed_tasks'  # zset, count completed tasks

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

    def get_result(self, task_str, freshness):
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
        if score < (time() - (freshness*60)):  # if item is too old
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
        res = self.db.zadd(self.REDIS_CACHE_TIMESTAMP, int(time()), uniq_key)
        return bool(res)

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
        return \
            (self.db.zremrangebyrank(self.REDIS_CACHE_STATS, 0, -1),
             self.db.zremrangebyrank(self.REDIS_COMPLETED_TASKS, 0, -1))

    def complete_task(self, task_str):
        task = json.loads(task_str)
        key = '%s_%s' % (task.get('task_id'), task.get('server_name'))
        return self.db.zadd(self.REDIS_COMPLETED_TASKS, int(time()), key)

    def get_cached_tasks_count(self):
        """
        get count of cached tasks
        """
        return self.db.zcard(self.REDIS_CACHE_TIMESTAMP)