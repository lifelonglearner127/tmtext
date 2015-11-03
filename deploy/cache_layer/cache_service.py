import json
from time import time, mktime
from redis import StrictRedis
from zlib import compress, decompress
from datetime import date, datetime, timedelta
from collections import OrderedDict
from os.path import realpath, dirname

try:
    from cache_layer import REDIS_HOST, REDIS_PORT
except ImportError:
    from . import REDIS_HOST, REDIS_PORT


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
    REDIS_CACHE_STATS_URL = 'cached_count_url'  # zset
    REDIS_CACHE_STATS_TERM = 'cached_count_term'  # zset
    REDIS_COMPLETED_TASKS = 'completed_tasks'  # zset, count completed tasks
    REDIS_INSTANCES_COUNTER = 'daily_sqs_instances_counter'  # int
    REDIS_INSTANCES_HISTORY = 'sqs_instances_history'  # zset
    REDIS_URGENT_STATS = 'urgent_stats'  # zset
    REDIS_FAILED_TASKS = 'failed_tasks'  # set, store failed tasks here
    MAX_FAILED_TRIES = 3
    REDIS_COMPLETED_COUNTER = 'completed_counter'  # hset
    REDIS_COMPLETED_COUNTER_DICT = {
        'url': 'url',
        'url_cached': 'url_cached',
        'term': 'term',
        'term_cached': 'term_cached'
    }

    def __init__(self, db=None, timeout=10):
        self.db = db if db else StrictRedis(REDIS_HOST, REDIS_PORT,
                                            socket_timeout=timeout)
        # self.db = db if db else StrictRedis()  # for local

    def _task_to_key(self, task):
        """
        generate unique key-string for the task, from server_name and task_id
        task should be dict
        """
        if not isinstance(task, dict):
            return None
        res = []
        is_term = False  # if task is for search terms
        keys_to_check = {'site': 'site', 'url': 'url', 'urls': 'urls',
                         'searchterms_str': 'term',
                         'with_best_seller_ranking': 'bsr',
                         'branch_name': 'branch'}
        for key in sorted(keys_to_check.keys()):
            val = task.get(key)
            if val is not None:
                if key == 'searchterms_str':
                    is_term = True
                res.append('%s-%s' % (keys_to_check[key], val))
        for key in sorted(task.get('cmd_args', {}).keys()):
            res.append('%s-%s' % (key, task['cmd_args'][key]))
        res = ':'.join(res)
        return is_term, res

    def _parse_freshness(self, task):
        allowed_values = ['day', 'hour', '30 minutes', '15 minutes']
        limit = task.get('sqs_cache_time_limit', 'day')
        if limit not in allowed_values:  # validate field
            limit = 'day'
        if limit == allowed_values[0]:
            d = date.today()
            return int(mktime(d.timetuple()))
        # timetuple: [0]-year, [1]-month, [2]-day, [3]-hour, [4]-min,
        #  [5]-sec, [6]-week day, [7]-year day, [8]-is dst
        d = list(datetime.now().timetuple())
        d[5] = 0  # seconds
        if limit == allowed_values[1]:
            d[4] = 0
        elif limit == allowed_values[2]:
            d[4] -= d[4] % 30
        elif limit == allowed_values[3]:
            d[4] -= d[4] % 15
        return int(mktime(d))

    def get_result(self, task_str, queue):
        """
        retrieve cached result
        freshness in minutes
        returns tuple (is_item_found_in_cache, item_or_None)
        """
        task = json.loads(task_str)
        is_term, uniq_key = self._task_to_key(task)
        if not uniq_key:
            return False, None
        if queue.endswith('urgent'):  # save how long task was in the queue
            sent_time = task.get('attributes', {}).get('SentTimestamp', '')
            if sent_time:
                # amazon's time differs
                sent_time = (int(sent_time) / 1000)
                cur_time = time()
                self.db.zadd(
                    self.REDIS_URGENT_STATS, int(cur_time-sent_time), cur_time)
        score = self.db.zscore(self.REDIS_CACHE_TIMESTAMP, uniq_key)
        if not score:  # if not found item in cache
            return False, None
        freshness = self._parse_freshness(task)
        if score < freshness:  # if item is too old
            return True, None
        item = self.db.hget(self.REDIS_CACHE_KEY, uniq_key)
        if not item:
            return False, None
        if is_term:
            self.db.zincrby(self.REDIS_CACHE_STATS_TERM, uniq_key, 1)
        else:
            self.db.zincrby(self.REDIS_CACHE_STATS_URL, uniq_key, 1)
        item = decompress(item)
        return True, item

    def put_result(self, task_str, result):
        """
        put task response into cache
        returns True if success
        """
        task = json.loads(task_str)
        is_term, uniq_key = self._task_to_key(task)
        if not uniq_key:
            return False
        # save some space using compress
        self.db.hset(self.REDIS_CACHE_KEY, uniq_key, compress(result))
        self.db.zadd(self.REDIS_CACHE_TIMESTAMP, int(time()), uniq_key)
        return True

    def fail_result(self, task_str):
        """
        store failed task and count of failed attempts
        returns True, if task failed max allowed times
        """
        task = json.loads(task_str)
        task_id = task.get('task_id')
        task_server = task.get('server_name')
        if not task_id or not task_server:  # not enough of data
            return None
        task_key = '%s_%s' % (task_server, task_id)
        new_val = self.db.hincrby(self.REDIS_FAILED_TASKS, task_key, 1)
        return new_val >= self.MAX_FAILED_TRIES

    def get_all_failed_results(self):
        return self.db.hgetall(self.REDIS_FAILED_TASKS)

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
        self.db.delete(self.REDIS_INSTANCES_COUNTER,
                       self.REDIS_COMPLETED_COUNTER,
                       self.REDIS_FAILED_TASKS)

        return \
            (self.db.zremrangebyrank(self.REDIS_CACHE_STATS_URL, 0, -1),
             self.db.zremrangebyrank(self.REDIS_CACHE_STATS_TERM, 0, -1),
             self.db.zremrangebyrank(self.REDIS_COMPLETED_TASKS, 0, -1),
             self.db.zremrangebyrank(self.REDIS_URGENT_STATS, 0, -1))

    def purge_cache(self):
        """
        removes all data, related to cache
        """
        self.db.delete(self.REDIS_CACHE_TIMESTAMP, self.REDIS_CACHE_KEY,
                       self.REDIS_CACHE_STATS_URL, self.REDIS_CACHE_STATS_TERM)

    def complete_task(self, task_str, is_from_cache_str='false'):
        task = json.loads(task_str)
        is_from_cache = json.loads(is_from_cache_str)
        is_term, _ = self._task_to_key(task)
        key = '%s_%s' % (task.get('task_id'), task.get('server_name'))
        key_counter = 'term' if is_term else 'url'
        if is_from_cache:
            key_counter += '_cached'
        self.db.hincrby(self.REDIS_COMPLETED_COUNTER,
                        self.REDIS_COMPLETED_COUNTER_DICT[key_counter])
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
        return self.db.get(self.REDIS_INSTANCES_COUNTER)

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

    def get_most_popular_cached_items(self, cnt=10, is_term=False):
        """
        gets 10 most popular items in cache
        """
        if is_term:
            key = self.REDIS_CACHE_STATS_TERM
        else:
            key = self.REDIS_CACHE_STATS_URL
        return self.db.zrevrangebyscore(key, 9999, 0, 0, cnt, True, int)

    def get_used_memory(self):
        return self.db.info().get('used_memory_human')

    def get_total_cached_responses(self, is_term=False):
        """
        returns tuple of 2 elements: unique elements, requested from cache and
        total number of elements requested from cache
        """
        if is_term:
            key = self.REDIS_CACHE_STATS_TERM
        else:
            key = self.REDIS_CACHE_STATS_URL
        data = self.db.zrange(key, 0, -1, withscores=True, score_cast_func=int)
        return len(data), sum([_[1] for _ in data])

    def get_urgent_stats(self):
        """
        returns tuple of five items:
          - item with lowest time stayed in queue
          - item with biggest time stayed in queue
          - average time, for which items stay in queue
          - count of items, which were in queue more then hour
          - total amount of records in urgent statistics
         """
        data = self.db.zrange(self.REDIS_URGENT_STATS, 0, -1,
                              withscores=True, score_cast_func=int)
        data_more_then_hour = self.db.zcount(
            self.REDIS_URGENT_STATS, 60*60, 999999)
        if data:
            min_val = data[0][1]
            max_val = data[-1][1]
            avg_val = sum([d[1] for d in data]) / float(len(data))
        else:
            min_val = 0
            max_val = 0
            avg_val = 0
        return min_val, max_val, avg_val, data_more_then_hour, len(data)

    def get_completed_stats(self):
        data = self.db.hgetall(self.REDIS_COMPLETED_COUNTER)
        for key in self.REDIS_COMPLETED_COUNTER_DICT:
            if key not in data or not data[key]:
                data[key] = 0
            else:
                data[key] = int(data[key])
        data['url_total'] = data['url'] + data['url_cached']
        data['term_total'] = data['term'] + data['term_cached']
        data['url_percent'] = '%0.4s' % (float(data['url_cached']) /
                                         (data['url_total'] or 1) * 100)
        data['term_percent'] = '%0.4s' % (float(data['term_cached']) /
                                          (data['term_total'] or 1) * 100)
        return data

    def get_cache_settings(self):
        """
        returns dict with current settings
        """
        path = '%s/%s' % (dirname(realpath(__file__)), self.CACHE_SETTINGS_PATH)
        with open(path, 'r') as f:
            s = f.read()
        data = json.loads(s or '{}')
        return data

    def save_cache_settings(self, data):
        """
        saves settings dict to file
        """
        if not data:
            return
        path = '%s/%s' % (dirname(realpath(__file__)), self.CACHE_SETTINGS_PATH)
        with open(path, 'w') as f:
            s = json.dumps(data)
            f.write(s)

    def del_redis_keys(self, *keys):
        self.db.delete(*keys)

    def save_today_instances_count(self, instances_num=None):
        cnt = instances_num or self.db.get(self.REDIS_INSTANCES_COUNTER)
        cnt = int(cnt or '0')
        today = date.today() - timedelta(days=1)
        today = int(mktime(today.timetuple()))  # get today's timestamp
        # score is current day timestamp, name is instances count
        return self.db.zadd(self.REDIS_INSTANCES_HISTORY, today,
                            '%s:%s' % (today, cnt))

    def get_instances_history(self, days):
        date_offset = date.today() - timedelta(days=days+1)
        offset = int(mktime(date_offset.timetuple()))
        data = self.db.zrevrangebyscore(self.REDIS_INSTANCES_HISTORY,
                                        9999999999, offset,
                                        withscores=True, score_cast_func=int)
        res = [(d[1], d[0].split(':')[-1]) for d in data]
        res = OrderedDict(res)
        return res
