import os.path
import re
import urlparse
import json

import scrapy
from scrapy.log import WARNING, ERROR
from scrapy.http import Request, HtmlResponse
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
            product['total_matches'] = self.quantity
            if is_prime:
                product['prime'] = 'Prime'
            if is_prime_pantry:
                product['prime'] = 'PrimePantry'
            yield urlparse.urljoin(response.url, _href), product

    def _scrape_total_matches(self, response):
        return self.quantity

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