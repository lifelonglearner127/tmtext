from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import ast
import json
import string
import urlparse

from scrapy.http import FormRequest
from scrapy.log import DEBUG, ERROR
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    populate_from_open_graph, cond_set_value


class ConvertBadJson(ast.NodeVisitor):
    """ Convert bad json text like
        [{sBoxName : 'relatedByCommonViewers',bShowPorn : '',...

        to array of tupples
        [(u'[0][sBoxName]', 'relatedByCommonViewers'),
         (u'[0][bShowPorn]', ''), (u'[0][bShowBPJM]', ''), ...
    """
    def __init__(self):
        self.indexes = list()
        self.result = list()

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Expr(self, node):
        return self.visit(node.value)

    def visit_Dict(self, node):
        for k, v in zip(node.keys, node.values):
            k = self.visit(k)
            self.indexes.append(k)
            v = self.visit(v)

            if type(v) == type(str()):
                key = "".join(["[%s]" % x for x in self.indexes])
                self.result.append((key, v))
            self.indexes.pop()

    def visit_List(self, node):
        self.indexes.append(0)
        for el in node.elts:
            self.visit(el)
            level = self.indexes.pop()
            self.indexes.append(level + 1)
        self.indexes.pop()

    def visit_Name(self, node):
        return node.id

    def visit_Num(self, node):
        return node.n

    def visit_Str(self, node):
        return node.s

    def get_result(self):
        return self.result


class SouqProductsSpider(BaseProductsSpider):
    name = 'souq_products'
    allowed_domains = ["souq.com"]
    start_urls = []
    SEARCH_URL = "http://uae.souq.com/ae-en/{search_term}/s/"
    _RECOM_URL = "http://uae.souq.com/ae-en/Action.php"

    def _populate_from_open_graph(self, response, product):
        """Populates from Open Graph and discards description, which is fake.
        """
        populate_from_open_graph(response, product)

        if 'description' in product:
            del product['description']

    def parse_product(self, response):
        product = response.meta['product']

        self._populate_from_open_graph(response, product)

        cond_set(product, 'title', map(string.strip, response.xpath(
            "//h1[@id='item_title']/text()").extract()))

        cond_set(product, 'brand', response.xpath(
            "//div[contains(@class,'product_middle')]"
            "/div/a[@id='brand']/text()").extract())

        cond_set(product, 'price', map(string.strip, response.xpath(
            "//div[@id='item_price']/div/text()").extract()))

        cond_set(product, 'upc', map(int, response.xpath(
            "//form[@id='addItemToCart']"
            "/input[@id='id_unit']/@value").extract()))

        desc = response.xpath("//div[contains(@class,'item-desc')]").extract()
        if desc:
            cond_set_value(product, 'description', desc, conv=''.join)

        product['related_products'] = {}

        # internal related-products
        res = response.xpath(
            "//section[contains(@class,'gallery-container')]"
            "/ul/li[not(contains(@class,'hide'))]/a")
        if len(res) > 0:
            prodlist = []
            for r in res:
                try:
                    url = r.xpath("@href").extract()[0]
                    if url.startswith("/"):
                        url = urlparse.urljoin(response.url, url)
                    title = r.xpath(
                        "span[contains(@class,'item-name')]"
                        "/text()").extract()[0].strip()

                    prodlist.append(RelatedProduct(title, url))
                except:
                    pass
            if prodlist:        
                product['related_products']["recommended"] = prodlist

        # Extrenal
        product_or_request = product
        res = response.xpath(
            "//script[contains(text(),'aBoxes')]").re(r'.*aBoxes = (.*);')

        if len(res) > 0:
            text = res[0]
            badjson = ConvertBadJson()
            nodes = ast.parse(text)
            badjson.visit(nodes)
            boxes = badjson.get_result()

            data = {
                'action': 'ajaxRemote',
                'type': 'getItemsBoxes',
                'sItemType': '',
                'sItemTitle': '',
                'sRef': ''
            }
            for k, v in boxes:
                data['aBoxes' + k] = v

            new_meta = response.meta.copy()

            product_or_request = FormRequest.from_response(
                response=response,
                url=self._RECOM_URL,
                method='POST',
                formdata=data,
                callback=self._parse_recomendar,
                meta=new_meta)

        return product_or_request

    def _parse_recomendar(self, response):

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        product = response.meta['product']
        try:
            jdata = json.loads(response.body)
        except:
            return product

        htmldata = jdata['html']
        hxs = Selector(text=htmldata)

        if not htmldata:
            self.log("AJAX: Empty htmldata", ERROR)
            return product

        res = hxs.xpath("//section/ul/li/a")
        self.log('AJAX_VIP_INTERESTS_LIST %s elements' % len(res), DEBUG)
        if len(res) > 0:
            prodlist = []
            for r in res:
                try:
                    title = r.xpath("@title").extract()[0]
                    url = r.xpath("@href").extract()[0]
                    if url.startswith("/"):
                        url = full_url(url)
                    prodlist.append(RelatedProduct(title, url))
                except:
                    pass
            product['related_products']["vip_interests"] = prodlist

        res = hxs.xpath(
            "//div[contains(@class,'box-style-featuerd')]"
            "/div[contains(@class,'feature-items-box')]/a")

        self.log('AJAX_RELATED_PRODUCTS_LIST %s elements' % len(res), DEBUG)
        if len(res) > 0:
            prodlist = []
            for r in res:
                try:
                    url = r.xpath("@href").extract()[0]
                    if url.startswith("/"):
                        url = full_url(url)
                    rr = r.xpath("../text()")
                    text = rr.extract()[-1].strip()
                    prodlist.append(RelatedProduct(text, url))
                except:
                    pass
            product['related_products']["featured"] = prodlist
        return product

    def _scrape_total_matches(self, response):
        total = response.xpath(
            "//div[@id='search-results-title']"
            "/b/text()").extract()
        if len(total) > 0:
            total = total[-1]
            try:
                return int(total)
            except ValueError:
                return 0
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[@id='ItemResultList']"
            "/div[contains(@class,'single-item-browse')]"
            "/table/tr/td/a/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath(
            "//ul[contains(@class,'paginator')]"
            "/li/a[@class='paginator-next']/@href")
        if len(next) > 0:
            return next.extract()[0]
