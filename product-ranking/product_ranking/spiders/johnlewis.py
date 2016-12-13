# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals

from collections import OrderedDict
import json
import re
import string
import urllib
import urlparse

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import FormatterWithDefaults
from product_ranking.spiders import cond_set, cond_set_value
from scrapy import Request
from scrapy import log
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
            log.msg("setApiKey not found in \n%s\n" % script, level=log.DEBUG)
            return
        m = re.match(
            r"^.*R3_COMMON.setSessionId\('(\S*)'\);", script, re.DOTALL)
        if m:
            self.rr_sessionid = m.group(1)
        else:
            log.msg(
                "setSessionId not found in \n%s\n" % script, level=log.DEBUG)
            return
        m = re.match(r"^.*R3_ITEM.setId\('(\S*)'\);", script, re.DOTALL)
        if m:
            self.rr_productid = m.group(1)
        else:
            log.msg("setId not found in \n%s\n" % script, level=log.DEBUG)
            return
        m = re.match(
            r"^.*R3_ITEM.addCategory\('([^\)]*)',\s'([^)]*)'\);.*",
            script, re.DOTALL + re.MULTILINE)
        if m:
            code = m.group(1)
            name = m.group(2)
            self.cs.append((code, name))
            self.rr_cs = "".join("|" + x + ":" + y for x, y in self.cs)
        else:
            log.msg(
                "addCategory not found in \n%s\n" % script, level=log.DEBUG)
            return

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
                log.msg(
                    "RicheRelevanceHelper need %s parm." % parm,
                    level=log.DEBUG)

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
                results[placement_type] = {'strategy': strategy,
                                           'items': items}
        else:
            raise AssertionError(
                "rr_recs = Not found in \n%s\n" % text.encode('utf-8'))
        return results


class JohnlewisProductsSpider(BaseProductsSpider):
    name = 'johnlewis_products'
    allowed_domains = ["www.johnlewis.com", "recs.richrelevance.com"]
    start_urls = []
    SEARCH_URL = "http://www.johnlewis.com/search/{search_term}" + \
        "?sortOption={sort_mode}"

    SORT_MODES = {
        "default": "Sort by: Relevance",
        "priceHigh": "Price: High - Low",
        "priceLow": "Price: Low - High",
        "AZ": "Alphabetically (A - Z)",
        "ZA": "Alphabetically (Z - A)",
        "New": "Newness",
        "popularity": "Popularity",
        "rating": "Rating",
    }

    def __init__(self, sort_mode="default", *args, **kwargs):
        if sort_mode not in self.SORT_MODES:
            self.log('"%s" not in SORT_MODES')
            sort_mode = 'default'
        formatter = FormatterWithDefaults(sort_mode=sort_mode)
        super(JohnlewisProductsSpider, self).__init__(
            formatter,
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        if 'page_not_found' in response.url:
            return
        product = response.meta['product']

        cond_set(
            product,
            'title',
            response.xpath(
                "//section/h1[@id='prod-title']"
                "/span[@itemprop='name']/text()").extract()
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

        # 2. try
        cond_set(
            product,
            'brand',
            response.xpath(
                "//section"
                "/descendant::div[contains(@class,'mod-brand-logo')]"
                "/a/img/@alt").extract(),
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

        reseller_id_regex = "/(p\d+)"
        reseller_id = re.findall(reseller_id_regex, response.url)
        reseller_id = reseller_id[0] if reseller_id else None
        cond_set_value(product, 'reseller_id', reseller_id)

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
            conv=lambda x: x.replace("$preview$", "")
        )

        # Text of description
        # description = response.xpath(
        #     "//div[@id='tabinfo-care-info']"
        #     "/descendant::*[text()]/text()").extract()

        # cond_set_value(
        #     product,
        #     'description',
        #     " ".join(line.strip()
        #              for line in description if len(line.strip()) > 0)
        # )

        description = response.xpath(
            "//div[@id='tabinfo-care-info']").extract()
        if description:
            description = "".join(description[0])
        cond_set_value(product, 'description', description)

        product['locale'] = "en-US"

        variants = self._parse_variants(response)
        rrhelper = RichRelevanceHelper()
        payload = rrhelper.prepare_johnlewis(response)
        if payload:
            new_meta = response.meta.copy()
            new_meta['rrs'] = rrhelper
            new_meta['variants'] = variants
            return Request(
                rrhelper.make_url(payload),
                self._parse_json,
                meta=new_meta)
        return self._populate_variants(response, product, variants)

    def _parse_variants(self, response):
        variants = response.meta.get('variants', OrderedDict())
        sizes = response.xpath("//div[@id='prod-product-size']")
        vsizes = OrderedDict()
        if sizes:
            sizes = sizes[0]
            slines = sizes.xpath("./ul/li")
            for sl in slines:
                name = sl.xpath("./a/span/text()").extract()
                if name:
                    name = name[0]
                    vsizes[name] = OrderedDict()
                    attrs = ["data-jl-sku", "data-jl-product-code",
                             "data-jl-stock", "data-jl-price", "data-jl-d2c"]
                    for attr in attrs:
                        value = sl.xpath("@%s" % attr).extract()
                        attrname = string.replace(attr, "data-jl-", "")
                        if value:
                            vsizes[name][attrname] = value[0]
        else:
            elements = response.css(
                "#prod-multi-product-types > "
                "section.mod-multi-product-types"
                ".mod-multi-product-types-new-section "
                "> div > ul "
                "> div[itemprop=offers] > li > div")
            for e in elements:
                size = e.css("div.left > h3::text").extract()
                if size:
                    size = size[0]
                else:
                    continue
                vsizes[size] = {}
                price = e.css("div.right > p > strong::text").extract()
                if price:
                    price = price[0]
                    vsizes[size]['price'] = price
                code = e.css("div.left > div > p::text").extract()
                if code:
                    code = code[0]
                    vsizes[size]['code'] = code
                stock = e.css(
                    "div.mod.mod-stock-availability"
                    "::attr(data-jl-stock)").extract()
                if stock:
                    stock = stock[0]
                    vsizes[size]['stock'] = stock
        image_url = response.xpath(
            "//meta[@property='og:image']/@content").extract()
        if image_url:
            image_url = image_url[0].replace("$preview$", "")
        colors = response.xpath("//div[@id='prod-product-colour']")
        if colors:
            colors = colors[0]
            cur_color_name = colors.xpath(
                "./div[@class='detail-pair']/p/text()").extract()
            if cur_color_name:
                cur_color_name = cur_color_name[0]
            clines = colors.xpath("./ul/li")
            for no, cl in enumerate(clines):
                cl_color = cl.xpath("./a/img/@title").extract()[0]
                variants[cl_color] = variants.get(cl_color, {})
                if cur_color_name == cl_color:
                    variants[cl_color]['image_url'] = image_url
                href = cl.xpath("./a/@href").extract()
                if href:
                    href = href[0]
                variants[cl_color]['href'] = urlparse.urljoin(
                    response.url, href)
                attrs = ["data-jl-sku", "data-jl-product-code",
                         "data-jl-stock", "data-jl-price", "data-jl-d2c"]
                for attr in attrs:
                    value = cl.xpath("@%s" % attr).extract()
                    attrname = string.replace(attr, "data-jl-", "")
                    if value:
                        variants[cl_color][attrname] = value[0]
            variants[cur_color_name]['sizes'] = vsizes

        if len(variants) == 0:
            variants['default-color'] = {}
            variants['default-color']['sizes'] = vsizes
            variants['default-color']['image_url'] = image_url
        return variants

    def _parse_variants_cb(self, response):
        product = response.meta['product']
        variants = self._parse_variants(response)
        response.meta['variants'] = variants
        return self._populate_variants(response, product, variants)

    def _populate_variants(self, response, product, variants):
        variants = response.meta.get('variants', {})
        if variants is None or len(variants) == 0:
            return product
        for k, v in variants.items():
            if 'sizes' in v:
                continue
            url = v['href']
            new_meta = response.meta.copy()
            request = Request(
                url, callback=self._parse_variants_cb, meta=new_meta)
            return request
        if len(variants) == 1:
            k = list(variants)[0]
            sizes = variants[k]['sizes']
            if len(sizes) == 0:
                return product
        prodlist = []
        for color, v in variants.items():
            image_url = variants[color]['image_url']
            if len(v['sizes']) == 0:
                new_product = product.copy()
                new_product['model'] = color
                new_product['price'] = v['price']
                if not '£' in new_product['price']:
                    self.log('Unknown currency at %s' % response.url)
                else:
                    new_product['price'] = Price(
                        price=new_product['price'].replace(',', '').replace(
                            '£', '').strip(),
                        priceCurrency='GBP'
                    )
                new_product['image_url'] = image_url
                stock = v['stock']
                if stock == '0':
                    new_product['is_out_of_stock'] = True
                prodlist.append(new_product)
            else:
                for size, sizeattrs in variants[color]['sizes'].items():
                    price = sizeattrs['price']
                    stock = sizeattrs['stock']
                    # print color, size, price, stock, image_url
                    new_product = product.copy()
                    new_product['model'] = color + ":" + size
                    new_product['price'] = price
                    new_product['image_url'] = image_url
                    if stock == '0':
                        new_product['is_out_of_stock'] = True
                    if 'code' in sizeattrs:
                        try:
                            new_product['upc'] = int(sizeattrs['code'])
                        except ValueError:
                            pass
                    prodlist.append(new_product)
        return prodlist

    def _parse_json(self, response):
        product = response.meta['product']
        variants = response.meta['variants']

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
        return self._populate_variants(response, product, variants)

    def _scrape_total_matches(self, response):
        total = response.xpath(
            "//section[@class='search-results']/header/h1/span/text()"
        ).extract()
        if not total:
            total = response.xpath(
                "//section[@class='search-results']/header/h1/text()"
            ).re(r'.*\((\d+)\)')
        if total:
            total = total[0]
            try:
                return int(total)
            except ValueError:
                return 0
        else:
            return 0

    def _scrape_brand_links(self, response):

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        gen_list = []
        count = response.meta.get('count')
        remaining = response.meta.get('remaining')

        links = response.xpath(
            "//div[@class='result-row']"
            "/article/a[@class='product-link']/@href").extract()

        pages_w_links = response.xpath(
            "//div[@id='content']/div/div/div/section/section"
            "/div/ul/li/a/@href").extract()

        stop_count = remaining

        for no, link in enumerate(links, start=count + 1):
            prod_item = SiteProductItem()

            prod_item['site'] = self.site_name
            prod_item['url'] = full_url(link)
            prod_item['search_term'] = response.meta['search_term']
            prod_item['total_matches'] = no + 1
            prod_item['results_per_page'] = no + 1

            # The ranking is the position
            prod_item['ranking'] = no

            new_meta = response.meta.copy()
            new_meta['product'] = prod_item

            gen_list.append(
                Request(
                    full_url(link),
                    callback=self.parse_product,
                    meta=new_meta))

            stop_count -= 1
            if stop_count < 1:
                break

        remaining -= len(links)
        if remaining <= 0:
            return gen_list

        new_meta = response.meta.copy()
        new_meta['remaining'] = remaining
        new_meta['count'] += len(links)
        total = self._scrape_total_matches(response)

        if len(links) == 0 and len(pages_w_links) > 0:
            pages_wlinks = response.meta['pages_wlinks'][:]

            for link in pages_w_links:
                pages_wlinks.insert(0, link)
            response.meta['pages_wlinks'] = pages_wlinks

        if total > len(links):
            # move to next  page
            next = self._scrape_next_results_page_link(response)
            if next:
                gen_list.append(
                    Request(
                        full_url(next),
                        self._scrape_brand_links,
                        meta=new_meta
                    )
                )
                return gen_list

        # move to next page_wlink
        if remaining > 0:
            # next
            pages_wlinks = response.meta['pages_wlinks']

            if not pages_wlinks:
                return gen_list

            new_pages_wlinks = pages_wlinks[:]
            url = new_pages_wlinks.pop(0)
            new_meta['pages_wlinks'] = new_pages_wlinks
            gen_list.append(
                Request(
                    full_url(url),
                    self._scrape_brand_links,
                    meta=new_meta
                )
            )
        return gen_list

    def _scrape_product_links(self, response):

        def full_url(url):
            return urlparse.urljoin(response.url, url)

        self.total_matched = 0

        links = response.xpath(
            "//div[@class='result-row']"
            "/article/a[@class='product-link']/@href").extract()

        if not links:
            no_results = response.xpath(
                "//div[@class='mod-important']/h1/text()").re(r'No results.*')
            if not no_results:
                # Exctract links form brand-page
                links = response.xpath(
                    "//div[@id='content']/div/div/div/section/section"
                    "/div/ul/li/a/@href").extract()

                url = full_url(links.pop(0))
                new_meta = response.meta.copy()
                new_meta['pages_wlinks'] = links
                new_meta['ranking'] = 1
                new_meta['count'] = 0
                new_meta['links'] = []
                yield Request(
                    url,
                    self._scrape_brand_links,
                    meta=new_meta), SiteProductItem()
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
