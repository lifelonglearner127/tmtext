import os.path
import re
import urlparse
import json

import scrapy
from scrapy.log import WARNING, ERROR
from scrapy.http import Request
from scrapy import Selector

from product_ranking.items import SiteProductItem
from product_ranking.marketplace import Amazon_marketplace
from spiders_shared_code.amazon_variants import AmazonVariants

is_empty = lambda x: x[0] if x else None

from .amazon import AmazonProductsSpider

try:
    from captcha_solver import CaptchaBreakerWrapper
except ImportError as e:
    import sys
    print(
        "### Failed to import CaptchaBreaker.",
        "Will continue without solving captchas:",
        e,
    )

    class FakeCaptchaBreaker(object):
        @staticmethod
        def solve_captcha(url):
            print("No CaptchaBreaker to solve: %s" % url)
            return None
    CaptchaBreakerWrapper = FakeCaptchaBreaker


class AmazonShelfPagesSpider(AmazonProductsSpider):
    name = 'amazon_shelf_urls_products'
    allowed_domains = ["amazon.com", "www.amazon.com"]  # without this find_spiders() fails

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = 99999
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.current_page = 1
        self.captcha_retries = 12

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': 99999, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        self._setup_class_compatibility()

        self.product_url = kwargs['product_url']

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
            " AppleWebKit/537.36 (KHTML, like Gecko)" \
            " Chrome/37.0.2062.120 Safari/537.36"

        # variants are switched off by default, see Bugzilla 3982#c11
        self.scrape_variants_with_extra_requests = False
        if 'scrape_variants_with_extra_requests' in kwargs:
            scrape_variants_with_extra_requests = kwargs['scrape_variants_with_extra_requests']
            if scrape_variants_with_extra_requests in (1, '1', 'true', 'True', True):
                self.scrape_variants_with_extra_requests = True

        # Default price currency
        self.price_currency = 'USD'
        self.price_currency_view = '$'

        # Locale
        self.locale = 'en-US'

        self.mtp_class = Amazon_marketplace(self)
        self._cbw = CaptchaBreakerWrapper()

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility())  # meta is for SC baseclass compatibility

    def _scrape_product_links(self, response):
        urls = response.xpath(
            '//*[@id="dealHoverContent"]//a[contains(@href, "/gp/product/")]/@href'
            ' | //div[contains(@class, "imageContainer")]'
            '/../../..//a[contains(@href, "/gp/product/")]/@href').extract()

        urls = [urlparse.urljoin(response.url, x) for x in urls]

        # TODO:
        # parse shelf category
        """
        shelf_categories = [c.strip() for c in response.css('ol.breadcrumb-list ::text').extract()
                            if len(c.strip()) > 1]
        shelf_category = shelf_categories[-1] if shelf_categories else None

        for url in urls:
            item = SiteProductItem()
            if shelf_category:
                item['shelf_name'] = shelf_category
            if shelf_categories:
                item['shelf_path'] = shelf_categories
            yield url, item
        """
        for url in urls:
            yield url, SiteProductItem(total_matches=self.quantity)

    def _scrape_total_matches(self, response):
        return self.quantity

    #def _scrape_next_results_page_link(self, response):
    #    if self.current_page >= self.num_pages:
    #        return
    #    self.current_page += 1
    #    return super(WalmartShelfPagesSpider, self)._scrape_next_results_page_link(response)

    """
    def parse_product(self, response):
        product = response.meta['product']
        # scrape Shelf Name, e.g. Diapers, and Shelf Path, e.g. Baby/Diapering/Diapers
        wcp = WalmartCategoryParser()
        wcp.setupSC(response)
        try:
            product['categories'] = wcp._categories_hierarchy()
        except Exception as e:
            self.log('Category not parsed: '+str(e), WARNING)
        try:
            product['category'] = wcp._category()
        except Exception as e:
            self.log('No department to parse: '+str(e), WARNING)
        response.meta['product'] = product
        return super(WalmartShelfPagesSpider, self).parse_product(response)
    """

    def _parse_marketplace(self, response):
        # we are currently not scraping & not using marketplaces
        return