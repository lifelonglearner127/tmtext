import json
import re
from spiders_shared_code.shoprite_categories import ShopriteCategoryParser
from scrapy.http import Request
from .shoprite import ShopriteProductsSpider


class ShopriteShelfPagesSpider(ShopriteProductsSpider):
    name = 'shoprite_shelf_urls_products'
    PRODUCTS_URL = "https://shop.shoprite.com/api/product/v5/products/category/" \
                   "{category_id}/store/{store}?sort=Brand&skip={skip}&take=20&userId={user_id}"

    def __init__(self, *args, **kwargs):
        super(ShopriteShelfPagesSpider, self).__init__(*args, **kwargs)
        self.store = self._parse_store(self.product_url)
        self.categories = []
        self._categories = self._parse_categories_from_url(self.product_url)
        self.current_page = 1

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1

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

    def _parse_configuration(self, response):
        configuration = self._parse_info(response)
        return configuration

    @staticmethod
    def _parse_request_headers(response, token):
        return {
            'Authorization': token,
            'Referer': response.url,
            'Accept': 'application/vnd.mywebgrocer.grocery-list+json'
        }

    def _parse_helper(self, response):
        meta = response.meta
        if not meta.get('token'):
            configuration = self._parse_configuration(response)
            meta['token'] = self._parse_token(configuration)
            meta['user_id'] = self._parse_user_id(configuration)
            meta['headers'] = self._parse_request_headers(response, meta['token'])
            categories_ch = ShopriteCategoryParser()
            categories_ch.setupSC(self._categories, meta['headers'], self.store, meta['user_id'])
            self.categories = categories_ch.get_categories_names()
        return Request(self.PRODUCTS_URL.format(user_id=meta['user_id'],
                                                store=self.store,
                                                skip=response.meta.get('skip', 0),
                                                category_id=self._categories[-1]),
                       headers=meta['headers'],
                       meta=meta,
                       dont_filter=True)

    @staticmethod
    def _parse_categories_from_url(url):
        pattern = re.compile(r'/category/(.+?)/')
        found = pattern.findall(url)
        return found[0].split(',') if found else None

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        info = json.loads(response.body)
        page = info.get('PageLinks')[-1]
        skip = info.get('Skip') + 20
        if page.get('Rel') == 'next':
            response.meta['skip'] = skip
            return self._parse_helper(response)
