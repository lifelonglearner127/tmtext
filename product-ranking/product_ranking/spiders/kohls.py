# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import re
import json
import string
import urllib

from scrapy.http import Request
from scrapy import Selector
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults
from product_ranking.spiders import cond_set_value
from product_ranking.guess_brand import guess_brand_from_first_words
from spiders_shared_code.kohls_variants import KohlsVariants

is_empty = lambda x, y="": x[0] if x else y

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

    RELATED_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js?" \
                  "a=648c894ab44bc04a&ts=1433226344391&p={product_id}&" \
                  "pt=%7Citem_page.recs_500x500_tab1%" \
                  "7Citem_page.recs_500x500_tab2&u=2254019586500985&" \
                  "s=2y6y2lj2VeejVt_wKaRQXP3H0FjpX3uAJK05OyhmpXH9fO0acBNb!" \
                  "137196239!1433224763639&cts=http%3A%2F%2Fwww.kohls.com&" \
                  "flv=17.0.0&pref=http%3A%2F%2Fwww.kohls.com%2Fsearch.jsp%" \
                  "3Fsearch%3Diphone%26submit-search%3Dweb-regular&" \
                  "rcs=eF4Ny7ERgDAIBdAmlbtwxwcS4gbOkSB3Fnbq_KZ_" \
                  "r5R3Hr2yextBMfdBluokiEGnVwVqprBs9_dcYQYmmCp0Jeu8ZCNAVX69phHt&" \
                  "l=1"

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

        kv = KohlsVariants()
        kv.setupSC(response)
        prod['variants'] = kv._variants()

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

        product['upc'] = ', '.join(upc_codes)

        price = response.xpath(
            '//div[@class="multiple-price"]/div[2]/text()[normalize-space()] |'
            '//div[@class="original original-reg"]/text()[normalize-space()] |'
            '//span[@class="price_ammount"]/text()[normalize-space()] |'
            '//div[@class="sale"]/text()[normalize-space()] |'
            '//div[contains(@class, "main_price")]/text()'
        ).re("\d+.?\d{0,2}")

        if price:
            product['price'] = Price(price=price[0], priceCurrency='USD')
        else:
            product['price'] = Price(price='0.0', priceCurrency='USD')
        product['marketplace'] = []
        marketplace_name = is_empty(response.xpath(
            '//a[@id="pdp_vendor"]/text()').extract())
        if marketplace_name:
            marketplace = {
                'name': marketplace_name,
                'price': product['price']
            }
        else:
            marketplace = {
                'name': 'Kohls',
                'price': product['price']
            }
        product['marketplace'].append(marketplace)

        rel_key = is_empty(response.xpath(
            '//div[@class="br-found-heading"]/text()').extract()
        )
        related = []
        related_products = {}
        for sel in response.xpath(
                '//div[@class="br-sf-widget-merchant-title"]/a'
        ):
            related.append(
                RelatedProduct(
                    title=is_empty(sel.xpath('text()').extract()),
                    url=is_empty(sel.xpath('@href').extract())
                ))
        if len(related) > 0:
            related_products[rel_key] = related

            product['related_products'] = related_products

        brand = is_empty(response.xpath(
            '//h1[contains(@class, "title")]/text()'
        ).extract())
        cond_set(
            product,
            'brand',
            (guess_brand_from_first_words(brand.strip()),2)
        )

    def _parse_related_products(self, response):
        product = response.meta['product']
        product_id = response.meta['product_id']
        text = re.findall('html:\s?\'(.*)\'', response.body_as_unicode())
        if text:
            html = Selector(text=text[0])
            key = is_empty(html.xpath(
                '//div[@id="rr0"]/div/div/text()[normalize-space()]'
            ).extract())
            related = []
            related_products = {}
            for sel in html.xpath('//div[@id="rr0"]/div/div/a'):
                url = is_empty(sel.xpath('@href').extract())
                if url:
                    related.append(
                        RelatedProduct(
                            title=is_empty(sel.xpath(
                                './div/p/text()').extract()),
                            url=urllib.unquote('http'+url.split('http')[-1])
                        ))

            if key:
                if 'related_products' in product.keys():
                    product['related_products'][key] = related
                else:
                    related_products[key] = related
                    product['related_products'] = related_products

            key = is_empty(html.xpath(
                '//div[@id="rr1"]/div/div/text()[normalize-space()]'
            ).extract())
            related = []
            for sel in html.xpath('//div[@id="rr1"]/div/div/a'):
                url = is_empty(sel.xpath('@href').extract())
                if url:
                    title = is_empty(sel.xpath('./div/p/text()').extract())
                    related.append(
                        RelatedProduct(
                            title=unicode.decode(title.replace("\xe9", "é")),
                            url=urllib.unquote('http'+url.split('http')[-1])
                        ))
            if key and key not in product['related_products'].keys():
                product['related_products'][key] = related
            elif key in product['related_products'].keys():
                product['related_products'][key] += related

        return product

    def _parse_reviews(self, response):
        product = response.meta['product']
        product_id = response.meta['product_id']
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
                        total = int(
                            total[0].replace(',', '')
                        )
                    except ValueError as exc:
                        total = 0
                        self.log(
                            "Error trying to extract number of BR in {url}: {exc}".format(
                                response.url, exc
                            ), WARNING
                        )
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
                            value = int(
                                value[0].replace(',', '')
                            )
                        distribution[name] = value
                    except ValueError:
                        self.log(
                            "Error trying to extract {star} value of BR in {url}: {exc}".format(
                                star=name,
                                url=response.url,
                                exc=exc
                            ), WARNING
                        )
                if distribution:
                    reviews = BuyerReviews(total, avrg, distribution)
                    cond_set_value(product, 'buyer_reviews', reviews)
        if 'buyer_reviews' not in product:
            cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
        new_meta = response.meta.copy()
        new_meta['product'] = product
        return Request(self.RELATED_URL.format(product_id=product_id),
                       meta=new_meta, callback=self._parse_related_products,
                       dont_filter=True)

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