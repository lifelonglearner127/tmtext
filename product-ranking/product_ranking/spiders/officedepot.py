from __future__ import division, absolute_import, unicode_literals

import json
import re
import time
import urllib
import urlparse
import os
import sys

from scrapy import Request

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FLOATING_POINT_RGEX, cond_set_value
#from product_ranking.validation import BaseValidator
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from scrapy import Selector
from spiders_shared_code.dockers_variants import DockersVariants
# from product_ranking.validators.dockers_validator import DockersValidatorSettings

is_empty =lambda x,y=None: x[0] if x else y


def is_num(s):
    try:
        int(s.strip())
        return True
    except ValueError:
        return False


# TODO: related products
# TODO: variants ?
# class DockersProductsSpider(BaseValidator, BaseProductsSpider):
class OfficedepotProductsSpider(BaseProductsSpider):
    name = 'officedepot_products'
    allowed_domains = ["officedepot.com", "www.officedepot.com"]
    start_urls = []

    # settings = DockersValidatorSettings

    SEARCH_URL = "http://www.officedepot.com/catalog/search.do?Ntt={search_term}&searchSuggestion=true&akamai-feo=off"

    PAGINATE_URL = ('http://www.officedepot.com/catalog/search.do?Ntx=mode+matchpartialmax&Nty=1&Ntk=all'
                    '&Ntt={search_term}&N=5&recordsPerPageNumber=24&No={nao}'
                    )

    CURRENT_NAO = 0
    PAGINATE_BY = 24  # 24 products
    TOTAL_MATCHES = None  # for pagination

    REVIEW_URL = "http://officedepot.ugc.bazaarvoice.com/2563" \
                 "/{product_id}/reviews.djs?format=embeddedhtml"
    #
    # RELATED_PRODUCT = "http://www.res-x.com/ws/r2/Resonance.aspx?" \
    #                   "appid=dockers01&tk=187015646137297" \
    #                   "&ss=182724939426407" \
    #                   "&sg=1&" \
    #                   "&vr=5.3x&bx=true" \
    #                   "&sc=product4_rr" \
    #                   "&sc=product3_rr" \
    #                   "&sc=product1_r" \
    #                   "r&sc=product2_rr" \
    #                   "&ev=product&ei={product_id}" \
    #                   "&no=20" \
    #                   "&language=en_US" \
    #                   "&cb=certonaResx.showResponse" \
    #                   "&ur=http%3A%2F%2Fwww.levi.com%2FUS%2Fen_US%" \
    #                   "2Fwomens-jeans%2Fp%2F095450043&plk=&"

    use_proxies = True

    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)

        # officedepot seems to have a bot protection, so we first get the cookies
        # and parse the site with them after that
        self.proxy = None
        self.timeout = 30
        self.width = 1024
        self.height = 768
        self.selenium_cookies = {}
        self.user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'
                           ' (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36')
        self._get_selenium_cookies_for_main_page()


        super(OfficedepotProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def _prepare_driver(self, driver):
        driver.set_page_load_timeout(int(self.timeout))
        driver.set_script_timeout(int(self.timeout))
        driver.set_window_size(int(self.width), int(self.height))

    def _get_selenium_cookies_for_main_page(self):
        from pyvirtualdisplay import Display
        display = Display(visible=False)
        driver = self._init_chromium()
        self._prepare_driver(driver)
        driver.get('http://' + self.allowed_domains[0])
        time.sleep(10)
        for cookie in driver.get_cookies():
            self.selenium_cookies[cookie['name']] = cookie['value']
        try:
            driver.quit()
            display.stop()
        except Exception as e:
            self.log('Error on driver & display destruction: %s' % str(e))

    def _init_chromium(self):
        from selenium import webdriver
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        RemoteConnection.set_timeout(30)
        chrome_flags = webdriver.DesiredCapabilities.CHROME  # this is for Chrome?
        chrome_options = webdriver.ChromeOptions()  # this is for Chromium
        if self.proxy:
            chrome_options.add_argument(
                '--proxy-server=%s' % self.proxy_type+'://'+self.proxy)
        chrome_flags["chrome.switches"] = ['--user-agent=%s' % self.user_agent]
        chrome_options.add_argument('--user-agent=%s' % self.user_agent)
        executable_path = '/usr/sbin/chromedriver'
        if not os.path.exists(executable_path):
            executable_path = '/usr/local/bin/chromedriver'
        # initialize webdriver, open the page and make a screenshot
        driver = webdriver.Chrome(desired_capabilities=chrome_flags,
                                  chrome_options=chrome_options,
                                  executable_path=executable_path)
        return driver

    def _init_firefox(self):
        from selenium import webdriver
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        RemoteConnection.set_timeout(30)
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", self.user_agent)
        profile.set_preference("network.proxy.type", 1)  # manual proxy configuration
        if self.proxy:
            if 'socks' in self.proxy_type:
                profile.set_preference("network.proxy.socks", self.proxy.split(':')[0])
                profile.set_preference("network.proxy.socks_port", int(self.proxy.split(':')[1]))
            else:
                profile.set_preference("network.proxy.http", self.proxy.split(':')[0])
                profile.set_preference("network.proxy.http_port", int(self.proxy.split(':')[1]))
        profile.update_preferences()
        driver = webdriver.Firefox(profile)
        return driver

    def _parse_single_product(self, response):
        return self.parse_product(response)

    @staticmethod
    def _get_product_id(url):
        match = re.search(r'/products/(\d{2,20})/', url)
        if match:
            return match.group(1)

    def parse_product(self, response):
        meta = response.meta.copy()
        product = meta.get('product', SiteProductItem())
        reqs = []
        meta['reqs'] = reqs

        product['_subitem'] = True

        # Parse locate
        locale = 'en_US'
        cond_set_value(product, 'locale', locale)

        # Parse title
        title = self.parse_title(response)
        cond_set(product, 'title', title)

        # Parse image
        image = self.parse_image(response)
        cond_set(product, 'image_url', image)

        # Parse brand
        brand = self.parse_brand(response)
        cond_set_value(product, 'brand', brand)

        # Parse sku
        sku = self.parse_sku(response)
        cond_set_value(product, 'sku', sku)

        # Parse description
        description = self.parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse price
        price = self.parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse variants
        # variants = self._parse_variants(response)
        # product['variants'] = variants

        br_count = is_empty(re.findall(r'<span itemprop="reviewCount">(\d+)<\/span>',
                                       response.body_as_unicode()))
        meta['_br_count'] = br_count
        yield Request(
            url=self.REVIEW_URL.format(product_id=self._get_product_id(response.url)),
            dont_filter=True,
            callback=self.parse_buyer_reviews,
            meta=meta
        )

        yield product

    def clear_text(self, str_result):
        return str_result.replace("\t", "").replace("\n", "").replace("\r", "").replace(u'\xa0', ' ').strip()

    # def _parse_variants(self, response):
    #     """
    #     Parses product variants.
    #     """
    #     dk = DockersVariants()
    #     dk.setupSC(response)
    #     variants = dk._variants()
    #
    #     return variants

    def parse_buyer_reviews(self, response):
        meta = response.meta.copy()

        self.br.br_count = meta['_br_count']
        buyer_reviews_per_page = self.br.parse_buyer_reviews_per_page(response)

        product = response.meta['product']
        product['buyer_reviews'] = BuyerReviews(**buyer_reviews_per_page)

        yield product

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """
        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs

        return req.replace(meta=new_meta)

    def parse_brand(self, response):
        brand = is_empty(response.xpath(
            '//td[@itemprop="brand"]/@content').extract())
        if not brand:
            brand = is_empty(response.xpath(
                '//td[@itemprop="brand"]/text()').extract())
        if brand:
            brand = brand.strip()
        return brand

    def parse_title(self, response):
        title = response.xpath(
            '//h1[contains(@itemprop, "name")]/text()').extract()
        return title

    def parse_data(self, response):
        data = re.findall(r'var MasterTmsUdo \'(.+)\'; ', response.body_as_unicode())
        if data:
            data = re.sub(r'\\(.)', r'\g<1>', data[0])
            try:
                js_data = json.loads(data)
            except:
                return
            return js_data

    def parse_image(self, response):
        img = response.xpath('//img[contains(@id, "mainSkuProductImage")]/@src').extract()
        return img

    def parse_description(self, response):
        description = response.xpath('//div[contains(@class, "sku_desc")]').extract()
        if description:
            return self.clear_text(description[0])
        else:
            return ''

    def parse_sku(self, response):
        sku = response.xpath('//td[contains(@id, "basicInfoManufacturerSku")]/text()').extract()
        # sku = response.xpath('//div[contains(@id, "skuValue")]/text()').extract()
        if sku:
            return self.clear_text(sku[0])

    def parse_price(self, response):

        price = response.xpath('//meta[contains(@itemprop, "price")]/@content').extract()
        currency = response.xpath('//meta[contains(@itemprop, "priceCurrency")]/@content').extract()

        if price and currency:
            price = Price(price=price[0], priceCurrency=currency[0])
        else:
            price = Price(price=0.00, priceCurrency="USD")

        return price

    def parse_paginate_link(self, response, nao):
        check_page = '&No=%s' % nao
        for link in response.xpath(
                '//a[contains(@class, "paging")]/@href'
        ).extract():
            if check_page in link:
                u = urlparse.urlparse(link)
                return urlparse.urljoin('http://www.officedepot.com', u.path)

    def parse_category_link(self, response):
        categories_links = []
        for link in response.xpath(
                '//div[contains(@class, "category_wrapper")]/a[contains(@class, "link")]/@href'
        ).extract():
            categories_links.append(link)

    def _scrape_total_matches(self, response):
        totals = response.xpath('//div[contains(@id, "resultCnt")]/text()').extract()
        if totals:
            totals = totals[0].replace(',', '').replace('.', '').strip()
            if totals.isdigit():
                if not self.TOTAL_MATCHES:
                    self.TOTAL_MATCHES = int(totals)
                return int(totals)

    def _scrape_product_links(self, response):
        for link in response.xpath(
                '//div[contains(@class, "descriptionFull")]/a[contains(@class, "med_txt")]/@href'
        ).extract():
            yield link, SiteProductItem()

    def _get_nao(self, url):
        nao = re.search(r'nao=(\d+)', url)
        if not nao:
            return
        return int(nao.group(1))

    def _replace_nao(self, url, new_nao):
        current_nao = self._get_nao(url)
        if current_nao:
            return re.sub(r'nao=\d+', 'nao='+str(new_nao), url)
        else:
            return url+'&nao='+str(new_nao)

    def _scrape_next_results_page_link(self, response):
        if self.TOTAL_MATCHES is None:
            self.log('No "next result page" link!')
            # # TODO: check result by categories
            # return self.parse_category_link(response)
            return
        #if self.CURRENT_NAO > self.TOTAL_MATCHES+self.PAGINATE_BY:
        #    return  # all the products have been collected
        if self.CURRENT_NAO > self.quantity+self.PAGINATE_BY:
            return  # num_products > quantity
        self.CURRENT_NAO += self.PAGINATE_BY
        if '/a/browse/' in response.url:    # paginate in category or subcategory
            new_paginate_url = self.parse_paginate_link(response, self.CURRENT_NAO)
            if new_paginate_url:
                return Request(new_paginate_url, callback=self.parse, meta=response.meta,
                               cookies=self.selenium_cookies)
        return Request(
            self.PAGINATE_URL.format(
                search_term=response.meta['search_term'],
                nao=str(self.CURRENT_NAO)),
            callback=self.parse, meta=response.meta,
            cookies=self.selenium_cookies
        )