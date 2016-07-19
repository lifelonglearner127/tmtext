from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import string
import urllib
import urlparse
import re

from scrapy import Request
from scrapy.log import ERROR, WARNING, INFO

from itertools import islice
from scrapy.conf import settings
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import cond_set, cond_set_value

is_empty = lambda x, y=None: x[0] if x else y


def is_num(s):
    try:
        int(s.strip())
        return True
    except ValueError:
        return False


_TRANSLATE_TABLE = string.maketrans('', '')


def _normalize(s):
    """Returns a representation of a string useful for comparing words and
    disregarding punctuation.

    :param s: The string to normalize.
    :type s: unicode
    :return: Normalized string.
    :rtype: unicode
    """
    try:
        return s.lower().encode('utf-8').translate(
            _TRANSLATE_TABLE, string.punctuation).decode('utf-8')
    except UnicodeEncodeError:
        # Less efficient version.
        for c in string.punctuation:
            s = s.replace(c, '')
        return s


class CvsProductsSpider(BaseProductsSpider):
    name = 'cvs_products'
    allowed_domains = ["cvs.com", "api.bazaarvoice.com"]
    start_urls = []

    SEARCH_URL = "https://www.cvs.com/search/N-0?searchTerm={search_term}"

    SEARCH_URL_AJAX = "https://www.cvs.com/" \
                      "retail/frontstore/OnlineShopService?" \
                      "apiKey=c9c4a7d0-0a3c-4e88-ae30-ab24d2064e43&" \
                      "apiSecret=4bcd4484-c9f5-4479-a5ac-9e8e2c8ad4b0&" \
                      "appName=CVS_WEB&" \
                      "channelName=WEB&" \
                      "contentZone=resultListZone&" \
                      "deviceToken=7780&" \
                      "deviceType=DESKTOP&" \
                      "lineOfBusiness=RETAIL&" \
                      "navNum=20&" \
                      "operationName=getProductResultList&" \
                      "pageNum={page_num}&" \
                      "referer={referer}&" \
                      "serviceCORS=False&" \
                      "serviceName=OnlineShopService&" \
                      "sortBy=relevance&" \
                      "version=1.0" \


    REVIEW_URL = "http://api.bazaarvoice.com/data/products.json?" \
                 "passkey=ll0p381luv8c3ler72m8irrwo&apiversion=5.5&" \
                 "filter=id:{product_id}&stats=reviews"

    PRICE_URL = "https://www.cvs.com/retail/frontstore/productDetails?" \
                "apiKey=c9c4a7d0-0a3c-4e88-ae30-ab24d2064e43&" \
                "apiSecret=4bcd4484-c9f5-4479-a5ac-9e8e2c8ad4b0&" \
                "appName=CVS_WEB&" \
                "channelName=WEB&" \
                "code={price_id}&" \
                "codeType=product&" \
                "deviceToken=2695&" \
                "deviceType=DESKTOP&" \
                "lineOfBusiness=RETAIL&" \
                "operationName=getSkuPricePromotions&" \
                "serviceCORS=True&" \
                "serviceName=productDetails&" \
                "storeId=2294&" \
                "version=1.0" \

    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)
        self.referer = None
        self.first_time_products = None
        self.current_page = 1
        super(CvsProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)
        settings.overrides['CRAWLERA_ENABLED'] = True

    def _set_brand(self, product, phrase, brands):
        phrase = _normalize(phrase)
        for brand in sorted(brands, key=len, reverse=True):
            if _normalize(brand) in phrase:
                cond_set_value(product, 'brand', brand)
                break

    def parse(self, response):
        print response.url
        if self.searchterms and not self.referer:
            self.referer = response.url
        return super(CvsProductsSpider, self).parse(response)

    def parse_product(self, response):
        brands = response.meta.get('brands', frozenset())
        product = response.meta['product']
        reqs = []

        if 'brand' not in product:
            descs = response.css('.brandBanner > a ::attr(title)')
            if descs:
                desc, = descs.extract()
                self._set_brand(product, desc, brands)
        product['locale'] = "en-US"

        ld_json = is_empty(response.xpath(
            '//*[@type="application/ld+json" '
            'and contains(text(),"product")]/text()').extract())
        if ld_json:
            try:
                clean_json = re.sub('([^"])\n|\t|\r', '',
                                    ld_json.replace('@', ''))
                product_data = json.loads(clean_json)

                cond_set_value(product, 'title', product_data.get('name'))
                cond_set_value(product, 'brand', product_data.get('brand'))

                variants = product_data.get('offers')
                main_variant = variants[0]
                description = main_variant.get('itemOffered', {}).get(
                    'description') or product_data.get('description')
                cond_set_value(product, 'description',
                               description)

                main_skuID_search = re.search("skuId=(\d+)", response.url)
                if main_skuID_search:
                    main_skuID = main_skuID_search.group(1)
                else:
                    main_skuID = variants[0].get(
                        'itemOffered', {}).get('sku', None)

                cond_set_value(product, 'image_url',
                               main_variant.get('itemOffered').get('image'))

                if main_variant.get('price'):
                    cond_set_value(product, 'price',
                                   Price(price=main_variant.get('price'),
                                         priceCurrency='USD'))

                elif product_data.get('productId'):
                    price_url = self.PRICE_URL.format(
                        price_id=product_data.get('productId'))
                    reqs.append(Request(price_url,
                                        self._parse_price,
                                        meta=response.meta))

                cond_set_value(product, 'variants',
                               self._parse_variants(variants, main_skuID))

                if main_skuID:
                    review_url = self.REVIEW_URL.format(product_id=main_skuID)
                    reqs.append(Request(review_url,
                                        self._parse_review,
                                        meta=response.meta))

            except:
                import traceback
                print traceback.print_exc()

        size = response.xpath(
            "//form[@id='addCart']/table/tr/td[@class='col1']/"
            "text()[.='Size:']/../../td[2]/text()"
        ).extract()
        cond_set(product, 'model', size, conv=string.strip)

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

    def _parse_price(self, response):
        product = response.meta['product']
        reqs = response.meta.get('reqs', [])
        data = json.loads(response.body)

        sku_price_promotions = data.get(
            'response', {}).get(
                'getSkuPricePromotions', [])

        if sku_price_promotions:
            sku_details = sku_price_promotions[0].get('skuDetails', [])

        if sku_details:
            price = sku_details[0].get('priceInfo', {}).get('listPrice', None)
            if price:
                cond_set_value(product, 'price', Price(price=price,
                                                       priceCurrency='USD'))
        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_variants(self, variants, main_skuID):
        if not variants:
            return None

        parsed_variants = []
        variants_visit = set()
        for variant in variants:
            # Check that the variant is not duplicated
            item_offered = variant.get('itemOffered', {})
            this_sku = item_offered.get('sku', None)
            if this_sku in variants_visit:
                continue
            variants_visit.add(this_sku)

            # Fill the Variant data
            vr = {}
            if variant['price']:
                vr['price'] = variant['price']
            availability = variant.get('availability', None)
            vr['in_stock'] = availability == "http://schema.org/InStock"
            vr['selected'] = main_skuID == this_sku
            if item_offered:
                attr = {}
                if item_offered.get('color'):
                    attr['Color'] = item_offered.get('color')
                if item_offered.get('color'):
                    attr['Weight'] = item_offered.get('weight').get('value')
                vr['properties'] = attr
                vr['url'] = item_offered.get('url')
            parsed_variants.append(vr)

        parsed_variants[0]['selected'] = True
        return parsed_variants

    def _parse_review(self, response):
        product = response.meta['product']
        reqs = response.meta.get('reqs', [])
        product['buyer_reviews'] = self.br.parse_buyer_reviews_products_json(response)
        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _scrape_total_matches(self, response):
        print "_scrape_total_matches"
        totals = response.xpath(
            '//*[@id="resultsTabs"]//'
            'a[@title="View Products"]/text()').re('\((\d+)\)')
        if len(totals) > 1:
            self.log(
                "Found more than one 'total matches' for %s" % response.url,
                ERROR
            )
        elif totals:
            total = totals[0].strip()
            return int(total)
        else:
            self.log(
                "Failed to find 'total matches' for %s" % response.url,
                WARNING
            )
        return None

    def _scrape_product_links(self, response):
        all_links_iter = re.finditer(
            'detailsLink"\s*:\s*"(.*?)(\?skuId=\d+)?",', response.body)

        # Clean the links for the different variants of a product
        links_without_dup = []
        [links_without_dup.append(item) for item in map((lambda x: x.group(1)), all_links_iter)
         if item not in links_without_dup]
        for link in links_without_dup:
                    yield link, SiteProductItem()

    def _scrape_results_per_page(self, response):
        return 20

    def _scrape_next_results_page_link(self, response):
        url_parts = urlparse.urlsplit(response.url)
        query_string = urlparse.parse_qs(url_parts.query)

        ajax_search_url = self.SEARCH_URL_AJAX.format(
            referer=urllib.quote_plus(self.referer, ':'),
            page_num=self.current_page)
        self.current_page += 1

        headers = {'Accept': 'application/json, text/plain, */*',
                   'Cache-Control': 'no-cache',
                   'Connection': 'keep-alive',
                   'Host': 'www.cvs.com',
                   'Pragma': 'no-cache',
                   'Referer': self.referer,
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'
                   ' AppleWebKit/537.36 (KHTML, like Gecko)'
                   ' Chrome/49.0.2623.110 Safari/537.36'}

        return Request(ajax_search_url,
                       self.parse,
                       headers=headers,
                       meta=response.meta,
                       priority=1)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _get_products(self, response):
        remaining = response.meta['remaining']
        search_term = response.meta['search_term']
        prods_per_page = response.meta.get('products_per_page')
        total_matches = response.meta.get('total_matches')
        scraped_results_per_page = response.meta.get('scraped_results_per_page')

        prods = self._scrape_product_links(response)

        if not prods_per_page:
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
                            "Failed to parse total matches for %s" % response.url,ERROR)

        if total_matches and not prods_per_page:
            # Parsing the page failed. Give up.
            self.log("Failed to get products for %s" % response.url, ERROR)
            return

        for i, (prod_url, prod_item) in enumerate(islice(prods, 0, remaining)):
            # Initialize the product as much as possible.
            prod_item['site'] = self.site_name
            prod_item['search_term'] = search_term
            prod_item['total_matches'] = total_matches
            prod_item['results_per_page'] = prods_per_page
            prod_item['scraped_results_per_page'] = scraped_results_per_page
            # The ranking is the position in this page plus the number of
            # products from other pages.
            prod_item['ranking'] = (i + 1) + (self.quantity - remaining)
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
                    meta={'product': prod_item})