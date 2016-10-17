#
# Custom extensions
#

import os
import sys
import datetime
from time import time
from multiprocessing.connection import Client
from socket import error as socket_error

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.xlib.pydispatch import dispatcher
import boto
from boto.s3.connection import S3Connection
from s3peat import S3Bucket, sync_to_s3  # pip install s3peat
import workerpool  # pip install workerpool

import cache
import settings
from cache_models import create_db_cache_record

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

CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CWD, '..', '..', 'deploy'))

try:
    from cache_layer.cache_service import SqsCache
except ImportError:
    print 'ERROR: CANNOT IMPORT SQSCACHE PACKAGE!'


bucket_name = 'spiders-cache'


def report_stats(signal_name):
    """
    Decorator, which sends signal to the connection
    with the signal_name as name parameter two times.
    One before method execution with status 'started'.
    Second after method execution with status 'closed'
    :param signal_name: name of the signal
    """
    def wrapper(func):

        def send_signal(name, status):
            data = dict(name=name, status=status)
            SignalsExtension.CONNECTION.send(data)

        def wrapped(*args, **kwargs):
            if not SignalsExtension.CONNECTION:
                return
            # 1) report signal start
            send_signal(signal_name, SignalsExtension.STATUS_STARTED)
            # 2) execute method
            res = func(*args, **kwargs)
            # 3) report signal finish
            send_signal(signal_name, SignalsExtension.STATUS_FINISHED)
            # 4) return result
            return res

        return wrapped

    return wrapper


def _ip_on_spider_open(spider):
    server_ip = getattr(spider, 'server_ip', None)
    if not server_ip:
        return
    ip_fname = '/tmp/_server_ip'
    if not os.path.exists(ip_fname):
        with open(ip_fname, 'w') as fh:
            fh.write(server_ip)
    print('Server IP: %s' % server_ip)
    if hasattr(spider, 'log'):
        spider.log('Server IP: %s' % server_ip)


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


class RequestsCounter(object):

    __sqs_cache = None

    def __init__(self, *args, **kwargs):
        dispatcher.connect(RequestsCounter.__handler, signals.spider_closed)

    @classmethod
    def get_sqs_cache(cls):
        if cls.__sqs_cache is None:
            cls.__sqs_cache = SqsCache()
        return cls.__sqs_cache

    @staticmethod
    def __handler(spider, reason):
        spider_stats = spider.crawler.stats.get_stats()
        try:
            request_count = int(spider_stats.get('downloader/request_count'))
        except (ValueError, TypeError):
            request_count = 0
        if request_count:
            try:
                RequestsCounter.get_sqs_cache().db.incr(
                    RequestsCounter.get_sqs_cache().REDIS_REQUEST_COUNTER,
                    request_count
                )
            except Exception as e:
                print 'ERROR WHILE STORE REQUEST METRICS. EXP: %s', e

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


def _s3_cache_on_spider_close(spider, reason):
    utcnow = datetime.datetime.utcnow()
    # upload cache
    bucket = S3Bucket(bucket_name, public=False)
    folder_path = cache.get_partial_request_path(
        settings.HTTPCACHE_DIR, spider, utcnow)
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
        uploaded_to_s3 = True
    except Exception as e:
        print('ERROR UPLOADING TO S3', str(e))
        pass
        uploaded_to_s3 = False
        #logger.error("Failed to load log files to S3. "
        #             "Check file path and amazon keys/permissions.")
    # create DB record
    if uploaded_to_s3:
        create_db_cache_record(spider, utcnow)
    # remove local cache
    # DO NOT CLEAR LOCAL CACHE on file upload - otherwise you may delete cache of
    #  a spider working in parallel!


class S3CacheUploader(object):

    def __init__(self, crawler, *args, **kwargs):
        # check cache map - maybe such cache already exists?
        enable_cache_upload = True
        utcdate = cache.UTC_NOW if cache.UTC_NOW else datetime.datetime.utcnow()
        utcdate = utcdate.date()
        print('Checking if cache already exists')
        cache_map = cache.get_cache_map(
            spider=crawler._spider.name, date=utcdate)
        if crawler._spider.name in cache_map:
            if utcdate in cache_map[crawler._spider.name]:
                if cache._get_searchterms_str_or_product_url() \
                        in cache_map[crawler._spider.name][utcdate]:
                    print('Cache for this date, spider,'
                          ' and searchterm already exists!'
                          ' Cache will NOT be uploaded!')
                    enable_cache_upload = False
        if enable_cache_upload:
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

    def __init__(self, crawler, *args, **kwargs):
        _load_from = cache._get_load_from_date()
        _blocker_fname = '/tmp/_cache_spider_blocker'
        os.system("echo '1' > %s" % _blocker_fname)
        # remove local cache
        cache.clear_local_cache(settings.HTTPCACHE_DIR, crawler._spider,
                                _load_from)
        # download s3 cache
        # TODO: speed up by using cache_map from DB!
        conn = S3Connection()
        bucket = conn.get_bucket(bucket_name)
        partial_path = cache.get_partial_request_path(
            settings.HTTPCACHE_DIR, crawler._spider, _load_from)
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
        print('Cache downloaded; ready for re-parsing the data, remove'
              ' %s file when you are ready' % _blocker_fname)
        while os.path.exists(_blocker_fname):
            import time
            time.sleep(0.5)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


class SignalsExtension(object):

    STATUS_STARTED = 'opened'
    STATUS_FINISHED = 'closed'
    CONNECTION = None

    def __init__(self, crawler):
        # self.send_finish_signal('script_opened')
        pass

    def item_scraped(self, item, spider):
        SignalsExtension.CONNECTION.send(dict(name='item_scraped'))

    def item_dropped(self, item, spider, exception):
        SignalsExtension.CONNECTION.send(dict(name='item_dropped'))

    def spider_error(self, failure, response, spider):
        SignalsExtension.CONNECTION.send(dict(name='spider_error'))

    def spider_opened(self, spider):
        self.send_finish_signal('spider_opened')

    def spider_closed(self, spider):
        self.send_finish_signal('spider_closed')
        SignalsExtension.CONNECTION.close()

    def send_finish_signal(self, name):
        if not SignalsExtension.CONNECTION:
            print 'Finish signal:', name
        else:
            SignalsExtension.CONNECTION.send(dict(
                name=name, status=SignalsExtension.STATUS_FINISHED)
            )

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('WITH_SIGNALS'):
            print 'pass signals ext'
            raise NotConfigured
        SignalsExtension.create_connection(('localhost', 9070))
        ext = cls(crawler)
        crawler.signals.connect(ext.spider_opened, signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signals.spider_closed)
        crawler.signals.connect(ext.item_scraped, signals.item_scraped)
        crawler.signals.connect(ext.item_dropped, signals.item_dropped)
        crawler.signals.connect(ext.spider_error, signals.spider_error)
        return ext

    @staticmethod
    def create_connection(address):
        print 'create connection'
        try:
            # raises after 20 secs of waiting
            SignalsExtension.CONNECTION = Client(address)
            print 'connection set'
        except socket_error:
            print 'no connection'
            raise NotConfigured


class IPCollector(object):

    def __init__(self, crawler, *args, **kwargs):
        dispatcher.connect(_ip_on_spider_open, signals.spider_opened)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


if __name__ == '__main__':
    from pprint import pprint
    from boto.s3.connection import S3Connection
    conn = S3Connection()
    bucket = conn.get_bucket(bucket_name)
    if 'clear_bucket' in sys.argv:  # be careful!
        if raw_input('Delete all files? y/n: ').lower() == 'y':
            for f in bucket.list():
                print '    removing', f
                bucket.delete_key(f.key)
        else:
            print('You did not type "y" - exit...')
    elif 'cache_map' in sys.argv:  # lists available cache
        cache_map = cache.get_cache_map()
        for spider, dates in cache_map.items():
            print '\n\n'
            print spider
            for date, searchterms in dates.items():
                print ' '*4, date
                for searchterm in searchterms:
                    print ' '*8, searchterm
    else:
        # list all files in bucket, for convenience
        from sqs_ranking_spiders.list_all_files_in_s3_bucket import \
            list_files_in_bucket
        for f in (list_files_in_bucket(bucket_name)):
            print f.key
