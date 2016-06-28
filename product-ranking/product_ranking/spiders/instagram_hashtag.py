# -*- coding: utf-8 -*-
import re
import json
from scrapy import Spider, FormRequest, Item, Field, Request


class InstagramHashtagItem(Item):
    handles = Field()
    count = Field()


class InstagramHashtagsSpider(Spider):
    name = "instagram_hashtags"
    allowed_domains = ["instagram.com"]
    download_delay = 0.25
    SEARCH_URL = 'https://www.instagram.com/explore/tags/{}'

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = 99999
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.zip_code = '12345'
        self.current_page = 1

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': 99999, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        self._setup_class_compatibility()
        super(InstagramHashtagsSpider, self).__init__(
            site_name="instagram.com",
            *args, **kwargs)
        self.hashtag =  self.searchterms_str



        self.num_pages = 1
        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
                          " AppleWebKit/537.36 (KHTML, like Gecko)" \
                          " Chrome/37.0.2062.120 Safari/537.36"

        # variants are switched off by default, see Bugzilla 3982#c11
        self.scrape_variants_with_extra_requests = False
        if 'scrape_variants_with_extra_requests' in kwargs:
            scrape_variants_with_extra_requests = kwargs['scrape_variants_with_extra_requests']
            if scrape_variants_with_extra_requests in (1, '1', 'true', 'True', True):
                self.scrape_variants_with_extra_requests = True

    @staticmethod
    def valid_url(url):
        if not re.findall(r"http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.SEARCH_URL.format(self.hashtag)),
                      meta=self._setup_meta_compatibility(),
                      callback=self._parse_single_product)  # meta is for SC baseclass compatibility

    def _parse_single_product(self, response):
        url = response.url
        hashtag = url.split('/')[-2]
        javascript = "".join(response.xpath(
            '//script[contains(text(), "sharedData")]/text()'
        ).extract())
        json_data = json.loads("".join(re.findall(
            r'window._sharedData = (.*);', javascript)))
        item = InstagramHashtagItem()
        data = json_data.get('entry_data').get('TagPage')[0]
        item['handles'] = []
        end_cursor = False

        csrf_token = json_data.get('config').get('csrf_token')
        yield self._build_request(hashtag, end_cursor, csrf_token, response.url, item)

    def _parse_handles(self, response):
        item = response.meta['item']
        data = json.loads(response.body_as_unicode()).get('media')
        page_info = data.get('page_info')
        handles = [node.get('owner').get('username') for node in data.get('nodes')]
        item['handles'] += handles
        meta = response.meta
        if page_info.get('has_next_page'):
            yield self._build_request(
                meta.get('hashtag'),
                page_info.get('end_cursor'),
                meta.get('csrf_token'),
                meta.get('url'),
                item
            )
        else:
            item['handles'] = list(set(item['handles']))
            item['count'] = len(item['handles'])
            yield item

    @staticmethod
    def _query_string(hashtag, end_cursor=False):
        """q (POST) parameter"""
        if end_cursor:
            return """ig_hashtag(%s) { media.after(%s, 500) {
                nodes {
                  comments {
                    count
                  },
                  likes {
                    count
                  },
                  owner {
                    id,
              username

                  }
                },
                page_info
              }
               }""" % (hashtag, end_cursor)
        else:
            return """ig_hashtag(%s) { media.first(1) {
                nodes {
                  comments {
                    count
                  },
                  likes {
                    count
                  },
                  owner {
                    id,
              username

                  }
                },
                page_info
              }
               }""" % (hashtag)

    def _build_request(self, hashtag, end_cursor, csrf_token, url, item):
        posts_url = 'https://www.instagram.com/query/'
        query = self._query_string(hashtag, end_cursor)
        ref = 'tags::show'

        # dicts required for /query
        formdata = {'q': query, 'ref': ref}
        headers = {'X-Instagram-AJAX': '1',
                   'X-CSRFToken': csrf_token,
                   'X-Requested-With': 'XMLHttpRequest',
                   'Referer': url,
                   'Content-Type': 'application/x-www-form-urlencoded'}

        request = FormRequest(posts_url, method='POST',
                              callback=self._parse_handles,
                              formdata=formdata,
                              headers=headers)
        request.meta['item'] = item
        request.meta['hashtag'] = hashtag
        request.meta['csrf_token'] = csrf_token
        request.meta['url'] = url
        return request
    