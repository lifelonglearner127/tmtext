# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

from itertools import islice
import json
import re
import string
import urllib
import urllib2
import urlparse

from scrapy import Selector
from scrapy.http import FormRequest, Request
from scrapy.log import DEBUG, INFO

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set, FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set_value, populate_from_open_graph
from spiders_shared_code.target_variants import TargetVariants
from product_ranking.validation import BaseValidator
from product_ranking.validators.target_validator import TargetValidatorSettings

is_empty = lambda x, y=None: x[0] if x else y



class TargetProductSpider(BaseValidator, BaseProductsSpider):
    name = 'target_products'
    allowed_domains = ["target.com", "recs.richrelevance.com",
                       'api.bazaarvoice.com']
    start_urls = ["http://www.target.com/"]

    settings = TargetValidatorSettings

    # TODO: support new currencies if you're going to scrape target.canada
    #  or any other target.* different from target.com!
    SEARCH_URL = "http://www.target.com/s?searchTerm={search_term}"
    SCRIPT_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js"
    CALL_RR = False
    CALL_RECOMM = True
    POPULATE_VARIANTS = False
    POPULATE_REVIEWS = True
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

    REVIEW_API_URL = "http://api.bazaarvoice.com/data/batch.json" \
                     "?passkey={apipass}&apiversion=5.5" \
                     "&displaycode=19988-en_us&resource.q0=products" \
                     "&filter.q0=id%3Aeq%3A{model}&stats.q0=reviews" \
                     "&filteredstats.q0=reviews"

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

    RELATED_URL = "{path}?productId={pid}&userId=-1002&min={min}&max={max}&context=placementId,{plid};categoryId,{cid}&callback=jsonCallback"

    def __init__(self, sort_mode=None, *args, **kwargs):
        if sort_mode:
            if sort_mode.lower() not in self.SORT_MODES:
                self.log('"%s" not in SORT_MODES')
            else:
                self.SORTING = self.SORT_MODES[sort_mode.lower()]

        super(TargetProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self._start_search)

    def _start_search(self, response):
        for request in super(TargetProductSpider, self).start_requests():
            #request.meta['dont_redirect'] = True
            request.meta['handle_httpstatus_list'] = [302]
            request.meta['search_start'] = True
            yield request

    def parse(self, response):
        regexp = re.compile('^http://[\w]*\.target\.com/c/[^/]+/-/([^#]+)')
        category = regexp.search(response.url)
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
                meta=new_meta)
        return list(super(TargetProductSpider, self).parse(response))

    def parse_product(self, response):
        # for some products (with many colors for example) target.com
        # insert at <meta> another url than you see at browser.
        # it used to calculate buyer_reviews correct.
        canonical_url = response.xpath(
            '//meta[@property="og:url"]/@content'
        ).extract()
        prod = response.meta['product']

        if 'sorry, that item is no longer available' \
                in response.body_as_unicode().lower():
            prod['not_found'] = True
            return prod

        tv = TargetVariants()
        tv.setupSC(response)
        prod['variants'] = tv._variants()

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
        #cond_set_value(prod, 'url', old_url)

        cond_set_value(prod, 'locale', 'en-US')
        self._populate_from_html(response, prod)
        # fiME: brand=None
        if 'brand' in prod and len(prod['brand']) == 0:
            prod['brand'] = 'No brand'
        if 'brand' not in prod:
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
                    meta=new_meta)

        if self.CALL_RR:
            if payload:
                new_meta = response.meta.copy()
                new_meta['canonical_url'] = canonical_url
                rr_url = urlparse.urljoin(self.SCRIPT_URL,
                                          "?" + urllib.urlencode(payload))
                return Request(
                    rr_url,
                    self._parse_rr_json,
                    meta=new_meta)
            else:
                self.log("No {rr} payload at %s" % response.url, DEBUG)

        if self.POPULATE_REVIEWS:
            return self._request_reviews(response, prod, canonical_url)
        else:
            return prod

    def _populate_from_html(self, response, product):
        if 'title' in product and product['title'] == '':
            del product['title']
        cond_set(
            product,
            'title',
            response.xpath(
                "//h2[contains(@class,'product-name')]"
                "/span[@itemprop='name']/text()"
                "|//h2[contains(@class,'collection-name')]"
                "/span[@itemprop='name']/text()"
            ).extract(),
            conv=string.strip
        )

        desc = product.get('description')
        if desc:
            desc = desc.replace("\n", "")
            product['description'] = desc
        desc = response.css(
            '#item-overview > div > div:nth-child(1)').extract()
        if desc:
            desc = desc[0]
            desc = desc.replace("\n", "")
            product['description'] = desc
        cond_set(product, 'image_url', response.xpath(
            "//img[@itemprop='image']/@src").extract())
        image = product.get('image_url')
        if image:
            image = image.replace("_100x100.", ".")
            product['image_url'] = image

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
                meta=new_meta)

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
                "a[contains(@class,'productBrand')]/text()").extract()
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
                    './div[@class="pricecontainer"]/span[@class="map"]/following::p/span/text()')\
                    .re(FLOATING_POINT_RGEX)
                if price:
                    price = price[0]

            bi_list.append((brand, link, isonline, price))
        return bi_list

    def _scrape_product_links(self, response):
        if response.meta.get('json'):
            return list(self._scrape_product_links_json(response))
        else:
            return list(self._scrape_product_links_html(response))

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
            yield url, product

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
            data = json.loads(data.group(1))
        except (ValueError, TypeError, AttributeError):
            self.log('JSON response expected.')
            return
        return data['searchResponse']

    def _scrape_total_matches(self, response):
        if response.meta.get('json'):
            return self._scrape_total_matches_json(response)
        else:
            return self._scrape_total_matches_html(response)

    def _json_get_args(self, data):
        args = {d['name']: d['value'] for d in
                data['searchState']['Arguments']['Argument']}
        return args

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
                #return FormRequest.from_response(
                #response=response,
                url=post_url,
                method='POST',
                formdata=data,
                callback=self._parse_link_post,
                meta=new_meta)

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
                meta=new_meta,dont_filter=True))
        return requests

    def _scrape_next_results_page_link(self, response):
        if self.SORTING is not None and response.meta.get('search_start'):
            return
        if response.meta.get('json'):
            return self._scrape_next_results_page_link_json(response)
        else:
            return self._scrape_next_results_page_link_html(response)

    def _scrape_next_results_page_link_json(self, response):
        #raw_input(len(list(self._scrape_product_links_json(response))))
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
            return Request(url, meta=new_meta)

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
        if canonical_url:
            main_url = canonical_url[0]
        else:
            main_url = product['url']
        prod_id = re.search('\d+\Z', main_url)
        if prod_id:
            prod_id = prod_id.group()
            url = self.REVIEW_API_URL.format(apipass=self.REVIEW_API_PASS,
                                             model=prod_id)
            return Request(url, self._parse_reviews, meta=response.meta, dont_filter=True)
        else:
            return product

    def _parse_reviews(self, response):
        product = response.meta['product']
        data = json.loads(response.body_as_unicode())
        data = data.get('BatchedResults', {}).get('q0', {})
        data = (data.get('Results') or [{}])[0]
        data = data.get('FilteredReviewStatistics', {})
        average = data.get('AverageOverallRating')
        total = data.get('TotalReviewCount')
        
        if average and total:
            distribution = data.get('RatingDistribution', [])
            distribution = {d['RatingValue']: d['Count']
                            for d in data.get('RatingDistribution', [])}
            fdist = {i: 0 for i in range(1, 6)}
            for i in range(1, 6):
                if i in distribution:
                    fdist[i] = distribution[i]
            reviews = BuyerReviews(total, average, fdist)
            cond_set_value(product, 'buyer_reviews', reviews)
        else:
            cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
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
