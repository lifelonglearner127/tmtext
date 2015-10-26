# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import re
import json
import string
import urllib
import itertools

import requests
from scrapy.http import Request, FormRequest
from scrapy import Selector
from scrapy.log import WARNING


from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults
from product_ranking.validation import BaseValidator
from product_ranking.spiders import cond_set_value
from product_ranking.guess_brand import guess_brand_from_first_words
from spiders_shared_code.jcpenney_variants import JcpenneyVariants, extract_ajax_variants
from product_ranking.validation import BaseValidator


is_empty = lambda x, y="": x[0] if x else y


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
        'benny benassi': 0,
        'water proof': [110, 210],
        'peace': [10, 70],
        'hot': [80, 180],
        'drink': [30, 130],
        'term': [30, 130],
        'tiny': [10, 80],
        'selling': [1, 30],
        'night': [40, 140],
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

    settings = JcpenneyValidatorSettings

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

    dynamic_props = {}
    processed_static_lots = []  # for variants

    @staticmethod
    def remove_old_static_variants_of_lot(variants, current_lot):
        for _x in xrange(10):  # TODO: refactor
            for var_indx, variant in enumerate(variants):
                var_lot = variant.get('properties', {}).get('lot', None)
                if var_lot and var_lot.lower() == current_lot.lower():
                    del variants[var_indx]

    @staticmethod
    def append_new_dynamic_variants(variants, current_lot, new_structure):
        all_pairs = []
        in_stock = []
        for option_name, vals in new_structure.items():
            for val in vals:
                if [option_name][0] != 'in_stock':
                    new_pair = [option_name, val]
                else:
                    in_stock.append([option_name, val])
                if not new_pair in all_pairs:
                    all_pairs.append(new_pair)
        groupped_results = [
            list(g) for k, g in itertools.groupby(all_pairs, lambda val: val[0])
        ]
        combined_results = list(itertools.product(*groupped_results))
        all_properties = []
        for combined_result in combined_results:

            new_pair = {}.copy()
            for prop_name, prop_value in combined_result:
                new_pair[prop_name.lower()] = prop_value
            if not new_pair in all_properties:
                all_properties.append(new_pair)
        for prop in all_properties:
            for k, v in in_stock[0][1].iteritems():
                if k in prop.values():
                    stock = v
            new_variant = {'lot': current_lot, 'price': 'todo', 'in_stock': True if 'true' in stock else False,
                           'selected': False, 'properties': prop}.copy()
            if not new_variant in variants:
                variants.append(new_variant)

    def _ajax_variant_request(self, pp_id, response, variants, variant, variant_num,
                              async=True, null_values=None):

        _props = variant['properties'].copy()
        color = _props.pop('color') if 'color' in _props else None
        neck = _props.pop('neck') if 'neck' in _props else None
        lot = _props.pop('lot') if 'lot' in _props else None
        sleeve = _props.pop('sleeve') if 'sleeve' in _props else None
        size = _props.pop('size') if 'size' in _props else None
        inseam = _props.pop('inseam') if 'inseam' in _props else None
        waist = _props.pop('waist') if 'waist' in _props else None
        chest = _props.pop('chest') if 'chest' in _props else None
        length = _props.pop('length') if 'length' in _props else None
        # check if there are still some keys
        if _props.keys():
            self.log('Error: extra variants found, url %s' % response.url, WARNING)

        _format_args = {}
        _format_args['pp_id'] = pp_id if pp_id else ''
        _format_args['pp_type'] = 'regular'  # TODO: shouldn't this be constant?
        _format_args['lot_value'] = lot if lot else ''
        _format_args['size'] = size if size else ''
        _format_args['waist'] = waist if waist else ''
        _format_args['inseam'] = inseam if inseam else ''
        _format_args['chest'] = chest if chest else ''
        _format_args['length'] = length if length else ''

        if null_values and isinstance(null_values, (list, tuple)):
            for null_value in null_values:
                _format_args[null_value] = ''

        product = response.meta['product']
        attribute_name = re.findall(r'lotSKUAttributes\[\'.*\']=\'\[(\w+)',
                                   response.body_as_unicode())

        # get attribute name
        """
        attribute_name = None
        #if color:
        #    attribute_name = 'COLOR'
        if sleeve:
            attribute_name = 'SLEEVE'
        elif neck:
            attribute_name = 'NECK_SIZE'
        elif lot:
            attribute_name = 'Lot'
        """
        # TODO: moar `attribute_name` values!
        _format_args['color'] = ''
        _format_args['neck'] = neck if neck else ''
        _format_args['sleeve'] = sleeve if sleeve else ''
        _format_args['attribute_name'] = attribute_name[0] \
            if attribute_name else 'Lot'

        size_url = ('http://www.jcpenney.com/jsp/browse/pp/graphical/'
                    'graphicalSKUOptions.jsp?fromEditBag=&fromEditFav=&'
                    'grView=&_dyncharset=UTF-8'
                    '&selectedSKUAttributeName={attribute_name}&'
                    '_D%3AselectedSKUAttributeName=+&'
                    'sucessUrl=%2Fjsp%2Fbrowse%2Fpp%2Fgraphical%'
                    '2FgraphicalSKUOptions.jsp%3FfromEditBag%3D%26fromEditFav%3D%26grView%'
                    '3D&_D%3AsucessUrl=+&ppType=regular&_D%'
                    '3AppType=+&shipToCountry=US&_D%'
                    '3AshipToCountry=+&ppId={pp_id}&_D%'
                    '3AppId=+&selectedLotValue={lot_value}&_D%'
                    '3AselectedLotValue=+&skuSelectionMap.{attribute_name}='
                    '&_D%3AskuSelectionMap.{attribute_name}=+&skuSelectionMap.COLOR='
                    '&_D%3AskuSelectionMap.COLOR=+&_DARGS=%'
                    '2Fdotcom%2Fjsp%2Fbrowse%2Fpp%2Fgraphical%'
                    '2FgraphicalLotSKUSelection.jsp').format(**_format_args)

        if async:
             return Request(
                size_url,
                meta={'pp_id': pp_id, 'product': product, 'post_data': _format_args,
                      'variants': variants, 'variant': variant, 'variant_num': variant_num},
                callback=self._on_variant_response,
             )
        else:
            # perform sync request
            result = requests.get(size_url)

            new_variants_structure = extract_ajax_variants(result.text)
            return lot, new_variants_structure


    def _on_variant_response(self, response):
        variant = response.meta['variant']
        product = response.meta['product']
        result = response.body
        color = variant['properties'].get('color', None)
        if 'function()' in result:
            variant['in_stock'] = None
            return
        try:
            result = json.loads(result)
        except Exception as e:
            self.log('Error loading JSON: %s at URL: %s' % (str(e), response.url), WARNING)
            variant['in_stock'] = None

        # find of such a combination is available
        if color:
            _avail = [a['options'] for a in result['skuOptions'] if a.get('key', None).lower() == 'color']
            if _avail:
                _avail = {k['option']: k['availability'] == 'true' for k in _avail[0]}
                if not color in _avail:

                    variant['in_stock'] = False
                    return  # not defined; availability unknown
                variant['in_stock'] = _avail[color]
        yield product

    def parse_product(self, response):
        prod = response.meta['product']
        prod['url'] = response.url
        prod['_subitem'] = True

        product_id = is_empty(re.findall('ppId=([a-zA-Z0-9]+)&{0,1}', response.url))

        jp = JcpenneyVariants()
        jp.setupSC(response)
        prod['variants'] = jp._variants()
        # perform blocking http request to scrape dynamic structure of variants,
        # otherwise invalid variants get into the output file
        processed_lots = []  # lots for which we collected dynamic variants
        new_lot_structure = {}
        for var_indx, variant in enumerate(prod['variants']):
            if getattr(self, 'scrape_variants_with_extra_requests', None):
                if variant.get('properties', {}).get('lot', '').lower() in processed_lots:
                    continue
                _lot, _dynamic_structure = self._ajax_variant_request(
                    product_id, response, prod['variants'], variant, var_indx,
                    async=False, null_values=['size']
                )
                processed_lots.append(variant.get('properties', {}).get('lot', '').lower())
                new_lot_structure[_lot] = _dynamic_structure
                if _lot:
                    self.remove_old_static_variants_of_lot(prod['variants'], _lot)
                    self.append_new_dynamic_variants(prod['variants'], _lot, _dynamic_structure)

        for var_indx, variant in enumerate(prod['variants']):

            if getattr(self, 'scrape_variants_with_extra_requests', None):
                yield self._ajax_variant_request(
                    product_id, response, prod['variants'], variant, var_indx)

        cond_set_value(prod, 'locale', 'en-US')
        self._populate_from_html(response, prod)

        new_meta = response.meta.copy()
        new_meta['product'] = prod
        if product_id:
            new_meta['product_id'] = product_id

        review_id = is_empty(response.xpath(
            '//script/text()[contains(.,"reviewId")]'
        ).re('reviewId:\"(\d+)\",'))
        if review_id:
            yield Request(self.url_formatter.format(self.REVIEW_URL,
                                                     product_id=review_id),
                           meta=new_meta, callback=self._parse_reviews,
                           dont_filter=True)
        elif product_id:
            yield Request(self.url_formatter.format(self.REVIEW_URL,
                                                     product_id=product_id),
                           meta=new_meta, callback=self._parse_reviews,
                           dont_filter=True)
        yield prod

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
                    dfr = dict({1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
                    dfr.update(distribution)
                    reviews = BuyerReviews(total, avrg, dfr)
                    #reviews = ZERO_REVIEWS_VALUE.update(distribution)
                    product['buyer_reviews'] = reviews

        if 'buyer_reviews' not in product:
            cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
        new_meta = response.meta.copy()
        new_meta['product'] = product
        return Request(self.RELATED_URL.format(product_id=product_id),
                       meta=new_meta, callback=self._parse_related_products)
                       #dont_filter=True)

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