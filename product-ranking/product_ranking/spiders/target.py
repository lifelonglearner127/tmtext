# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from itertools import islice
import json
import re
import string
import urllib
import urllib2
import urlparse

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.spiders import cond_set_value, populate_from_open_graph
from scrapy import Selector
from scrapy.http import FormRequest, Request
from scrapy.log import DEBUG,INFO, ERROR


class TargetProductSpider(BaseProductsSpider):
    name = 'target_products'
    allowed_domains = ["target.com", "recs.richrelevance.com"]
    start_urls = ["http://www.target.com/"]
    # TODO: support new currencies if you're going to scrape target.canada
    #  or any other target.* different from target.com!
    SEARCH_URL = "http://www.target.com/s?searchTerm={search_term}"
    SCRIPT_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js"
    CALL_RR = True
    POPULATE_VARIANTS = True
    SORTING = None

    SORT_MODES = {
        "relevance": "relevance",
        "featured": "Featured",
        "pricelow": "PriceLow",
        "pricehigh": "PriceHigh",
        "newest": "newest"
    }

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
            request.meta['dont_redirect'] = True
            request.meta['handle_httpstatus_list'] = [302]
            yield request

    def parse_product(self, response):
        prod = response.meta['product']
        populate_from_open_graph(response, prod)
        cond_set_value(prod, 'locale', 'en-US')
        self._populate_from_html(response, prod)

        variants = self._extract_variants(response, prod)
        payload = self._extract_rr_parms(response)

        if self.CALL_RR:
            if payload:
                new_meta = response.meta.copy()
                new_meta['variants'] = variants
                rr_url = urlparse.urljoin(self.SCRIPT_URL,
                                          "?" + urllib.urlencode(payload))
                return Request(
                    rr_url,
                    self._parse_rr_json,
                    meta=new_meta)
            else:
                self.log("No {rr} payload at %s" % response.url, DEBUG)

        if self.POPULATE_VARIANTS:
            if variants:
                return self._populate_variants(response, prod, variants)
        return prod

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

    def _extract_variants(self, response, product):
        js = response.xpath(
            "//script[contains(text(),'Target.globals.refreshItems = ')]"
            "/text()").re('.*Target.globals.refreshItems = (.*)')
        variants = []
        if js:
            try:
                jsdata = json.loads(js[0])
            except ValueError:
                jsdata = {}
            for item in jsdata:
                try:
                    itype = item['Attributes']['catent_type']
                    try:
                        color = item['Attributes']['preselect']['var1']
                    except KeyError:
                        color = ""
                    price = item['Attributes']['price']['formattedOfferPrice']
                    code = item['Attributes']['partNumber']
                    variants.append((itype, color, price, code))
                except KeyError:
                    pass
        return variants

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
        variants = response.meta.get('variants')
        if variants:
            return self._populate_variants(response, product, variants)
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
            bi_list.append((brand, link, isonline))
        return bi_list

    def _scrape_product_links(self, response):
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

    def _scrape_total_matches(self, response):
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
            return FormRequest.from_response(
                response=response,
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
        next_page = response.xpath(
            "//div[@id='pagination1']/div[@class='col2']"
            "/ul[@class='pagination1']/li[@class='next']/a/@href").extract()
        if next_page:
            next_page = next_page[0]
            return self._gen_next_request(response, next_page)
