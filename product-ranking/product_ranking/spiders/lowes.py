# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re
import json
import string
import urllib

from scrapy.http import Request, FormRequest
from scrapy.log import DEBUG, ERROR
from scrapy import Selector
from urlparse import urljoin

from scrapy.conf import settings


from product_ranking.items import SiteProductItem, BuyerReviews, \
    RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set, cond_set_value


class LowesProductsSpider(BaseProductsSpider):
    name = 'lowes_products'
    allowed_domains = ["lowes.com","bazaarvoice.com"]
    start_urls = []

    SEARCH_URL = "http://www.lowes.com/Search={search_term}?storeId="\
        "10151&langId=-1&catalogId=10051&N=0&newSearch=true&Ntt={search_term}"

    RATING_URL = "http://lowes.ugc.bazaarvoice.com/0534/{prodid}"\
        "/reviews.djs?format=embeddedhtml"

    def __init__(self, zip_code='94117', *args, **kwargs):
        self.zip_code = zip_code
        settings.overrides['CRAWLERA_ENABLED'] = True
        formatter = None
        super(LowesProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def start_requests(self):
        yield Request(url="http://www.lowes.com/", 
                      meta={'zip_code_stage': 1},
                      callback=self.set_zip_code)

    def set_zip_code(self, response):
        zip_code_stage = response.meta.get('zip_code_stage')
        self.log("zip code stage: %s" % zip_code_stage, DEBUG)
        if zip_code_stage == 1:
            data = {'zipCode': self.zip_code}
            new_meta = response.meta.copy()
            new_meta['zip_code_stage'] = 2
            request = FormRequest.from_response(
                response=response,
                formname='storeSearchForm',
                method='POST',
                formdata=data,
                callback=self.set_zip_code,
                meta=new_meta)
            yield request

        else:
            for result in super(LowesProductsSpider, self).start_requests():
                yield result


    def _parse_single_product(self  , response):
        return self.parse_product(response)

    def parse_product(self, response):
        product = response.meta['product']
        return product

    def _scrape_total_matches(self, response):
        total_matches = response.xpath(
            '//*[@title="productduct Search Results"]/span/text()').re('\d+')
        return int(total_matches[0]) if total_matches else None

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//*[@name="listpage_productname"]/@href').extract()

        for link in links:
            product = SiteProductItem()
            yield link, product

    def _scrape_next_results_page_link(self, response):
        next_page_url = response.xpath(
            '(//*[@title="Next Page"]/@href)[1]').extract()

        return urljoin(response.url, next_page_url[0]) if \
             next_page_url else None
             
    def _parse_title(self, response):
        title = response.xpath('//h1/text()').extract()
        return title[0] if title else None

    def _parse_model(self, response):
        models = response.xpath('//*[@id="ModelNumber"]/text()').extract()
        return models[0] if models else None

    def _parse_categories(self, response):
        return response.xpath(
            '//*[@id="breadcrumbs-list"]//a/text()').extract() or None

    def _parse_category(self, response):
        categories = self._parse_categories(response)
        return categories[-1] if categories else None

    def _parse_price(self, response):
        price = response.xpath(
            '//*[@class="price"]/text()').re('[\d\.\,]+')

        if not price:
            return None
        price = price[0].replace(',', '')
        return Price(price=price, priceCurrency='USD')

    def _parse_image_url(self, response):
        image_url = response.xpath(
            '//*[@id="prodPrimaryImg"]/@src').extract()
        return image_url[0] if image_url else None

    def _parse_variants(self, response):
        return None

    def _parse_is_out_of_stock(self, response):
        status = response.xpath(
            '//*[@itemprop="availability" '
            'and not(@href="http://schema.org/InStock")]')
        return bool(status)

    def _parse_description(self, response):
        description = response.xpath('//*[@id="description-tab"]').extract()
        return ''.join(description).strip() if description else None

    def _parse_related_products(self, response):
        related_products = []
        for a in response.xpath('//a[contains(@name, "relatedItems_Desc")]'):
            title = a.xpath('text()').extract()
            url = a.xpath('@href').extract()

            if title and url:
                related_products.append(RelatedProduct(title=title[0], 
                                         url=urljoin(response.url,url[0])))
        return related_products or None

    def _parse_no_longer_available(self, response):
        return bool(response.xpath('//*[@class="prodUnavailable"]'))

    def parse_product(self, response):
        reqs = response.meta.get('reqs',[])
        product = response.meta['product']

        # Set locale
        product['locale'] = 'en_US'

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse model
        model = self._parse_model(response)
        cond_set_value(product, 'model', model)

        # Parse categories
        categories = self._parse_categories(response)
        cond_set_value(product, 'categories', categories)

        # Parse category
        category = self._parse_category(response)
        cond_set_value(product, 'category', category)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse image url
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Parse variants
        variants = self._parse_variants(response)
        cond_set_value(product, 'variants', variants)

        # Parse stock status
        out_of_stock = self._parse_is_out_of_stock(response)
        cond_set_value(product, 'is_out_of_stock', out_of_stock)

        no_longer_available = self._parse_no_longer_available(response)
        cond_set_value(product, 'no_longer_available', no_longer_available)

        related_products = self._parse_related_products(response) 
        cond_set_value(product, 'related_products', related_products)

        # Reviews
        bv_product_id = response.xpath('//*[@id="bvProductId"]/@value').extract()
        if bv_product_id:
            url = self.RATING_URL.format(prodid=bv_product_id[0])                        
            reqs.append(Request(
                    url,
                    meta=response.meta.copy(),
                    callback=self._parse_bazaarv))

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_bazaarv(self, response):
        reqs = response.meta.get('reqs',[])
        product = response.meta['product']
        text = response.body_as_unicode().encode('utf-8')
        if response.status == 200:
            x = re.search(
                r"var materials=(.*),\sinitializers=", text, re.M + re.S)
            if x:
                jtext = x.group(1)
                jdata = json.loads(jtext)

                html = jdata['BVRRSourceID']
                sel = Selector(text=html)
                avrg = sel.xpath(
                    "//div[contains(@id,'BVRRRatingOverall')]"
                    "/div[@class='BVRRRatingNormalOutOf']"
                    "/span[contains(@class,'BVRRRatingNumber')]"
                    "/text()").extract()
                if avrg:
                    try:
                        avrg = float(avrg[0])
                    except ValueError:
                        avrg = 0.0
                else:
                    avrg = 0.0
                total = sel.xpath(
                    "//div[@class='BVRRHistogram']"
                    "/div[@class='BVRRHistogramTitle']"
                    "/span[contains(@class,'BVRRNonZeroCount')]"
                    "/span[@class='BVRRNumber']/text()").extract()
                if total:
                    try:
                        total = int(total[0])
                    except ValueError:
                        total = 0
                else:
                    total = 0

                hist = sel.xpath(
                    "//div[@class='BVRRHistogram']"
                    "/div[@class='BVRRHistogramContent']"
                    "/div[contains(@class,'BVRRHistogramBarRow')]")
                distribution = {}
                for ih in hist:
                    name = ih.xpath(
                        "span/span[@class='BVRRHistStarLabelText']"
                        "/text()").re("(\d) star")
                    try:
                        if name:
                            name = int(name[0])
                        value = ih.xpath(
                            "span[@class='BVRRHistAbsLabel']/text()").extract()
                        if value:
                            value = int(value[0])
                        distribution[name] = value
                    except ValueError:
                        pass
                if distribution:
                    reviews = BuyerReviews(total, avrg, distribution)
                    cond_set_value(product, 'buyer_reviews', reviews)

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