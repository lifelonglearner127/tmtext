from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse

import ast
from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set
from scrapy.http import FormRequest
from scrapy.log import DEBUG, ERROR
from scrapy.selector import Selector
import simplejson


class ConvertBadJson(ast.NodeVisitor):
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

    def __init__(self, *args, **kwargs):
        super(SouqProductsSpider, self).__init__(
            #url_formatter=FormatterWithDefaults(pagenum=1, prods_per_page=32),
            *args, **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        product = response.meta['product']

        cond_set(product, 'title', map(string.strip, response.xpath(
            "//h1[@id='item_title']/text()").extract()))

        cond_set(product, 'brand', response.xpath(
            "//div[contains(@class,'product_middle')]/div/a[@id='brand']/text()").extract())

        cond_set(product, 'price', map(string.strip, response.xpath(
            "//div[@id='item_price']/div/text()").extract()))

        cond_set(product, 'image_url', response.xpath(
            "//meta[@property='og:image']/@content").extract())

        cond_set(product, 'locale', response.xpath(
            "//meta[@property='og:locale']/@content").extract())

        cond_set(product, 'upc', map(int, response.xpath(
            "//form[@id='addItemToCart']/input[@id='id_unit']/@value").extract()))

        desc = response.xpath(
            "//div[contains(@class,'item-desc')]/../descendant::*[text()]/text()").extract()
        info = " ".join([x.strip() for x in desc if len(x.strip()) > 0])
        product['description'] = info

        product['related_products'] = {}

        # internal related-products
        res = response.xpath("//section[contains(@class,'gallery-container')]/ul/li[not(contains(@class,'hide'))]/a")
        if len(res) > 0:
            prodlist = []
            for r in res:
                try:
                    url = r.xpath("@href").extract()[0]
                    if url.startswith("/"):
                        url = full_url(url)
                    title = r.xpath("span[contains(@class,'item-name')]/text()").extract()[0].strip()
                    prodlist.append(RelatedProduct(title, url))
                except:
                    pass
            product['related_products']["recomended"] = prodlist

        # Extrenal
        product_or_request = product
        res = response.xpath("//script[contains(text(),'aBoxes')]").re(r'.*aBoxes = (.*);')

        if len(res) > 0:
            text = res[0]
            badjson = ConvertBadJson()
            nodes = ast.parse(text)
            badjson.visit(nodes)
            boxes = badjson.get_result()

            data = {'action': 'ajaxRemote',
                    'type': 'getItemsBoxes',
                    'sItemType': '',
                    'sItemTitle': '',
                    'sRef': ''
                    }
            for k, v in boxes:
                data['aBoxes' + k] = v

            recom_url = "http://uae.souq.com/ae-en/Action.php"
            new_meta = response.meta.copy()

            product_or_request = FormRequest.from_response(
                response=response,
                url=recom_url,
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
            jdata = simplejson.loads(response.body)
        except:
            return product

        htmldata = jdata['html']
        hxs = Selector(text=htmldata)

        if not htmldata:
            self.log("AJAX: Empty htmldata", ERROR)
            return product

        res = hxs.xpath("//section/ul/li/a")
        self.log('AJAX_VIP_INTERESTS_LIST %s' % len(res), DEBUG)
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

        res = hxs.xpath("//div[contains(@class,'box-style-featuerd')]/div[contains(@class,'feature-items-box')]/a")
        self.log('AJAX_RELATED_PRODUCTS_LIST %s' % len(res), DEBUG)
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
        total = response.xpath("//div[@id='search-results-title']/b/text()").extract()
        if len(total) > 0:
            total = total[-1]
            try:
                return int(total)
            except:
                return 0
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[@id='ItemResultList']/div[contains(@class,'single-item-browse')]/table/tr/td/a/@href"
            ).extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath("//ul[contains(@class,'paginator')]/li/a[@class='paginator-next']/@href")
        #print "NEXT=", next.extract()[0]
        if len(next) > 0:
            return next.extract()[0]