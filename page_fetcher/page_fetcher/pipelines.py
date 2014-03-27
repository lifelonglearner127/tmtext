# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.log import INFO, ERROR
from scrapy.log import msg
import requests

from page_fetcher.items import (PageItem, RequestErrorItem)


class PageFetcherPipeline(object):

    URL_BASE = 'http://localhost:8080/'
    URL_SAVED_PARSED_FROM_TEXT = 'save_parsed_from_text/'
    URL_URL_LOAD_FAILED = 'url_load_failed/'

    def __init__(self):
        self.log = msg

    def process_item(self, item, spider):
        if isinstance(item, PageItem):
            self.save_page(item)
        elif isinstance(item, RequestErrorItem):
            self.save_error(item)

        return item

    def save_page(self, page_item):
        self.log("Saving page %s." % page_item.get('url'), level=INFO)
        r = requests.post(self.URL_BASE + self.URL_SAVED_PARSED_FROM_TEXT, {
            'url': page_item['url'],
            'id': page_item['id'],
            'imported_data_id': page_item['imported_data_id'],
            'category_id': page_item['category_id'],
            'text': page_item['body'],
            'info': '',
        })

        if r.status_code < 400:
            msg = "Page saved (%d)." % r.status_code
            level = INFO
        elif r.status_code < 500:
            msg = "Page save failed because of us (%d)!" % r.status_code
            level = ERROR
        else:
            msg = "Page save failed because of server (%d)!" % r.status_code
            level = ERROR
        self.log(msg, level=level)

    def save_error(self, error_item):
        self.log("Saving load failure for URL id %d." % error_item.get('id'),
                 level=INFO)
        r = requests.post(self.URL_BASE + self.URL_URL_LOAD_FAILED, {
            'id': error_item['id'],
            'http_code': error_item['http_code'],
            'error_string': error_item['error_string'],
        })

        if r.status_code < 400:
            msg = "Load failure saved (%d)." % r.status_code
            level = INFO
        elif r.status_code < 500:
            msg = "Load failure not saved because of us (%d)!" \
                % r.status_code
            level = ERROR
        else:
            msg = "Load failure not saved because of server (%d)!" \
                % r.status_code
            level = ERROR
        self.log(msg, level=level)
