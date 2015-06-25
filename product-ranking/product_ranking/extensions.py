#
# Custom extensions
#

import os
import sys
import datetime

from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import boto
from boto.s3.connection import S3Connection
from s3peat import S3Bucket, sync_to_s3  # pip install s3peat
import workerpool  # pip install workerpool

from cache import get_partial_request_path
import cache
import settings

try:
    from monitoring import push_simmetrica_event
except ImportError:
    try:
        from spiders import push_simmetrica_event
    except ImportError:
        try:
            from product_ranking.spiders import push_simmetrica_event
        except ImportError:
            print 'ERROR: CAN NOT IMPORT MONITORING PACKAGE!'

amazon_public_key = 'AKIAIKTYYIQIZF3RWNRA'
amazon_secret_key = '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'
bucket_name = 'spiders-cache'


def _stats_on_spider_open(spider):
    if not push_simmetrica_event('monitoring_spider_opened'):
        print 'pushing simmetrica event failed, check redis server and all'\
              ' the events'
    push_simmetrica_event('monitoring_spider_opened_'+spider.name)


def _stats_on_spider_close(spider, reason):
    spider_stats = spider.crawler.stats.get_stats()
    running_time = (spider_stats['finish_time']
                    - spider_stats['start_time']).total_seconds()

    # TODO:
    # also send closing values
    # memory overusage: memusage_exceeded
    # normal: finished
    # ctrl+c: shutdown
    from pprint import pprint
    pprint(spider_stats)
    if not push_simmetrica_event('monitoring_spider_closed'):
        print 'pushing simmetrica event failed, check redis server and all'\
              ' the events'
    push_simmetrica_event('monitoring_spider_closed_'+spider.name)
    push_simmetrica_event('monitoring_spider_working_time',  # general config
                          increment_by=int(running_time))
    push_simmetrica_event('monitoring_spider_working_time_'+spider.name,
                          increment_by=int(running_time))
    if spider_stats.get('dupefilter/filtered', None):
        push_simmetrica_event(
            'monitoring_spider_dupefilter_filtered_'+spider.name,
            increment_by=int(spider_stats['dupefilter/filtered'])
        )
    if spider_stats.get('downloader/request_count', None):
        push_simmetrica_event(
            'monitoring_spider_downloader_request_count_'+spider.name,
            increment_by=int(spider_stats['downloader/request_count'])
        )
    if spider_stats.get('downloader/response_bytes', None):
        push_simmetrica_event(
            'monitoring_spider_downloader_response_bytes_'+spider.name,
            increment_by=int(
                spider_stats['downloader/response_bytes'] / 1024 / 1024  # MBytes
            )
        )
    print 'Simmetrica events have been pushed...'


class StatsCollector(object):

    def __init__(self, *args, **kwargs):
        dispatcher.connect(_stats_on_spider_open, signals.spider_opened)
        dispatcher.connect(_stats_on_spider_close, signals.spider_closed)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


def _s3_cache_on_spider_close(spider, reason):
    # upload cache
    bucket = S3Bucket(bucket_name, amazon_public_key, amazon_secret_key,
                      public=False)
    folder_path = get_partial_request_path(settings.HTTPCACHE_DIR, spider)
    if not os.path.exists(folder_path):
        print('Path to upload does not exist:', folder_path)
        return
    print('Uploading cache to', folder_path)
    try:
        # Upload file to S3
        sync_to_s3(
            directory=folder_path,
            prefix=os.path.relpath(folder_path, settings.HTTPCACHE_DIR),
            bucket=bucket,
            concurrency=20
        )
    except Exception as e:
        print('ERROR UPLOADING TO S3', str(e))
        pass
        #logger.error("Failed to load log files to S3. "
        #             "Check file path and amazon keys/permissions.")


class S3CacheUploader(object):

    def __init__(self, *args, **kwargs):
        dispatcher.connect(_s3_cache_on_spider_close, signals.spider_closed)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


def _download_s3_file(key):
    _local_cache_file = os.path.join(settings.HTTPCACHE_DIR, key.key)
    _dir = os.path.dirname(_local_cache_file)
    if not os.path.exists(_dir):
        os.makedirs(_dir)
    print('Downloading cache file', _local_cache_file)
    try:
        res = key.get_contents_to_filename(_local_cache_file)
    except Exception as e:
        print(str(e))


class S3CacheDownloader(object):

    def _get_load_from_date(self):
        arg = [a for a in sys.argv if 'load_from_s3_cache' in a]
        if arg:
            arg = arg[0].split('=')[1].strip()
            return datetime.datetime.strptime(arg, '%Y-%m-%d')

    def __init__(self, crawler, *args, **kwargs):
        # download s3 cache
        cache.UTC_NOW = self._get_load_from_date()
        conn = S3Connection(amazon_public_key, amazon_secret_key)
        bucket = conn.get_bucket(bucket_name)
        partial_path = get_partial_request_path(settings.HTTPCACHE_DIR,
                                                crawler._spider)

        _cache_found = False
        _keys2download = []
        for key in bucket.list():
            if key.key.startswith(os.path.relpath(
                    partial_path, settings.HTTPCACHE_DIR)):
                _cache_found = True
                _keys2download.append(key)
        if not _cache_found:
            print('Cache is not found! Check the date param!')
            sys.exit(1)
        # TODO: fix! (threaded downloading hangs up for unknown reasons)
        """
        # init pool
        pool = workerpool.WorkerPool(size=10)
        # The ``download`` method will be called with a line from the second
        # parameter for each job.
        pool.map(_download_s3_file, _keys2download)
        # Send shutdown jobs to all threads, and wait until all the jobs have been completed
        pool.shutdown()
        pool.wait()
        """
        for key2download in _keys2download:
            _download_s3_file(key2download)
        # TODO: it's for debugging! remove me
        while os.path.exists('/tmp/_removeme'):
            import time
            time.sleep(0.5)


    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


if __name__ == '__main__':
    if 'clear_bucket' in sys.argv:  # be careful!
        from boto.s3.connection import S3Connection
        conn = S3Connection(amazon_public_key, amazon_secret_key)
        bucket = conn.get_bucket(bucket_name)
        for f in bucket.list():
            bucket.delete_key(f.key)
    else:
        # list all files in bucket, for convenience
        CWD = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(os.path.join(CWD, '..', '..', 'deploy',
                                     'sqs_ranking_spiders'))
        from list_all_files_in_s3_bucket import list_files_in_bucket
        for f in (list_files_in_bucket(
                amazon_public_key, amazon_secret_key, bucket_name)):
            print f
