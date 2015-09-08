import json
from time import time
from redis import StrictRedis
from zlib import compress, decompress

from cache_layer import REDIS_HOST, REDIS_PORT


class SqsCache(object):
    """
    interact with redis DB in terms of cache (put/get item to/from cache)
    """
    REDIS_CACHE_TIMESTAMP = 'cached_timestamps'
    REDIS_CACHE_KEY = 'cached_responses'

    def __init__(self, db=None):
        self.db = db if db else StrictRedis(REDIS_HOST, REDIS_PORT)

    def _task_to_key(self, task):
        """
        generate unique key-string for the task, from server_name and task_id
        task should be dict
        """
        # todo: check url, urls (maybe it's product_url(s))
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