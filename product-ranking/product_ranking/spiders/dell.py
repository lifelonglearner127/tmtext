from __future__ import division, absolute_import, unicode_literals

import hjson
import re
import time
import socket
import urlparse
from collections import OrderedDict
from itertools import product
from datetime import datetime
import urllib

from scrapy import Request, Selector, FormRequest
from scrapy.log import ERROR, WARNING
from pyvirtualdisplay import Display

from product_ranking.items import RelatedProduct
from product_ranking.items import SiteProductItem, Price, LimitedStock
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.spiders import cond_set_value
from product_ranking.guess_brand import guess_brand_from_first_words


socket.setdefaulttimeout(60)


is_empty = lambda x, y="": x[0] if x else y


class DellProductSpider(BaseProductsSpider):
    name = 'dell_products'
    allowed_domains = ["dell.com", "recs.richrelevance.com"]

    handle_httpstatus_list = [404, 403, 502, 520]

    SEARCH_URL = "http://pilot.search.dell.com/{search_term}"
    REVIEW_URL = "http://reviews.dell.com/2341_mg/{product_id}/reviews.htm?format=embedded"
    VARIANTS_URL = "http://www.dell.com/api/configService.svc/postmoduleoverrides/json"
    VARIANTS_DATA = {
        'c': 'us', 'l': 'en', 's': 'dhs', 'cs': '19',
        'moduleTemplate': 'products/ProductDetails/mag/config_popup_mag',
        'modErrorTemplate': 'products/module_option_validation',
        'resultType': 'SingleModule', 'productCode': 'undefined'
    }
    # there are two types of product pages, each of them requires different related products processing
    RELATED_PROD_URL_V1 = (
        "http://recs.richrelevance.com/rrserver/p13n_generated.js?"
        "pt=|item_page.mag_syspdpoc1|item_page.mag_syspdpoc2|item_page.mag_syspdpoc3|item_page.mag_syspdpoc4|item_page.mag_syspdpoc5&"
        "a=usdhsa5d5af7012d61fd1&rid=us_19_en_dhs&sgs=|us_19_en_dhs:us_19_en_dhs&flv=15.0.0&"
        "s=undefined{date}&n={n}&chi={chi}&ts={ts}&p={p}"
    )
    RELATED_PROD_URL_V2 = (
        "http://recs.richrelevance.com/rrserver/p13n_generated.js?"
        "pt=|item_page.storm_snp_pdp1|item_page.storm_snp_pdp2|item_page.storm_snp_pdp3|item_page.storm_snp_pdp4|item_page.storm_snp_pdp5&"
        "sgs=|us_04_en_bsd:us_04_en_bsd&rid=us_04_en_bsd&flv=11.2.999&l=1&"
        "u=ykOA15fokzi417dpJeveUF65A0NwWJeGhQ6pvWEfbCuYOurQKpNgzVVXCdsYKqf4&"
        "s=ykOA15fokzi417dpJeveUF65A0NwWJeGhQ6pvWEfbCuYOurQKpNgzVVXCdsYKqf4{date}&"
        "a=usbsda5d5af7012d61fd1&ts={ts}&p={p}"
    )

    def __init__(self, sort_mode=None, *args, **kwargs):
        from scrapy.conf import settings
        settings.overrides['DEPTH_PRIORITY'] = 1
        settings.overrides['SCHEDULER_DISK_QUEUE'] = 'scrapy.squeue.PickleFifoDiskQueue'
        settings.overrides['SCHEDULER_MEMORY_QUEUE'] = 'scrapy.squeue.FifoMemoryQueue'

        self.quantity = kwargs.get('quantity', 1000)  # default is 1000

        self.br = BuyerReviewsBazaarApi(called_class=self)

        super(DellProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def start_requests(self):
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote(st.encode('utf-8')),
                ),
                meta={'search_term': st, 'remaining': self.quantity},
            )

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod})

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _get_product_links_from_serp(self, driver):
        results = []
        links = driver.find_elements_by_xpath('//h4/../../a[contains(@href, "/")]')
        for l in links:
            href = l.get_attribute('href')
            if href:
                if not href.startswith('http'):
                    href = urlparse.urljoin('http://' + self.allowed_domains[0], href)
                results.append(href)
        return results

    def _is_product_page(self, response):
        return 'is_product_page' in response.meta

    def _init_webdriver(self):
        from selenium import webdriver
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        RemoteConnection.set_timeout(30)
        driver = webdriver.Firefox()
        driver.set_window_size(1280, 1024)
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)
        return driver

    def parse(self, response):

        if not self._is_product_page(response):
            product_links = []
            # scrape "quantity" products
            display = Display(visible=0, size=(1280, 1024))
            display.start()
            driver = self._init_webdriver()
            driver.get(response.url)
            time.sleep(6)  # let AJAX finish
            new_meta = response.meta.copy()
            # get all products we need (or till the "show more products" button exists)
            paging_button = '//button[contains(@id, "paging-button")]'
            num_of_errors = 0
            while driver.find_elements_by_xpath(paging_button):
                try:
                    button = driver.find_elements_by_xpath(paging_button)
                    button[0].click()
                    time.sleep(4)
                    product_links = self._get_product_links_from_serp(driver)
                    if len(product_links) > self.quantity:
                        break
                    print 'Collected %i product links' % len(product_links)
                    self.log('Collected %i product links' % len(product_links))
                except Exception as e:
                    print str(e)
                    self.log('Error while doing pagination: %s' % str(e), WARNING)
                    num_of_errors += 1
                    if num_of_errors > 10:
                        self.log('Too many webdriver errors', ERROR)
                        driver.quit()
                        display.stop()
                        return

            #driver.save_screenshot('/tmp/1.png')
            new_meta['is_product_page'] = True
            for i, product_link in enumerate(product_links):
                new_meta['_ranking'] = i+1
                yield Request(product_link, meta=new_meta, callback=self.parse_product)

            driver.quit()
            try:
                display.stop()
            except Exception as e:
                self.log('Exception on display.stop(): [%s]' % str(e))

    @staticmethod
    def _parse_price(response):
        dell_price = response.xpath('//*[contains(text(), "Dell Price")]')
        dell_price = re.search('\$([\d,]+\.\d+)', ''.join(dell_price.xpath('./..//text()').extract()))
        if dell_price:
            dell_price = dell_price.group(1)
            price = Price(price=dell_price, priceCurrency='USD')
            return price
        price = response.xpath('//*[contains(@name, "pricing_sale_price")]'
                               '[contains(text(), "$")]//text()').extract()
        if not price:
            price = response.xpath('//*[contains(@name, "pricing_retail_price")]'
                                   '[contains(text(), "$")]//text()').extract()
        if price:
            price = Price(price=price[0].strip().replace('$', ''), priceCurrency='USD')
            return price

    @staticmethod
    def _parse_image(response):
        img_src = response.xpath('//*[contains(@id, "product_main_image")]'
                                 '//img[contains(@src, ".jp")]/@src').extract()
        if not img_src:
            img_src = response.xpath('//*[contains(@class, "oneImageUp")]'
                                     '//img[contains(@src, ".jp")]/@src').extract()
        if not img_src:
            img_src = response.xpath('//*[contains(@class, "leftRightMainImg")]'
                                     '//img[contains(@src, ".jp")]/@src').extract()
        if not img_src:
            img_src = response.xpath('//*[contains(@class, "oneImageUp")]'
                                     '//img[contains(@data-original, ".jp")]/@data-original').extract()
        if img_src:
            return img_src[0]

    @staticmethod
    def _parse_brand(response, prod_title):
        # <meta itemprop="brand" content = "DELL"/>
        brand = response.xpath('//meta[contains(@itermprop, "brand")]/@content').extract()
        if not brand:
            brand = response.xpath('//a[contains(@href, "/brand.aspx")]/img/@alt').extract()
        if brand:
            return brand[0].title()
        if prod_title:
            brand = guess_brand_from_first_words(prod_title)
            if not brand:
                prod_title = prod_title.replace('New ', '').strip()
                brand = guess_brand_from_first_words(prod_title)
            if brand:
                return brand

    @staticmethod
    def _parse_description(response):
        desc = response.xpath('//*[@id="cntTabsCnt"]').extract()
        if not desc:
            desc = response.xpath('.//*[@id="AnchorZone3"]'
                                  '//div[not(contains(@class, "anchored_returntotop"))]').extract()
        if desc:
            return desc[0]

    def _related_products(self, response):
        results = []
        rps = response.xpath('//*[contains(@class, "psItemDescription")]//'
                             'div[contains(@class, "psTeaser")]//a[contains(@href, "productdetail.aspx")]')
        for rp in rps:
            results.append(RelatedProduct(rp.xpath('text()').extract()[0].strip(),
                                          rp.xpath('@href').extract()[0].strip()))  # TODO: check if it's a valid format
        # TODO: scrape dynamic related products
        return results

    def parse_buyer_reviews(self, response):
        product = response.meta['product']
        buyer_reviews = self.br.parse_buyer_reviews_per_page(response)
        product['buyer_reviews'] = buyer_reviews
        yield product

    def _get_stock_status(self, response, product):
        oos_element = response.xpath(
            '//a[contains(@class, "smallBlueBodyText")]'
            '[contains(@href, "makeWin")]//text()').extract()
        if oos_element:
            oos_element = oos_element[0].lower()
            if ('temporarily out of stock' in oos_element
                    or 'pre-order' in oos_element):
                product['is_out_of_stock'] = True
                return product
            if 'limited supply available' in oos_element:
                product['is_out_of_stock'] = False
                product['limited_stock'] = LimitedStock(is_limited=True, items_left=-1)
                return product

    @staticmethod
    def _get_product_id(response):
        prod_id = re.findall(':productdetails:([\da-zA-Z\-\.]{1,50})\",', response.body_as_unicode())
        if prod_id:
            return prod_id[0]

    def parse_product(self, response):
        prod = response.meta.get('product', SiteProductItem())

        prod['_subitem'] = True

        _ranking = response.meta.get('_ranking', None)
        prod['ranking'] = _ranking
        prod['url'] = response.url

        cond_set(prod, 'title', response.css('h1 ::text').extract())
        prod['price'] = DellProductSpider._parse_price(response)
        prod['image_url'] = DellProductSpider._parse_image(response)

        prod['description'] = DellProductSpider._parse_description(response)
        prod['brand'] = DellProductSpider._parse_brand(response, prod.get('title', ''))
        prod['related_products'] = self._related_products(response)
        response.meta['product'] = prod
        is_links, variants = self._parse_variants(response)
        if is_links:
            yield variants.pop(0)
        else:
            cond_set_value(prod, 'variants', self._collect_variants_from_dict(variants))

        if 'This product is currently unavailable.' in response.body_as_unicode():
            prod['is_out_of_stock'] = True
        else:
            yield self._get_stock_status(response, prod)  # this should be OOS field

        meta = {'product': prod}
        prod_id = self._get_product_id(response)
        if prod_id:  # first page type
            if response.css('#bazaarVoice').extract():
                meta.update({'br_page_type': 1})
                yield Request(  # reviews request
                    url=self.REVIEW_URL.format(product_id=prod_id),
                    dont_filter=True,
                    callback=self.parse_buyer_reviews,
                    meta=meta
                )
        buyer_reviews_iframe_src = response.xpath('//iframe[contains(@src,"reviews.htm")]/@src').extract()
        if buyer_reviews_iframe_src:  # second page type
            meta.update({'br_page_type': 2})
            yield Request(  # reviews request
                url=buyer_reviews_iframe_src[0].replace('format=noscript', ''),
                dont_filter=True,
                callback=self.parse_buyer_reviews,
                meta=meta
            )

        try:
            r_url, related_data = self.RELATED_PROD_URL_V1, self._collect_related_products_data_v1(response)
        except Exception:
            r_url, related_data = self.RELATED_PROD_URL_V2, self._collect_related_products_data_v2(response)
        yield Request(  # related products request
            r_url.format(**related_data),
            callback=self._parse_related_products,
            meta=meta
        )

        yield prod

    def _collect_common_variants_data(self, response):
        data = self.VARIANTS_DATA.copy()
        _ = is_empty(response.xpath('//meta[@name="Country"]/@content').extract())
        if _:
            data['c'] = _
        _ = is_empty(response.xpath('//meta[@name="Language"]/@content').extract())
        if _:
            data['l'] = _
        _ = is_empty(response.xpath('//meta[@name="Segment"]/@content').extract())
        if _:
            data['s'] = _
        _ = is_empty(response.xpath('//meta[@name="CustomerSet"]/@content').extract())
        if _:
            data['cs'] = _
        _ = is_empty(response.xpath('//meta[@name="currentOcId"]/@content').extract())
        if _:
            data['oc'] = _
        else:
            self.log('No "OC" and/or "modId data found" <%s>' % response.url, WARNING)
            return None
        return data

    def _collect_specific_variants_data(self, variant, common_data):
        data = common_data.copy()
        oc = data.get('oc')
        if not oc:
            self.log('No OC data', ERROR)
        uniq_id = is_empty(variant.xpath('//input[@value="%s"][contains(@id, "OrderCode")]/@id' % oc).extract())
        uniq_id = uniq_id.replace('OrderCode', '')
        mod_id = is_empty(variant.xpath('.//span[contains(@class,"spec~%s~")]/@class' % uniq_id).extract())
        mod_id = mod_id.split('~')[-1]
        data['modId'] = mod_id
        data['uiParameters'] = 'mainModuleId=%s&uniqueId=%s' % (mod_id, uniq_id)
        return data

    def _collect_variants_from_dict(self, variants):
        if not variants:
            return None
        max_options = 4
        _variants = OrderedDict()
        keys = sorted(variants.keys()[:max_options])
        for tmp in keys:
            _variants[tmp] = variants[tmp]
        options = product(*_variants.values()[:max_options])
        data = []
        for option in options:
            tmp = {}
            for i, key in enumerate(keys):
                tmp[key] = option[i]
            data.append(
                dict(in_stock=None, price=None, selected=None, properties=tmp)
            )
        return data

    def _parse_variant_data(self, response):
        json_resp = hjson.loads(response.body_as_unicode())
        html = json_resp['ModulesHtml']
        html = Selector(text=html)
        add_requests = response.meta.get('additional_requests')
        variants = response.meta['variants']
        cur_var = response.meta['cur_variant']
        choices = html.css('.catContent .optDescription::text').extract()
        variants[cur_var] = choices
        if add_requests:
            next_request = add_requests.pop(0)
            return next_request
        vs = self._collect_variants_from_dict(variants)
        prod = response.meta['product']
        prod['variants'] = vs
        return prod

    def _parse_variants(self, response):
        variants_exist = bool(response.css('#Configurations').extract())
        if variants_exist:
            common_req_params = self._collect_common_variants_data(response)
            variants_names = response.xpath('//div[contains(@class, "specContent")]')
            data = {}
            additional_requests = []
            for v_n in variants_names:
                k = is_empty(v_n.xpath('normalize-space(preceding-sibling::div[@class="specTitle"][1]/h5/text())').extract())
                v = ' '.join(v_n.xpath('span/text()').extract())
                is_ajax = bool(v_n.xpath('div[@class="dropdown"]').extract())
                if is_ajax:
                    form_data = self._collect_specific_variants_data(v_n, common_req_params)
                    meta = response.meta.copy()
                    meta['variants'] = data
                    meta['cur_variant'] = k
                    meta['additional_requests'] = additional_requests
                    meta['product'] = response.meta['product']
                    additional_requests.append(
                        FormRequest(self.VARIANTS_URL, callback=self._parse_variant_data,
                                    formdata=form_data, meta=meta)
                    )
                else:
                    data[k] = [v]
            if additional_requests:
                return True, additional_requests
            else:
                return False, data
        return None, None

    def _collect_related_products_data_v1(self, response):
        data = dict()
        cur_date = datetime.now()
        js_node = response.xpath('//div[@id="mbox_default"]/following-sibling::script[1]')
        js_data = js_node.xpath('following-sibling::script[1]/text()').re('profile = (\{.*\})')
        js_data = hjson.loads(js_data[0])
        data['p'] = is_empty(response.css('meta[name=currentOcId]::attr(content)').extract())
        data['date'] = cur_date.today().strftime('%Y%m%d')
        data['ts'] = '%s000' % int(time.mktime(cur_date.timetuple()))
        data['n'] = js_data['catid']
        data['chi'] = is_empty(js_node.xpath('text()').re("'profile.catid=(.*?)'"))
        return data

    def _collect_related_products_data_v2(self, response):
        data = dict()
        js_data = response.xpath('normalize-space(/html/head/script[@type="text/javascript"][1]/text())').re('\{.*\}')
        js_data = hjson.loads(js_data[0])
        cur_date = datetime.now()
        data['date'] = cur_date.today().strftime('%Y%m%d')
        data['ts'] = '%s000' % int(time.mktime(cur_date.timetuple()))
        data['p'] = js_data['CJ']['ORDERCODE'].lower()
        return data

    def _parse_related_products(self, response):
        prod = response.meta['product']
        html = re.search(r"html:'(.+?)'\}\]\},", response.body_as_unicode())
        if not html:
            return prod
        html = Selector(text=html.group(1))
        key_name = is_empty(html.css('.rrStrat::text').extract())
        items = html.css('.rrRecs > ul > li')
        rel_prods = []
        for item in items:
            title = is_empty(item.css('.rrItemName > a ::text').extract())
            url = is_empty(item.css('a.rrLinkUrl::attr(href)').extract())
            url = urlparse.urlparse(url)
            qs = urlparse.parse_qs(url.query)
            url = is_empty(qs['ct'])
            rel_prods.append(RelatedProduct(title=title, url=url))
        prod['related_products'] = {key_name: rel_prods}
        return prod
