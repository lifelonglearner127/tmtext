from __future__ import division, absolute_import, unicode_literals

import json
import pprint
import re
import urlparse
import hashlib
import random
import re
import string
from datetime import datetime
import lxml.html

from scrapy import Selector
from scrapy.http import Request, FormRequest
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.items import (SiteProductItem, RelatedProduct,
                                   BuyerReviews, Price)
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX
from product_ranking.validation import BaseValidator
from spiders_shared_code.walmart_variants import WalmartVariants
from spiders_shared_code.walmart_categories import WalmartCategoryParser
from product_ranking.validators.walmart_validator import WalmartValidatorSettings


is_empty = lambda x, y="": x[0] if x else y


def get_string_from_html(xp, link):
    loc = is_empty(link.xpath(xp).extract())
    return Selector(text=loc).xpath('string()').extract()


def get_walmart_id_from_url(url):
    """ Returns item ID from the given URL """
    # possible variants:
    # http://walmart.com/ip/37002591?blabla=1
    # http://www.walmart.com/ip/Pampers-Swaddlers-Disposable-Diapers-Economy-Pack-Plus-Choose-your-Size/27280840
    if '?' in url:
        url = url.rsplit('?', 1)[0]
    if '/ip/' in url:
        url = url.split('/ip/')[1]
    if re.match(r'^[0-9]{3,20}$', url):
        return url
    g = re.search(r'\/([0-9]{3,20})', url)
    if not g:
        return
    return g.group(1)


def _get_walmart_original_redirect_item_id(response):
    """ Detects if the item was redirected, see BZ #2126
    :return: None if no redirect; item ID otherwise
    """
    redirects = response.request.meta.get('redirect_urls')
    if not redirects:
        return
    original_url = redirects[0]
    return get_walmart_id_from_url(original_url)


def _get_walmart_api_key():
    # TODO: implement loading from a config file!
    keys = ['yahac2smt4p4fjhgpz394kbp', 'upg664pajfcj7scau9ajq5zq',
            '63y2yz3qnes9vwn97tjpshtb']
    key = random.choice(keys)
    return key


# class WalmartValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
#     optional_fields = ['model', 'brand', 'description', 'recent_questions',
#                        'related_products', 'upc', 'buyer_reviews', 'price']
#     ignore_fields = ['google_source_site', 'is_in_store_only', 'bestseller_rank',
#                      'is_out_of_stock']
#     ignore_log_errors = False  # don't check logs for errors?
#     ignore_log_duplications = False  # ... duplicated requests?
#     ignore_log_filtered = False  # ... filtered requests?
#     ignore_log_duplications_and_ranking_gaps = True
#     test_requests = {
#         'abrakadabrasdafsdfsdf': 0,  # should return 'no products' or just 0 products
#         'nothing_found_123': 0,
#         'vodka': [50, 250],
#         'taker': [100, 500],
#         'socket 775': [10, 150],
#         'hexacore': [50, 700],
#         '300c': [50, 250],
#         'muay': [50, 200],
#         '14-pack': [1, 100],
#         'voltmeter': [50, 250]
#     }


class WalmartProductsSpider(BaseValidator, BaseProductsSpider):
    """Implements a spider for Walmart.com.

    This spider has 2 very peculiar things.
    First, it receives 2 types of pages so it need 2 rules for every action.
    Second, the site sometimes redirects a request to the same URL so, by
    default, Scrapy would discard it. Thus we override everything to handle
    redirects.

    FIXME: Currently we redirect infinitely, which could be a problem.
    """
    name = 'walmart_products'
    allowed_domains = ["walmart.com", "msn.com", 'api.walmartlabs.com']

    default_hhl = [404, 500, 502, 520]

    SEARCH_URL = "http://www.walmart.com/search/search-ng.do?Find=Find" \
        "&_refineresult=true&ic=16_0&search_constraint=0" \
        "&search_query={search_term}&sort={search_sort}"

    LOCATION_URL = "http://www.walmart.com/location"

    QA_URL = "http://www.walmart.com/reviews/api/questions" \
             "/{product_id}?sort=mostRecentQuestions&pageNumber={page}"

    REVIEW_URL = 'http://walmart.ugc.bazaarvoice.com/1336/{product_id}/' \
                 'reviews.djs?format=embeddedhtml&sort=submissionTime'

    REVIEW_DATE_URL = 'http://www.walmart.com/reviews/api/product/{product_id}?' \
                      'limit=3&sort=submission-desc&filters=&showProduct=false'

    QA_LIMIT = 0xffffffff

    _SEARCH_SORT = {
        'best_match': 0,
        'high_price': 'price_high',
        'low_price': 'price_low',
        'best_sellers': 'best_seller',
        'newest': 'new',
        'rating': 'rating_high',
    }

    settings = WalmartValidatorSettings

    sponsored_links = []

    _JS_DATA_RE = re.compile(
        r'define\(\s*"product/data\"\s*,\s*(\{.+?\})\s*\)\s*;', re.DOTALL)

    user_agent = 'default'

    def __init__(self, search_sort='best_match', zipcode='94117',
                 *args, **kwargs):
        if zipcode:
            self.zipcode = zipcode
        if search_sort == 'best_sellers':
            self.SEARCH_URL += '&soft_sort=false&cat_id=0'
        super(WalmartProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                search_sort=self._SEARCH_SORT[search_sort]
            ),
            *args, **kwargs)

    def start_requests(self):
        for st in self.searchterms:
            url = "http://www.walmart.com/midas/srv/ypn?" \
                "query=%s&context=Home" \
                "&clientId=walmart_us_desktop_backfill_search" \
                "&channel=ch_8,backfill" % (st,)
            yield Request(
                url=url, 
                callback=self.get_sponsored_links,
                dont_filter=True, 
                meta={"handle_httpstatus_list": [404]},
            )

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod, 'handle_httpstatus_list': [404]},
                          dont_filter=True)

    def get_sponsored_links(self, response):
        self.reql = []
        self.sponsored_links = []
        for link in response.xpath(
            '//div[contains(@class, "yahoo_sponsored_link")]'
                '/div[contains(@class, "yahoo_sponsored_link")]'):
            ad_title = is_empty(
                get_string_from_html('div/span[@class="title"]/a', link))
            ad_text = is_empty(
                get_string_from_html('div/span[@class="desc"]/a', link))
            visible_url = is_empty(
                get_string_from_html('div/span/span[@class="host"]/a', link))
            actual_url = is_empty(
                link.xpath('div/span[@class="title"]/a/@href').extract())
            sld = {"ad_title": ad_title,
                   "ad_text": ad_text,
                   "visible_url": visible_url,
                   "actual_url": actual_url,
                   }
            new_meta = response.meta.copy()
            new_meta["sld"] = sld
            new_meta['handle_httpstatus_list'] = [400, 403, 404, 405]
            self.reql.append(Request(
                actual_url,
                callback=self.parse_sponsored_links,
                errback=self.parse_sponsored_links,
                meta=new_meta,
                dont_filter=True))
        if self.reql:
            req1 = self.reql.pop(0)
            new_meta = req1.meta
            new_meta['reql'] = self.reql
            self.sld = new_meta["sld"]
            return req1.replace(meta=new_meta)
        return self.update_native_start_requests()

    def parse_sponsored_links(self, response):
        self.temp_spons_link = None
        if hasattr(response, "meta"):
            if response.status == 200:
                self.sld['actual_url'] = response.url
                self.sponsored_links.append(self.sld)

            if self.reql:
                req1 = self.reql.pop(0)
                new_meta = req1.meta
                new_meta['reql'] = self.reql
                self.temp_spons_link = req1.url
                self.sld = new_meta["sld"]
                return req1.replace(meta=new_meta)
        else:
            self.sld['actual_url'] = self.temp_spons_link
            self.sponsored_links.append(self.sld)
            if not self.reql:
                del self.temp_spons_link, self.sld, self.reql
                return super(WalmartProductsSpider, self).start_requests()
            req1 = self.reql.pop(0)
            new_meta = req1.meta
            new_meta['reql'] = self.reql
            self.temp_spons_link = req1.url
            self.sld = new_meta["sld"]
            return req1.replace(meta=new_meta)
        del self.temp_spons_link, self.sld, self.reql
        return self.update_native_start_requests()

    def update_native_start_requests(self):
        reqs = []
        for req in super(WalmartProductsSpider, self).start_requests():
            new_meta = req.meta.copy()
            new_meta["handle_httpstatus_list"] = self.default_hhl
            reqs.append(req.replace(meta=new_meta))
        return reqs

    def parse_product(self, response):
        product = response.meta.get("product")

        if "we can't find the product you are looking for" \
                in response.body_as_unicode().lower():
            product['not_found'] = True
            return product

        if response.status in self.default_hhl:
            product.update({"locale":'en-US'})
            return product
        if self._search_page_error(response):
            self.log(
                "Got 404 when coming from %r." % response.request.url, ERROR)
            return

        not_available = self.parse_available(response)
        cond_set_value(product, 'no_longer_available', not_available)

        wv = WalmartVariants()
        wv.setupSC(response)
        product['variants'] = wv._variants()

        if self.sponsored_links:
            product["sponsored_links"] = self.sponsored_links

        self._populate_from_js(response, product)
        self._populate_from_html(response, product)
        buyer_reviews = self._build_buyer_reviews(response)
        if buyer_reviews:
            product['buyer_reviews'] = buyer_reviews
        else:
            product['buyer_reviews'] = 0
        cond_set_value(product, 'locale', 'en-US')  # Default locale.
        if 'brand' not in product:
            cond_set_value(product, 'brand', u'NO BRAND')
        self._gen_related_req(response)

        # parse category and department
        wcp = WalmartCategoryParser()
        wcp.setupSC(response)
        try:
            product['categories'] = wcp._categories_hierarchy()
        except Exception as e:
            self.log('Category not parsed: '+str(e), WARNING)
        try:
            product['department'] = wcp._category()
        except Exception as e:
            self.log('No department to parse: '+str(e), WARNING)

        model = is_empty(
            response.xpath('//tr[@class="js-product-specs-row"]/'
                           'td[contains(text(), "Model No")]/'
                           'following::td[1]/text() |'
                           '//table[@class="SpecTable"]/tr/'
                           'td[contains(text(), "Walmart No")]'
                           '/following::td[1]/text()').extract())
        if model:
            product['model'] = model.strip()
        else:
            cond_set(product,
                     'model',
                     response.xpath(
                         '//meta[@itemprop="model"]/@content'
                     ).extract())
        flag = 'not available'
        if response.xpath('//meta[@name="Keywords"]').extract():
            if not flag in response.body_as_unicode():
                cond_set_value(product,
                               'shipping',
                               False)
            else:
                cond_set_value(product,
                               'shipping',
                               True)
        else:
            shipping = response.xpath(
                '//div[@class="product-no-fulfillment Grid-col '
                'u-size-6-12-l active"][1]/span/text()'
                '[contains(.,"not available")] |'
                '//span[@class="js-shipping-delivery-date-msg '
                'delivery-date-msg"]/text()[contains(., "Not available")]'
            ).extract()

            if len(shipping) > 0:
                cond_set_value(product,
                               'shipping',
                               False)
            else:
                cond_set_value(product,
                               'shipping',
                               True)

        sku = response.xpath('//*[@itemprop="sku"]/text()').extract()
        if sku:
            product['sku'] = sku[0]

        id = re.findall('\/(\d+)', response.url)
        response.meta['product_id'] = id[-1] if id else None
        # if id:
        #    url = 'http://www.walmart.com/reviews/api/questions/{0}?' \
        #          'sort=mostRecentQuestions&pageNumber=1'.format(id[0])
        #    meta = {
        #        "product": product,
        #        "relreql": response.meta["relreql"],
        #        "response": response
        #    }

        #    return Request(url=url, meta=meta, callback=self.get_questions)
        

        if re.search(
                "only available .{0,20} Walmart store",
                response.body_as_unicode()):
            product['is_in_store_only'] = True

        special_pricing = response.xpath(
            '//div[contains(@class, "price-flags")]//text()').extract()
        special_pricing = [
            r.strip() for r in special_pricing if len(r.strip())>0]
        if 'Rollback' in special_pricing:
            product['special_pricing'] = True
        else:
            product['special_pricing'] = False

        if not product.get('price'):
            cond_set_value(product, 'url', response.url)
            return self._gen_location_request(response)

        _na_text = response.xpath(
            '//*[contains(@class, "NotAvailable")]'
            '[contains(@style, "block")]/text()'
        ).extract()
        if not _na_text:
            _na_text = response.css('#WMNotAvailableLine ::text').extract()
        if _na_text:
            if 'not available' in _na_text[0].lower():
                product['is_out_of_stock'] = True

        return self._start_related(response)

    def parse_available(self, response):
        available = is_empty(response.xpath(
            '//div[@class="prod-no-buying-option"]/'
            'div[@class="heading-d"]/text()').extract())
        if available == 'This Item is no longer available':
            not_available = True
        else:
            not_available = False
        if response.xpath('//*[contains(@class, "invalid")'
                          ' and contains(text(), "tem not available")]'):
            not_available = True
        if response.xpath('//*[contains(@class, "invalid")'
                          ' and contains(text(), "no longer available")]'):
            not_available = True
        if response.xpath('//*[contains(@class, "NotAvailable")'
                          ' and contains(text(), "ot Available")]'):
            not_available = True
        if response.xpath('//*[contains(@class, "heading")'
                          ' and contains(text(), "nformation unavailable")]'):
            not_available = True
        return not_available

    def _on_api_response(self, response):
        if hasattr(response, 'getErrorMessage'):
            if response.getErrorMessage():
                # API request failed
                with open('/tmp/walmart_api_requests_failed.log', 'a') as fh:
                    fh.write(str(datetime.utcnow())+'\n')
                _response_from_parse_single_product = getattr(
                    self, '_response_from_parse_single_product', None)
                if _response_from_parse_single_product:
                    if not 'product' in _response_from_parse_single_product.meta:
                        _response_from_parse_single_product.meta['product'] = {}
                    _response_from_parse_single_product.meta['product'][
                        '_walmart_original_oos'] = True
                    yield self.parse_product(_response_from_parse_single_product)
                    return

        # if API request succeed
        original_id = response.meta['original_id']
        current_id = response.meta['current_id']
        original_response = response.meta['original_response_']
        if not 'product' in response.meta:
            response.meta['product'] = {}
        product = response.meta['product']
        j = json.loads(response.body)
        if str(j['itemId']) != str(original_id):
            self.log('API: itemId mismatch at URL %s' % response.url,
                     level=ERROR)
        else:
            product['_walmart_original_oos'] \
                = j.get('stock', '').lower() == 'not available'
            product['_walmart_original_price'] \
                = j.get('price', j.get('salePrice'))
            product['upc'] = j.get('upc', product.get('upc', ''))  # set original item UPC
        original_response.meta['product'] = product
        yield self.parse_product(original_response)

    def _get_walmart_api_data_for_item_id(self, original_response, original_id, current_id, meta):
        api_url = 'http://api.walmartlabs.com/v1/items/%s?apiKey=%s&format=json'
        api_key = _get_walmart_api_key()
        meta['original_id'] = original_id
        meta['current_id'] = current_id
        meta['original_response_'] = original_response
        self._response_from_parse_single_product = original_response  # needed for FailedRequest
        return Request(
            url=api_url % (original_id, api_key),
            callback=self._on_api_response, meta=meta,
            errback=self._on_api_response
        )

    def _parse_single_product(self, response):
        if response.status == 404:
            if 'product' not in response.meta:
                product = SiteProductItem()
            else:
                product = response.meta['product']
            product['response_code'] = 404
            if not 'url' in product:
                product['url'] = getattr(self, 'product_url', '')
            yield product
            return

        original_parent_id = _get_walmart_original_redirect_item_id(response)
        current_id = get_walmart_id_from_url(response.url)
        if str(original_parent_id) == str(current_id):
            # there was redirect but the IDs are the same, so it's the same product
            original_parent_id = None
        # store current ID to identify it later to match the products
        if 'product' not in response.meta:
            response.meta['product'] = {}
        response.meta['product']['_walmart_original_id'] = original_parent_id
        response.meta['product']['_walmart_current_id'] = current_id
        if original_parent_id:
            # ok we've been redirected and we get the original item ID. Now:
            # * perform API call (in method _get_walmart_api_data_from_item_id
            # * get the original ("parent") item Price and Out_of_stock (in _on_api_response)
            # * replace the existing data with the original Price and OOS in WalmartRedirectedItemFieldReplace
            yield self._get_walmart_api_data_for_item_id(
                original_response=response,
                original_id=original_parent_id, current_id=current_id,
                meta=response.meta)
        else:
            yield self.parse_product(response)

    def _search_page_error(self, response):
        path = urlparse.urlsplit(response.url)[2]
        return path == '/FileNotFound.aspx'

    def _build_related_products(self, url, related_product_nodes):
        also_considered = []
        for node in related_product_nodes:
            link = urlparse.urljoin(url, node.xpath('@href | ../@href').
                                    extract()[0])
            title = node.xpath('text()').extract()[0]
            also_considered.append(RelatedProduct(title.strip(), link))
        return also_considered

    def _build_buyer_reviews(self, response):
        overall_block = response.xpath(
            '//*[contains(@class, "review-summary")]'
            '//p[contains(@class, "heading")][contains(text(), "|")]//text()'
        ).extract()
        overall_text = ' '.join(overall_block)
        if not overall_text.strip():
            return ZERO_REVIEWS_VALUE
        buyer_reviews = {}
        num_of_reviews = int(overall_text.split('review')[0].strip())
        if not num_of_reviews:
            return ZERO_REVIEWS_VALUE
        buyer_reviews['num_of_reviews'] = num_of_reviews
        buyer_reviews['average_rating'] = float(
            overall_text.split('|')[1].split('out')[0].strip())
        buyer_reviews['rating_by_star'] = {}
        for _revs in response.css('.review-histogram .rating-filter'):
            _star = _revs.css('.meter-inline ::text').extract()[0].strip()

            try:
                _reviews = _revs.css('.rating-val ::text').extract()[0].strip()
            except:
                _reviews = 0
            _star = (_star.lower().replace('stars', '').replace('star', '')
                     .strip())
            buyer_reviews['rating_by_star'][int(_star)] = int(_reviews)
        return BuyerReviews(**buyer_reviews)

    def _parse_marketplaces_from_page_html(self, response, product):
        marketplaces = []
        for seller in response.xpath(
            "//ul[contains(@class, 'sellers-list')]"
            "/li[contains(@class,'js-marketplace-seller')]"
        ):
            price = is_empty(seller.xpath(
                ".//div[contains(@class, 'price')]/strong/text()"
            ).re(FLOATING_POINT_RGEX))
            if not price:
                price = is_empty(seller.xpath(
                    ".//strong[contains(@class, 'price')]/text()"
                ).re(FLOATING_POINT_RGEX))

            name = is_empty(seller.xpath(
                "div/div/div[contains(@class, 'name')]/a/text() |"
                "div/div/div[contains(@class, 'name')]/a/b/text()"
            ).extract())
            if not name:
                name = is_empty(seller.xpath(
                        "div/div/div[contains(@class, 'name')]/text()"
                ).extract()).strip()
            if not name:
                name = is_empty(seller.xpath(
                    './/div[contains(@class, "seller-name")]/text()'
                ).extract()).strip()
            if not name:
                name = is_empty(seller.xpath(
                    './/div[contains(@class, "seller-name")]//a/text()'
                ).extract()).strip()
            if price:
                price = Price(price=price, priceCurrency="USD")
            else:
                price = Price(price=0, priceCurrency="USD")
            marketplaces.append({
                "price": price,
                "name": name.strip()
            })

        if marketplaces:
            product["marketplace"] = marketplaces
        else:
            name = is_empty(response.xpath(
                '//div[@class="product-seller"]/div/span/b/text() |'
                '//div[@class="product-seller"]/div/span/a/b/text()'
            ).extract())
            if not name:
                name = is_empty(response.xpath(
                    '//meta[@itemprop="seller"]/@content'
                ).extract())
            if not name:
                name_json = re.search(r',\"sellerName\"\:\"(.*?)\",',
                                      response.body)
                if name_json:
                    name = name_json.group(1).strip()

            price_amount = is_empty(
                response.xpath('//meta[@itemprop="price"]'
                               '/@content').re(FLOATING_POINT_RGEX)
            )
            currency = is_empty(
                response.xpath('//meta[@itemprop="priceCurrency"]'
                               '/@content').extract(),
                "USD"
            )
            if price_amount:
                price = Price(price=price_amount,
                              priceCurrency=currency)
            else:
                price = Price(price=0,
                              priceCurrency=currency)
            if name:
                marketplaces.append({
                    "price": price,
                    "name": name
                })
            product["marketplace"] = marketplaces

    def _populate_from_html(self, response, product):
        cond_set_value(product, 'url', response.url)
        cond_set(
            product,
            'description',
            response.css('.about-product-section, #SITCC_1column').extract(),
            conv=''.join
        )

        title = is_empty(response.xpath(
                "//h1[contains(@class,'product-name')]/text() |"
                "//h1[@class='productTitle']/text()"
        ).extract(), "")
        if not title.strip():
            title = is_empty(response.xpath(
                "//h1[contains(@class,'product-name')]/span/text()"
            ).extract())
        if title:
            title = Selector(text=title).xpath('string()').extract()
            product["title"] = is_empty(title, "").strip()
        if ((isinstance(title, (str, unicode)) and not title.strip())
                or (isinstance(title, (list, tuple)) and not ''.join(title).strip())):
            title = response.css('h1[itemprop="name"] ::text').extract()
            title = ''.join(title).strip()
            if title:
                product['title'] = title

        cond_set(
            product,
            'brand',
            response.xpath(
                "//div[@class='product-subhead-section']"
                "/a[@id='WMItemBrandLnk']/text()").extract())

        try:
            cond_set(
                product, 'image_url',
                response.xpath('//img[contains(@class, "product-image")]/@src'),
                ""
            )
        except TypeError:
            pass
        if not product.get('image_url', None):
            product['image_url'] = is_empty(response.xpath(
                    '//meta[@property="og:image"]/@content').extract(), "")

        if not product.get("brand"):
            brand = is_empty(response.xpath(
                "//h1[contains(@class, 'product-name product-heading')]/text()"
                " | //h1[@class='productTitle']/text()"
            ).extract())
            cond_set(
                product,
                'brand',
                (guess_brand_from_first_words(brand.strip()),)
            )

        if not product.get("marketplace"):
            seller = response.xpath(
                '//div[@class="product-seller"]/div/' \
                'span[contains(@class, "primary-seller")]/b/text()'
            ).extract()
            if not seller:
                seller_all = response.xpath(
                    '//div[@class="product-seller"]/div/' \
                    'span[contains(@class, "primary-seller")]/a'
                )
                seller = seller_all.xpath('b/text()').extract()
            if seller and "price" in product:
                product["marketplace"] = [{
                    "price": product["price"],
                    "name": is_empty(seller)
                }]

        also_considered = self._build_related_products(
            response.url,
            response.xpath('//*[@class="top-product-recommendations'
                           ' tile-heading"]'),
        )
        if also_considered:
            product.setdefault(
                'related_products', {})["buyers_also_bought"] = also_considered

        recommended = self._build_related_products(
            response.url,
            response.xpath(
                "//p[contains(text(), 'Check out these related products')]/.."
                "//*[contains(@class, 'tile-heading')] |"
                "//div[@class='related-item']/a[contains(@class,"
                "'related-link')] |"
                "//div[@class='rel0']/a"
            ),
        )
        if recommended:
            product.setdefault(
                'related_products', {})['recommended'] = recommended
        if not product.get('price'):
            currency = response.css('[itemprop=priceCurrency]::attr(content)')
            price = response.css('[itemprop=price]::attr(content)')
            if price and currency:
                currency = currency.extract()[0]
                price = re.search('[,. 0-9]+', price.extract()[0])
                if price:
                    price = price.group()
                    price = price.replace(',', '').replace(' ', '')
                    cond_set_value(product, 'price',
                                   Price(priceCurrency=currency, price=price))

        if not product.get('upc'):
            cond_set(
                product,
                'upc',
                response.xpath('//strong[@id="UPC_CODE"]/text()').extract()
            )

        self._parse_marketplaces_from_page_html(response, product)

    def _gen_location_request(self, response):
        data = {"postalCode": ""}
        new_meta = response.meta.copy()
        new_meta['handle_httpstatus_list'] = [404, 405]
        # Need Conetnt-Type= app/json
        req = FormRequest.from_response(
            response=response,
            url=self.LOCATION_URL,
            method='POST',
            formdata=data,
            callback=self._after_location,
            meta=new_meta,
            headers={'x-requested-with': 'XMLHttpRequest',
                     'Content-Type': 'application/json'},
            dont_filter=True)
        req = req.replace(body='{"postalCode":"' + self.zipcode + '"}')
        return req

    def _gen_related_req(self, response):
        prodid = response.meta.get('productid')
        if not prodid:
            prodid = response.xpath(
                "//div[@id='recently-review']/@data-product-id").extract()
            if prodid:
                prodid = prodid[0]
        if not prodid:
            self.log("No PRODID in %r." % response.url, WARNING)
            return
        cid = hashlib.md5(prodid).hexdigest()
        reql = []
        url1 = (
            "http://www.walmart.com/irs?parentItemId%5B%5D={prodid}"
            "&module=ProductAjax&clientGuid={cid}").format(
                prodid=prodid,
                cid=cid)
        reql.append((url1, self._proc_mod_related))
        response.meta['relreql'] = reql
        return reql

    def _start_related(self, response):
        product = response.meta['product']
        reql = response.meta.get('relreql')
        if not reql:
            return self._request_questions_info(response)
            #return product
        (url, proc) = reql.pop(0)
        response.meta['relreql'] = reql
        return Request(
            url,
            meta=response.meta.copy(),
            callback=proc,
            dont_filter=True)

    def _proc_mod_related(self, response):
        product = response.meta['product']
        text = response.body_as_unicode().encode('utf-8')
        try:
            jdata = json.loads(text)
            modules = jdata['moduleList']
            for m in modules:
                html = m['html']
                sel = Selector(text=html)
                title, rel = self._parse_related(sel, response)
                if 'related_products' not in product:
                    product['related_products'] = {}
                if rel:
                    product['related_products'][title] = rel[:]
        except ValueError:
            self.log(
                "Unable to parse JSON from %r." % response.request.url, ERROR)
        return self._start_related(response)

    def _parse_related(self, sel, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        related = []
        title = sel.xpath("//div[@class='parent-heading']/h4/text()").extract()
        if not title:
            title = sel.xpath("//p[@class='heading-a']/text()").extract()
        if not title:
            title = sel.xpath("//div/h1/text()").extract()
        if title:
            title = title[0]
        els = sel.xpath("//ol/li//a[@class='tile-section']/p/..")
        for el in els:
            name = el.xpath("p/text()").extract()
            if name:
                name = name[0]
            href = el.xpath("@href").extract()
            if href:
                href = href[0]
                if 'dest=' in href:
                    url_split = urlparse.urlsplit(href)
                    query = urlparse.parse_qs(url_split.query)
                    original_url = query.get('dest')
                    if original_url:
                        original_url = original_url[0]
                else:
                    original_url = href
                related.append(RelatedProduct(name, full_url(original_url)))
        return (title, related)

    def _after_location(self, response):
        if response.status == 200:
            url = response.meta['product']['url']
            return Request(
                url,
                meta=response.meta.copy(),
                callback=self._reload_page,
                dont_filter=True)
        return self._start_related(response)

    def _reload_page(self, response):
        product = response.meta['product']
        self._populate_from_js(response, product)
        self._populate_from_html(response, product)
        return self._start_related(response)

    def _populate_from_js(self, response, product):
        data = {}
        m = re.search(
            self._JS_DATA_RE, response.body_as_unicode().encode('utf-8'))
        if m:
            text = m.group(1)
            try:
                data = json.loads(text)
            except ValueError:
                pass
        if not data:
            self.log("No JS matched in %r." % response.url, WARNING)
            return
        try:
            response.meta['productid'] = str(data['buyingOptions']['usItemId'])
            title = is_empty(Selector(text=data['productName']).xpath(
                'string()').extract())
            cond_set_value(product, 'title', title)
            available = data['buyingOptions']['available']
            cond_set_value(
                product,
                'is_out_of_stock',
                not available,
            )
            # the next 2 lines of code should not be uncommented, see BZ #1459
            #if response.xpath('//button[@id="WMItemAddToCartBtn"]').extract():
            #    product['is_out_of_stock'] = False
            cond_set_value(
                product,
                'is_in_store_only',
                data['buyingOptions']['storeOnlyItem'],
            )
            if available:
                price_block = None
                try:
                    price_block = data['buyingOptions']['price']
                except KeyError:
                    # Packs of products have different buyingOptions.
                    try:
                        price_block =\
                            data['buyingOptions']['minPrice']
                        #     data['buyingOptions']['maxPrice']
                    except KeyError:
                        self.log((
                            "Product with unknown buyingOptions "
                            "structure: %s\n%s") % (
                                response.url, pprint.pformat(data)),
                            WARNING
                        )
                if price_block:
                    try:
                        _price = Price(
                            priceCurrency=price_block['currencyUnit'],
                            price=price_block['currencyAmount']
                        )
                        cond_set_value(product, 'price', _price)
                    except KeyError:
                        try:
                            if price_block["currencyUnitSymbol"] == "$":
                                _price = Price(
                                    priceCurrency="USD",
                                    price=price_block['currencyAmount']
                                )
                            cond_set_value(product, 'price', _price)
                        except KeyError:
                            self.log(
                                ("Product with unknown buyingOptions "
                                    "structure: %s\n%s") % (
                                        response.url, pprint.pformat(data)),
                                ERROR
                            )
        except KeyError:
            pass
        if not product.get('upc', None):
            try:
                cond_set_value(
                    product, 'upc', data['analyticsData']['upc'], conv=unicode)
            except (ValueError, KeyError):
                pass  # Not really a UPC.
        try:
            cond_set_value(
                product,
                'image_url',
                data['primaryImageUrl'],
                conv=unicode)
        except KeyError:
            pass

        try:
            cond_set_value(
                product,
                'brand',
                data['analyticsData']['brand'],
                conv=unicode)
        except KeyError:
            pass

    def _scrape_total_matches(self, response):
        if response.css('.no-results'):
            return 0

        matches = response.css('.result-summary-container ::text').re(
            'Showing \d+ of (.+) results')
        if matches:
            num_results = matches[0].replace(',', '')
            num_results = int(num_results)
        else:
            num_results = None
            self.log(
                "Failed to extract total matches from %r." % response.url,
                ERROR
            )
        return num_results

    def _scrape_results_per_page(self, response):
        num = response.css('.result-summary-container ::text').re(
            'Showing (\d+) of')
        if num:
            return int(num[0])
        return None

    def _scrape_product_links(self, response):
        items = response.xpath(
            '//div[@class="js-tile tile-landscape"] | '
            '//div[contains(@class, "js-tile js-tile-landscape")]'
        )
        if not items:
            items = response.xpath('//div[contains(@class, "js-tile")]')

        if not items:
            self.log("Found no product links in %r." % response.url, INFO)

        for item in items:
            link = item.css('a.js-product-title ::attr(href)')[0].extract()

            title = ''.join(item.xpath(
                'div/div/h4[contains(@class, "tile-heading")]/a/node()'
            ).extract()).strip()
            title = is_empty(Selector(text=title).xpath('string()').extract())

            image_url = is_empty(item.xpath(
                "a/img[contains(@class, 'product-image')]/@data-default-image"
            ).extract())

            if item.css('div.pick-up-only').xpath('text()').extract():
                is_pickup_only = True
            else:
                is_pickup_only = False

            if item.xpath(
                './/div[@class="tile-row"]'
                '/span[@class="in-store-only"]/text()'
            ).extract():
                is_in_store_only = True
            else:
                is_in_store_only = False

            if item.xpath(
                './/div[@class="tile-row"]'
                '/span[@class="flag-rollback"]/text()'
            ).extract():
                special_pricing = True
            else:
                special_pricing = False

            if item.css('div.out-of-stock').xpath('text()').extract():
                shelf_page_out_of_stock = True
            else:
                shelf_page_out_of_stock = False

            res_item = SiteProductItem()
            if title:
                res_item["title"] = title.strip()
            if image_url:
                res_item["image_url"] = image_url
            res_item['is_pickup_only'] = is_pickup_only
            res_item['is_in_store_only'] = is_in_store_only
            res_item['special_pricing'] = special_pricing
            res_item['shelf_page_out_of_stock'] = shelf_page_out_of_stock
            yield link, res_item

    def _scrape_next_results_page_link(self, response):
        next_page = None

        next_page_links = response.css(".paginator-btn-next ::attr(href)")
        if len(next_page_links) == 1:
            next_page = next_page_links.extract()[0]
        elif len(next_page_links) > 1:
            self.log(
                "Found more than one 'next page' link in %r." % response.url,
                ERROR
            )
        else:
            self.log(
                "Found no 'next page' link in %r (which could be OK)."
                % response.url,
                INFO
            )

        return next_page

    def _request_questions_info(self, response):
        product_id = response.meta['product_id']
        if product_id is None:
            return response.meta['product']
        new_meta = response.meta.copy()
        new_meta['product']['recent_questions'] = []
        url = self.QA_URL.format(product_id=product_id, page=1)
        return Request(url, self._parse_questions,
                       meta=new_meta, dont_filter=True)

    def _parse_questions(self, response):
        data = json.loads(response.body_as_unicode())
        product = response.meta['product']
        last_date = product.get('date_of_last_question')
        questions = product['recent_questions']
        dateconv = lambda date: datetime.strptime(date, '%m/%d/%Y').date()
        for question_data in data.get('questionDetails', []):
            date = dateconv(question_data['submissionDate'])
            if last_date is None:
                product['date_of_last_question'] = last_date = date
            if date == last_date:
                questions.append(question_data)
            else:
                break
        else:
            total_pages = min(self.QA_LIMIT,
                              data['pagination']['pages'][-1]['num'])
            current_page = response.meta.get('current_qa_page', 1)
            if current_page < total_pages:
                url = self.QA_URL.format(
                    product_id=response.meta['product_id'],
                    page=current_page + 1)
                response.meta['current_qa_page'] = current_page + 1
                return Request(url, self._parse_questions, meta=response.meta,
                               dont_filter=True)
        if not questions:
            del product['recent_questions']
        else:
            product['date_of_last_question'] = str(last_date)
        if 'buyer_reviews' in product.keys():
            new_meta = response.meta.copy()
            return Request(url=self.REVIEW_DATE_URL.format(
                product_id=response.meta['product_id']),
                    callback=self._parse_last_buyer_review_date,
                    meta=new_meta,
                    dont_filter=True)
        else:
            return product

    def _parse_last_buyer_review_date(self, response):
        product = response.meta['product']
        data = json.loads(response.body_as_unicode())
        sel = Selector(text=data['reviewsHtml'])
        lbrd = sel.xpath('//span[contains(@class, "customer-review-date")]'
                         '/text()').extract()
        if lbrd:
            lbrd = datetime.strptime(lbrd[0].strip(), '%m/%d/%Y')
            product['last_buyer_review_date'] = lbrd.strftime('%d-%m-%Y')

        return product