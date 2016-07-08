# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals

import json
import re
import time
import urllib
import urlparse

import datetime
from scrapy import Request, FormRequest

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value

is_empty = lambda x, y=None: x[0] if x else y


# TODO: variants warranty
class StaplesProductsSpider(BaseProductsSpider):
    name = 'staples_products'
    allowed_domains = ['staples.com', "www.staples.com"]
    start_urls = []

    SEARCH_URL = "http://www.staples.com/{search_term}/directory_{search_term}?sby=0&pn=0"

    PAGINATE_URL = "http://www.staples.com/{search_term}/directory_{search_term}?sby=0&pn={nao}"

    CURRENT_NAO = 0
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

    use_proxies = True

    def __init__(self, *args, **kwargs):

        super(StaplesProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

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

        sku_url, js_data = self.parse_js_data(response)

        # Parse title
        title = self.parse_title(response)
        cond_set_value(product, 'title', title)

        # Parse image
        image = self.parse_image(response)
        cond_set(product, 'image_url', image)

        # # Parse brand
        # brand = self.parse_brand(response)
        # cond_set_value(product, 'brand', brand)
        #
        # Parse sku
        sku = self.parse_sku(response)
        cond_set_value(product, 'sku', sku)

        # Parse model
        model = self.parse_model(response)
        cond_set_value(product, 'model', model)
        # Parse brand

        # Parse description
        description = self.parse_description(response)
        cond_set_value(product, 'description', description)

        product['buyer_reviews'] = BuyerReviews(
            num_of_reviews=js_data['review']['count'],
            average_rating=js_data['review']['rating'],
            rating_by_star={'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        )

        self.parse_data_variant_price(response)

        # Parse price, related_product, reviews
        return self.parse_addition_data(response, sku, js_data)

    def parse_js_data(self, response):
        data = re.findall(r' products\["(.+)"\] = (.+);', response.body_as_unicode())
        if data:
            try:
                js_data = json.loads(data[0][1])
                return data[0], js_data
            except:
                return

    def clear_text(self, str_result):
        return str_result.replace("\t", "").replace("\n", "").replace("\r", "").replace(u'\xa0', ' ').strip()

    def parse_buyer_reviews(self, response):
        meta = response.meta.copy()
        product = response.meta['product']
        reqs = meta.get('reqs', [])

        try:
            jsonresponse = json.loads(response.body_as_unicode())

            num_reviews = 0
            avg_rating = 0

            stars = product['buyer_reviews'].rating_by_star
            for k in stars:
                rate = re.findall(r'quot;%s&amp;quot;&amp;gt;\((\d+)\)&amp;' % k, jsonresponse['result'])
                if rate:
                    stars[k] = rate[0]
                    num_reviews += int(rate[0])
                    avg_rating += int(k) * int(rate[0])

            if num_reviews > 0:
                avg_rating = round(avg_rating/num_reviews, 1)

            last_date = re.findall(r'yotpo-review-date&amp;quot;&amp;gt;(\d+/\d+/\d+)&amp;lt;', jsonresponse['result'])

            product['buyer_reviews'] = BuyerReviews(
                num_of_reviews=num_reviews,
                average_rating=avg_rating,
                rating_by_star=stars
            )
            if last_date:
                last_buyer_review_date = datetime.datetime.strptime(last_date[0], '%m/%d/%y')
                product['last_buyer_review_date'] = last_buyer_review_date.strftime('%d-%m-%Y')
        except:
            pass

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
            meta['product']['price'] = Price(price=0.00, priceCurrency=str(currency[0]))

        if js_data['review']['count'] > 0:
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
                    meta=meta
                ))
        except:
            pass

        for v in response.meta['product']['variants']:
            try:
                reqs.append(
                    Request(
                        url=self.PRICE_URL.format(sku=v['properties']['partnumber'],
                                                  metadata__coming_soon_flag=js_data['metadata']['coming_soon_flag'],
                                                  metadata__price_in_cart_flag=js_data['metadata']['price_in_cart_flag'],
                                                  prod_doc_key=v['properties']['prod_doc_key'],
                                                  metadata__product_type__id=js_data['metadata']['product_type']['id'],
                                                  metadata__preorder_flag=js_data['metadata']['preorder_flag'],
                                                  street_date=time.time(),
                                                  metadata__channel_availability_for__id=
                                                  js_data['metadata']['channel_availability_for']['id'],
                                                  metadata__backorder_flag=js_data['metadata']['backorder_flag']),
                        dont_filter=True,
                        callback=self.get_variant_price,
                        meta=meta
                    ))

            except:
                pass

        if reqs:
            return self.send_next_request(reqs, response)
        else:
            return product

    def get_price_and_stockstatus(self, response):
        meta = response.meta.copy()
        product = response.meta['product']
        reqs = meta.get('reqs', [])
        jsonresponse = json.loads(response.body_as_unicode())
        if u'currentlyOutOfStock' in jsonresponse['cartAction']:
            product['is_out_of_stock'] = True
        else:
            product['is_out_of_stock'] = False
        try:
            product['price'] = Price(price=jsonresponse['pricing']['finalPrice'],
                                     priceCurrency=str(product['price'].priceCurrency))
            #import pdb
            #pdb.set_trace()
            # additionalProductsWarrantyServices
            new_variants = []
            if jsonresponse['additionalProductsWarrantyServices']:
                for w in jsonresponse['additionalProductsWarrantyServices']:
                    new_price = Price(price=jsonresponse['pricing']['finalPrice'] + w['price'],
                                      priceCurrency=product['price'].priceCurrency)
                    new_variants.append({
                        'price': new_price,
                        'properties': {"name": product['title'] if 'title' in product else '',
                                       "partnumber": w['partnumber'] if 'partnumber' in w else '',
                                       "prod_doc_key": w['prod_doc_key'] if 'prod_doc_key' in w else '',
                                       'warranty': w['name'] if 'name' in w else '',
                                       'isWarranty': w['isWarranty'] if 'isWarranty' in w else '',
                                       },
                        'selected': False,
                    })
            meta['product']['variants'].extend(new_variants)
        except:
            pass
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
            id = jsonresponse['pricing']['id']
            new_variants = []
            for v in meta['product']['variants']:
                if v['properties']['prod_doc_key'] == id:
                    v['price'] = Price(price=jsonresponse['pricing']['finalPrice'],
                                       priceCurrency=str(product['price'].priceCurrency))

                    # additionalProductsWarrantyServices
                    if jsonresponse['additionalProductsWarrantyServices']:
                        for w in jsonresponse['additionalProductsWarrantyServices']:
                            new_price = Price(price=jsonresponse['pricing']['finalPrice'] + w['price'],
                                              priceCurrency=str(product['price'].priceCurrency))
                            new_variants.append({
                                'price': new_price,
                                'properties': {"name": v['properties']['name'] if 'name' in v['properties'] else '',
                                               "partnumber": w['partnumber'] if 'partnumber' in w else '',
                                               "variant_name": v['properties']['variant_name'] if 'variant_name' in v['properties'] else '',
                                               "prod_doc_key": v['properties']['prod_doc_key'] if 'prod_doc_key' in v['properties'] else '',
                                               "variant_image": v['properties']['variant_image'] if 'variant_image' in v['properties'] else '',
                                               'warranty': w['name'] if 'name' in w else '',
                                               'isWarranty': w['isWarranty'] if 'isWarranty' in w else '',
                                               },
                                'selected': False,
                            })
            if new_variants:
                meta['product']['variants'].extend(new_variants)
        except:
            pass

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
        if self.CURRENT_NAO > self.TOTAL_MATCHES + self.PAGINATE_BY:
            return  # it's over
        self.CURRENT_NAO += self.PAGINATE_BY
        return Request(
            self.PAGINATE_URL.format(
                search_term=response.meta['search_term'],
                nao=str(self.CURRENT_NAO)),
            callback=self.parse, meta=response.meta
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
            print(js_data['child_product'])
            for child in js_data['child_product']:
                meta['product']['variants'].append({
                                                    'price': 0,
                                                    'properties': {"name": child['name'] if 'name' in child else '',
                                                                   "partnumber": child['partnumber'] if 'partnumber' in child else '',
                                                                   "variant_name": child['variant_name'] if 'variant_name' in child else '',
                                                                   "prod_doc_key": child['prod_doc_key'] if 'prod_doc_key' in child else '',
                                                                   "variant_image": child['variant_image'] if 'variant_image' in child else '',
                                                                   },
                                                    'selected': True if meta['product']['sku'] == child['partnumber'] else False,
                                                    })

        return js_data
