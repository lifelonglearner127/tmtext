# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import re
import json
import string
import urllib

import requests
from scrapy.http import Request
from scrapy import Selector


from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults
from product_ranking.spiders import cond_set_value


class KohlsProductsSpider(BaseProductsSpider):
    """ kohls.com product ranking spider.

    `upc` field is missing

    Takes `order` argument with following possible values:

    * `rating` (default)
    * `best`
    * `new`
    * `price_asc`, `price_desc`
    """

    name = 'kohls_products'

    allowed_domains = [
        'kohls.com',
        'kohls.ugc.bazaarvoice.com',
    ]

    SEARCH_URL = "http://www.kohls.com/search.jsp?" \
                 "N=0&" \
                 "search={search_term}&" \
                 "WS={start}&S={sort_mode}"
    SORTING = None
    SORT_MODES = {
        'default': '',
        'featured': '1',
        'new': '2',
        'best_sellers': '3',
        'price_asc': '4',
        'price_desc': '5',
        'highest_rated': '6'
    }

    REVIEW_URL = "http://kohls.ugc.bazaarvoice.com/9025" \
                 "/{product_id}/reviews.djs?format=embeddedhtml"
    #
    # RELATED_URL = "http://www.ulta.com/ulta/common/recommendedProduct.jsp?" \
    #               "schemaVal=item_page.rvi,item_page.horizontal&productId={product_id}"

    def __init__(self, sort_mode=None, *args, **kwargs):
        if sort_mode:
            if sort_mode.lower() not in self.SORT_MODES:
                self.log('"%s" not in SORT_MODES')
            else:
                self.SORTING = self.SORT_MODES[sort_mode.lower()]

        super(KohlsProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                sort_mode=self.SORTING or self.SORT_MODES['default']),
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def start_requests(self):
        for st in self.searchterms:
            url = self.url_formatter.format(
                self.SEARCH_URL,
                search_term=urllib.quote_plus(st.encode('utf-8')),
                start=0,
                sort_mode=self.SORTING or ''
            )
            yield Request(
                url,
                meta={'search_term': st, 'remaining': self.quantity}
            )

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod})

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        prod = response.meta['product']
        prod['url'] = response.url

        cond_set_value(prod, 'locale', 'en-US')
        self._populate_from_html(response, prod)

        product_id = re.findall('prd-(.*)\/', response.url)

        new_meta = response.meta.copy()
        new_meta['product'] = prod
        new_meta['product_id'] = product_id[0]
        return Request(self.url_formatter.format(self.REVIEW_URL,
                                                 product_id=product_id[0]),
                       meta=new_meta, callback=self._parse_reviews)

    def _populate_from_html(self, response, product):
        if 'title' in product and product['title'] == '':
            del product['title']
        cond_set(product,
                 'title',
                 response.xpath(
                     '//h1[contains(@class, "title")]/text()').extract(),
                 conv=string.strip)

        cond_set(
            product,
            'description',
            response.xpath('//div[@class="Bdescription"]').extract(),
            conv=string.strip
        )

        cond_set(
            product,
            'image_url',
            response.xpath(
                '//div[@id="easyzoom_wrap"]/div/a/img/@src'
            ).extract()
        )

        upc_codes = []
        upc_codes_from_script = response.xpath(
            '//script[contains(text(), "allVariants")]'
        ).re('\"skuUpcCode\":\"(\d+)\"')

        for upc in upc_codes_from_script:
            if upc not in upc_codes:
                upc_codes.append(upc)

        product['upc'] = upc_codes

        price = response.xpath(
            '//div[@class="multiple-price"]/div[2]/text()[normalize-space()]'
        ).re("\d+.?\d{0,2}")

        if price:
            product['price'] = Price(price=price[0], priceCurrency='USD')
        else:
            product['price'] = Price(price='0.0', priceCurrency='USD')


        # in_store_only = response.xpath(
        #     '//div[@id="productBadge"]/img/@data-blzsrc[contains(.,"instore")]')
        #
        # if in_store_only:
        #     product['is_in_store_only'] = True
        # else:
        #     product['is_in_store_only'] = False


    def _parse_price(self, response):
        product = response.meta['product']
        product_id = response.meta['product_id']
        price = re.findall("\d+.?\d{0,2}", response.body_as_unicode())
        if price:
            if len(price) == 1:
                price = float(price[0].replace(',', '.'))
                product['price'] = Price(price=price, priceCurrency='USD')
            else:
                price = float(price[-1].replace(',', '.'))
                product['price'] = Price(price=price, priceCurrency='USD')
        else:
            product['price'] = Price(price='0.0', priceCurrency='USD')

        new_meta = response.meta.copy()
        new_meta['product'] = product
        return Request(url=self.RELATED_URL.format(product_id=product_id),
                       meta=new_meta,
                       callback=self._parse_related_products)

    def _parse_related_products(self, response):
        product = response.meta['product']
        product_id = response.meta['product_id']
        related_products = {}
        nodes = response.xpath('//div[@class="liquid"]')
        keys = response.xpath('//h3[@id="title"]/text()').extract()
        for i in range(0, len(nodes)):
            key = keys[i].strip()
            titles = nodes[i].xpath(
                './/p[@class="prod-desc"]/a/text()'
            ).extract()
            links = nodes[i].xpath(
                './/p[@class="prod-desc"]/a/@href'
            ).extract()
            products = []
            for j in range(0, len(titles)):
                try:
                    url = requests.get(links[j], timeout=5).url or links[j]
                    products.append(RelatedProduct(titles[j].strip(), url))
                except Exception:
                    self.log("Can't get related product!!!")
            related_products[key] = products
        product['related_products'] = related_products

        initial_response = response.meta['initial_response']
        total = initial_response.xpath(
            '//span[@class="count"]/text()'
        ).extract()
        if len(total) == 0:
            product['buyer_reviews'] = ZERO_REVIEWS_VALUE
            return product
        else:
            total = int(total[0])
        if total == 0:
            product['buyer_reviews'] = ZERO_REVIEWS_VALUE
            return product
        new_meta = response.meta.copy()
        new_meta['product'] = product
        new_meta['total_stars'] = total
        code = self._get_product_code(product_id)
        return Request(self.REVIEW_URL.format(code=code,
                                              product_id=product_id),
                       meta=new_meta, callback=self._parse_reviews)

    def _get_product_code(self, product_id):
        # override js function
        cr = 0
        for i in range(0, len(product_id)):
            cp = ord(product_id[i])
            cp = cp * abs(255-cp)
            cr += cp
        cr %= 1023
        cr = str(cr)
        ct = 4
        for i in range(0, ct - len(cr)):
            cr = '0' + cr
        cr = cr[0:2] + "/" + cr[2:4]
        return cr

    def _parse_reviews(self, response):
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
                    "//div[@id='BVRRRatingOverall_']"
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
        if 'buyer_reviews' not in product:
            cond_set_value(product, 'buyer_reviews', 0)
        return product

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//ul[@id="product-matrix"]/li/a/@href'
        ).extract()

        for link in links:
            yield 'http://www.kohls.com'+link, SiteProductItem()

    def _scrape_total_matches(self, response):
        if response.xpath('//div[@class="search-failed"]').extract():
            print('Not Found')
            return 0
        else:
            total = response.xpath(
                '//div[@class="view-indicator"]/p/text()'
            ).re('\d{1,},?\d+')
            if total:
                total_matches = int(total[1].replace(',', ''))
            else:
                total_matches = 0
            return total_matches

    def _scrape_next_results_page_link(self, response):
        next_page = response.xpath('//a[@rel="next"]/@href').extract()
        if next_page:
            next_page = 'http://www.kohls.com'+next_page[0]
            return next_page