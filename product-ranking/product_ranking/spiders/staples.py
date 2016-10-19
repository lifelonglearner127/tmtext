# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals

import json
import re
import time
import urllib
import urlparse
import datetime
from scrapy import Request, FormRequest, Selector
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews, scrapy_price_serializer
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value
from product_ranking.guess_brand import guess_brand_from_first_words
from scrapy.conf import settings
is_empty = lambda x, y=None: x[0] if x else y


# TODO: variants warranty
class StaplesProductsSpider(BaseProductsSpider):
    name = 'staples_products'
    allowed_domains = ['staples.com', "www.staples.com"]
    start_urls = []

    SEARCH_URL = "http://www.staples.com/{search_term}/directory_{search_term}?sby=0&pn=0"

    PAGINATE_URL = "http://www.staples.com/{search_term}/directory_{search_term}?sby=0&pn={nao}"

    CURRENT_NAO = 1
    PAGINATE_BY = 18  # 18 products
    TOTAL_MATCHES = None  # for pagination

    PRICE_URL = 'http://www.staples.com/asgard-node/v1/nad/staplesus/price/{sku}?offer_flag=true' \
                '&warranty_flag=true' \
                '&coming_soon={metadata__coming_soon_flag}&' \
                'price_in_cart={metadata__price_in_cart_flag}' \
                '&productDocKey={prod_doc_key}' \
                '&product_type_id={metadata__product_type__id}&' \
                'preorder_flag={metadata__preorder_flag}' \
                '&street_date={street_date}' \
                '&channel_availability_for_id={metadata__channel_availability_for__id}' \
                '&backOrderFlag={metadata__backorder_flag}'

    REVIEW_URL = 'http://www.staples.com/asgard-node/v1/nad/staplesus/yotporeview/{sku}'

    RELATED_PRODUCT = "http://www.staples.com/asgard-node/v1/nad/staplesus/bloomreach/{sku}"

    #use_proxies = True

    def __init__(self, *args, **kwargs):

        super(StaplesProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)
        settings.overrides['CRAWLERA_ENABLED'] = True
        # This may be useful for debug
        settings.overrides['RETRY_HTTP_CODES'] = [500, 502, 503, 504, 400, 403, 404, 408, 429]

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        meta = response.meta.copy()
        product = meta.get('product', SiteProductItem())
        reqs = []
        meta['reqs'] = reqs

        # Parse locate
        locale = 'en_US'
        cond_set_value(product, 'locale', locale)

        if 'Good thing this is not permanent' in response.body_as_unicode():
            product['not_found'] = True
            return product
        maintenance_error = response.xpath('.//*[contains(text(), "The site is currently under maintenance.")]')
        if maintenance_error:
            self.log("Website under maintenance error, retrying request: {}".format(response.url), WARNING)
            return Request(response.url, callback=self.parse_product, meta=meta, dont_filter=True)
        try:
            sku_url, js_data = self.parse_js_data(response)
        except Exception as e:
            self.log("Error extracting json data from product page, repeating request: {}".format(e), WARNING)
            return Request(response.url, callback=self.parse_product, meta=meta, dont_filter=True)

        # Parse title
        title = self.parse_title(response)
        cond_set_value(product, 'title', title)

        # Parse image
        image = self.parse_image(response)
        cond_set(product, 'image_url', image)

        # Parse brand
        brand = self.parse_brand(product)
        if brand:
            product['brand'] = brand
        #
        # Parse sku
        sku = self.parse_sku(response)
        cond_set_value(product, 'sku', sku)

        # Parse model
        model = self.parse_model(response)
        cond_set_value(product, 'model', model)

        # Parse description
        description = self.parse_description(response)
        cond_set_value(product, 'description', description)

        product['buyer_reviews'] = BuyerReviews(
            num_of_reviews=js_data['review']['count'],
            average_rating=js_data['review']['rating'],
            rating_by_star={'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        )
        if self.scrape_variants_with_extra_requests:
            self.parse_data_variant_price(response)
        else:
            product['variants'] = []
        # Parse price, related_product, reviews
        return self.parse_addition_data(response, sku, js_data)

    def parse_brand(self, product):
        title = product.get('title', None)
        if title:
            brand = guess_brand_from_first_words(title)
            return brand

    def parse_js_data(self, response):
        data = response.xpath('.//script[contains(text(), "products[")]/text()').extract()
        data = data[0] if data else None
        if data:
            try:
                data = re.findall(r'\s?products\[[\"\'](.+)[\"\']\]\s?=\s?(.+);', data)
                js_data = json.loads(data[0][1])
                return data[0], js_data
            except BaseException:
                return

    def clear_text(self, str_result):
        return str_result.replace("\t", "").replace("\n", "").replace("\r", "").replace(u'\xa0', ' ').strip()

    def parse_buyer_reviews(self, response):
        meta = response.meta.copy()
        product = response.meta['product']
        reqs = meta.get('reqs', [])
        try:
            jsonresponse = json.loads(response.body_as_unicode())
            response_selector = Selector(text=self._htmlspecialchars_decode(
                jsonresponse.get('result')))
            try:
                num_reviews = response_selector.xpath(
                    '//span[@class="font-color-gray based-on"]/text()').re('\d+')[0]
            except IndexError:
                num_reviews = 0
            try:
                avg_rating = response_selector.xpath('//span[@class="yotpo-star-digits"]/text()').extract()[0].strip()
            except IndexError:
                avg_rating = 0
            review_stars = response_selector.xpath(
                '//span[contains(@class, "yotpo-sum-reviews")]/text()').re('\((\d+)\)')[::-1]
            stars = product['buyer_reviews'].rating_by_star
            for star_index, star_value in enumerate(review_stars):
                star_index = str(star_index+1)
                stars[star_index] = star_value
            last_date = response_selector.xpath('//label[contains(@class, "yotpo-review-date")]/text()').extract()

            product['buyer_reviews'] = BuyerReviews(
                num_of_reviews=num_reviews,
                average_rating=avg_rating,
                rating_by_star=stars
            )
            if last_date:
                last_buyer_review_date = datetime.datetime.strptime(last_date[0], '%m/%d/%y')
                product['last_buyer_review_date'] = last_buyer_review_date.strftime('%d-%m-%Y')
        except BaseException as e:
            self.log("Error extracting buyers reviews - {}".format(e), WARNING)
            if 'No JSON object could be decoded' in e:
                self.log("Repeating buyers reviews request", WARNING)
                reqs.append(Request(response.url, callback=self.get_price_and_stockstatus, meta=meta, dont_filter=True))

        if reqs:
            return self.send_next_request(reqs, response)
        else:
            return product

    def parse_related_product(self, response):
        meta = response.meta.copy()
        product = response.meta['product']
        reqs = meta.get('reqs', [])

        try:
            jsonresponse = json.loads(response.body_as_unicode())

            related_prods = []
            if jsonresponse and jsonresponse['bloomReach']['relatedProducts']:
                for prod in jsonresponse['bloomReach']['relatedProducts']:
                    related_prods.append(
                        RelatedProduct(
                            title=prod['title'],
                            url=prod['url']
                        )
                    )
            product['related_products'] = {}

            if related_prods:
                product['related_products']['buyers_also_bought'] = related_prods
        except:
            pass

        if reqs:
            return self.send_next_request(reqs, response)
        else:
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

    def parse_title(self, response):
        title = response.xpath('//span[contains(@itemprop, "name")]//text()').extract()
        return self.clear_text(title[0])

    def parse_image(self, response):
        img = response.xpath('//img[contains(@class, "stp--sku-image")]/@src').extract()
        return img

    def parse_description(self, response):
        description = response.xpath('//div[contains(@id, "productInfo")]').extract()
        if description:
            return self.clear_text(description[0])
        else:
            return ''

    def parse_sku(self, response):
        sku = response.xpath('//span[contains(@itemprop, "sku")]/text()').extract()
        if sku:
            return self.clear_text(sku[0])

    def parse_model(self, response):
        model = response.xpath('//span[contains(@ng-bind, "product.metadata.mfpartnumber")]/text()').extract()
        if model:
            return self.clear_text(model[0])

    def parse_addition_data(self, response, sku, js_data):

        meta = response.meta.copy()
        product = response.meta['product']
        reqs = meta.get('reqs', [])
        currency = response.xpath('//meta[contains(@itemprop, "priceCurrency")]/@content').extract()

        if currency:
            meta['product']['price'] = Price(price=0.00, priceCurrency='USD')

        # if js_data['review']['count'] > 0:
        reqs.append(
            Request(
                url=self.REVIEW_URL.format(sku=sku),
                dont_filter=True,
                callback=self.parse_buyer_reviews,
                meta=meta
            ))

        url = self.RELATED_PRODUCT.format(sku=sku)
        params = {'pType': 'product',
                  'prodId': sku,
                  'prodName': product['title'].encode('ascii', 'ignore'),
                  'ref': '',
                  'status': 'ok',
                  'url': 'http://www.staples.com/product_%s' % sku,
                  'userAgent': self.user_agent,
                  }

        url_parts = list(urlparse.urlparse(url))
        url_parts[4] = urllib.urlencode(params)
        new_url = urlparse.urlunparse(url_parts)

        reqs.append(
            Request(
                url=new_url,
                dont_filter=True,
                callback=self.parse_related_product,
                meta=meta
            ))
        # Get base product data and child "additionalProductsWarrantyServices" variants, if any
        try:
            reqs.append(
                Request(
                    url=self.PRICE_URL.format(sku=sku,
                                              metadata__coming_soon_flag=js_data['metadata']['coming_soon_flag'],
                                              metadata__price_in_cart_flag=js_data['metadata']['price_in_cart_flag'],
                                              prod_doc_key=js_data['prod_doc_key'],
                                              metadata__product_type__id=js_data['metadata']['product_type']['id'],
                                              metadata__preorder_flag=js_data['metadata']['preorder_flag'],
                                              street_date=time.time(),
                                              metadata__channel_availability_for__id=
                                              js_data['metadata']['channel_availability_for']['id'],
                                              metadata__backorder_flag=js_data['metadata']['backorder_flag']),
                    dont_filter=True,
                    callback=self.get_price_and_stockstatus,
                    meta=meta,
                ))
        except Exception as e:
            self.log("Error while forming request for base product data: {}".format(e), WARNING)
        # Get real variants, if any
        # import pprint
        # pprint.pprint(response.meta['product']['variants'])
        if self.scrape_variants_with_extra_requests:
            for v in response.meta['product']['variants']:
                try:
                    reqs.append(
                        Request(
                            url=self.PRICE_URL.format(sku=v['partnumber'],
                                                      metadata__coming_soon_flag=js_data['metadata']['coming_soon_flag'],
                                                      metadata__price_in_cart_flag=js_data['metadata']['price_in_cart_flag'],
                                                      prod_doc_key=v['prod_doc_key'],
                                                      metadata__product_type__id=js_data['metadata']['product_type']['id'],
                                                      metadata__preorder_flag=js_data['metadata']['preorder_flag'],
                                                      street_date=time.time(),
                                                      metadata__channel_availability_for__id=
                                                      js_data['metadata']['channel_availability_for']['id'],
                                                      metadata__backorder_flag=js_data['metadata']['backorder_flag']),
                            dont_filter=True,
                            callback=self.get_variant_price,
                            meta=meta,
                        ))

                except Exception as e:
                    self.log("Error while forming request for variant: {}".format(e), WARNING)

        if reqs:
            return self.send_next_request(reqs, response)
        else:
            return product

    def get_price_and_stockstatus(self, response):
        meta = response.meta.copy()
        product = response.meta['product']
        reqs = meta.get('reqs', [])
        try:
            jsonresponse = json.loads(response.body_as_unicode())
            if u'currentlyOutOfStock' in jsonresponse['cartAction']:
                product['is_out_of_stock'] = True
            else:
                product['is_out_of_stock'] = False

            product['price'] = Price(price=jsonresponse['pricing']['finalPrice'],
                                     priceCurrency=product['price'].priceCurrency)
            #import pdb
            #pdb.set_trace()
            # additionalProductsWarrantyServices
            if self.scrape_variants_with_extra_requests:
                new_variants = []
                if jsonresponse.get('additionalProductsWarrantyServices'):
                    for warranty_variant in jsonresponse.get('additionalProductsWarrantyServices'):
                        # changed format for variants from price object to simple float
                        new_price = float(jsonresponse['pricing']['finalPrice']) + float(warranty_variant['price'])
                        in_stock = not product.get('is_out_of_stock') if product.get('is_out_of_stock') else None
                        new_variants.append({
                            'price': new_price,
                            "partnumber": warranty_variant.get('partnumber',''),
                            'isWarranty': warranty_variant.get('isWarranty', False),
                            'warranty': warranty_variant.get('name',''),
                            "prod_doc_key": warranty_variant.get('product_key_to',''),
                            'properties': {"variant_name": warranty_variant.get('name',''),},
                            'in_stock':in_stock,
                            'selected': False,
                        })
                meta['product']['variants'].extend(new_variants)
        except BaseException as e:
            self.log("Error parsing base product data: {}".format(e), WARNING)
            if 'No JSON object could be decoded' in e:
                self.log("Repeating base product data request: {}".format(e), WARNING)
                reqs.append(Request(response.url, callback=self.get_price_and_stockstatus, meta=meta, dont_filter=True))
        if reqs:
            return self.send_next_request(reqs, response)
        else:
            return product

    def get_variant_price(self, response):
        meta = response.meta.copy()
        reqs = meta.get('reqs', [])
        product = response.meta['product']
        try:
            jsonresponse = json.loads(response.body_as_unicode())
            id = jsonresponse['pricing'].get('id')
            # Getting exact variant that is parsed currently
            v = [x for x in meta['product']['variants'] if x['prod_doc_key'] == id]
            v = v[0] if v else None

            if 'currentlyOutOfStock' in jsonresponse.get('cartAction'):
                in_stock = False
            else:
                in_stock = True
            new_price = jsonresponse['pricing'].get('finalPrice')
            # If variant exists, set parameters
            if v['prod_doc_key'] == id:
                v['price'] = new_price
                v['warranty'] = jsonresponse.get('name','')
                v['in_stock'] = in_stock
                v['selected'] = False
            else:
                # create new variant
                new_variant = {
                    'price': new_price,
                    "partnumber": jsonresponse.get('partnumber', ''),
                    "prod_doc_key": v.get('prod_doc_key',''),
                    "variant_image": v.get('variant_image',''),
                    'warranty': jsonresponse.get('name',''),
                    'isWarranty': False,
                    'properties':{"variant_name": v['properties'].get('variant_name',''),},
                    'in_stock': in_stock,
                    'selected': False,
                }
                if new_variant:
                    meta['product']['variants'].append(new_variant)
        except Exception as e:
            self.log("Error parsing variant data: {}".format(e), WARNING)
            if 'No JSON object could be decoded' in e:
                self.log("Repeating variant data request: {}".format(e), WARNING)
                reqs.append(Request(response.url, callback=self.get_variant_price, meta=meta, dont_filter=True))

        if reqs:
            return self.send_next_request(reqs, response)
        else:
            return product

    def _scrape_total_matches(self, response):
        totals = response.xpath('//input[contains(@id, "allProductsTabCount")]/@value').extract()
        if totals:
            totals = totals[0].replace(',', '').replace('.', '').strip()
            if totals.isdigit():
                if not self.TOTAL_MATCHES:
                    self.TOTAL_MATCHES = int(totals)
                return int(totals)

    def _scrape_product_links(self, response):
        for link in response.xpath(
                '//a[contains(@class, "product-title")]/@href'
        ).extract():
            yield link, SiteProductItem()

    def _get_nao(self, url):
        nao = re.search(r'pn=(\d+)', url)
        if not nao:
            return
        return int(nao.group(1))

    def _replace_nao(self, url, new_nao):
        current_nao = self._get_nao(url)
        if current_nao:
            return re.sub(r'nao=\d+', 'pn=' + str(new_nao), url)
        else:
            return url + '&pn=' + str(new_nao)

    def _scrape_next_results_page_link(self, response):
        if self.TOTAL_MATCHES is None:
            self.log('No "next result page" link!')
            return
        if self.CURRENT_NAO * self.PAGINATE_BY >= self.TOTAL_MATCHES:
            return  # it's over
        self.CURRENT_NAO += 1
        return Request(
            self.PAGINATE_URL.format(
                search_term=response.meta['search_term'],
                nao=str(self.CURRENT_NAO)),
            callback=self.parse, meta=response.meta,
            dont_filter=True
        )

    def parse_data_variant_price(self, response):
        meta = response.meta.copy()
        selected_sku = re.findall(r'var selectedSKU = "(.+?)";', response.body_as_unicode())
        parent_sku = re.findall(r'parentSKU = "(.+?)";', response.body_as_unicode())
        js_data = {}
        if parent_sku:
            data = re.findall(r' products\["%s"\] = {(.+?)};' % parent_sku[0], response.body_as_unicode())
            if data:
                js_data = json.loads("{%s}" % data[0])
        if selected_sku:
            data = re.findall(r' products\["%s"\] = {(.+?)};' % selected_sku[0], response.body_as_unicode())
            if data:
                js_data = json.loads("{%s}" % data[0])
        else:
            data = re.findall(r' products\["(.+?)"\] = (.+?);', response.body_as_unicode())
            if data:
                try:
                    js_data = json.loads(data[0][1])
                except:
                    js_data = {}

        meta['product']['variants'] = []
        if 'child_product' in js_data:
            # print(js_data['child_product'])
            for child in js_data['child_product']:
                swatch_image = child.get('collection')
                swatch_image = swatch_image.get('collection_image').split('$')[0] if swatch_image else None
                v_image = swatch_image if not child.get('variant_image', '') else child.get('variant_image', '')
                meta['product']['variants'].append({
                                                    'in_stock':True,
                                                    'isWarranty': False,
                                                    'price': 0.0,
                                                    "partnumber": child.get('partnumber',''),
                                                    "prod_doc_key": child.get('prod_doc_key',''),
                                                    "variant_image": v_image ,
                                                    'properties': {"variant_name": child.get('variant_name',''),},
                                                    'selected': True if meta['product']['sku'] == child['partnumber'] else False,
                                                    })

        return js_data

    @staticmethod
    def _htmlspecialchars_decode(text):
        if text:
            return (
                text.replace('&amp;', '&').
                    replace('&quot;', '"').
                    replace('&lt;', '<').
                    replace('&gt;', '>')
            )
        else:
            return ''
