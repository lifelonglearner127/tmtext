#
# Custom extensions
#

from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

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