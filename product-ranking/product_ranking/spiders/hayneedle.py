from __future__ import division, absolute_import, unicode_literals

import json
import re
import time
import urlparse
import socket
import lxml.html as html

from scrapy import Request
from scrapy.log import ERROR, WARNING
from pyvirtualdisplay import Display

from product_ranking.items import BuyerReviews
from product_ranking.items import SiteProductItem, Price
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.settings import CRAWLERA_APIKEY
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.spiders import cond_set_value
from spiders_shared_code.nike_variants import NikeVariants


socket.setdefaulttimeout(60)


class HayneedleProductSpider(BaseProductsSpider):
    name = 'hayneedle_products'
    allowed_domains = ["www.hayneedle.com"]

    SEARCH_URL = "http://www.hayneedle.com/#{search_term}"

    REVIEW_URL = "http://nike.ugc.bazaarvoice.com/9191-en_us/{product_model}" \
                 "/reviews.djs?format=embeddedhtml"

    #handle_httpstatus_list = [404, 403, 429]

    use_proxies = False  # we'll be using Crawlera instead

    def __init__(self, sort_mode=None, *args, **kwargs):
        from scrapy.conf import settings
        settings.overrides['DEPTH_PRIORITY'] = 1
        settings.overrides['SCHEDULER_DISK_QUEUE'] = 'scrapy.squeue.PickleFifoDiskQueue'
        settings.overrides['SCHEDULER_MEMORY_QUEUE'] = 'scrapy.squeue.FifoMemoryQueue'
        settings.overrides['CRAWLERA_ENABLED'] = True

        self.quantity = kwargs.get('quantity', 1000)  # default is 1000

        self.proxy = 'content.crawlera.com:8010'
        self.proxy_type = 'http'
        #self.user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0'
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'

        self.br = BuyerReviewsBazaarApi(called_class=self)

        super(HayneedleProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    @staticmethod
    def _get_antiban_headers():
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0',
            'Connection': 'keep-alive',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate'
        }

    def _fix_image_url(url):
        if isinstance(url, (list, tuple)):
            if not url:
                return
            url = url[0]
        url = url.replace('?is=70,70,0xffffff', '')
        return url

    def start_requests(self):
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=st.encode('utf-8'),
                ),
                meta={'search_term': st, 'remaining': self.quantity},
                headers=self._get_antiban_headers()
            )
        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            meta = {}
            meta['is_product_page'] = True
            meta['product'] = prod
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta=meta,
                          headers=self._get_antiban_headers())

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _get_product_links_from_serp(self, driver):
        results = []
        links = driver.find_elements_by_xpath(
            '//*[contains(@class, "grid-item-image")]'
            '//a[contains(@href, "/pd/") or contains(@href, "/product/")]')

        for l in links:
            href = l.get_attribute('href')
            if href:
                if not href.startswith('http'):
                    href = urlparse.urljoin('http://' + self.allowed_domains[0], href)
                results.append(href)
        return results

    def _is_product_page(self, response):
        return 'is_product_page' in response.meta

    @staticmethod
    def _get_proxy_ip(driver):
        driver.get('http://icanhazip.com')
        ip = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', driver.page_source)
        if ip:
            ip = ip.group(1)
            return ip

    @staticmethod
    def _auth_firefox_proxy(driver):
        driver.set_page_load_timeout(10)
        try:
            driver.get('http://icanhazip.com')
        except:
            from selenium.webdriver.common.alert import Alert
            time.sleep(3)
            alert = Alert(driver)
            time.sleep(3)
            #alert.authenticate(CRAWLERA_APIKEY, '')
            alert.send_keys(CRAWLERA_APIKEY + '\n')
            alert.accept()
            #alert.send_keys('\t')
            #alert.send_keys('\n')
            #import pdb; pdb.set_trace()
        driver.set_page_load_timeout(30)

    @staticmethod
    def last_five_digits_the_same(lst):
        if len(lst) < 6:
            return
        return lst[-1] == lst[-2] == lst[-3] == lst[-4] == lst[-5]

    def _reliable_get(self, driver, url, max_attempts=40, check_element='title'):
        """ Acts like driver.get() but with failsafety """
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        for i in range(max_attempts):
            try:
                driver.get(url)
                if driver.find_elements_by_xpath('//%s' % check_element):
                    return driver
            except:
                self.log('_reliable_get error #%i while getting url %s' % (i, url))
        self.log('_reliable_get failed to get url %s' % url, ERROR)

    def parse(self, response):

        if not self._is_product_page(response):
            display = Display(visible=0, size=(1024, 768))
            display.start()

            product_links = []
            # scrape "quantity" products
            driver = self._init_firefox()
            self._auth_firefox_proxy(driver)
            if self.proxy:
                ip_via_proxy = HayneedleProductSpider._get_proxy_ip(driver)
                print 'IP via proxy:', ip_via_proxy
                self.log('IP via proxy: %s' % ip_via_proxy)
            try:
                self._reliable_get(driver, 'http://store.nike.com/us/en_us')
            except Exception as e:
                print(str(e))
                self.log(str(e), WARNING)
            driver.find_element_by_name('searchList').send_keys(self.searchterms[0] + '\n')
            time.sleep(6)  # let AJAX finish
            new_meta = response.meta.copy()
            # get all products we need (scroll down)
            collected_products_len = []
            num_exceptions = 0
            while 1:
                try:
                    driver.execute_script("scrollTo(0,50000)")
                    time.sleep(10)
                    product_links = self._get_product_links_from_serp(driver)
                    collected_products_len.append(len(product_links))
                    print 'Collected %i product links' % len(product_links)
                    self.log('Collected %i product links' % len(product_links))
                    if len(product_links) > self.quantity:
                        break
                    if self.last_five_digits_the_same(collected_products_len):
                        break  # last five iterations collected equal num of products
                except Exception as e:
                    print str(e)
                    self.log('Exception while scrolling page: %s' % str(e), WARNING)
                    num_exceptions += 1
                    if num_exceptions > 10:
                        self.log('Maximum number of exceptions reached', ERROR)
                        driver.quit()
                        display.stop()
                        return

            for i in xrange(10):
                time.sleep(3)
                try:
                    selenium_cookies = driver.get_cookies()
                    break
                except Exception as e:
                    print('Exception while loading cookies %s attempt %i' % (str(e), i))
                    self.log('Exception while loading cookies %s attempt %i' % (str(e), i))
            try:
                driver.quit()
                display.stop()
            except:
                pass
            #driver.save_screenshot('/tmp/1.png')
            new_meta['is_product_page'] = True
            new_meta['proxy'] = self.proxy
            for i, product_link in enumerate(product_links):
                new_meta['_ranking'] = i+1
                yield Request(product_link, meta=new_meta, callback=self.parse_product,
                              headers=self._get_antiban_headers())
                              #cookies=selenium_cookies)

    def parse_product(self, response):
        meta = response.meta.copy()
        product = meta.get('product', SiteProductItem())

        product['_subitem'] = True

        _ranking = response.meta.get('_ranking', None)
        product['ranking'] = _ranking
        product['url'] = response.url
        product['search_term'] = response.meta.get('search_term', None)

        # Parse product title
        title = self.parse_title(response)
        cond_set_value(product, 'title', title)

        if not product.get('title', None):
            return

        # Parse sku
        sku = self.parse_sku(response)
        cond_set_value(product, 'sku', sku)

        # Parse description
        description = self.parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse Image
        image = self.parse_image(response)
        cond_set(product, 'image_url', image)

        # Parse locate
        locale = 'en_US'
        cond_set_value(product, 'locale', locale)

        # Parse model
        # product_model = self.parse_product_model(response)
        # cond_set_value(product, 'model', product_model)

        # Parse brand
        # brand = self.parse_brand(response)
        # cond_set_value(product, 'brand', brand)

        # Parse upc
        # upc = self.parse_upc(response)
        # cond_set_value(product, 'upc', upc)


        # Parse price
        price = self.parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse price
        self.parse_buyer_reviews(response)

        # Parse variants
        # nv = NikeVariants()
        # nv.setupSC(response)
        # try:
        #     product['variants'] = nv._variants()
        # except:  # "/product/" urls that are non-standard and not supported (yet)?
        #     pass
        # meta['product'] = product

        # parse buyer reviews
        # yield Request(
        #     url=self.REVIEW_URL.format(product_model=product_model),
        #     dont_filter=True,
        #     callback=self.parse_buyer_reviews,
        #     meta=meta
        # )
        yield product

    def parse_count_reviews(self, response):
        count_review = response.xpath(
            '//div[contains(@class, "pr-snapshot-rating")]//span[contains(@class, "pr-rating")]/text()'
        ).extract()
        return count_review[0] if count_review else None

    def parse_image(self, response):
        images = response.xpath("//div[@class='preloaded-preview-container']/img/@src").extract()
        return images

    def parse_description(self, response):
        desc = response.xpath("//div[contains(@class, 'desc-section')]/h2[text()='Description']/following-sibling::div").extract()
        if desc:
            return html.fromstring(desc[0]).text_content()

        return desc

    def parse_sku(self, response):
        sku = response.xpath("//row[contains(@class, 'title-container')]//div[contains(@class, 'sku-display')]/span[contains(@class, 'text-large')]/following-sibling::span/text()").extract()
        return sku[0] if sku else None

    def parse_price(self, response):
        price = response.xpath("//column[contains(@class, 'display-price-container label')]/div/text()").extract()
        return price[0] if price else None

        return None

    def _scrape_total_matches(self, response):
        totals = response.css('.productCount ::text').extract()
        if totals:
            totals = totals[0].replace(',', '').replace('.', '').strip()
            if totals.isdigit():
                if not self.TOTAL_MATCHES:
                    self.TOTAL_MATCHES = int(totals)
                return int(totals)

    def _scrape_product_links(self, response):
        for link in response.xpath(
                '//li[contains(@class, "product-tile")]'
                '//a[contains(@rel, "product")]/@href'
        ).extract():
            yield link, SiteProductItem()

    def parse_product_id(self, response, js_data):
        product_id = response.xpath("//row[contains(@class, 'title-container')]//div[contains(@class, 'sku-display')]/span[contains(@class, 'text-large')]/following-sibling::span/text()").extract()
        return product_id[0] if product_id else None

    def parse_title(self, response):
        title = response.xpath("//row[contains(@class, 'title-container')]//h1[contains(@class, 'inline')]/text()").extract()
        return title[0] if title else None

    def parse_product_model(self, response):
        model = response.xpath(
            '//div[contains(@class, "hero-product-style-color-info")]/@data-stylenumber'
        ).extract()
        return model[0] if model else None

    def parse_product_color(self, response, js_data):
        if js_data:
            try:
                product_color = js_data['colorDescription']
                return product_color
            except:
                return

    def parse_buyer_reviews(self, response):
        total = response.xpath(
            '//div[contains(@class, "pr-snapshot-rating")]//span[contains(@class, "pr-rating")]/text()'
        ).extract()[0]
        avg = response.xpath(
            '//div[contains(@class, "pr-snapshot-rating")]//p[contains(@class, "pr-snapshot-average-based-on-text")]/span[@class="count"]/text()'
        ).extract()[0]
        ratings = []

        cond_set_value(response.meta['product'], 'buyer_reviews',
                       BuyerReviews(total, avg,
                                    ratings) if total else ZERO_REVIEWS_VALUE)
