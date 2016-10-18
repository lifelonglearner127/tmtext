# TODO: request to fetch all categories names: https://shop.shoprite.com/api/product/v5/categories/store/{store}?userId={user_id}
from spiders_shared_code.shoprite_categories import ShopriteCategoryParser
from .shoprite import ShopriteProductsSpider
import re
import json
from scrapy.http import Request, FormRequest
from product_ranking.items import SiteProductItem
from scrapy.conf import settings
import requests


class ShopriteShelfPagesSpider(ShopriteProductsSpider):
    name = 'shoprite_shelf_urls_products'
    PRODUCTS_URL = "https://shop.shoprite.com/api/product/v5/products/category/{category_id}/store/{store}?sort=Brand&skip={skip}&take=20&userId={user_id}"

    def __init__(self, *args, **kwargs):
        super(ShopriteShelfPagesSpider, self).__init__(*args, **kwargs)
        self.configuration = None
        self.user_id = None
        self.token = None
        self.store = None
        self.categories = []
        self._categories = None
        self.current_page = 1

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

    def start_requests(self):
        if self.product_url:
            yield Request(self.product_url,
                          self._parse_helper,
                          meta={'search_term': '',
                                'remaining': self.quantity})

    def _parse_shelf_path(self):
        return self.categories

    def _parse_shelf_name(self):
        return self.categories[-1]

    def _parse_helper(self, response):
        meta = response.meta
        self.configuration = self._parse_info(
            response) if not self.configuration else self.configuration
        self.token = self._parse_token(
            self.configuration) if not self.token else self.token
        self.user_id = self._parse_user_id(
            self.configuration) if not self.user_id else self.user_id
        self._categories = self._parse_categories_from_url(
            self.product_url) if not self._categories else self._categories
        self.store = self._parse_store(
            self.product_url) if not self.store else self.store

        headers = {}
        headers['Authorization'] = self.token
        headers['Referer'] = response.url
        headers['Accept'] = 'application/vnd.mywebgrocer.grocery-list+json'

        if not self.categories:
            categories_CH = ShopriteCategoryParser()
            categories_CH.setupSC(self._categories, headers, self.store, self.user_id)
            self.categories = categories_CH.main()

        return Request(self.PRODUCTS_URL.format(user_id=self.user_id,
                                                store=self.store,
                                                skip=response.meta.get('skip', 0),
                                                category_id=self._categories[-1]),
                       headers=headers,
                       meta=meta)

    @staticmethod
    def _parse_categories_from_url(url):
        p = re.compile('\/category\/(.+?)\/')
        found = p.findall(url)
        return found[0].split(',') if found else None

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        super(ShopriteShelfPagesSpider, self)._scrape_next_results_page_link(response)

