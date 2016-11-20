# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

from itertools import islice
import json
import re
import urllib
import urllib2
import urlparse
import copy
import datetime

import requests
from scrapy import Selector
from scrapy.http import FormRequest, Request
from scrapy.log import DEBUG, INFO

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set_value, populate_from_open_graph
from spiders_shared_code.target_variants import TargetVariants
from product_ranking.validation import BaseValidator
from product_ranking.validators.target_validator import TargetValidatorSettings
from product_ranking.guess_brand import guess_brand_from_first_words

is_empty = lambda x, y=None: x[0] if x else y


class TargetProductSpider(BaseValidator, BaseProductsSpider):
    name = 'target_products'
    allowed_domains = ["target.com", "recs.richrelevance.com",
                       'api.bazaarvoice.com']
    start_urls = ["http://www.target.com/"]

    settings = TargetValidatorSettings

    user_agent_override = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36'

    user_agent_googlebot = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

    # TODO: support new currencies if you're going to scrape target.canada
    #  or any other target.* different from target.com!
    SEARCH_URL = "http://tws.target.com/searchservice/item/search_" \
                 "results/v2/by_keyword?search_term={search_term}&alt=json" \
                 "&pageCount=24&response_group=Items" \
                 "&zone=mobile&offset=0"

    SCRIPT_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js"
    CALL_RR = False
    CALL_RECOMM = True
    POPULATE_VARIANTS = False
    POPULATE_REVIEWS = True
    POPULATE_QA = True
    SORTING = None

    SORT_MODES = {
        "relevance": "relevance",
        "featured": "Featured",
        "pricelow": "PriceLow",
        "pricehigh": "PriceHigh",
        "newest": "newest",
        "bestselling": "bestselling"
    }

    REVIEW_API_PASS = "aqxzr0zot28ympbkxbxqacldq"
    QA_API_PASS = "tr1a5rnjztlsup5cvro29iv8w"

    REVIEW_API_URL = "http://api.bazaarvoice.com/data/batch.json" \
                     "?passkey={apipass}&apiversion=5.5" \
                     "&displaycode=19988-en_us&resource.q0=products" \
                     "&filter.q0=id%3Aeq%3A{model}&stats.q0=reviews" \
                     "&filteredstats.q0=reviews"

    REVIEW_API_URL_V2 = ('http://api.bazaarvoice.com/data/batch.json?passkey=lqa59dzxi6cbspreupvfme30z'
                         '&apiversion=5.4&resource.q0=products&filter.q0=id%3Aeq%3A{tcin}'
                         '&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_US'
                         '&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_US')

    REDSKY_API_URL = 'http://redsky.target.com/v1/pdp/tcin/{}?excludes=taxonomy&storeId={}'

    QUESTION_API_URL = "http://api.bazaarvoice.com/data/questions.json" \
                       "?passkey={apipass}&Offset=0&apiversion=5.4" \
                       "&Filter=Productid:{product_id}" \
                       "&Sort=TotalAnswerCount:desc,HasStaffAnswers:desc"

    ANSWER_API_URL = "http://api.bazaarvoice.com/data/answers.json" \
                     "?passkey={apipass}&apiversion=5.4" \
                     "&Filter=Questionid:{question_id}"

    JSON_SEARCH_URL = "http://tws.target.com/searchservice/item" \
                      "/search_results/v1/by_keyword" \
                      "?callback=getPlpResponse" \
                      "&searchTerm=null" \
                      "&category={category}" \
                      "&sort_by={sort_mode}" \
                      "&pageCount=60" \
                      "&start_results={index}" \
                      "&page={page}" \
                      "&zone=PLP" \
                      "&faceted_value=" \
                      "&view_type=medium" \
                      "&stateData=" \
                      "&response_group=Items" \
                      "&isLeaf=true" \
                      "&parent_category_id={category}"

    RELATED_URL = "{path}?productId={pid}&userId=-1002&min={min}&max={max}&context=placementId," \
                  "{plid};categoryId,{cid}&callback=jsonCallback"

    def __init__(self, sort_mode=None, store='2768', zip_code='94117', *args, **kwargs):
        if sort_mode:
            if sort_mode.lower() not in self.SORT_MODES:
                self.log('"%s" not in SORT_MODES')
            else:
                self.SORTING = self.SORT_MODES[sort_mode.lower()]

        self.zip_code = zip_code
        self.store = store

        super(TargetProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self._start_search,
                      headers={'User-Agent': self.user_agent_override},
                      dont_filter=True)

    def _start_search(self, response):
        for request in super(TargetProductSpider, self).start_requests():
            # request.meta['dont_redirect'] = True
            request.meta['handle_httpstatus_list'] = [302, 301]
            request.meta['search_start'] = True
            request.headers['User-Agent'] = self.user_agent_override
            yield request

    def parse(self, response):
        regexp = re.compile('^http://[\w]*\.target\.com/c/[^/]+/-/([^#]+)')
        category = regexp.search(response.url)

        # New Search
        if "results/v2/by_keyword" in response.url:
            return list(super(TargetProductSpider, self).parse(response))

        if response.meta.get('search_start') and category:
            new_meta = response.meta
            new_meta['search_start'] = False
            new_meta['json'] = True
            category = category.group(1)[2:]
            new_meta['category'] = category
            return Request(
                self.url_formatter.format(self.JSON_SEARCH_URL,
                                          category=category, index=90,
                                          sort_mode=self.SORTING or '',
                                          page=1),
                meta=new_meta,
                headers={'User-Agent': self.user_agent_override})
        return list(super(TargetProductSpider, self).parse(response))

    def _request_reviews_v2(self, product, response):
        response.meta['product'] = product
        yield Request(
            self.REVIEW_API_URL_V2.format(tcin=self._get_tcin(response)),
            meta=response.meta,
            callback=self._parse_reviews,
            dont_filter=True,
            headers={'User-Agent': self.user_agent_override}
        )

    def _get_tcin(self, response):
        if not self._is_v1(response):
            if response.meta['item_info'].get('parentPartNumber'):
                return response.meta['item_info']['parentPartNumber']
            else:
                return self._product_id_v2(response)
        tcin = re.search(u'Online Item #:[^\d]*(\d+)', response.body_as_unicode())
        if tcin:
            return tcin.group(1)
        return self._product_id_v2(response)

    def parse_product(self, response):
        # for some products (with many colors for example) target.com
        # insert at <meta> another url than you see at browser.
        # it used to calculate buyer_reviews correct.
        canonical_url = response.xpath(
            '//meta[@property="og:url"]/@content'
        ).extract()
        prod = response.meta['product']

        response.meta['item_info'] = self._item_info_v2(response)

        response.meta['average'] = is_empty(
            re.findall(r'var averageRating=  (\d+)', response.body_as_unicode()))
        response.meta['total'] = is_empty(
            re.findall(r'var totalReviewsValue=(\d+)', response.body_as_unicode()))

        if 'sorry, that item is no longer available' in response.body_as_unicode().lower() \
                or 'product not available' in response.body_as_unicode().lower():
            prod['not_found'] = True
            return prod

        cond_set_value(prod, 'locale', 'en-US')

        tv = TargetVariants()
        tv.setupSC(response, zip_code=self.zip_code, item_info=response.meta['item_info'])
        # prod['variants'] = tv._variants()
        if not prod.get('upc') and prod.get('variants'):
            selected_upc = [v.get('upc') for v in prod.get('variants') if v.get('selected')]
            prod['upc'] = selected_upc[0] if selected_upc else None

        price = is_empty(response.xpath(
            '//p[contains(@class, "price")]/span/text()').extract())
        if not price:
            price = is_empty(response.xpath(
                '//*[contains(@class, "price")]'
                '/*[contains(@itemprop, "price")]/text()'
            ).extract())
        if price:
            price = is_empty(re.findall("\d+\.{0,1}\d+", price))
            if price:
                prod['price'] = Price(
                    price=price.replace('$', '').replace(',', '').strip(),
                    priceCurrency='USD'
                )

        special_pricing = is_empty(response.xpath(
            '//li[contains(@class, "eyebrow")]//text()').extract())
        if special_pricing == "TEMP PRICE CUT":
            prod['special_pricing'] = True
        else:
            prod['special_pricing'] = False

        if 'url' not in prod:
            prod['url'] = response.url

        old_url = prod['url'].rsplit('#', 1)[0]
        prod['url'] = None
        populate_from_open_graph(response, prod)

        prod['url'] = old_url
        # cond_set_value(prod, 'url', old_url)

        item_info = self._item_info_v3(response)
        self._populate_from_v3(prod, item_info)

        if not self._is_v1(response):
            # scrape v2 reviews
            return self._request_reviews_v2(prod, response)

        if 'title' in prod:
            if isinstance(prod['title'], (list, tuple)):
                prod['title'] = prod['title'][0].strip()

        if not prod.get('brand', None):
            brand = guess_brand_from_first_words(prod['title'])
            if brand:
                prod['brand'] = brand

            else:
                # Check last part of the title
                brand = guess_brand_from_first_words(
                    prod['title'].split('-')[-1])
                if brand:
                    prod['brand'] = brand
                elif 'brand' in prod:
                    prod['brand'] = 'No brand'
                else:
                    prod['brand'] = 'No brand for single result'

        payload = self._extract_rr_parms(response)

        collection_items = response.xpath('//div[@id="CollectionItems"]//h3/a')
        # assume that product from collection
        if collection_items:
            self._populate_collection_items(response, prod)

        if self.CALL_RECOMM:
            rurls = self._extract_recomm_urls(response)
            if rurls:
                new_meta = response.meta.copy()
                new_meta['rurls'] = rurls[1:]
                new_meta['canonical_url'] = canonical_url
                return Request(
                    rurls[0],
                    self._parse_recomm_json,
                    meta=new_meta,
                    headers={'User-Agent': self.user_agent_override})

        if self.CALL_RR:
            if payload:
                new_meta = response.meta.copy()
                new_meta['canonical_url'] = canonical_url
                rr_url = urlparse.urljoin(self.SCRIPT_URL,
                                          "?" + urllib.urlencode(payload))
                return Request(
                    rr_url,
                    self._parse_rr_json,
                    meta=new_meta,
                    headers={'User-Agent': self.user_agent_override})
            else:
                self.log("No {rr} payload at %s" % response.url, DEBUG)
        if self.POPULATE_QA:
            response.meta['canonical_url'] = canonical_url
            return self._request_QA(response, prod)
        if self.POPULATE_REVIEWS:
            return self._request_reviews(response, prod, canonical_url)
        else:
            return prod

    @staticmethod
    def _scrape_title_v1(response):
        title = response.xpath(
            "//h2[contains(@class,'product-name')]"
            "/span[@itemprop='name']/text()"
            "|//h2[contains(@class,'collection-name')]"
            "/span[@itemprop='name']/text()"
        ).extract()
        if title:
            return title[0].strip()

    def _is_v1(self, response):
        is_v1 = bool(self._scrape_title_v1(response))
        if is_v1:
            self.log('Scraping V1')
            print('Scraping V1')
        else:
            self.log('Scraping V2')
            print('Scraping V2')
        return is_v1

    @staticmethod
    def _product_id_v2(response_or_url):
        if not isinstance(response_or_url, (str, unicode)):
            response_or_url = response_or_url.url
        # else get it from the url
        _id = re.search('A-(\d+)', response_or_url)
        if _id:
            return _id.group(1)

    def _item_info_helper(self, partNumber):
        response = requests.get(
            'http://tws.target.com/productservice/services/item_service/v1/by_itemid?id='
            + partNumber + '&alt=json&callback=itemInfoCallback&_=1464382778193',
            headers={'User-Agent': self.user_agent_googlebot}).content

        item_info = re.match('itemInfoCallback\((.*)\)$', response, re.DOTALL)
        try:
            item_info = item_info.group(1) if item_info else None
            return json.loads(item_info)['CatalogEntryView'][0]
        except Exception:
            return {}

    def _item_info_v2(self, response):
        item_info = self._item_info_helper(self._product_id_v2(response))

        if item_info.get('parentPartNumber') \
                and item_info['parentPartNumber'] != self._product_id_v2(response):
            item_info = self._item_info_helper(item_info['parentPartNumber'])

        return item_info

    def _item_info_v3_request(self, tcin):
        content = requests.get(
            self.REDSKY_API_URL.format(tcin, self.store)
        ).content
        return content

    def _item_info_v3(self, response, tcin=None):
        if not tcin:
            tcin = self._get_tcin(response)
        content = self._item_info_v3_request(tcin)
        content_json = json.loads(content)
        parent_tcin = content_json.get('product').get('item').get('parent_items', None)
        if isinstance(parent_tcin, unicode):
            return self._item_info_v3(response, parent_tcin)
        else:
            return content_json.get('product', None)

    @staticmethod
    def _item_info_v3_image(image_info):
        base_url = image_info.get('base_url')
        image_id = image_info.get('primary')
        return base_url + image_id

    @staticmethod
    def _item_info_v3_price(amount, currency='USD'):
        return Price(priceCurrency=currency, price=amount)

    @staticmethod
    def _item_info_v3_price_helper(item):
        amount = item.get(
            'price').get('offerPrice').get(
            'formattedPrice', '').replace('$', '').replace(',', '')
        if not amount or 'see low price in cart' in amount:
            amount = item.get(
                'price').get('offerPrice').get('price')
        try:
            return float(amount)
        except ValueError:
            return 0

    @staticmethod
    def _item_info_v3_store_only(item):
        try:
            return item.get('available_to_promise_network').get(
                'availability') == 'UNAVAILABLE' and item.get(
                'available_to_promise_store').get('products')[0].get(
                'availability') == 'AVAILABLE'
        except TypeError:
            return False

    @staticmethod
    def _item_info_v3_reviews(item_info):
        tcin = item_info.get('item').get('tcin')
        rating_review = item_info.get(
            'rating_and_review_statistics', {}).get('result', {}).get(tcin, {}).get('coreStats', {})
        average_rating = rating_review.get('AverageOverallRating', 0)
        num_of_reviews = rating_review.get('TotalReviewCount', 0)
        rating_distribution = rating_review.get('RatingDistribution', [])
        rating_by_star = {i: 0 for i in range(1, 6)}
        rating_new = {i.get('RatingValue'): i.get('Count') for i in rating_distribution}
        rating_by_star.update(rating_new)
        reviews = BuyerReviews(int(num_of_reviews), float(average_rating), rating_by_star)
        return reviews

    @staticmethod
    def _item_info_v3_availability(item):
        return item.get('available_to_promise_network').get(
            'availability') != 'UNAVAILABLE'

    def _item_info_v3_variants(self, item_info):
        items = item_info.get('item').get('child_items', [])
        variants = []
        for number, item in enumerate(items):
            selected = not bool(number)
            variant = self._item_info_v3_variant(item, selected)
            variants.append(variant)
        return variants

    def _item_info_v3_variant(self, item, selected):
        variant = {}
        variant['selected'] = selected
        variant['dpci'] = item.get('dpci')
        variant['tcin'] = item.get('tcin')
        variant['upc'] = item.get('upc')
        variant['properties'] = {}
        properties = item.get('variation', [])
        for attribute in properties:
            variant['properties'][attribute] = properties.get(attribute)
        variant['price'] = self._item_info_v3_price_helper(item)
        image_info = item.get('enrichment').get('images')[0]
        variant['image_url'] = self._item_info_v3_image(image_info)
        in_stock = item.get('available_to_promise_network').get(
            'availability') != 'UNAVAILABLE'
        variant['is_in_store_only'] = self._item_info_v3_store_only(item)
        variant['in_stock'] = in_stock or variant['is_in_store_only']
        return variant

    def _populate_from_v3(self, product, item_info):
        item = item_info.get('item')
        if not 'Unauthorized' in item.get('message', '') and not 'Forbidden' in item.get('message', ''):
            product['title'] = item.get('product_description').get('title')
            product['tcin'] = item.get('tcin')
            product['description'] = item.get('product_description').get('downstream_description', '')
            product['brand'] = item.get('product_brand').get('manufacturer_brand')
            product['buyer_reviews'] = self._item_info_v3_reviews(item_info)
            variants = self._item_info_v3_variants(item_info)
            if variants:
                product['variants'] = variants
            product['origin'] = item.get('country_of_origin')
            try:
                selected_variant = product.get('variants', [])[0]
                product['image_url'] = selected_variant.get('image_url')
                amount = selected_variant.get('price')
                amount = float(amount) if amount else None
                product['price'] = self._item_info_v3_price(amount)
                product['dpci'] = selected_variant.get('dpci')
                product['upc'] = selected_variant.get('upc')
                product['image_url'] = selected_variant.get('image_url')
                product['is_out_of_stock'] = False if selected_variant.get('in_stock') else True
                product['no_longer_available'] = product['is_out_of_stock']
                product['is_in_store_only'] = selected_variant.get('is_in_store_only')
            except IndexError:
                amount = self._item_info_v3_price_helper(item_info)
                product['price'] = self._item_info_v3_price(amount)
                product['dpci'] = item.get('dpci')
                product['upc'] = item.get('upc')
                image_info = item.get('enrichment').get('images')[0]
                product['image_url'] = self._item_info_v3_image(image_info)
                product['is_out_of_stock'] = False if self._item_info_v3_availability(
                    item_info) else True
                product['no_longer_available'] = product['is_out_of_stock']
                product['is_in_store_only'] = self._item_info_v3_store_only(item_info)
        else:
            product['not_found'] = True
            product['no_longer_available'] = True

    @staticmethod
    def _get_price_v2(item_info):
        """ Returns (price, in cart) """
        in_cart = False
        offer = item_info.get('Offers', [{}])[0].get('OfferPrice', [{}])[0]
        try:
            if 'low to display' in offer['formattedPriceValue'].lower():
                # in-cart pricing
                offer = item_info.get('Offers', [{}])[0].get('OriginalPrice', [{}])[0]
                in_cart = True
        except:
            pass
        price = Price(
            priceCurrency=offer['currencyCode'],
            price=offer['formattedPriceValue'].split(' -', 1)[0].replace('$', ''))
        return price, in_cart

    def _extract_recomm_urls(self, response):
        script = response.xpath(
            "//script[contains(text(),'var recommendationConfig')]"
            "/text()").re("var recommendationConfig = {(.*)};")
        if script:
            script = script[0]
        try:
            jsdata = json.loads("{" + script + "}")
        except (ValueError, TypeError):
            urls = []
            # self.log
            return urls
        urls = []
        for name in jsdata['components']:
            item = jsdata['components'][name]
            url = self.RELATED_URL.format(
                path=jsdata['serviceHostName'],
                pid=item['productId'],
                min=item['min'],
                max=item['max'],
                plid=item['placementName'],
                cid=item['categoryId'])
            urls.append(url)
        return urls

    def _extract_rr_parms(self, response):
        rscript = response.xpath(
            "//script[contains(text(),'R3_COMMON')]").extract()
        if rscript:
            rscript = rscript[0]
        else:
            self.log(
                "No {rr} scrtipt with R3_COMMON at %s" % response.url, DEBUG)
            return
        m = re.match(r".*R3_COMMON\.setApiKey\('(\S*)'\);", rscript,
                     re.DOTALL)
        if m:
            apikey = m.group(1)
        else:
            self.log("No {rr} apikey at %s" % response.url, DEBUG)
            return
        m = re.match(r".*R3_ITEM\.setId\('(\S*)'\);", rscript, re.DOTALL)
        if m:
            productid = m.group(1)
        else:
            self.log("No {rr} productid at %s" % response.url, DEBUG)
            return

        param = response.xpath("//div[@id='param']/text()").extract()
        if param:
            param = param[0].strip()
            try:
                param = json.loads(param)
            except ValueError:
                self.log("No {rr} param json 1 at %s" % response.url, DEBUG)
                return
        else:
            self.log("No {rr} param json 2 at %s" % response.url, DEBUG)
            return

        pt = [k for k in param.keys() if k.startswith('placementType')]
        pt.sort()
        pt = [param[k] for k in pt]
        pt.append('item_page.pdp_siteskin_1')
        pt = "".join("|" + x for x in pt)

        chi = "|" + param['RRCategoryId']

        m = re.match(
            r".*R3_COMMON\.addContext\(([^\)]*)\);", rscript, re.DOTALL)
        if m:
            cntx = m.group(1)
            try:
                jcntx = json.loads(cntx)
            except ValueError as e:
                self.log("{rr} Json error %s" % e, DEBUG)
                return
            k = jcntx.keys()[0]
            v = jcntx[k]
            rcntx = ""
            for k1, v1 in v.items():
                rcntx += (k1 + ":" + v1)
        else:
            self.log("No {rr} addContent at %s" % response.url, DEBUG)
            return

        payload = {"a": apikey,
                   "p": productid,
                   "pt": urllib.quote(pt),
                   "u": '2262401509',
                   "s": '2262401509',
                   "sgs": "|2:no redcard",
                   "cts": "http://www.target.com",
                   "chi": urllib.quote(chi),
                   "pageAttribute": urllib.quote(rcntx),
                   "flv": "15.0.0",
                   "l": 1}
        return payload

    def _parse_recomm_json(self, response):
        product = response.meta['product']
        text = response.body_as_unicode()
        rurls = response.meta['rurls']

        jm = re.search(r"jsonCallback\((.*)},", text)
        rels = []
        if jm:
            jtext = jm.group(1)
            jtext += "}"
            try:
                jdata = json.loads(jtext)
            except ValueError:
                jdata = {}
            rlist = jdata.get('recommendations', [])
            for ritem in rlist:
                title = ritem['productTitle']
                href = ritem['productLink']
                rels.append(RelatedProduct(title, href))

            related = product.get('related_products', {})
            rel_recom = related.get('recommended', [])
            rel_recom.extend(rels)
            product['related_products'] = {"recommended": rel_recom}

        if rurls:
            url = rurls[0]
            rurls = rurls[1:]
            print "url=", url, "rurls=", rurls

            new_meta = response.meta.copy()
            new_meta['rurls'] = rurls
            return Request(
                url,
                self._parse_recomm_json,
                meta=new_meta,
                headers={'User-Agent': self.user_agent_override})

        if self.POPULATE_QA:
            return self._request_QA(response, product)

        if self.POPULATE_REVIEWS:
            canonical_url = response.meta['canonical_url']
            return self._request_reviews(response, product, canonical_url)
        else:
            return product

    def _parse_rr_json(self, response):
        product = response.meta['product']
        text = response.body_as_unicode()
        pattern = re.compile(
            "jsonObj = {([^}]*)};\s+RR\.TGT\.fixAndPushJSON\(([^)]*)\);")
        mlist = re.findall(pattern, text)
        if mlist:
            results = {}
            for m in mlist:
                if len(m) > 1:
                    try:
                        answ = "{" + m[0] + "}"
                        jsdata = json.loads(answ)

                        title = jsdata['productTitle']
                        link = jsdata['productLink']

                        url_split = urlparse.urlsplit(link)
                        query = urlparse.parse_qs(url_split.query)
                        original_url = query.get('ct')
                        ctlink = urllib2.unquote(original_url[0])

                        data = m[1].split(",")
                        chan = data[1]
                        if chan not in results:
                            results[chan] = []
                        rlist = results[chan]
                        rlist.append((title, ctlink))
                    except (ValueError, KeyError, IndexError) as e:
                        self.log(
                            "{rr} json response parse error %s" % e, DEBUG)

            def make_product_list(mlist):
                mitems = []
                for mname, mlink in mlist:
                    mitems.append(RelatedProduct(mname, mlink))
                return mitems

            rlist = results.get('0', [])
            ritems = make_product_list(rlist)
            rlist = results.get('1', [])
            obitems = make_product_list(rlist)

            product['related_products'] = {"recommended": ritems,
                                           "buyers_also_bought": obitems}
        if self.POPULATE_QA:
            return self._request_QA(response, product)

        if self.POPULATE_REVIEWS:
            canonical_url = response.meta['canonical_url']
            return self._request_reviews(response, product, canonical_url)
        else:
            return product

    def _extract_links_with_brand(self, containers):
        bi_list = []
        for ci in containers:
            link = ci.xpath(
                "*[@class='productClick productTitle']/@href").extract()
            if link:
                link = link[0]
            else:
                self.log("no product link in %s" % ci.extract(), DEBUG)
                continue
            brand = ci.xpath(
                "*//a[contains(@class,'productBrand')]/text()").extract()
            if brand:
                brand = brand[0]
            else:
                brand = ""
            isonline = ci.xpath(
                "../div[@class='rating-online-cont']"
                "/div[@class='onlinestorecontainer']"
                "/div/p/text()").extract()
            if isonline:
                isonline = isonline[0].strip()

            # TODO: isonline: u'out of stock online'
            # ==  'out of stock' & 'online'
            price = ci.xpath(
                './div[@class="pricecontainer"]/p/text()').re(FLOATING_POINT_RGEX)
            if price:
                price = price[0]
            else:
                price = ci.xpath(
                    './div[@class="pricecontainer"]/span[@class="map"]/following::p/span/text()') \
                    .re(FLOATING_POINT_RGEX)
                if price:
                    price = price[0]

            bi_list.append((brand, link, isonline, price))
        return bi_list

    def _is_search_v2(self, response):
        return "search_results/v2/by_keyword" in response.url

    def _scrape_product_links(self, response):
        if response.meta.get('json'):
            return list(self._scrape_product_links_json(response))

        elif self._is_search_v2(response):
            return list(self._scrape_product_links_json_2(response))

        else:
            return list(self._scrape_product_links_html(response))

    def _scrape_product_links_json_2(self, response):
        data = json.loads(response.body)
        for item in data['searchResponse']['items']['Item']:
            url = item['productDetailPageURL']
            url = urlparse.urljoin('http://www.target.com', url)
            product = SiteProductItem()
            attrs = item.get('itemAttributes', {})
            cond_set_value(product, 'title', attrs.get('title'))
            cond_set_value(product, 'brand',
                           attrs.get('productManufacturerBrand'))

            p = item.get('priceSummary', {})
            priceattr = p.get('offerPrice', p.get('listPrice'))
            if priceattr:
                currency = priceattr['currencyCode']
                amount = priceattr['amount']
                if amount == 'Too low to display' or 'see store for price':
                    price = None
                else:
                    amount = is_empty(re.findall(
                        '\d+\.{0,1}\d+', priceattr['amount']
                    ))
                    price = Price(priceCurrency=currency, price=amount)
                cond_set_value(product, 'price', price)
            new_meta = copy.deepcopy(response.meta)
            new_meta['product'] = product
            yield (Request(url, callback=self.parse_product, meta=new_meta,
                           headers={'User-Agent': self.user_agent_override}),
                   product)

    def _scrape_product_links_json(self, response):
        for item in self._get_json_data(response)['items']['Item']:
            url = item['productDetailPageURL']
            url = urlparse.urljoin('http://www.target.com', url)
            product = SiteProductItem()
            attrs = item.get('itemAttributes', {})
            cond_set_value(product, 'title', attrs.get('title'))
            cond_set_value(product, 'brand',
                           attrs.get('productManufacturerBrand'))
            p = item.get('priceSummary', {})
            priceattr = p.get('offerPrice', p.get('listPrice'))
            if priceattr:
                currency = priceattr['currencyCode']
                amount = priceattr['amount']
                if amount == 'Too low to display':
                    price = None
                else:
                    amount = is_empty(re.findall(
                        '\d+\.{0, 1}\d+', priceattr['amount']
                    ))
                    price = Price(priceCurrency=currency, price=amount)
                cond_set_value(product, 'price', price)
            new_meta = copy.deepcopy(response.meta)
            new_meta['product'] = product
            yield (Request(url, callback=self.parse_product, meta=new_meta,
                           headers={'User-Agent': self.user_agent_override}),
                   product)

    def _scrape_product_links_html(self, response):
        sterm = response.xpath(
            "//div[@id='searchMessagingHeader']/h2/span"
            "/span[@class='srhTerm']/text()").extract()
        if sterm:
            sterm = sterm[0]
            if sterm != response.meta['search_term']:
                self.log("Search '%s' but site returns data for '%s'." % (
                    response.meta['search_term'], sterm), INFO)
                return
        containers = response.xpath("//li/form/div[@class='tileInfo']")
        if not containers:
            nolinks = response.css(
                "#searchMessagingHeader > h2 > span "
                "> span.srhCount::text").extract()
            if nolinks:
                nolinks = nolinks[0]
                if nolinks == u'no\xa0results\xa0found':
                    self.log("No results found.", DEBUG)
                    return
            self.log("Try again after 1-3 min.", DEBUG)
            return

        bi_list = self._extract_links_with_brand(containers)

        if not bi_list:
            self.log("Found no product links.", DEBUG)
        if self.SORTING:
            next_page = ("Nao=0&sortBy={0}&searchTerm={1}&category=0|All|" +
                         "matchallpartial|all categories" +
                         "&lnk=snav_sbox_catnip&viewType=medium").format(
                self.SORTING, response.meta['search_term'])
            post_req = self._gen_next_request(response, next_page)
            new_meta = post_req.meta.copy()
            new_meta['json'] = True
            post_req = post_req.replace(meta=new_meta)
            yield post_req, SiteProductItem()
            return

        for brand, link, isonline, price in bi_list:
            product = SiteProductItem(brand=brand)

            product['is_out_of_stock'] = False
            if "out of stock" in isonline:
                product['is_out_of_stock'] = True

            product['is_in_store_only'] = False
            if 'in stores only' in isonline:
                product['is_in_store_only'] = True
            if price:
                product['price'] = Price(price=price, priceCurrency='USD')

            # FIXME: 'online_only' status
            # if 'online only' in isonline:
            #     product['???'] = True
            yield link, product

    def _get_json_data(self, response):
        data = re.search('getPlpResponse\((.+)\)', response.body_as_unicode())
        try:
            if data is not None:
                data = json.loads(data.group(1))
            else:
                data = json.loads(response.body_as_unicode())
        except (ValueError, TypeError, AttributeError):
            self.log('JSON response expected.')
            return
        return data['searchResponse']

    def _scrape_total_matches(self, response):
        if response.meta.get('json'):
            return self._scrape_total_matches_json(response)

        elif self._is_search_v2(response):
            return self._scrape_total_matches_json_2(response)

        else:
            return self._scrape_total_matches_html(response)

    def _json_get_args(self, data):
        args = {d['name']: d['value'] for d in
                data['searchState']['Arguments']['Argument']}
        return args

    def _scrape_total_matches_json_2(self, response):
        data = json.loads(response.body)
        args = self._json_get_args(data['searchResponse'])
        if not 'prodCount' in data['searchResponse']:
            return 0
        return int(args.get('prodCount'))

    def _scrape_total_matches_json(self, response):
        data = self._get_json_data(response)
        return int(self._json_get_args(data)['prodCount'])

    def _scrape_total_matches_html(self, response):
        str_results = response.xpath(
            "//div[@id='searchMessagingHeader']/h2"
            "/span/span[@class='srhCount']/text()")

        num_results = str_results.re('(\d+)\s+result')
        if num_results:
            try:
                return int(num_results[0])
            except ValueError:
                self.log(
                    "Failed to parse total number of matches: %r"
                    % num_results[0],
                    DEBUG
                )
                return None
        else:
            if any('related' in f or u'no\xa0results\xa0found' in f
                   for f in str_results.extract()):
                return 0

        self.log("Failed to parse total number of matches.", DEBUG)
        return None

    def _gen_next_request(self, response, next_page, remaining=None):
        next_page = urllib.unquote(next_page)
        data = {'formData': next_page,
                'stateData': "",
                'isDLP': 'false',
                'response_group': 'Items'
                }

        new_meta = response.meta.copy()
        if 'total_matches' not in new_meta:
            new_meta['total_matches'] = self._scrape_total_matches(response)
        if remaining and remaining > 0:
            new_meta['remaining'] = remaining
        post_url = "http://www.target.com/SoftRefreshProductListView"
        # new_meta['json'] = True

        return FormRequest(
            # return FormRequest.from_response(
            # response=response,
            url=post_url,
            method='POST',
            formdata=data,
            callback=self._parse_link_post,
            meta=new_meta,
            headers={'User-Agent': self.user_agent_override})

    def _parse_link_post(self, response):
        jsdata = json.loads(response.body)
        pagination1 = jsdata['productListArea']['pagination1']
        sel = Selector(text=pagination1.encode('utf-8'))

        next_page = sel.xpath(
            "//div[@id='pagination1']/div[@class='col2']"
            "/ul[@class='pagination1']/li[@class='next']/a/@href").extract()

        requests = []

        remaining = response.meta.get('remaining')
        plf = jsdata['productListArea']['productListForm']

        sel = Selector(text=plf.encode('utf-8'))
        containers = sel.xpath("//div[@class='tileInfo']")

        links = self._extract_links_with_brand(containers)

        if next_page:
            next_page = next_page[0]
            new_remaining = remaining - len(links)
            if new_remaining > 0:
                requests.append(self._gen_next_request(
                    response, next_page, remaining=new_remaining))

        for i, (brand, url, isonline, price) in enumerate(islice(links, 0, remaining)):
            new_meta = response.meta.copy()
            product = SiteProductItem(brand=brand)
            product['search_term'] = response.meta.get('search_term')
            product['site'] = self.site_name
            product['total_matches'] = response.meta.get('total_matches')
            product['results_per_page'] = len(links)
            product['url'] = url
            if isonline == 'out of stock':
                product['is_out_of_stock'] = True

            # The ranking is the position in this page plus the number of
            # products from other pages.
            ranking = (i + 1) + (self.quantity - remaining)
            product['ranking'] = ranking
            new_meta['product'] = product
            requests.append(Request(
                url,
                callback=self.parse_product,
                meta=new_meta, dont_filter=True,
                headers={'User-Agent': self.user_agent_override}), )
        return requests

    def _scrape_next_results_page_link(self, response):
        if self.SORTING is not None and response.meta.get('search_start'):
            return
        if response.meta.get('json'):
            return self._scrape_next_results_page_link_json(response)
        elif self._is_search_v2(response):
            return self._scrape_next_results_page_link_json_2(response)
        else:
            return self._scrape_next_results_page_link_html(response)

    def _scrape_next_results_page_link_json_2(self, response):
        data = json.loads(response.body)
        args = self._json_get_args(data['searchResponse'])
        next_offset = (int(args.get('currentPage', 0))) * int(args.get('resultsPerPage', 0))
        search_term = args['keyword']
        url = self.SEARCH_URL.format(
            search_term=search_term).replace('offset=0', 'offset=%d' % next_offset)
        return Request(url, meta=response.meta, headers={'User-Agent': self.user_agent_override})

    def _scrape_next_results_page_link_json(self, response):
        # raw_input(len(list(self._scrape_product_links_json(response))))
        args = self._json_get_args(self._get_json_data(response))
        current = int(args['currentPage'])
        total = int(args['totalPages'])
        per_page = int(args['resultsPerPage'])
        if current <= total:
            sort_mode = self.SORTING or ''
            category = response.meta['category']
            new_meta = response.meta.copy()
            url = self.url_formatter.format(self.JSON_SEARCH_URL,
                                            sort_mode=sort_mode,
                                            index=per_page * current,
                                            page=current + 1,
                                            category=response.meta['category'])
            return Request(url, meta=new_meta, headers={'User-Agent': self.user_agent_override})

    def _scrape_next_results_page_link_html(self, response):
        next_page = response.xpath(
            "//div[@id='pagination1']/div[@class='col2']"
            "/ul[@class='pagination1']/li[@class='next']/a/@href |"
            "//li[contains(@class, 'pagination--next')]/a/@href"
        ).extract()
        if next_page:
            search = "?searchTerm=%s" % self.searchterms[0].replace(" ", "+")
            if search in next_page[0] and "page=" in next_page[0]:
                return next_page[0]
            next_page = next_page[0]
            return self._gen_next_request(response, next_page)

    def _request_reviews(self, response, product, canonical_url=None):
        return self._request_reviews_v2(product, response)
        """
        if canonical_url:
            main_url = canonical_url[0]
        else:
            main_url = product['url']
        if self._is_v1(response):
            prod_id = re.search('\d+\Z', main_url)
            prod_id = prod_id.group()
        else:
            prod_id = self._product_id_v2(product['url'])
        if prod_id:
            url = self.REVIEW_API_URL.format(apipass=self.REVIEW_API_PASS,
                                             model=prod_id)
            return Request(url, self._parse_reviews, meta=response.meta, dont_filter=True,
                           headers={'User-Agent': self.user_agent_override})
        else:
            return product
        """

    def _parse_reviews(self, response):
        product = response.meta['product']
        data = json.loads(response.body_as_unicode())
        data = data.get('BatchedResults', {}).get('q0', {})
        data = (data.get('Results') or [{}])[0]
        data = data.get('FilteredReviewStatistics', {})
        average = data.get('AverageOverallRating')
        total = data.get('TotalReviewCount')
        # import pdb; pdb.set_trace()
        if not average:
            average = response.meta['average']
            total = response.meta['total']
            if average == '0':
                cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
            else:
                fdist = ZERO_REVIEWS_VALUE[-1]
                if total is None or average is None:
                    # product['buyer_reviews'] = ZERO_REVIEWS_VALUE
                    return product
                reviews = BuyerReviews(int(total), int(average), fdist)
                cond_set_value(product, 'buyer_reviews', reviews)
        if average and total:
            distribution = {d['RatingValue']: d['Count']
                            for d in data.get('RatingDistribution', [])}
            fdist = {i: 0 for i in range(1, 6)}
            for i in range(1, 6):
                if i in distribution:
                    fdist[i] = distribution[i]
            reviews = BuyerReviews(total, average, fdist)
            cond_set_value(product, 'buyer_reviews', reviews)
        return product

    def _populate_collection_items(self, response, prod):
        collection_items = response.xpath('//div[@id="CollectionItems"]//h3/a')
        rp = []
        for item in collection_items:
            link = item.xpath('@href').extract()
            if link:
                link = 'http://www.target.com' + link[0]
            name = item.xpath('text()').extract()
            if name and link:
                rp.append(RelatedProduct(name[0].strip(), link))
        prod['related_products'] = {'recommended': rp}

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _request_QA(self, response, product):
        product_id = re.search('\d+\w', response.url)
        if not product_id:
            product_id = re.search('\d+\Z', product['url'])
        if product_id:
            product_id = product_id.group()
            url = self.QUESTION_API_URL.format(apipass=self.QA_API_PASS,
                                               product_id=product_id)
            return Request(url, self._parse_questions, meta=response.meta, dont_filter=True,
                           headers={'User-Agent': self.user_agent_override})
        else:
            return product

    def _parse_questions(self, response):
        product = response.meta['product']
        data = json.loads(response.body_as_unicode())
        reqs = []
        if data and data['Results']:
            for question in data['Results']:
                q = {}
                q['questionSummary'] = question['QuestionSummary']
                time = question['SubmissionTime']
                date = is_empty(time.split('T'))
                if date:
                    q['submissionDate'] = date
                q['userNickname'] = question['UserNickname']
                q['totalAnswersCount'] = question['TotalAnswerCount']
                q['questionId'] = question['Id']
                if q['questionId']:
                    url = self.ANSWER_API_URL.format(apipass=self.QA_API_PASS,
                                                     question_id=q['questionId'])
                    meta = response.meta
                    meta['q'] = q
                    reqs.append(Request(url, self._parse_answer, meta=meta, dont_filter=True,
                                        headers={'User-Agent': self.user_agent_override}))
            if reqs:
                return self.send_next_request(reqs, response)
        else:
            product['all_questions'] = []
            if self.POPULATE_REVIEWS:
                canonical_url = response.meta['canonical_url']
                return self._request_reviews(response, product, canonical_url)
            else:
                return product

    def _parse_answer(self, response):
        product = response.meta['product']
        reqs = response.meta.get('reqs', [])
        all_questions = product.get('all_questions', [])
        q = response.meta['q']
        q['answers'] = []
        data = json.loads(response.body_as_unicode())
        if data['Results']:
            for answer in data['Results']:
                a = {}
                a['userNickname'] = answer['UserNickname']
                a['answerSummary'] = a['answerText'] = answer['AnswerText'].replace('\xa0', '')
                time = answer['SubmissionTime']
                date = is_empty(time.split('T'))
                if date:
                    a['submissionDate'] = date
                a['PositiveVoteCount'] = answer['TotalPositiveFeedbackCount']
                a['NegativeVoteCount'] = answer['TotalNegativeFeedbackCount']
                q['answers'].append(a)
        if q['answers'] or not data['Results']:
            all_questions.append(q)
            product['all_questions'] = all_questions
            product['recent_questions'] = product['all_questions']
            # get date_of_last_question
            product['date_of_last_question'] = self._get_latest_questions_date(
                product['all_questions'])
            for req in reqs:
                req.meta['product'] = product
            if reqs:
                return self.send_next_request(reqs, response)
            elif self.POPULATE_REVIEWS:
                canonical_url = response.meta['canonical_url']
                return self._request_reviews(response, product, canonical_url)
            else:
                return product

    @staticmethod
    def _get_latest_questions_date(all_questions):
        dateconv = lambda date: datetime.datetime.strptime(date, '%Y-%m-%d').date()

        last_date = None
        for q in all_questions:
            date = q.get('submissionDate', None)
            if date is not None:
                date = dateconv(date)
                if date:
                    if last_date is None:
                        last_date = date
                    elif date > last_date:
                        last_date = date

        if last_date is None:
            return
        else:
            return last_date.strftime('%Y-%m-%d')

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests for parsing QA
        """

        req = reqs.pop(0)
        new_meta = req.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs

        return req.replace(meta=new_meta)
