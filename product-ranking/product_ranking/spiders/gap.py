# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

from itertools import islice
import json
import re
import urllib
import urlparse

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import cond_set, cond_set_value
from product_ranking.spiders import FLOATING_POINT_RGEX
from scrapy.http import Request
from scrapy.log import DEBUG, ERROR

is_empty = lambda x, y=None: x[0] if x else y

class GapProductsSpider(BaseProductsSpider):
    name = 'gap_products'
    allowed_domains = ["www.gap.com"]
    start_urls = ["http://www.gap.com"]
    SEARCH_URL = "http://www.gap.com/browse/search.do?searchText={search_term}"
    PRODUCT_URL_JS = (
        "http://www.gap.com/browse/productData.do?pid={pid}&vid={vid}"
        "&scid=&actFltr=false&locale=en_US&internationalShippingCurrencyCode="
        "&internationalShippingCountryCode=us&globalShippingCountryCode=us")

    PRODUCT_URL = "http://www.gap.com/browse/product.do?vid={vid}&pid={pid}"
    LINK_FORMAT = (
        "http://www.gap.com/resources/productSearch/v1/{query}?"
        "isFacetsEnabled=true"
        "&pageId={page_no}&globalShippingCountryCode=us&locale=en_US"
        "&segment=PVIDSEGC")
    BRAND = "GAP"
    DO_VARIANTS = True

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def start_requests(self):
        for request in super(GapProductsSpider, self).start_requests():
            request.meta['total_matches'] = 1
            yield request.replace(dont_filter=True)

    def parse_product(self, response):
        product = response.meta['product']
        vid = 1
        if "vid" in response.meta:
            vid = response.meta['vid']
        if 'OutOfStockNoResults' in response.url:
            self.log("Product OutOfStock %s %s" % (
                response.url, product), DEBUG)
            return

        if not product.get("price"):
            price = is_empty(
                response.xpath(
                    "//span[@id='priceText']/text() |" \
                    "//div[@id='tabWindow']/noscript"
                ).extract(),
                ""
            )
            price = is_empty(re.findall("\d+\.\d+", price)[::-1])
            if price:
                product["price"] = Price(price=price, priceCurrency="USD")

        title = product.get('title')
        if isinstance(title, str):
            product['title'] = title.decode('utf-8', 'ignore')
            title = product.get('title')
        else:
            title = is_empty(response.xpath(
                "//div[@id='productNameText']/h1/text()").extract())
            if title:
                product["title"] = title

        brindex = title.find("&#153")
        if brindex > 1:
            brand = title[:brindex]
            cond_set_value(product, 'brand', brand)
            # print "BRAND=", brand
        cond_set_value(product, 'brand', self.BRAND)
        cond_set(product, 'description', response.xpath(
            "//div[@id='tabWindow']").extract())
        product['locale'] = "en-US"

        new_meta = response.meta.copy()
        pid = product.get('upc')
        if not pid:
            pid = re.findall("pid=(\d+)", response.url)
            if pid:
                pid = pid[0]
        url = self.PRODUCT_URL_JS.format(pid=pid, vid=vid)
        return Request(
            url, callback=self._parse_product_js,
            meta=new_meta, priority=100)

    def _extract_variants(self, text):
        mlist = re.findall(r'(\d+)\]\.styleColorImagesMap = ([^;]*);', text)
        images = {}
        if mlist:
            for m in mlist:
                no = m[0]
                jstext = m[1]
                jstext = jstext.replace('\'', '"')
                jsdata = json.loads(jstext)
                try:
                    images[no] = jsdata['P01']
                except LookupError:
                    images[no] = ''

        mlist = re.findall(
            r'(\d+)\] = new objP\.StyleColor\("(\d+)",([^)]*)\);', text)
        variants = {}
        if mlist:
            for m in mlist:
                array_index = m[0]
                image = images.get(array_index)
                product_code = m[1]
                m1 = m[2].split(",")
                color = m1[0].replace('"', '')
                price = m1[7].replace('"', '')
                saleprice = m1[8].replace('"', '')
                variants[product_code] = {'array_index': array_index,
                                          'image': image,
                                          'color': color,
                                          'price': price,
                                          'saleprice': saleprice}
        return variants

    def _parse_product_js(self, response):
        product = response.meta['product']
        text = response.body_as_unicode().encode('utf-8')
        mlist = re.findall(r'new objP\.crossSellItem\((\d+),"([^"]*)"', text)
        recommended = []
        if mlist:
            for m in mlist:
                title = m[1]
                href = m[0]
                href = self.PRODUCT_URL.format(vid=1, pid=href)
                recommended.append(RelatedProduct(title, href))
        if recommended:
            product['related_products'] = {}
            product['related_products']["recommended"] = recommended

        variants = self._extract_variants(text)

        def get_price(v):
            price = v['saleprice']
            if price == 'undefined':
                price = v['price']
            return price

        prices = set([])
        ikeys = []
        for k in variants.keys():
            pr = get_price(variants[k])
            if pr not in prices:
                ikeys.append(k)
                prices.add(pr)

        self.log(
            "Product '%s' ikeys=%s prices=%s" % (
                product.get("title", ""),
                ikeys, prices), DEBUG)

        if len(ikeys) < 2:
            self.log("Product '%s' without variants. ikeys=%s" % (
                product.get("title", ""), ikeys), DEBUG)
            return product

        if len(prices) < 2:
            self.log("Product '%s' without variants. prices= %s" % (
                product.get("title", ""), prices), DEBUG)
            return product

        if not self.DO_VARIANTS:
            self.log("Skip variants by DO_VARIANTS", DEBUG)
            return product

        product_variants = []
        for k in ikeys:
            new_product = product.copy()
            try:
                new_product['upc'] = k
                #new_product['price'] = get_price(variants[k])
                price = FLOATING_POINT_RGEX.search(get_price(variants[k]))
                if price:
                    new_product['price'] = Price(price=price.group(),
                                                 priceCurrency='USD')
                new_product['model'] = "color: " + variants[k]['color']
                new_product['image_url'] = urlparse.urljoin(
                    response.url, variants[k]['image'])
                new_product['url'] = self.PRODUCT_URL.format(vid=1, pid=k)
            except KeyError:
                pass
            product_variants.append(new_product)
            self.upc_list.append(k)
        # print "upc_list=", len(self.upc_list), self.upc_list
        return product_variants

    def _parse_json_list(self, response):
        remaining = response.meta['remaining']
        link_query = response.meta['link_query']
        link_page = response.meta['link_page']

        jtext = response.body_as_unicode()
        try:
            jsdata = json.loads(jtext)
        except ValueError:
            self.log("Bad non-JS response %s" % response.url, ERROR)
            return

        search_result = jsdata[u'productCategoryFacetedSearch']
        product_category = search_result['productCategory']

        total = search_result['totalItemCount']
        total = int(total)

        if remaining > total:
            remaining = total

        if 'childProducts' not in product_category:
            return
        child_products = product_category['childProducts']

        if isinstance(child_products, dict):
            child_products = [child_products]
        prods_per_page = len(child_products)

        products = []
        st = response.meta.get("search_term")

        if not hasattr(self, 'upc_list'):
            self.upc_list = []

        for cp in child_products:
            upc = cp['businessCatalogItemId']
            self.upc_list.append(upc)

        for no, cp in enumerate(islice(child_products, 0, remaining), start=1):

            product = SiteProductItem()
            try:
                #product['price'] = cp['price']['currentMaxPrice']
                price = FLOATING_POINT_RGEX.search(cp['price']['currentMaxPrice'])
                if price:
                    product['price'] = Price(price=price.group(),
                                             priceCurrency='USD')
                product['image_url'] = cp['quicklookImage']['path']
                name = cp['name'].encode('utf-8')
                productid = cp['businessCatalogItemId']
                vid = cp['defaultSizeVariantId']
            except LookupError:
                pass

            product['title'] = name
            product['upc'] = productid
            product['search_term'] = st
            product['ranking'] = no
            product['total_matches'] = total
            product['site'] = self.site_name
            product['results_per_page'] = prods_per_page
            url = self.PRODUCT_URL.format(vid=vid, pid=productid)
            product['url'] = url

            product = Request(url=url, callback=self.parse_product,
                              meta={'product': product, 'search_term': st,
                                    'remaining': self.quantity,
                                    'total_matches': total, 'vid': vid})
            products.append(product)
            remaining -= 1

        if remaining > 0:
            link_page += 1
            link = self.LINK_FORMAT.format(query=link_query, page_no=link_page)
            new_meta = response.meta.copy()
            new_meta['link_page'] = link_page
            new_meta['remaining'] = remaining
            products.append(Request(link, callback=self._parse_json_list,
                            meta=new_meta))
        return products

    def _scrape_product_links(self, response):
        st = response.meta.get('search_term')
        st1 = urllib.quote(st.lower().replace(' ', '+')).replace('%', '!')
        link = self.LINK_FORMAT.format(query=st1, page_no=0)

        new_meta = response.meta.copy()
        new_meta['link_query'] = st1
        new_meta['link_page'] = 0

        yield Request(link, callback=self._parse_json_list,
                      meta=new_meta), SiteProductItem()
        return

    def _scrape_next_results_page_link(self, response):
        return None
