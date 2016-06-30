import os.path
import re
import urlparse
import json

import scrapy
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG
from scrapy.http import Request, HtmlResponse
from scrapy import Selector
from product_ranking.spiders import cond_set_value
from product_ranking.items import SiteProductItem
from product_ranking.marketplace import Amazon_marketplace
from spiders_shared_code.amazon_variants import AmazonVariants
from itertools import islice

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

        #backup when total matches cannot be scraped
        self.total_items_scraped = 0
        self.remaining = self.quantity
        # self.ranking_override = 0
        self.total_matches_re = r'of\s([\d\,]+)\s'
        super(AmazonShelfPagesSpider, self).__init__(*args, **kwargs)

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility())  # meta is for SC baseclass compatibility

    _scraped_product_links_count = 0  # TODO: remove and implement another way of controlling the limits
    def _scrape_product_links(self, response):
        links_xpath = (
            '//*[@id="dealHoverContent"]//a[contains(@href, "p/")]'
            ' | //div[contains(@class, "imageContainer")]'
            '/../../..//a[contains(@href, "p/")]'
            ' | //div[contains(@id, "atfResults")]//a[contains(@href, "p/")]'
            ' | //a[contains(@href, "p/") and contains(@class, "dealTitle")]'
            ' | //*[contains(@class, "imagebox_imagemap")]/../../a[contains(@href, "p/")]'
            ' | //li[contains(@id, "result_")]//h2/../../a[contains(@href, "p/")]'
            ' | //*[contains(@class, "dv-shelf-item")]//img/../../a[contains(@href, "p/")]'
        )
        links = response.xpath(links_xpath)

        # TODO: remove later
        self._scraped_product_links_count += 1
        if self._scraped_product_links_count > 50:
            return

        if not links:
            # page with lots of JS requests? try selenium
            # TODO: thread-safe
            from selenium import webdriver
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            self.log('No product links found at first attempt'
                     ' - trying PhantomJS with UA %s' % self.user_agent)
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = self.user_agent
            driver = webdriver.PhantomJS(desired_capabilities=dcap)
            driver.set_page_load_timeout(60)
            driver.set_script_timeout(60)
            driver.set_window_size(1280, 1024)
            try:
                driver.get(self.product_url)
                driver.save_screenshot('/tmp/page.png')
            except Exception as e:
                print('Exception while loading url: %s' % str(e))
            scrapy_response = HtmlResponse(
                url=response.url, body=driver.page_source.encode('utf8'))
            links = scrapy_response.xpath(links_xpath)
            driver.quit()

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
        for link in links:
            _href = link.xpath('./@href').extract()[0]
            if '/product-reviews/' in _href:
                continue
            is_prime = link.xpath(
                './..//*[contains(@class, "a-icon-prime")]')
            is_prime_pantry = link.xpath(
                './..//*[contains(@class, "a-icon-prime-pantry")]')
            product = SiteProductItem()
            if is_prime:
                product['prime'] = 'Prime'
            if is_prime_pantry:
                product['prime'] = 'PrimePantry'
            yield urlparse.urljoin(response.url, _href), product

    def _get_products(self, response):
        remaining = response.meta['remaining']
        search_term = response.meta['search_term']
        prods_per_page = response.meta.get('products_per_page')
        total_matches = response.meta.get('total_matches')
        scraped_results_per_page = response.meta.get('scraped_results_per_page')

        prods = self._scrape_product_links(response)

        if prods_per_page is None:
            # Materialize prods to get its size.
            prods = list(prods)
            prods_per_page = len(prods)
            response.meta['products_per_page'] = prods_per_page

        if scraped_results_per_page is None:
            scraped_results_per_page = self._scrape_results_per_page(response)
            if scraped_results_per_page:
                self.log(
                    "Found %s products at the first page" % scraped_results_per_page
                    , INFO)
            else:
                scraped_results_per_page = prods_per_page
                if hasattr(self, 'is_nothing_found'):
                    if not self.is_nothing_found(response):
                        self.log(
                            "Failed to scrape number of products per page", ERROR)
            response.meta['scraped_results_per_page'] = scraped_results_per_page

        if total_matches is None:
            total_matches = self._scrape_total_matches(response)
            if total_matches is not None:
                response.meta['total_matches'] = total_matches
                self.log("Found %d total matches." % total_matches, INFO)
            else:
                if hasattr(self, 'is_nothing_found'):
                    if not self.is_nothing_found(response):
                        self.log(
                            "Failed to parse total matches for %s" % response.url, ERROR)

        if total_matches and not prods_per_page:
            # Parsing the page failed. Give up.
            self.log("Failed to get products for %s" % response.url, ERROR)
            return

        if self.current_page == 1:
            self.quantity = min(total_matches, self.quantity) if total_matches else self.quantity
            self.remaining = self.quantity
        else:
            self.remaining -= prods_per_page

        for i, (prod_url, prod_item) in enumerate(islice(prods, 0, self.remaining)):
            # Initialize the product as much as possible.
            prod_item['site'] = self.site_name
            prod_item['search_term'] = search_term
            prod_item['total_matches'] = total_matches
            prod_item['results_per_page'] = prods_per_page
            prod_item['scraped_results_per_page'] = scraped_results_per_page
            # The ranking is the position in this page plus the number of
            # products from other pages.

            if not total_matches:
                prod_item['ranking'] = (i + 1) + self.total_items_scraped
            else:
                prod_item['ranking'] = (i + 1) + (self.quantity - self.remaining)
            if self.user_agent_key not in ["desktop", "default"]:
                prod_item['is_mobile_agent'] = True

            if prod_url is None:
                # The product is complete, no need for another request.
                yield prod_item
            elif isinstance(prod_url, Request):
                cond_set_value(prod_item, 'url', prod_url.url)  # Tentative.
                yield prod_url
            else:
                # Another request is necessary to complete the product.
                url = urlparse.urljoin(response.url, prod_url)
                cond_set_value(prod_item, 'url', url)  # Tentative.
                yield Request(
                    url,
                    callback=self.parse_product,
                    meta={'product': prod_item},
                )

        self.total_items_scraped += prods_per_page

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        next_link = super(AmazonShelfPagesSpider, self).\
            _scrape_next_results_page_link(response)
        if not next_link:
            next_link = response.xpath(
                '//*[contains(@id, "pagnNextLink")]/@href').extract()
        if next_link:
            return next_link

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