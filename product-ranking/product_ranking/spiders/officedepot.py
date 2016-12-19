from __future__ import division, absolute_import, unicode_literals

import json
import re
import time
import socket
import urlparse
import urllib
import os
import string

from scrapy import Request

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi

from datetime import datetime

is_empty =lambda x,y=None: x[0] if x else y


def is_num(s):
    try:
        int(s.strip())
        return True
    except ValueError:
        return False


class OfficedepotProductsSpider(BaseProductsSpider):
    name = 'officedepot_products'
    allowed_domains = ["officedepot.com", "www.officedepot.com", 'bazaarvoice.com']
    start_urls = []
    _extra_requests = False
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

    VARIANTS_URL = 'http://www.officedepot.com/mobile/getSkuAvailable' \
            'Options.do?familyDescription={name}&sku={sku}&noLogin=true'
    QA_URL = "http://officedepot.ugc.bazaarvoice.com/answers/2563/product/{product_id}/questions.djs?format=embeddedhtml"
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


    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)
        # officedepot seems to have a bot protection, so we first get the cookies
        # and parse the site with them after that
        self.proxy = None
        self.timeout = 60
        self.width = 1024
        self.height = 768
        self.selenium_cookies = {}
        self.user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'
                           ' (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36')
        socket.setdefaulttimeout(60)
        self._get_selenium_cookies_for_main_page()
        if kwargs.get('scrape_variants_with_extra_requests'):
            self._extra_requests = True
        super(OfficedepotProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def _prepare_driver(self, driver):
        driver.set_page_load_timeout(int(self.timeout))
        driver.set_script_timeout(int(self.timeout))
        driver.set_window_size(int(self.width), int(self.height))

    def _get_selenium_cookies_for_main_page(self):
        from pyvirtualdisplay import Display
        display = Display(visible=False)
        display.start()
        driver = self._init_chromium()
        self._prepare_driver(driver)
        try:
            driver.get('http://' + self.allowed_domains[0])
            time.sleep(10)
            for cookie in driver.get_cookies():
                self.selenium_cookies[cookie['name']] = cookie['value']
            driver.quit()
        except Exception as e:
            driver.quit()
            time.sleep(10)
            self.log('Error getting cookies from homepage, trying one more time: %s' % str(e))
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
        meta = response.meta
        product = meta.get('product', SiteProductItem())
        reqs = []
        meta['reqs'] = reqs

        product['_subitem'] = True

        # Parse locate
        locale = 'en_US'
        cond_set_value(product, 'locale', locale)

        # Parse title
        title = self.parse_title(response)
        cond_set(product, 'title', title, conv=string.strip)

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

        # Parse model
        model = self._parse_model(response)
        cond_set_value(product, 'model', model)

        # Parse reseller_id
        reseller_id = self.parse_reseller_id(response)
        cond_set_value(product, "reseller_id", reseller_id)

        # Parse is out of stock
        oos = self._parse_is_out_of_stock(response)
        cond_set_value(product, 'is_out_of_stock', oos)

        # Parse categories and category
        categories = self._parse_categories(response)
        cond_set_value(product, 'categories', categories)
        if categories:
            cond_set_value(product, 'category', categories[-1])

        # Parse related products
        related_product = self._parse_related_product(response)
        cond_set_value(product, 'related_products', related_product)

        br_count = is_empty(re.findall(r'<span itemprop="reviewCount">(\d+)<\/span>',
                                       response.body_as_unicode()))
        meta['_br_count'] = br_count
        meta['product'] = product

        reqs.append(Request(
            url=self.REVIEW_URL.format(product_id=self._get_product_id(
                response.url)),
            dont_filter=True,
            callback=self.parse_buyer_reviews,
            meta=meta
        ))

        sku = is_empty(response.xpath('//input[@name="id"]/@value').extract())
        name = is_empty(response.xpath(
            '//h1[@itemprop="name"]/text()').re('(.*?),'))

        if sku and name and self.scrape_variants_with_extra_requests:
            name = urllib.quote_plus(name.strip().encode('utf-8'))
            reqs.append(Request(url=self.VARIANTS_URL.format(name=name,
                                                             sku=sku),
                        callback=self._parse_variants,
                        meta=meta))
        # parse questions & answers
        reqs.append(Request(
            url=self.QA_URL.format(product_id=self._get_product_id(
            response.url)),
            callback=self._parse_questions,
            meta=meta,
            dont_filter=True
        ))

        if reqs:
            return self.send_next_request(reqs, response)
        return product

    def parse_reseller_id(self, response):
        regex = "\/(\d+)"
        reseller_id = re.findall(regex, response.url)
        reseller_id = reseller_id[0] if reseller_id else None
        return reseller_id

    def _parse_questions(self, response):
        meta = response.meta
        reqs = response.meta['reqs']
        product = response.meta['product']
        qa = []
        questions_ids_regex = """BVQAQuestionSummary.+?javascript:void.+?>([^<]+)[^"']+["']BVQAQuestionMain(\d+)(?:.+?BVQAQuestionDetails.+?div>([^<]+)?).+?BVQAElapsedTime.+?>([^<]+)"""
        questions_ids = re.findall(questions_ids_regex, response.body_as_unicode())
        for (question_summary, question_id, question_details, question_date) in questions_ids:
            # Convert date format
            if question_date:
                try:
                    from dateutil.relativedelta import relativedelta
                    years = re.findall("(\d+?)\s+?years", question_date)
                    years = years[0] if years else '0'
                    years = int(years) if years.isdigit() else '0'
                    months = re.findall("(\d+?)\s+?months", question_date)
                    months = months[0] if months else '0'
                    months = int(months) if months.isdigit() else '0'
                    if not months and not years:
                        converted_date = None
                    else:
                        converted_date = datetime.now() - relativedelta(years=years, months=months)
                        converted_date = converted_date.strftime("%Y-%m-%d")
                except Exception as e:
                    converted_date = None
                    self.log('Failed to parse date, setting date to None {}'.format(e))
            else:
                converted_date = None
            # regex to get part of response that contain all answers to question with given id
            text_r = "BVQAQuestion{}Answers(.+?)BVQAQuestionDivider".format(question_id)
            all_a_text = re.findall(text_r, response.body_as_unicode())
            all_a_text = ''.join(all_a_text[0]) if all_a_text else ''
            answers_regex = r"Answer:.+?>([^<]+)"
            answers = re.findall(answers_regex, all_a_text)
            answers = [{'answerText':a} for a in answers]
            question = {
                'questionDate': converted_date,
                'questionId': question_id,
                'questionDetail': question_details.strip() if question_details else '',
                'qestionSmmary': question_summary.strip() if question_summary else '',
                'answers': answers,
                'totalAnswersCount': len(answers)
            }
            qa.append(question)
        product['all_questions'] = qa
        if reqs:
            return self.send_next_request(reqs, response)
        return product

    def clear_text(self, str_result):
        return str_result.replace("\t", "").replace("\n", "").replace("\r", "").replace(u'\xa0', ' ').strip()

    def _parse_is_out_of_stock(self, response):
        oos = response.xpath(
            '//*[@itemprop="availability"'
            ' and @content="http://schema.org/OutOfStock"]')
        return bool(oos)

    def _parse_model(self, response):
        model = response.xpath(
            '//*[@id="attributemodel_namekey"]/text()').extract()
        if model:
            return model[0].strip()

    def _parse_categories(self, response):
        categories = response.xpath(
            '//*[@id="siteBreadcrumb"]//'
            'span[@itemprop="name"]/text()').extract()
        return categories

    def _parse_related_product(self, response):
        results = []
        base_url = response.url
        for related_product in response.xpath(
                '//*[@id="relatedItems"]'
                '//tr[contains(@class,"hproduct")]'
                '/td[@class="description"]/a'):
            name = is_empty(related_product.xpath('text()').extract())
            url = is_empty(related_product.xpath('@href').extract())
            if name and url:
                results.append(RelatedProduct(title=name,
                                              url=urlparse.urljoin(base_url,
                                                                   url)))
        return results

    def _parse_variants(self, response):
        """
        Parses product variants.
        """
        reqs = response.meta['reqs']
        product = response.meta['product']
        data = json.loads(response.body)
        variants = []

        if data.get('success'):
            for sku in data.get('skus', []):
                vr = {}
                vr['url'] = urlparse.urljoin(response.url, sku.get('url'))
                vr['skuId'] = sku.get('sku')
                price = is_empty(re.findall(
                    '\$([\d\.]+)', sku.get('attributesDescription', '')))
                if price:
                    vr['price'] = price

                name = sku.get('description', '')
                if name:
                    vr['properties'] = {'title': name}

                vr['image_url'] = sku.get('thumbnailImageUrl').split('?')[0]
                variants.append(vr)

            product['variants'] = variants
        if product.get('variants') and self._extra_requests:
            variants_urls = [p.get('url') for p in product['variants']]
            for var_url in variants_urls:
                req = Request(url=var_url, callback=self._parse_in_stock_for_variants)
                req.meta['product'] = product
                reqs.append(req)
        if reqs:
            return self.send_next_request(reqs, response)

        return product

    # parse variants one by one and set out of stock status for each variant
    def _parse_in_stock_for_variants(self, response):
        reqs = response.meta['reqs']
        product = response.meta['product']
        oos = self._parse_is_out_of_stock(response)
        for variant in product['variants']:
            if variant['url'] == response.url:
                variant['in_stock'] = not oos
                break
        if reqs:
            return self.send_next_request(reqs, response)
        return product

    def parse_buyer_reviews(self, response):
        meta = response.meta.copy()
        reqs = meta['reqs']

        self.br.br_count = meta['_br_count']
        buyer_reviews_per_page = self.br.parse_buyer_reviews_per_page(response)

        product = response.meta['product']
        product['buyer_reviews'] = BuyerReviews(**buyer_reviews_per_page)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

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
        items = response.xpath(
            '//div[contains(@class, "descriptionFull")]/'
            'a[contains(@class, "med_txt")]/@href'
        ).extract() or response.css('.desc_text a::attr("href")').extract()
        # Scraper was redirected to product page instead of search results page
        if not items and "officedepot.com/a/products" in response.url:
            prod = SiteProductItem(search_redirected_to_product=True)
            req = Request(response.url, callback=self.parse_product, dont_filter=True)
            req.meta["remaining"] = 0
            req.meta['product'] = prod
            yield req, prod
        else:
            for link in items:
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
