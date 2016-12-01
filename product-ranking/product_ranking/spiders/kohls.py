# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import re
import json
import urllib

from scrapy.http import Request
from scrapy import Selector
from scrapy.log import WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    _extract_open_graph_metadata, populate_from_open_graph, cond_set
from product_ranking.spiders import cond_set_value
from product_ranking.guess_brand import guess_brand_from_first_words
from spiders_shared_code.kohls_variants import KohlsVariants
from product_ranking.validation import BaseValidator
from product_ranking.validators.kohls_validator import KohlsValidatorSettings

is_empty = lambda x, y="": x[0] if x else y


class KohlsProductsSpider(BaseValidator, BaseProductsSpider):
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

    settings = KohlsValidatorSettings

    # use_proxies = True

    SEARCH_URL = "http://www.kohls.com/search.jsp?N=0&search={search_term}&" \
                 "submit-search=web-regular&S={sort_mode}&PPP=60&WS={start}&exp=c"

    SEARCH_URL_AJAX = "http://www.kohls.com/search.jsp?N=0&search={search_term}&PPP=60&WS=0&srp=e2&ajax=true&gNav=false"

    SORTING = None

    SORT_MODES = {
        'default': '1',
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

    handle_httpstatus_list = [404]

    def __init__(self, sort_mode=None, *args, **kwargs):
        self.start_pos = 0
        #settings.overrides['CRAWLERA_ENABLED'] = True
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
            yield Request(
                self.product_url, self._parse_single_product,
                dont_filter=True, meta={
                    'product': prod,
                    'handle_httpstatus_list': self.handle_httpstatus_list}
            )

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _is_not_found(self, response):
        if response.status == 404:
            return True

    def parse_product(self, response):
        prod = response.meta['product']
        prod['url'] = response.url

        if self._is_not_found(response):
            if response.xpath('//div[@id="content"]/@class')[0].extract() == 'pdp_outofstockproduct':
                prod = response.meta['product']
                prod['title'] = response.xpath('//div[@id="content"]//b/text()')[0].extract()
                prod['is_out_of_stock'] = True
                return prod
            else:
                prod['not_found'] = True
                return prod

        kv = KohlsVariants()
        kv.setupSC(response)
        prod['variants'] = kv._variants()

        reseller_id_regex = "prd-(\d+)"
        reseller_id = re.findall(reseller_id_regex, response.url)
        reseller_id = reseller_id[0] if reseller_id else None
        cond_set_value(prod, 'reseller_id', reseller_id)

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

        metadata = _extract_open_graph_metadata(response)
        cond_set_value(product, 'title', metadata.get('title'))

        populate_from_open_graph(response, product)
        product['title'] = self.parse_title(response)

        # title = response.css('.productTitleName ::text').extract()
        # cond_set(product, 'title', title, conv=string.strip)

        product['description'] = self.parse_description(response)
        # cond_set_value(product, 'description', description)

        if product.get('image_url'):
            product['image_url'] = KohlsProductsSpider._fix_image_url(product['image_url'])

        cond_set(
            product,
            'image_url',
            KohlsProductsSpider._fix_image_url(
                response.xpath('//div[@id="easyzoom_wrap"]/div/a/img/@src').extract()
            )
        )
        if not product.get('variants'):
            try:
                product_info_json = \
                response.xpath("//script[contains(text(), 'var productJsonData = {')]/text()").extract()
                product_info_json = product_info_json[0].strip() if product_info_json else ''
                start_index = product_info_json.find("var productJsonData = ") + len("var productJsonData = ")
                end_index = product_info_json.rfind(";")
                product_info_json = product_info_json[start_index:end_index].strip()
                product_info_json = json.loads(product_info_json)
                upc = product_info_json.get('productItem').get('skuDetails')[0].get('skuUpcCode')
            except:
                upc = None
            product['upc'] = upc

        self._set_price(response, product)

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

        brand = response.xpath('//meta[@itemprop="brand"]/@content').extract()
        if brand:
            product['brand'] = brand[0].strip()
        else:
            brand = is_empty(response.xpath(
                '//h1[contains(@class, "title")]/text()'
            ).extract())
            cond_set(
                product,
                'brand',
                (guess_brand_from_first_words(brand.strip()),2)
            )

    def parse_title(self, response):
        title = is_empty(response.xpath(
            '//h1[@class="title productTitleName"]/text() | '
            '//h1[@class="title"]/text() | //title/text()').extract())

        return title

    def parse_description(self, response):
        try:
            product_info_json = \
                response.xpath("//script[contains(text(), 'var productJsonData = {')]/text()").extract()
            product_info_json = product_info_json[0].strip() if product_info_json else ''
            start_index = product_info_json.find("var productJsonData = ") + len("var productJsonData = ")
            end_index = product_info_json.rfind(";")
            product_info_json = product_info_json[start_index:end_index].strip()
            product_info_json = json.loads(product_info_json)

            description = product_info_json["productItem"]["accordions"]["productDetails"]["content"]
            search = re.search(r'<(p).*?>(.*?)</\1>.*?', description)
            if search:
                description = search.group(2)
        except:
            description = is_empty(response.xpath(
                '//meta[@name="description"][string-length(@content)>0]/@content').extract())

        return description

    @staticmethod
    def _get_product_json_data(response):
        start = response.body_as_unicode().find('var productJsonData =')
        end = response.body_as_unicode().find('};', start)
        if start < 0 or end < 0:
            return
        product_json_data = response.body_as_unicode()[
                            start+len('var productJsonData ='):end]
        product_json_data = json.loads(product_json_data.strip() + '}')
        return product_json_data

    def _set_price(self, response, product):
        price = response.xpath(
            '//div[@class="multiple-price"]/div[2]/text()[normalize-space()] |'
            '//div[@class="original original-reg"]/text()[normalize-space()] |'
            '//span[@class="price_ammount"]/text()[normalize-space()] |'
            '//div[@class="sale"]/text()[normalize-space()] |'
            '//div[contains(@class, "main_price")]/text()'
        ).re("\d+.?\d{0,2}")
        if not price:
            price = response.xpath(
                '//*[contains(@class, "price-holder")]'
                '//*[contains(@class, "price_label")]/..//text()').re("\d+.?\d{0,2}")
        if price:
            product['price'] = Price(price=price[0], priceCurrency='USD')
        else:
            price = response.xpath(
                '//meta[contains(@property, "og:product:price:amount")]/@value').extract()
            if price and price[0]:
                product['price'] = Price(price=price[0], priceCurrency='USD')
                return
            price = None
            json_data = self._get_product_json_data(response)
            pricing_info = json_data.get('productItem', {}).get('pricing', {})
            if pricing_info.get('salePrice', ''):
                price = re.search('\$([\d\.]+)', pricing_info.get('salePrice', ''))
            elif pricing_info.get('regularPrice', ''):
                price = re.search('\$([\d\.]+)', pricing_info.get('regularPrice', ''))
            if price:
                price = price.group(1)
                product['price'] = Price(price=price, priceCurrency='USD')
                return
            product['price'] = Price(price='0.0', priceCurrency='USD')

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
                    _original_type_str = False
                    if isinstance(title, str):
                        _original_type_str = True
                        title = title.decode('utf8')
                    title = title.replace(u"\xe9", u"Ã©")\
                        .replace(u"\xf6", "").replace(u"\xb0", "")
                    if _original_type_str:
                        title = title.decode('utf8')
                    related.append(
                        RelatedProduct(
                            title=title,
                            url=urllib.unquote('http'+url.split('http')[-1])
                        ))
            if key and key not in product['related_products'].keys():
                product['related_products'][key] = related
            elif key in product['related_products'].keys():
                product['related_products'][key] += related

        return product

    @staticmethod
    def _fix_image_url(url):
        if isinstance(url, (list, tuple)):
            if not url:
                return
            url = url[0]
        url = url.rstrip('&op_sharpen')
        url = url.replace('wid=130', 'wid=256').replace('hei=130', 'hei=256')
        return url

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
        # V2
        prod_json_data = re.search('pmpSearchJsonData(.*?)</script>', response.body_as_unicode(), re.MULTILINE | re.DOTALL)
        if prod_json_data:
            prod_json_data = prod_json_data.group(1).strip()
            if prod_json_data.startswith('='):
                prod_json_data = prod_json_data[1:].strip()
            if prod_json_data.endswith(';'):
                prod_json_data = prod_json_data[0:-1].strip()
            prod_json_data = json.loads(prod_json_data)
            collected_products = 0
            for product in prod_json_data.get('productInfo', {}).get('productList', []):
                prod_url = product.get('prodSeoURL', None)
                if prod_url:
                    if prod_url.startswith('/'):
                        prod_url = 'http://www.' + self.allowed_domains[0] + prod_url
                    collected_products += 1
                    product = SiteProductItem()
                    new_meta = response.meta.copy()
                    new_meta['product'] = product
                    new_meta['handle_httpstatus_list'] = [404]
                    yield Request(
                        prod_url,
                        callback=self.parse_product,
                        meta=new_meta,
                        errback=self._handle_product_page_error), product
            if collected_products:
                self.per_page = collected_products
                return

        # var pmpSearchJsonData = {
        prod_blocks = response.xpath('//ul[@id="product-matrix"]/li')

        if prod_blocks:
            for block in prod_blocks:
                product = SiteProductItem()

                link = block.xpath('./a/@href').extract()[0]

                cond_set(
                    product,
                    'title',
                    block.xpath('.//div/div/h2/a/text()').extract())

                cond_set(
                    product,
                    'image_url',
                    KohlsProductsSpider._fix_image_url(block.xpath('.//a/img/@src').extract())
                )

                self._set_price(response, product)

                url = 'http://www.kohls.com'+link
                cond_set_value(product, 'url', url)

                new_meta = response.meta.copy()
                new_meta['product'] = product
                new_meta['handle_httpstatus_list'] = [404]

                yield Request(
                    url,
                    callback=self.parse_product,
                    meta=new_meta,
                    errback=self._handle_product_page_error), product
        else:
            prod_urls = re.findall(
                r'"prodSeoURL"\s?:\s+\"(.+)\"',
                response.body_as_unicode()
            )
            for prod_url in prod_urls:
                self.per_page = len(prod_urls)

                product = SiteProductItem()
                new_meta = response.meta.copy()
                new_meta['product'] = product
                new_meta['handle_httpstatus_list'] = [404]

                url = 'http://www.' + self.allowed_domains[0] + prod_url

                yield Request(
                    url,
                    callback=self.parse_product,
                    meta=new_meta,
                    errback=self._handle_product_page_error), product

    def _handle_product_page_error(self, failure):
        self.log('Request failed: %s' % failure.request)
        product = failure.request.meta['product']
        product['locale'] = 'en-US'
        return failure.request.meta['product']

    def _scrape_total_matches(self, response):
        # V2
        count = re.search('productInfo\".*?count\":(.*?,)', response.body, re.MULTILINE)
        if count:
            count = count.group(1).replace(',', '').strip()
            if count and count.isdigit():
                self.total = int(count)
                return self.total
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
                total_matches = is_empty(re.findall(
                    r'"allProducts":\s+\{(?:.|\n)\s+"count":( \d+)',
                    response.body_as_unicode()
                ), 0)

                try:
                    total_matches = int(total_matches)
                except ValueError:
                    total_matches = 0
            self.total = total_matches
            return total_matches

    def _scrape_next_results_page_link(self, response):
        if self.start_pos != self.total:
            self.start_pos += self.per_page

            url = self.SEARCH_URL.format(search_term=self.searchterms[0],
                                         start=self.start_pos,
                                         sort_mode=self.SORTING or '')
            return url
        else:
            return
