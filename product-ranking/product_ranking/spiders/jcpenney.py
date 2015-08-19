# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import re
import json
import string
import urllib

from scrapy.http import Request
from scrapy import Selector


from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults
from product_ranking.spiders import cond_set_value
from product_ranking.guess_brand import guess_brand_from_first_words
from spiders_shared_code.jcpenney_variants import JcpenneyVariants
from product_ranking.validation import BaseValidator


is_empty = lambda x, y="": x[0] if x else y

ip = "http://151.236.56.213:80"

class JcpenneyValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = []
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'description', 'special_pricing', 
        'bestseller_rank', 'model',
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = True  # ... duplicated requests?
    ignore_log_filtered = True  # ... filtered requests?
    test_requests = {
        'sdfsdgdf': 0,  #+ should return 'no products' or just 0 products
        'benny benassi': 0, #+
        'water proof': [110, 210],
        'peace': [10, 70],#+
        'hot': [80, 180],
        'drink': [30, 130],
        'term': [30, 130],
        'tiny': [10, 80],#+
        'selling': [1, 30],#+
        'night': [40, 140],#+
    }


class JcpenneyProductsSpider(BaseValidator, BaseProductsSpider):
    """ jcpenny.com product ranking spider.

    Takes `order` argument with following possible values:

    * `rating` (default)
    * `best`
    * `new`
    * `price_asc`, `price_desc`
    """

    name = 'jcpenney_products'

    settings = JcpenneyValidatorSettings

    allowed_domains = [
        'jcpenney.com',
        'jcpenney.ugc.bazaarvoice.com',
        'recs.richrelevance.com',
        'www.jcpenney.comjavascript'
    ]

    SEARCH_URL = "http://www.jcpenney.com/jsp/search/results.jsp?" \
                 "fromSearch=true&" \
                 "Ntt={search_term}&" \
                 "ruleZoneName=XGNSZone&" \
                 "Ns={sort_mode}&pageSize=72&" \
                 "redirectTerm=skirts{search_term}"
    SORTING = None
    SORT_MODES = {
        'default': '',
        'best_match': '',
        'new arrivals': 'NA',
        'best_sellers': 'BS',
        'price_asc': 'PLH',
        'price_desc': 'PHL',
        'rating_desc': 'RHL'
    }

    REVIEW_URL = "http://jcpenney.ugc.bazaarvoice.com/1573-en_us/{product_id}" \
                 "/reviews.djs?format=embeddedhtml"

    RELATED_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js?" \
                  "a=5387d7af823640a7&" \
                  "ts=1434100234104&" \
                  "p={product_id}&" \
                  "pt=%7Citem_page.dpcontent1%7Citem_page.dpcontent3%" \
                  "7Citem_page.dpcontent2_json&" \
                  "s=9ecf276c73e4a7eef696974bf7794dc8&cts=http%3A%2F%2" \
                  "Fwww.jcpenney.com%3A80%2Fdotcom&ctp=%7C0%3Acmvc%25253DJCP%" \
                  "25257CSearchResults%25257CRICHREL%252526grView%25253D%" \
                  "252526eventRootCatId%25253D%252526currentTabCatId%25253D%" \
                  "252526regId%25253D&flv=17.0.0&" \
                  "pref=http%3A%2F%2Fwww.jcpenney.com%2Fdotcom%2Fjsp%2Fsearch%2" \
                  "Fresults.jsp%3FfromSearch%3Dtrue%26Ntt%3Ddisney%2Bpajamas%" \
                  "26ruleZoneName%3DXGNSZone%26successPage%3Dnull%" \
                  "26_dyncharset%3DUTF-8&" \
                  "rcs=eF4NzLkNgDAMAMAmFbtYin-zAXM4JhIFHTA_aa-" \
                  "41t5xhHZ3y4Iae4JMdiCshNOVEXVO6rTd33OVIBmgsPQwDg5SkAW4hh--nxIA&l=1"

    def __init__(self, sort_mode=None, *args, **kwargs):
        if sort_mode:
            if sort_mode.lower() not in self.SORT_MODES:
                self.log('"%s" not in SORT_MODES')
            else:
                self.SORTING = self.SORT_MODES[sort_mode.lower()]

        super(JcpenneyProductsSpider, self).__init__(
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
                meta={'search_term': st, 'remaining': self.quantity, "proxy": ip}
            )

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod, "proxy": ip})

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        prod = response.meta['product']
        prod['url'] = response.url

        jp = JcpenneyVariants()
        jp.setupSC(response)
        prod['variants'] = jp._variants()

        cond_set_value(prod, 'locale', 'en-US')
        self._populate_from_html(response, prod)

        product_id = is_empty(re.findall('ppId=([a-zA-Z0-9]+)&{0,1}', response.url))

        new_meta = response.meta.copy()
        new_meta['product'] = prod
        new_meta["proxy"] = ip
        if product_id:
            new_meta['product_id'] = product_id

        review_id = is_empty(response.xpath(
            '//script/text()[contains(.,"reviewId")]'
        ).re('reviewId:\"(\d+)\",'))
        if review_id:
            return Request(self.url_formatter.format(self.REVIEW_URL,
                                                     product_id=review_id),
                           meta=new_meta, callback=self._parse_reviews,
                           dont_filter=True)
        elif product_id:
            print response.url, '!'*40
            return Request(self.url_formatter.format(self.REVIEW_URL,
                                                     product_id=product_id),
                           meta=new_meta, callback=self._parse_reviews,
                           dont_filter=True)
        return prod

    def _populate_from_html(self, response, product):
        if 'title' in product and product['title'] == '':
            del product['title']
        cond_set(product,
                 'title',
                 response.xpath(
                     '//h1[@itemprop="name"]/text()'
                 ).extract(),
                 conv=string.strip)

        cond_set(
            product,
            'description',
            response.xpath('//div[@itemprop="description"]').extract(),
            conv=string.strip
        )

        image_url = is_empty(
            response.xpath(
                '//div[@id="izView"]/noscript/img/@src'
            ).extract())

        if image_url:
            cond_set_value(
                product,
                'image_url',
                'http:' + image_url
            )

        json_data = is_empty(
            response.xpath('//script').re('jcpPPJSON\s?=\s?({.*});'))

        if json_data:
            data = json.loads(json_data)
            brand = is_empty(is_empty(data['products'])['lots'])['brandName']
            cond_set_value(
                product,
                'brand',
                brand
            )

        price = is_empty(response.xpath(
            '//span[@itemprop="price"]/a/text() |'
            '//span[@itemprop="price"]/text() '
        ).re("\d+.?\d{0,2}"))

        if price:
            product['price'] = Price(price=price, priceCurrency='USD')
        else:
            product['price'] = Price(price='0.0', priceCurrency='USD')

    def _parse_related_products(self, response):
        product = response.meta['product']
        product_id = response.meta.get('product_id')
        text = is_empty(re.findall('html:\'(.*)\'}', response.body))
        if text:
            html = Selector(text=text)
            also_browsed = is_empty(
                html.xpath(
                    '//div[@class="grid_14 saled_view flt_rgt"]'
                    '/div/p/strong/text()').extract())

            related = []
            related_products = {}
            for sel in html.xpath(''
                                  '//div[@class="grid_14 saled_view flt_rgt"]'
                                  '/div/ul/li/a'):
                url = is_empty(sel.xpath('@href').extract())
                if url:
                    related.append(
                        RelatedProduct(
                            title=is_empty(sel.xpath(
                                './div[@class="ftProductDesc"]/text()'
                            ).extract()),
                            url=urllib.unquote('http'+url.split('http')[-1])
                        ))
            if len(related) > 0:
                related_products[also_browsed] = related
                product['related_products'] = related_products

            also_bought = is_empty(
                html.xpath(
                    '//div[@class="grid_1 saled_view flt_rgt"]'
                    '/div/p/strong/text()').extract())

            related = []
            related_products = {}
            for sel in html.xpath(''
                                  '//div[@class="grid_1 saled_view flt_rgt"]'
                                  '/div/ul/li/a'):
                url = is_empty(sel.xpath('@href').extract())
                if url:
                    related.append(
                        RelatedProduct(
                            title=is_empty(sel.xpath(
                                './div[@class="ftProductDesc"]/text()'
                            ).extract()),
                            url=urllib.unquote('http'+url.split('http')[-1])
                        ))
            if len(related) > 0:
                if 'related_products' in product:
                    product['related_products'][also_bought] = related
                else:
                    related_products[also_bought] = related
                    product['related_products'] = related_products

        return product

    def _parse_reviews(self, response):
        product = response.meta['product']
        product_id = response.meta.get('product_id')
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
                    product['buyer_reviews'] = reviews

        if 'buyer_reviews' not in product:
            cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
        new_meta = response.meta.copy()
        new_meta['product'] = product
        new_meta["proxy"] = ip
        return Request(self.RELATED_URL.format(product_id=product_id),
                       meta=new_meta, callback=self._parse_related_products,
                       dont_filter=True)

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[@class="product_holder"]/div/div/'
            'span[contains(@class, "product_image")]/a/@href'
        ).extract()

        for link in links:
            if 'javascript:void(price)' in link:
                continue
            else:
                yield 'http://www.jcpenney.com'+link, SiteProductItem()

    def _scrape_total_matches(self, response):
        if response.xpath('//div[@class="null_result_holder"]').extract():
            print('Not Found')
            return 0
        else:
            total = is_empty(
                response.xpath(
                    '//div[@class="sorted_items flt_wdt"]/p/text()'
                ).re('of\s?(\d+)'))

            if total:
                total_matches = int(total.replace(',', ''))
            else:
                total_matches = 0
            return total_matches

    def _scrape_next_results_page_link(self, response):
        next_page = response.xpath(
            '//ul[@id="paginationIdTOP"]/li/a/@href'
        ).extract()

        if next_page:
            next_page = 'http://www.jcpenney.com'+next_page[-1]
            return next_page