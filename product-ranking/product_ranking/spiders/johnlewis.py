from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import re
import string
import urllib
import urlparse
# Uncomment this line! import requests

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import cond_set, cond_set_value
from scrapy import Request
from scrapy import Selector
from scrapy.log import DEBUG


class RichRelevanceHelper(object):
    SCRIPT_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js"

    def __init__(self):
        self.cs = []
        self.pt = []

    def prepare_johnlewis(self, response):
        script = response.xpath(
            "//script[contains(text(),'R3_COMMON')"
            " or contains(text(),'R3_ITEM')  ]/text()")
        if script:
            script = "".join(script.extract())
        else:
            return None

        m = re.match(r"^.*R3_COMMON.setApiKey\('(\S*)'\);", script, re.DOTALL)
        if m:
            self.rr_apikey = m.group(1)
        else:
            raise AssertionError("setApiKey not found in \n%s\n" % script)

        m = re.match(r"^.*R3_COMMON.setSessionId\('(\S*)'\);", script, re.DOTALL)
        if m:
            self.rr_sessionid = m.group(1)
        else:
            raise AssertionError("setSessionId not found in \n%s\n" % script)

        m = re.match(r"^.*R3_ITEM.setId\('(\S*)'\);", script, re.DOTALL)
        if m:
            self.rr_productid = m.group(1)
        else:
            raise AssertionError("setId not found in \n%s\n" % script)

        m = re.match(
            r"^.*R3_ITEM.addCategory\('([^\)]*)',\s'([^)]*)'\);.*",
            script, re.DOTALL + re.MULTILINE)
        if m:
            code = m.group(1)
            name = m.group(2)
            self.cs.append((code, name))
            self.rr_cs = "".join("|" + x + ":" + y for x, y in self.cs)
        else:
            raise AssertionError("addCategory not found in \n%s\n" % script)

        pt = response.xpath(
            "//div[@data-jl-rr-placement]"
            "/@data-jl-rr-placement").extract()
        self.rr_pt = "".join("|" + x for x in pt)
        self.rr_recommendable = True
        self._check_rr_parms()                

        payload = {"a": self.rr_apikey,
                   "cs": urllib.quote(self.rr_cs),
                   "p": self.rr_productid,
                   "re": self.rr_recommendable,
                   "je": "t",
                   "pt": urllib.quote(self.rr_pt),
                   "u": self.rr_sessionid,
                   "s": self.rr_sessionid,
                   "l": 1}
        return payload

    def _check_rr_parms(self):
        need_parms = ["rr_apikey", "rr_sessionid",
                      "rr_productid", "rr_recommendable", "rr_pt", "rr_cs"]

        for parm in need_parms:
            if not hasattr(self, parm):
                raise AssertionError("RicheRelevanceHelper need %s parm." % parm)

    def make_url(self, payload):
        return urlparse.urljoin(self.SCRIPT_URL,
                                "?" + urllib.urlencode(payload))

    @staticmethod
    def parse_rr_js_response_johnlewis(text):
        results = {}
        m = re.match(r'.*rr_recs = (.+);RR.useJsonRecs =.*', text)
        if m:
            jstext = m.group(1)
            data = json.loads(jstext)

            for placement in data.get('placements'):
                placement_type = placement.get('placementType')
                strategy = placement.get('strategy')
                items = []

                for item in placement.get('items'):
                    name = item.get('name')
                    url = item.get('url')
                    url_split = urlparse.urlsplit(url)
                    query = urlparse.parse_qs(url_split.query)
                    original_url = query.get('ct')
                    if original_url:
                        items.append((name, original_url[0]))
                results[placement_type] = {'strategy': strategy, 'items': items}
        else:
            raise AssertionError("rr_recs = Not found in \n%s\n" % text.encode('utf-8'))
        return results


class JohnlewisProductsSpider(BaseProductsSpider):
    name = 'johnlewis_products'
    allowed_domains = ["www.johnlewis.com", "recs.richrelevance.com"]
    start_urls = []
    SEARCH_URL = "http://www.johnlewis.com/search/{search_term}"

    def __init__(self, *args, **kwargs):
        # All this is to set the site_name since we have several
        # allowed_domains.

        super(JohnlewisProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(
            product,
            'title',
            response.xpath(
                "//section/h1[@id='prod-title']/span[@itemprop='name']/text()").extract()
        )

        cond_set(
            product,
            'brand',
            response.xpath(
                "//section/div[@id='prod-info-tab']"
                "/descendant::div[@itemprop='brand']"
                "/span[@itemprop='name']/text()").extract(),
            conv=string.strip
        )

        def strip_price(price):
            price = price.strip()
            mprice = re.match(r'.*\s(\S*)$', price, re.DOTALL)
            if mprice:
                price = mprice.group(1)
            return price

        cond_set(
            product,
            'price',
            response.xpath(
                "//section/div[@id='prod-price']/p[@class='price']"
                "/strong/text()").extract(),
            conv=strip_price
        )

        cond_set(
            product,
            'upc',
            response.xpath(
                "//div[@id='prod-product-code']/p/text()").extract(),
            conv=int
        )

        cond_set(
            product,
            'image_url',
            response.xpath(
                "//meta[@property='og:image']/@content").extract(),
        )

        description = response.xpath(
            "//div[@id='tabinfo-care-info']"
            "/descendant::*[text()]/text()").extract()

        cond_set_value(
            product,
            'description',
            " ".join(line.strip() for line in description if len(line.strip()) > 0)
        )

        product['locale'] = "en-US"

        rrhelper = RichRelevanceHelper()
        payload = rrhelper.prepare_johnlewis(response)

        new_meta = response.meta.copy()
        new_meta['rrs'] = rrhelper

        return Request(rrhelper.make_url(payload), self._parse_json, meta=new_meta)

    def _parse_json(self, response):
        product = response.meta['product']

        rrs = response.meta['rrs']
        result = rrs.parse_rr_js_response_johnlewis(response.body)

        lists_names = {'item_page.PD_20': "recommended",
                       'item_page.PD_28': 'buyers_also_bought',
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
        tm = getattr(self, 'total_matched')
        if tm:
            return tm

        total = response.xpath(
            "//section[@class='search-results']/header/h1/span/text()"
        ).extract()
        if total:
            total = total[0]
            try:
                return int(total)
            except ValueError:
                return 0
        else:
            return 0

    def get_all_prod_brand_links(self, url, linksession):
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
            if not body:
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
            no_results = response.xpath("//div[@class='mod-important']/h1/text()").re(r'No results.*')
            if not no_results:
                # Exctract links form brand-page
                links = response.xpath(
                    "//div[@id='content']/div/div/div/section/section"
                    "/div/ul/li/a/@href").extract()

                linksession = requests.Session()
                linksession.get(response.url)
                product_links = []

                for link in links:
                    link = full_url(link) + "/pg{page_number}"
                    response_links = self.get_all_prod_brand_links(
                        link, linksession)
                    product_links.extend(response_links)

                links = product_links
                self.total_matched = len(links)
                print "self.total_matched=", self.total_matched
                yield None, SiteProductItem()
                return
        if not links:
            self.log("Found no product links.", DEBUG)

        for link in links:
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
