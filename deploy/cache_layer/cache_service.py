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
        server_name = task.get('server_name')
        task_id = task.get('task_id')
        if not server_name or not task_id:
            return None
        return '%s_%s' % (server_name, task_id)

    def get_result(self, task_str, freshness):
        """
        retrieve cached result
        freshness in minutes
        returns tuple (found_item_in_cache, item_or_None)
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
        res = self.db.hset(self.REDIS_CACHE_KEY, uniq_key, compress(result))
        if not res:  # if failed to save item in cache
            return False
        res = self.db.zadd(uniq_key, int(time()))
        return bool(res)