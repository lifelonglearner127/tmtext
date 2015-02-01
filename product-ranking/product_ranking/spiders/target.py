# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

from itertools import islice
import json
import re
import string
import urllib
import urlparse
import uuid

from scrapy import Selector
from scrapy.http import FormRequest, Request
from scrapy.log import DEBUG, INFO

from product_ranking.items import SiteProductItem, Price, \
    BuyerReviews, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.spiders import cond_set_value, populate_from_open_graph


class TargetProductSpider(BaseProductsSpider):
    name = 'target_products'
    allowed_domains = ["target.com", "recs.richrelevance.com",
                       'api.bazaarvoice.com', 'www.hlserve.com']
    start_urls = ["http://www.target.com/"]
    # TODO: support new currencies if you're going to scrape target.canada
    #  or any other target.* different from target.com!
    SEARCH_URL = "http://www.target.com/s?searchTerm={search_term}"
    SCRIPT_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js"
    SORTING = None

    SORT_MODES = {
        "relevance": "relevance",
        "featured": "Featured",
        "pricelow": "PriceLow",
        "pricehigh": "PriceHigh",
        "newest": "newest"
    }

    RELATED_PRODUCTS_URL = "https://prz-secure.target.com/recommendations/v1" \
                           "?productId={prod_id}" \
                           "&context=placementId,{placement};" \
                           "categoryId,{category}"

    FEATURED_PRODUCTS_URL = "http://www.hlserve.com/Delivery/ClientPaths" \
                            "/Library/Delivery.aspx?version=0.9.0" \
                            "&pageGUID={guid}" \
                            "&clientid=131" \
                            "&pagetype=product" \
                            "&taxonomy={category}" \
                            "&prodid={prod_id}" \
                            "&qty=1" \
                            "&prodp={price}" \
                            "&maxmes=4&bm_type=2&bm_taxoff=2" \
                            "&productid={prod_id}" \
                            "&loc=hl_1_999"

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
        prod = response.meta['product']
        old_url = prod['url'].rsplit('#', 1)[0]
        prod['url'] = None
        populate_from_open_graph(response, prod)
        cond_set_value(prod, 'url', old_url)
        cond_set_value(prod, 'locale', 'en-US')
        self._populate_from_html(response, prod)
        return list(self._request_additional_info(response, prod)) or prod

    def _populate_from_html(self, response, product):
        if 'title' in product and product['title'] == '':
            del product['title']
        cond_set(
            product,
            'title',
            response.xpath(
                "//h2[contains(@class,'product-name')]"
                "/span[@itemprop='name']/text()").extract(),
            conv=string.strip
        )

        price = response.xpath(
            "//span[@itemprop='price']/text()"
            "|//*[@id='see-low-price']/a/text()"
        ).extract()
        if not price or price[0] == 'See Low Price in Cart':
            cond_set(product, 'price', ['$0.00'])
        else:
            cond_set(product, 'price', price)
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
        image = product.get('image_url')
        if image:
            image = image.replace("_100x100.", ".")
            product['image_url'] = image

    def _populate_variants(self, response, product, variants):
        product_list = []
        for itype, color, price, code in variants:
            if itype == 'ITEM':
                new_product = product.copy()
                new_product['price'] = price
                if not isinstance(new_product, Price):
                    new_product['price'] = Price(
                        price=new_product['price'].replace(
                            '$', '').replace(',', '').strip(),
                        priceCurrency='USD'
                    )
                new_product['model'] = color
                new_product['upc'] = code
                product_list.append(new_product)
        return product_list

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
            bi_list.append((brand, link, isonline))
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
                    amount = re.sub('[^0-9.]', '', priceattr['amount'])
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
            yield post_req, SiteProductItem()
            return

        for brand, link, isonline in bi_list:
            product = SiteProductItem(brand=brand)
            if 'out of stock' in isonline:
                product['is_out_of_stock'] = True
            if 'in stores only' in isonline:
                product['is_in_store_only'] = True

            # FIXME: 'onilne_only' status
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
            if remaining and remaining > 0:
                new_meta['remaining'] = remaining
            post_url = "http://www.target.com/SoftRefreshProductListView"
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

        for i, (brand, url, isonline) in enumerate(islice(links, 0, remaining)):
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
                meta=new_meta))
        return requests

    def _scrape_next_results_page_link(self, response):
        if response.meta.get('json'):
            return self._scrape_next_results_page_link_json(response)
        else:
            return self._scrape_next_results_page_link_html(response)

    def _scrape_next_results_page_link_json(self, response):
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
            "/ul[@class='pagination1']/li[@class='next']/a/@href").extract()
        if next_page:
            next_page = next_page[0]
            return self._gen_next_request(response, next_page)

    def _request_reviews(self, response, product):
        prod_id = re.search('\d+\Z', product['url'])
        if prod_id:
            prod_id = prod_id.group()
            url = self.REVIEW_API_URL.format(apipass=self.REVIEW_API_PASS,
                                             model=prod_id)
            return Request(url, self._parse_reviews, meta=response.meta)

    def _return_if_finished(self, response):
        response.meta['pending'].remove(response.meta['id_'])
        if not response.meta['pending']:
            return response.meta['product']

    def _parse_reviews(self, response):
        product = response.meta['product']
        data = json.loads(response.body_as_unicode())
        data = data.get('BatchedResults', {}).get('q0', {})
        data = (data.get('Results') or [{}])[0]
        data = data.get('FilteredReviewStatistics', {})
        average = data.get('AverageOverallRating')
        total = data.get('TotalReviewCount')
        if average is None or total is None:
            return self._return_if_finished(response)
        distribution = data.get('RatingDistribution', [])
        distribution = {d['Count']: d['RatingValue']
                        for d in data.get('RatingDistribution', [])}
        reviews = BuyerReviews(total, average, distribution)
        cond_set_value(product, 'buyer_reviews', reviews)
        return self._return_if_finished(response)

    def _extract_rp_args(self, response):
        prod_id = re.search('"partNumber" *: *"([^"]+)"',
                            response.body_as_unicode())
        category = re.search('"RRCategoryId" *: *"([^"]+)"',
                             response.body_as_unicode())
        return category, prod_id

    def _request_related_products(self, response, product):
        placements = ['pdpv1', 'pdph1', ]
        category, prod_id = self._extract_rp_args(response)
        if prod_id and category:
            prod_id = prod_id.group(1)
            category = category.group(1)
        else:
            self.log('Could not scrape related products (%s)' % response.url)
            return
        for placement in placements:
            url = self.RELATED_PRODUCTS_URL.format(prod_id=prod_id,
                                                   category=category,
                                                   placement=placement)
            yield Request(url, self._parse_related_products,
                          meta=response.meta)

    def _request_featured_products(self, response, product):
        product['related_products']['featured products'] = []
        category, prod_id = self._extract_rp_args(response)
        price = product.get('price')
        if prod_id and category and price:
            prod_id = prod_id.group(1)
            category = category.group(1)
            price = price.price
        else:
            self.log('Could not scrape featured products (%s)' % response.url)
            return
        guid = uuid.uuid4()
        url = self.FEATURED_PRODUCTS_URL.format(category=category,
                                                prod_id=prod_id,
                                                price=price,
                                                guid=guid)
        return Request(url, self._parse_featured_products, meta=response.meta)

    def _parse_related_products(self, response):
        product = response.meta['product']
        data = json.loads(response.body_as_unicode())
        strategy = data['strategyDescription']
        products = []
        for item in data['recommendations']:
            url = item['productLink']
            title = item['productTitle']
            products.append(RelatedProduct(url=url, title=title))
        product['related_products'][strategy] = products
        return self._return_if_finished(response)

    def _parse_featured_products(self, response):
        regexp = '"ProductName" *: *"([^"]+)".+?"ProductPage" *: *"([^"]+)"'
        found = re.findall(regexp, response.body_as_unicode())
        for title, url in found:
            title = title.decode('unicode-escape')
            url = url.decode('unicode-escape')
            url = "http://" + url if 'http://' not in url else url
            meta = response.meta.copy()
            meta['title'] = title
            meta['pending'].add(title)
            meta['id_'] = title
            meta['dont_redirect'] = True
            meta['handle_httpstatus_list'] = [302]
            yield Request(url, self._fetch_fp_url, meta=meta, dont_filter=True)
        yield self._return_if_finished(response)

    def _fetch_fp_url(self, response):
        product = response.meta['product']
        url = response.headers['location']
        rp = RelatedProduct(url=url, title=response.meta['title'])
        product['related_products']['featured products'].append(rp)
        return self._return_if_finished(response)

    def _request_additional_info(self, response, prod):
        prod['related_products'] = {}
        reviews_request = self._request_reviews(response, prod)
        relprod_requests = self._request_related_products(response, prod)
        fp_requests = self._request_featured_products(response, prod)
        requests = [reviews_request, fp_requests] + list(relprod_requests)
        #requests = [reviews_request] + list(relprod_requests)
        requests = filter(None, requests)
        pending = set(request.url for request in requests)
        for request in requests:
            request.meta['pending'] = pending
            request.meta['id_'] = request.url
            yield request
