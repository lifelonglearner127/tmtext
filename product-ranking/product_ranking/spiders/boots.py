# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals
from future_builtins import zip

from datetime import datetime
import json
import re
import string
import urllib
import urlparse
import ast

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.spiders import FormatterWithDefaults
from product_ranking.spiders import populate_from_open_graph
from scrapy import Request
from scrapy.log import ERROR
from scrapy.selector import Selector


class NormalizejsonHelper(ast.NodeVisitor):

    def __init__(self):
        self.result = []

    def write(self, x):
        self.result.append(x)

    def visit_Dict(self, node):
        self.write('{')
        for idx, (key, value) in enumerate(zip(node.keys, node.values)):
            if idx:
                self.write(', ')
            self.visit(key)
            self.write(': ')
            self.visit(value)
        self.write('}\n')

    def visit_List(self, node):
        self.write('[')
        for idx, item in enumerate(node.elts):
            if idx:
                self.write(', ')
            self.visit(item)
        self.write(']')

    def visit_Name(self, node):
        self.write('"' + node.id + '"')

    def visit_Num(self, node):
        self.write(repr(node.n))

    def visit_Str(self, node):
        text = node.s
        text = text.decode('utf-8')
        text = text.replace('"', '\\"')
        text = text.replace('\t', ' ')
        self.write('"' + text + '"')


class BootsProductsSpider(BaseProductsSpider):
    name = 'boots_products'
    allowed_domains = ["boots.com", "recs.richrelevance.com"]
    start_urls = []

    SEARCH_URL = \
        "http://www.boots.com/webapp/wcs/stores/servlet/SolrSearchLister" \
        "?storeId=10052&langId=-1&catalogId=11051" \
        "&stReq=1&searchTerm={search_term}#container"
    SEARCH_URL2 = \
        "http://www.boots.com/webapp/wcs/stores/servlet/SolrSearchLister" \
        "?storeId=10052&langId=-1&catalogId=11051" \
        "&stReq=1&searchTerm={search_term}&t1_sort={T1}&sortByProdOptCM={CM}#container"
    SCRIPT_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js?"
    SORT_MODES = {"bestmatch": {"CM": 0, "T1": 2},
                  "pricelh": {"CM": 1, "T1": 3},
                  "pricehl": {"CM": 2, "T1": 4},
                  "azbybrand": {"CM": 3, "T1": 1},
                  "zabybrand": {"CM": 4, "T1": 6},
                  "bestsellers": {"CM": 5, "T1": 7},
                  "toprated": {"CM": 6, "T1": 8},
                  "newest": {"CM": 7, "T1": 5},
                  "onpromotion": {"CM": 8, "T1": 9},
                  }

    def __init__(self, sort_mode=None, *args, **kwargs):
        formatter = None
        if sort_mode:
            if sort_mode in self.SORT_MODES:
                formatter = FormatterWithDefaults(
                    CM=self.SORT_MODES[sort_mode]['CM'],
                    T1=self.SORT_MODES[sort_mode]['T1'])
                self.SEARCH_URL = self.SEARCH_URL2

        super(BootsProductsSpider, self).__init__(
            formatter,
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        product = response.meta['product']

        populate_from_open_graph(response, product)

        cond_set(
            product,
            'title',
            response.xpath("//h1/span/text()").extract(),
            conv=string.strip,
        )

        cond_set(
            product,
            'upc',
            response.xpath("//p[@class='itemNumber']/span/text()").extract(),
            conv=int,
        )

        cond_set(
            product,
            'reseller_id',
            response.xpath("//p[@class='itemNumber']/span/text()").extract(),
            conv=string.strip,
        )

        cond_set(
            product,
            'price',
            response.xpath("//p[@class='productOfferPrice']/text()").extract(),
            conv=string.strip,
        )
        if product.get('price', None):
            if not '£' in product['price']:
                self.log('Unknown currency at' % response.url)
            else:
                product['price'] = Price(
                    price=product['price'].replace(',', '').replace(
                        '£', '').strip(),
                    priceCurrency='GBP'
                )

        cond_set(
            product,
            'brand',
            response.xpath("//div[@class='brandLogo']/a/img/@alt").extract(),
            conv=lambda s: None if not s.strip() else s,
        )
        # The following is a low quality source that uses an internal name
        # which sometimes includes extraneous words or numbers.
        # "div#brandHeader > a > img::attr(src)" also contains this ID.
        cond_set(
            product,
            'brand',
            response.xpath(
                "//form[@name='TMS_RR_PD']/input[@name='page_brand']/@value"
            ).extract(),
            conv=lambda s: s.replace('_', ' '),
        )

        content = response.xpath(
            "//div[@id='tab1content']"
            "/div[@id='productDescriptionContent']"
            "/descendant::*[text()]/text()").extract()
        if content:
            product['description'] = " ".join(
                line.strip() for line in content if len(line.strip()) > 0)

        product['locale'] = "en-GB"

        apikey = response.xpath(
            "//form[@name='TMS_RR']/input[@name='api_key']/@value").extract()
        if apikey:
            apikey = apikey[0]
        productid = response.xpath(
            "//form[@name='TMS_RR_PD']/input[@name='id']/@value").extract()
        if productid:
            productid = productid[0]
        pt = response.xpath(
            "//div[contains(@class,'gp_100a')]"
            "/div/div[@class='rr_block']/@id").extract()
        pts = set(pt)
        pts = u"|" + (u'|'.join(pts))
        sess = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1111.0)
        payload = {"a": apikey,
                   "p": productid,
                   "pt": pts,
                   "u": sess,
                   "s": sess,
                   "l": 1}
        script_url = self.SCRIPT_URL + urllib.urlencode(payload)
        new_meta = response.meta.copy()
        new_meta['product'] = product
        return Request(
            script_url,
            callback=self._process_richrelevance,
            meta=new_meta)

    def _process_richrelevance(self, response):
        product = response.meta['product']
        lists_names = {'item_page.rr2': 'buyers_also_bought',
                       'item_page.rr1': "recommended",
                       }
        product['related_products'] = {}
        text = response.body
        m = re.match(r'.*var rr_recs=(.*),rr_call_after_flush', text)
        if m:
            jstext = m.group(1)
            helper = NormalizejsonHelper()
            node = ast.parse(jstext)
            helper.visit(node)
            normalize_json = ''.join(helper.result)
            data = json.loads(normalize_json)
            placements = data.get('placements')
            for item in placements:
                placementtype = item.get('placementType')
                related_name = lists_names.get(placementtype)
                html = item.get('html')
                prodlist = []
                selector = Selector(text=html)
                items = selector.xpath("//div[@class='pdProductRecItem']/h5/a")
                for titem in items:
                    href = titem.xpath("@href").extract()
                    if href:
                        url = href[0]
                        url_split = urlparse.urlsplit(url)
                        query = urlparse.parse_qs(url_split.query)
                        original_url = query.get('ct')
                        if original_url:
                            original_url = original_url[0]
                    name = titem.xpath("text()").extract()
                    if name:
                        name = name[0]
                    prodlist.append(RelatedProduct(name, original_url))

                if prodlist:
                    related_name = lists_names.get(placementtype)
                    if related_name:
                        product['related_products'][related_name] = prodlist
            return product

    def _scrape_brand_links(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)

        gen_list = []
        remaining = response.meta.get('remaining')
        count = response.meta.get('count')

        links = response.xpath(
            "//div[@id='ProductViewListGrid']"
            "/div[contains(@class,'product_item')]"
            "/div/div/div[@class='pl_productName']"
            "/*/a[@class='productName']/@href").extract()

        stop_count = remaining
        for no, link in enumerate(links, start=count + 1):
            prod_item = SiteProductItem()
            prod_item['site'] = self.site_name
            prod_item['url'] = full_url(link)
            prod_item['search_term'] = response.meta['search_term']
            prod_item['total_matches'] = no
            prod_item['ranking'] = no
            new_meta = response.meta.copy()
            new_meta['product'] = prod_item
            gen_list.append(
                Request(
                    full_url(link),
                    callback=self.parse_product,
                    meta=new_meta))
            count += 1
            remaining -= 1
            stop_count -= 1
            if stop_count < 1:
                break

        if remaining < 1:
            return gen_list

        next_page_link = response.xpath(
            "//div[@class='productSearchResultsControls']"
            "//ul/li[@class='paginationTop']/ul"
            "/li[@class='next']/a/@href").extract()

        if next_page_link:
            url = next_page_link[0]
            new_meta = response.meta.copy()
            new_meta['remaining'] = remaining
            new_meta['count'] = count
            gen_list.append(Request(
                full_url(url),
                self._scrape_brand_links,
                meta=new_meta))
        else:
            new_meta = response.meta.copy()
            pages_wlinks = response.meta['pages_wlinks'][:]
            if not pages_wlinks:
                return
            next_url = pages_wlinks.pop(0)
            new_meta['pages_wlinks'] = pages_wlinks
            new_meta['remaining'] = remaining
            new_meta['count'] = count
            gen_list.append(Request(
                next_url,
                self._scrape_brand_links,
                meta=new_meta))
        return gen_list

    def _scrape_total_matches(self, response):
        total = response.xpath(
            "//div[@class='searchResultsSummary']"
            "/h1/span/text()").re(r'\((\d+)\)')
        if len(total) > 0:
            return int(total[0])
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[@class='productSearchResults']"
            "/div[@id='ProductViewListGrid']"
            "/div[contains(@class,'product_item')]"
            "/*/*/div[@class='pl_productName']/h5/a/@href").extract()

        no_results = response.xpath(
            "//div[@class='searchResultsSummary']"
            "/h1/text()").re(r'.*We\'re sorry.*could not find.*')

        if no_results:
            links = []

        if not links:
            menu_links = response.xpath(
                "//div[@class='narrowResults']/div/ul/li/a/@href").extract()
            url = menu_links.pop(0)
            new_meta = response.meta.copy()
            new_meta['pages_wlinks'] = menu_links
            new_meta['count'] = 0
            yield Request(
                url,
                self._scrape_brand_links,
                meta=new_meta), SiteProductItem()
            return

        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath(
            "//li[contains(@class,'paginationTop')]/ul"
            "/li[@class='next']/a/@href"
        ).re(r'javascript:.*setPageNumber\((.*)\);')
        if next:
            x = next[0]
            x = x.split(',')
            x = [e.replace("'", '').strip() for e in x]
            pname = x[0] + "_page"
            pvalue = x[1]

            url_parts = urlparse.urlsplit(response.url)
            query_string = urlparse.parse_qs(url_parts.query)

            query_string[pname] = pvalue

            url_parts = url_parts._replace(
                query=urllib.urlencode(query_string, True))
            link = urlparse.urlunsplit(url_parts)
            return link
        else:
            return None
