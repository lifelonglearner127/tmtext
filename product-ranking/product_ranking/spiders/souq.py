from __future__ import division, absolute_import, unicode_literals

import ast
import json
import string
import urlparse

from scrapy.http import FormRequest
from scrapy.log import DEBUG, INFO, ERROR
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    populate_from_open_graph, cond_set_value
from product_ranking.spiders import FormatterWithDefaults


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

            if isinstance(v, basestring):
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
    SEARCH_URL = "http://uae.souq.com/ae-en/{search_term}/s/?sortby={sort_by}"
    _RECOM_URL = "http://uae.souq.com/ae-en/Action.php"

    SORT_MODES = {
        "default": "",
        "bestmatch": "",
        "popularity": "sr",
        "pricelh": "cp_asc",
        "pricehl": "cp_desc",
    }

    def __init__(self, sort_mode="default", *args, **kwargs):
        if sort_mode not in self.SORT_MODES:
            self.log('"%s" not in SORT_MODES')
            sort_mode = 'default'
        formatter = FormatterWithDefaults(sort_by=self.SORT_MODES[sort_mode])
        super(SouqProductsSpider, self).__init__(
            formatter,
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def _populate_from_open_graph(self, response, product):
        """Populates from Open Graph and discards description, which is fake.
        """
        populate_from_open_graph(response, product)

        if 'description' in product:
            del product['description']

    def parse_product(self, response):
        product = response.meta['product']

        self._populate_from_open_graph(response, product)

        cond_set(
            product,
            'title',
            response.xpath(
                "//h1[@id='item_title']/text()").extract(),
            conv=string.strip
        )

        cond_set(
            product,
            'brand',
            response.xpath(
                "//div[contains(@class,'product_middle')]"
                "/div/a[@id='brand']/text()").extract()
        )

        cond_set(
            product,
            'price',
            response.xpath(
                "//div[@id='item_price']/div/text()").extract(),
            conv=string.strip

        )

        # unify price
        currency = response.css('#item_price .currency::text') \
            or response.css('#item_price .price-holder span::text')
        price = product.get('price', '').replace(',', '')
        if price.replace('.', '').isdigit() and currency:
            currency = currency[0].extract()
            try:
                product['price'] = Price(currency, price)
            except ValueError:
                product['price'] = '%s %s' % (currency, price)

        cond_set(
            product,
            'upc',
            response.xpath(
                "//form[@id='addItemToCart']"
                "/input[@id='id_unit']/@value").extract(),
            conv=int
        )

        desc = response.xpath(
            "//div[@class='ui-tabs-panel']"
            "/div[contains(@class,'item-desc')]"
            "/descendant::*[text()]/text()").extract()
        if desc:
            cond_set_value(product, 'description', desc, conv=' '.join)

        product['related_products'] = {}

        # internal related-products
        res = response.xpath(
            "//section[contains(@class,'gallery-container')]"
            "/ul/li[not(contains(@class,'hide'))]/a")
        if res:
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
                except (ValueError, KeyError, IndexError):
                    pass
            if prodlist:
                product['related_products']["recommended"] = prodlist

        # Extrenal
        product_or_request = product
        res = response.xpath(
            "//script[contains(text(),'aBoxes')]").re(r'.*aBoxes = (.*);')

        if res:
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
        except ValueError:
            return product

        htmldata = jdata['html']
        hxs = Selector(text=htmldata)

        if not htmldata:
            self.log("AJAX: Empty htmldata", ERROR)
            return product

        res = hxs.xpath("//section/ul/li/a")
        self.log('AJAX_VIP_INTERESTS_LIST %s elements' % len(res), DEBUG)
        if res:
            prodlist = []
            for r in res:
                try:
                    title = r.xpath("@title").extract()[0]
                    url = r.xpath("@href").extract()[0]
                    if url.startswith("/"):
                        url = full_url(url)
                    prodlist.append(RelatedProduct(title, url))
                except (ValueError, KeyError, IndexError):
                    pass
            if prodlist:
                product['related_products']["vip_interests"] = prodlist

        res = hxs.xpath(
            "//div[contains(@class,'box-style-featuerd')]"
            "/div[contains(@class,'feature-items-box')]/a")

        self.log('AJAX_RELATED_PRODUCTS_LIST %s elements' % len(res), DEBUG)
        if res:
            prodlist = []
            for r in res:
                try:
                    url = r.xpath("@href").extract()[0]
                    if url.startswith("/"):
                        url = full_url(url)
                    rr = r.xpath("../text()")
                    text = rr.extract()[-1].strip()
                    prodlist.append(RelatedProduct(text, url))
                except (ValueError, KeyError, IndexError):
                    pass
            if prodlist:
                product['related_products']["featured"] = prodlist
        return product

    def _scrape_total_matches(self, response):
        if response.css('#box-results').re(
                'returns no results|did not match any products'):
            self.log("No products found.", INFO)
            return 0

        total = response.xpath(
            "//div[@id='search-results-title']"
            "/b/text()").extract()
        if total:
            total = total[-1]
            try:
                return int(total)
            except ValueError:
                self.log("Error while processing total.", ERROR)
                return None
        else:
            self.log("Found no product links.", ERROR)
            return None

    def _scrape_product_links(self, response):
        errmsg = response.xpath(
            "//div[@id='box-results']/div"
            "/div[contains(@class,'bord_b_dash')]/text()").re(
                "did not match any products. Did you mean:")
        if errmsg:
            return
        links = response.xpath(
            "//div[@id='ItemResultList']"
            "/div[contains(@class,'single-item-browse')]"
            "/table/tr/td/a/@href").extract()

        if not links:
            nomatches = response.css('#box-results').re('returns no results')
            if nomatches:
                self.log("No products links found.", INFO)
            else:
                self.log("Found no product links.", ERROR)
            return

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        errmsg = response.xpath(
            "//div[@id='box-results']/div"
            "/div[contains(@class,'bord_b_dash')]/text()").re(
                "did not match any products. Did you mean:")
        if errmsg:
            return
        next = response.xpath(
            "//ul[contains(@class,'paginator')]"
            "/li/a[@class='paginator-next']/@href")
        if next:
            return next.extract()[0]