# ~~coding=utf-8~~
from __future__ import division, absolute_import, unicode_literals

import re

from scrapy.log import ERROR, WARNING
from scrapy.http import Request

from product_ranking.items import SiteProductItem
from product_ranking.marketplace import Amazon_marketplace

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


is_empty = lambda x: x[0] if x else None


class AmazonShelfPagesSpider(AmazonProductsSpider):
    name = 'amazon_shelf_urls_products'

    # without this find_spiders() fails
    allowed_domains = ["amazon.com", "www.amazon.com"]

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = 99999
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.current_page = 1
        self.captcha_retries = 12

    @staticmethod
    def _setup_meta_compatibility():
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': 99999, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        # For some reason amazon fail to scrape most data
        # when you turn off variants
        self.ignore_variant_data = False
        self.product_url = kwargs['product_url']

        # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0
        self.num_pages = int(kwargs.get('num_pages', 1))

        # # variants are switched off by default, see Bugzilla 3982#c11
        # self.scrape_variants_with_extra_requests = False
        # if 'scrape_variants_with_extra_requests' in kwargs:
        #     scrape_variants_with_extra_requests = \
        #         kwargs['scrape_variants_with_extra_requests']
        #     if scrape_variants_with_extra_requests in \
        #             (1, '1', 'true', 'True', True):
        #         self.scrape_variants_with_extra_requests = True

        # Default price currency
        self.price_currency = 'USD'
        self.price_currency_view = '$'

        # Locale
        self.locale = 'en-US'

        self.mtp_class = Amazon_marketplace(self)
        self._cbw = CaptchaBreakerWrapper()

        # #backup when total matches cannot be scraped
        # self.total_items_scraped = 0
        # # self.ranking_override = 0
        self.total_matches_re = r'of\s([\d\,]+)\s'
        super(AmazonShelfPagesSpider, self).__init__(*args, **kwargs)
        self._setup_class_compatibility()
        # self.remaining = self.quantity
        # settings.overrides['CRAWLERA_ENABLED'] = True

    @staticmethod
    def valid_url(url):
        if not url.startswith('http'):
            url = 'http://' + url
        return url

    def start_requests(self):
        yield Request(
            self.valid_url(self.product_url),
            meta={
                'search_term': '',
                'remaining': self.quantity
            },
        )

    def _scrape_product_links(self, response):
        """
        Overrides BaseProductsSpider method to scrape product links.
        """
        shelf_categories = [c.strip() for c in response.xpath(
            ".//*[@id='s-result-count']/span/*/text()").extract()
                            if len(c.strip()) > 1]
        shelf_category = shelf_categories[-1] if shelf_categories else None

        try:
            lis = response.xpath(
                "//div[@id='resultsCol']/./ul/li |"
                "//div[@id='mainResults']/.//ul/li [contains(@id, 'result')] |"
                "//div[@id='atfResults']/.//ul/li[contains(@id, 'result')] |"
                "//div[@id='mainResults']/.//div[contains(@id, 'result')] |"
                "//div[@id='btfResults']//ul/li[contains(@id, 'result')]")
            links = []
            last_idx = -1

            for li in lis:
                is_prime = li.xpath(
                    "*/descendant::i[contains(concat(' ', @class, ' '),"
                    "' a-icon-prime ')] |"
                    ".//span[contains(@class, 'sprPrime')]"
                )
                is_prime_pantry = li.xpath(
                    "*/descendant::i[contains(concat(' ',@class,' '),'"
                    "a-icon-prime-pantry ')]"
                )
                data_asin = self._is_empty(
                    li.xpath('@id').extract()
                )

                is_sponsored = \
                    bool(li.xpath('.//h5[contains(text(), "ponsored")]').extract())

                try:
                    idx = int(self._is_empty(
                        re.findall(r'\d+', data_asin)
                    ))
                except ValueError:
                    continue

                if idx > last_idx:
                    link = self._is_empty(
                        li.xpath(
                            ".//a[contains(@class,'s-access-detail-page')]/@href |"
                            ".//h3[@class='newaps']/a/@href"
                        ).extract()
                    )
                    if not link:
                        continue

                    if 'slredirect' in link:

                        link = 'http://' + self.allowed_domains[0] + '/' + link

                    links.append((link, is_prime, is_prime_pantry, is_sponsored))
                else:
                    break

                last_idx = idx
        except Exception as e:
            self.log('Link fail. ERROR: %s.' % str(e), ERROR)

        links2 = []
        try:
            if not links:
                # added for New fall toys
                lis = response.xpath(
                    '//div[contains(@class,"a-carousel-viewport")]'
                    '//li[contains(@class,"a-carousel-card")]')
                for li in lis:
                    is_prime = \
                        bool(li.xpath('.//i[contains(@class,"a-icon-prime")]'))
                    is_prime_pantry = False
                    is_sponsored = False
                    link = li.xpath(
                        './a[contains(@class,"acs_product-image")]/@href'
                    ).extract()
                    if len(link):
                        link = 'http://' + self.allowed_domains[0] + '/' + \
                               link[0]
                        links2.append((link, is_prime, is_prime_pantry,
                                       is_sponsored))
        except Exception as e:
            self.log('Links2 is fail. ERROR: %s.' % str(e), ERROR)

        links += links2

        try:
            if not links:
                links2 = []
                items = response.xpath('//div[@id="zg"]//div[contains(@class,"zg_itemImmersion")]')
                for item in items:
                    urls = item.xpath(
                        './/a/@href'
                    ).extract()
                    urls = list(set([r.strip() for r in urls if len(r.strip())>0 and '/dp/' in r]))
                    if len(urls) > 0:
                        is_prime = \
                            bool(item.xpath('.//i[contains(@class,"a-icon-prime")]'))
                        is_prime_pantry = False
                        is_sponsored = False
                        link = 'http://' + self.allowed_domains[0] + '/' + \
                               urls[0]
                        links2.append((link, is_prime, is_prime_pantry,
                                       is_sponsored))
        except Exception as e:
            self.log('Links2 is fail. ERROR: %s.' % str(e), ERROR)

        links += links2

        if not links:
            ul = response.xpath('//div[@id="zg_centerListWrapper"]/'
                                'div[@class="zg_itemImmersion"]')
            if ul:
                def __parse_category():
                    _get_text = lambda x: is_empty(x.xpath('text()').extract())

                    __categories = []

                    category_root = \
                        response.xpath('//ul[@id="zg_browseRoot"]')
                    if not category_root:
                        return []

                    curent_ul = \
                        category_root.xpath('//span[@class="zg_selected"]')
                    text = _get_text(curent_ul)
                    if text:
                        __categories.insert(0, text.strip())

                    while curent_ul:
                        curent_ul = curent_ul.xpath(
                            'parent::li/parent::ul/preceding::li[1]/a')
                        text = _get_text(curent_ul)
                        if text:
                            __categories.insert(0, text.strip())
                        if text.strip().startswith('Any'):
                            break

                    return __categories

                shelf_categories = __parse_category()
                shelf_category = shelf_categories[-1] if shelf_categories \
                    else None

            for i, li in enumerate(ul):
                link = is_empty(li.xpath(
                    './/div[@class="zg_itemImageImmersion"]/a/@href'
                ).extract())
                if not link:
                    continue

                prod = SiteProductItem(
                    ranking=i,
                    shelf_path=shelf_categories,
                    shelf_name=shelf_category
                )

                yield Request(
                    link.strip(),
                    callback=self.parse_product,
                    headers={
                        'Referer': None
                    },
                    meta={
                        'product': prod
                    }
                ), prod

                # break

            if ul:
                return

        if not links:
            self.log("Found no product links.", WARNING)
            # from scrapy.shell import inspect_response
            # inspect_response(response, self)
        return
        if links:
            for link, is_prime, is_prime_pantry, is_sponsored in links:
                prime = None
                if is_prime:
                    prime = 'Prime'
                if is_prime_pantry:
                    prime = 'PrimePantry'
                prod = SiteProductItem(
                    prime=prime, shelf_path=shelf_categories,
                    shelf_name=shelf_category, is_sponsored_product=is_sponsored)
                yield Request(link, callback=self.parse_product,
                              headers={'Referer': None},
                              meta={'product': prod}), prod

    # TODO This was done to to make ranking work again with self.num_pages>1
    # TODO fix this
    # def _get_products(self, response):
    #     remaining = response.meta['remaining']
    #     search_term = response.meta['search_term']
    #     prods_per_page = response.meta.get('products_per_page')
    #     total_matches = response.meta.get('total_matches')
    #     scraped_results_per_page = response.meta.get('scraped_results_per_page')
    #
    #     prods = self._scrape_product_links(response)
    #
    #     if prods_per_page is None:
    #         # Materialize prods to get its size.
    #         prods = list(prods)
    #         prods_per_page = len(prods)
    #         response.meta['products_per_page'] = prods_per_page
    #
    #     if scraped_results_per_page is None:
    #         scraped_results_per_page = self._scrape_results_per_page(response)
    #         if scraped_results_per_page:
    #             self.log(
    #                 "Found %s products at the first page" % scraped_results_per_page
    #                 , INFO)
    #         else:
    #             scraped_results_per_page = prods_per_page
    #             if hasattr(self, 'is_nothing_found'):
    #                 if not self.is_nothing_found(response):
    #                     self.log(
    #                         "Failed to scrape number of products per page", ERROR)
    #         response.meta['scraped_results_per_page'] = scraped_results_per_page
    #
    #     if total_matches is None:
    #         total_matches = self._scrape_total_matches(response)
    #         if total_matches is not None:
    #             response.meta['total_matches'] = total_matches
    #             self.log("Found %d total matches." % total_matches, INFO)
    #         else:
    #             if hasattr(self, 'is_nothing_found'):
    #                 if not self.is_nothing_found(response):
    #                     self.log(
    #                         "Failed to parse total matches for %s" % response.url, ERROR)
    #
    #     if total_matches and not prods_per_page:
    #         # Parsing the page failed. Give up.
    #         self.log("Failed to get products for %s" % response.url, ERROR)
    #         return
    #
    #     if self.current_page == 1:
    #         self.quantity = min(total_matches, self.quantity) if total_matches else self.quantity
    #         self.remaining = self.quantity
    #     else:
    #         self.remaining -= prods_per_page
    #
    #     for i, (prod_url, prod_item) in enumerate(islice(prods, 0, self.remaining)):
    #         # Initialize the product as much as possible.
    #         prod_item['site'] = self.site_name
    #         prod_item['search_term'] = search_term
    #         prod_item['total_matches'] = total_matches
    #         prod_item['results_per_page'] = prods_per_page
    #         prod_item['scraped_results_per_page'] = scraped_results_per_page
    #         # The ranking is the position in this page plus the number of
    #         # products from other pages.
    #
    #         if not total_matches:
    #             prod_item['ranking'] = (i + 1) + self.total_items_scraped
    #         else:
    #             prod_item['ranking'] = (i + 1) + (self.quantity - self.remaining)
    #         if self.user_agent_key not in ["desktop", "default"]:
    #             prod_item['is_mobile_agent'] = True
    #
    #         if prod_url is None:
    #             # The product is complete, no need for another request.
    #             yield prod_item
    #         elif isinstance(prod_url, Request):
    #             cond_set_value(prod_item, 'url', prod_url.url)  # Tentative.
    #             yield prod_url
    #         else:
    #             # Another request is necessary to complete the product.
    #             url = urlparse.urljoin(response.url, prod_url)
    #             cond_set_value(prod_item, 'url', url)  # Tentative.
    #             yield Request(
    #                 url,
    #                 callback=self.parse_product,
    #                 meta={'product': prod_item},
    #             )
    #
    #     self.total_items_scraped += prods_per_page

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        next_link = super(AmazonShelfPagesSpider, self)._scrape_next_results_page_link(response)
        if next_link:
            return next_link
