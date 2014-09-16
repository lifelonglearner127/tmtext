from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from datetime import datetime
import json
import re
import string
import urllib
import urlparse
#import requests

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, populate_from_open_graph
from product_ranking.spiders import cond_set, cond_set_value
from scrapy import Request
from scrapy import Selector
from scrapy.log import ERROR, DEBUG


class RRSpider(object):
    SCRIPT_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js"

    def __init__(self):
        self.cs = []
        self.pt = []

    def prepare_johnlewis(self, text):
        sel = Selector(text=text, type="html")
        script = sel.xpath(
            "//script[contains(text(),'R3_COMMON')"
            " or contains(text(),'R3_ITEM')  ]/text()")
        if script:
            script = "".join(script.extract())

        m = re.match(r"^.*R3_COMMON.setApiKey\('(\S*)'\);", script, re.S)
        if m:
            self.rr_apikey = m.group(1)
        else:
            raise AssertionError("apikey nof found")

        m = re.match(r"^.*R3_COMMON.setSessionId\('(\S*)'\);", script, re.S)
        if m:
            self.rr_sessionid = m.group(1)
        else:
            raise AssertionError("SessionId nof found")

        m = re.match(r"^.*R3_ITEM.setId\('(\S*)'\);", script, re.S)
        if m:
            self.rr_productid = m.group(1)
        else:
            raise AssertionError("productId nof found")

        m = re.match(
            r"^.*R3_ITEM.addCategory\('([^\)]*)',\s'([^)]*)'\);.*",
            script, re.S + re.M)
        if m:
            code = m.group(1)
            name = m.group(2)
            self.cs.append((code, name))
            self.rr_cs = "".join(["|" + x + ":" + y for x, y in self.cs])
        else:
            print "SCRIPT=", script
            raise AssertionError("addCategory nof found")

        pt = sel.xpath(
            "//div[@data-jl-rr-placement]"
            "/@data-jl-rr-placement").extract()
        self.rr_pt = "".join(["|" + x for x in pt])

        self.rr_recommendable = True
        ts = int((datetime.utcnow() - datetime(1970, 1, 1)).
                 total_seconds() * 1000.0)

        self.payload = {"a": self.rr_apikey,
                        "cs": urllib.quote(self.rr_cs),
                        "p": self.rr_productid,
                        "re": self.rr_recommendable,
                        "je": "t",
                        "pt": urllib.quote(self.rr_pt),
                        "u": self.rr_sessionid,
                        "s": self.rr_sessionid,
                        "ts": ts,
                        "l": 1}
        return self.payload

    def check_payload(self):
        need_parms = ["rr_apikey", "rr_sessionid",
                      "rr_productid", "rr_recommendable", "rr_pt", "rr_cs"]

        for parm in need_parms:
            if parm in self.__dict__:
                pass
            else:
                raise AssertionError("Need %s parm." % (parm,))

    def make_url(self):
        return urlparse.urljoin(self.SCRIPT_URL,
                                "?" + urllib.urlencode(self.payload))

    def razbor(self, text):
        self.results = {}
        m = re.match(r'.*rr_recs = (.+);RR.useJsonRecs =.*', text)
        if m:
            jstext = m.group(1)
            data = json.loads(jstext)
            for placement in data['placements']:
                ptype = placement.get('placementType')
                strategy = placement.get('strategy')
                items = []
                for item in placement['items']:
                    name = item.get('name')
                    url = item.get('url')
                    url_split = urlparse.urlsplit(url)
                    query = urlparse.parse_qs(url_split.query)
                    original_url = query['ct'][0]
                    items.append((name, original_url))
                self.results[ptype] = {'strategy': strategy, 'items': items}
        else:
            raise AssertionError("rr_recs = Not found")
        return self.results


class JohnlewisProductsSpider(BaseProductsSpider):
    name = 'johnlewis_products'
    allowed_domains = ["www.johnlewis.com", "recs.richrelevance.com"]
    start_urls = []
    SEARCH_URL = "http://www.johnlewis.com/search/{search_term}"
    # _USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 " \
    #     "(KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36"

    def __init__(self, *args, **kwargs):
        # All this is to set the site_name since we have several
        # allowed_domains.

        super(JohnlewisProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        populate_from_open_graph(response, product)

        cond_set(
            product,
            'brand',
            response.xpath(
                "//section/div[@id='prod-info-tab']"
                "/descendant::div[@itemprop='brand']"
                "/span[@itemprop='name']/text()").extract(),
            conv=string.strip
        )

        cond_set(
            product,
            'price',
            response.xpath(
                "//section/div[@id='prod-price']/p[@class='price']"
                "/strong/text()").extract(),
            conv=string.strip
        )
        price = product['price']
        mprice = re.match(r'.*\s(\S*)$', price, re.S)
        if mprice:
            product['price'] = mprice.group(1)
        cond_set(
            product,
            'upc',
            response.xpath(
                "//div[@id='prod-product-code']/p/text()").extract(),
            conv=int
        )

        rrs = RRSpider()
        rrs.prepare_johnlewis(response.body)
        rrs.check_payload()
        json_link = rrs.make_url()

        new_meta = response.meta.copy()
        new_meta['rrs'] = rrs

        return Request(json_link, self._parse_json, meta=new_meta)

    def _parse_json(self, response):
        product = response.meta['product']
        rrs = response.meta['rrs']
        result = rrs.razbor(response.body)

        lists_names = {'item_page.PD_20': "recommended",
                       'item_page.PD_28': 'buyers_also_bought',
                       # 'item_page.WF_HF': 'R3'
                       }
        product['related_products'] = {}

        for name, strategy_list in result.items():
            items = strategy_list.get('items')
            prodlist = []
            for item_name, item_url in items:
                prodlist.append(RelatedProduct(item_name, item_url))

            if prodlist:
                    related_name = lists_names.get(name)
                    if related_name:
                        product['related_products'][related_name] = prodlist

        return product

    def _scrape_total_matches(self, response):
        tm = self.__dict__.get('total_matched')
        if tm:
            return tm

        total = response.xpath(
            "//section[@class='search-results']/header/h1/span/text()"
        ).extract()
        print "TOTAL=", total
        if total:
            total = total[0]
            try:
                return int(total)
            except ValueError:
                return 0
        else:
            return 0

    def get_all_department_prod_links(self, url, linksession):
        page_number = 1
        all_links = []
        run_again = True
        extracted_count = 0

        while run_again:
            run_again = False

            # linksession.headers.update({'User-Agent': self._USER_AGENT})
            rurl = url.format(page_number=page_number)
            r = linksession.get(rurl)
            self.log("Request %s" % rurl, DEBUG)
            if not r.status_code == 200:
                break

            body = r.text
            if len(body) < 1:
                break

            response = Selector(text=body)
            links = response.xpath(
                "//div[@class='result-row']"
                "/article/a[@class='product-link']/@href").extract()

            extracted_count += len(links)

            if not links:
                break

            all_links.extend(links)

            total = response.xpath(
                "//section[@class='search-results']/header/h1/text()"
            ).re(r'.*\((\d+)\)')

            if total:
                total = int(total[0])

            if total > extracted_count:
                run_again = True
                page_number += 1

        return all_links

    def _scrape_product_links(self, response):

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        self.total_matched = 0

        links = response.xpath(
            "//div[@class='result-row']"
            "/article/a[@class='product-link']/@href").extract()

        if not links:
            links = response.xpath(
                "//div[@id='content']/div/div/div/section/section"
                "/div/ul/li/a/@href").extract()

            linksession = requests.Session()
            linksession.get(response.url)
            product_links = []

            for no, link in enumerate(links):
                link = full_url(link) + "/pg{page_number}"
                response_links = self.get_all_department_prod_links(
                    link, linksession)
                product_links.extend(response_links)

            links = product_links
            self.total_matched = len(links)

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield full_url(link), SiteProductItem()

    def _scrape_next_results_page_link(self, response):

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        next = response.xpath(
            "//div[@class='pagination']/ul[@role='navigation']"
            "/li[@class='next']/a/@href").extract()
        if next:
            if next[0] == '#':
                return None
            next = full_url(next[0])
            return next
