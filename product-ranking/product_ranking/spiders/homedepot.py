from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import re
import string
import urllib
import urlparse

from scrapy import Request, Selector
from scrapy.log import DEBUG

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FLOATING_POINT_RGEX
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.validation import BaseValidator

from lxml import html

is_empty =lambda x,y=None: x[0] if x else y

def is_num(s):
    try:
        int(s.strip())
        return True
    except ValueError:
        return False


class HomedepotValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['brand', 'price']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'description', 'special_pricing', 
        'bestseller_rank',
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = True  # ... duplicated requests?
    ignore_log_filtered = True  # ... filtered requests?
    test_requests = {
        'sdfsdgdf': 0,  # should return 'no products' or just 0 products
        'benny benassi': 0,
        'red car': [20, 150],
        'red stone': [40, 150],
        'musci': [110, 210],
        'funky': [10, 110],
        'bunny': [7, 90],
        'soldering iron': [30, 120],
        'burger': [1, 40],
        'hold': [30, 110],
    }


class HomedepotProductsSpider(BaseValidator, BaseProductsSpider):
    name = 'homedepot_products'
    allowed_domains = ["homedepot.com", "www.res-x.com"]
    start_urls = []

    settings = HomedepotValidatorSettings

    SEARCH_URL = "http://www.homedepot.com/s/{search_term}?NCNI-5"
    SCRIPT_URL = "http://www.res-x.com/ws/r2/Resonance.aspx"
    DETAILS_URL = "http://www.homedepot.com/p/getSkuDetails?itemId=%s"
    REVIEWS_URL = "http://homedepot.ugc.bazaarvoice.com/1999m/%s/" \
        "reviews.djs?format=embeddedhtml"

    product_filter = []

    def __init__(self, *args, **kwargs):
        # All this is to set the site_name since we have several
        # allowed_domains.
        super(HomedepotProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(
            product,
            'title',
            response.xpath("//h1[@class='product_title']/text()").extract())

        cond_set(
            product,
            'brand',
            response.xpath("//h2[@class='brandName']/span/text()").extract(),
            conv=string.strip)

        cond_set(
            product,
            'image_url',
            response.xpath(
                "//div[@class='product_mainimg']/img/@src |"
                "//img[@id='mainImage']/@src"
            ).extract())

        cond_set(
            product,
            'price',
            response.xpath(
                "//div[@class='pricingReg']"
                "/span[@itemprop='price']/text()").extract())

        if product.get('price', None):
            if not '$' in product['price']:
                self.log('Unknown currency at' % response.url)
            else:
                product['price'] = Price(
                    price=product['price'].replace(',', '').replace(
                        '$', '').strip(),
                    priceCurrency='USD'
                )

        if not product.get('price'):
            price = response.xpath(
                    "//div[@class='pricingReg']"
                    "/span[@itemprop='price']/text() |"
                    "//div[contains(@class, 'pricingReg')]/span[@itemprop='price']"
            ).re(FLOATING_POINT_RGEX)
            if price:
                product["price"] = Price(
                    priceCurrency="USD",
                    price=price[0]
                )

        cond_set(
            product,
            'model',
            response.xpath(
                "//h2[@class='internetNo']"
                "/span[@itemprop='productID']/text()").extract(),
            conv=str
        )

        upc = is_empty(re.findall(
            "ItemUPC=\'(\d+)\'", response.body))
        if upc:
            product["upc"] = upc

        desc = response.xpath(
            "//div[@id='product_description']"
            "/div[contains(@class,'main_description')]"
            "/descendant::*[text()]/text()"
            "//div[contains(@class, 'main_description')] |"
            "//div[@id='product_description']"
        ).extract()
        desc = " ".join(l.strip() for l in desc if len(l.strip()) > 0)
        product['description'] = desc

        product['locale'] = "en-US"

        metadata = response.xpath(
            "//script[contains(text(),'PRODUCT_METADATA_JSON')]"
            "/text()").re('var PRODUCT_METADATA_JSON = (.*);')
        skus = []
        if metadata:
            metadata = metadata[0]
            try:
                jsmeta = json.loads(metadata.replace(
                    'label:"', '"label":"').replace(
                    'guid: "', '"guid":"').replace(
                    ",]", "]")
                )
            except ValueError:
                print('+'*50)
                print(metadata.count('guid: "'))
                print('+'*50)
                fl=open('file.html', 'w')
                fl.write(metadata.replace(
                'label:"', '"label":"').replace(
                'guid: "', '"guid":"').replace(
                ",]", "]"))
                fl.close()
            try:
                #skus = jsmeta['attributeDefinition']['attributeLookup']
                skus = [jsmeta["attributeDefinition"]["defaultSku"]]
                response.meta['skus'] = skus
                metaname = jsmeta['attributeDefinition']['attributeListing'][0][
                    'label']
                response.meta['attributelabel'] = metaname
            except (KeyError, IndexError):
                self.log("Incomplete data from Javascript.", DEBUG)

        certona_url = self._gen_certona_url(response)
        if certona_url:
            new_meta = response.meta.copy()
            new_meta['product'] = product
            new_meta['handle_httpstatus_list'] = [404]
            return Request(
                certona_url,
                self._parse_certona,
                meta=new_meta,
                priority=1000,
            )

        if product.get("model"):
            return Request(
                url=self.REVIEWS_URL % (product.get("model"),),
                callback=self.parse_buyer_reviews,
                meta={"product": product},
                dont_filter=True,
            )

        return self._gen_variants_requests(response, product, skus)

    def _gen_variants_requests(self, response, product, skus):
        reqs = []

        for sku in skus:
            # if sku:
            #     sku = sku[len(sku)-1]
            new_product = product.copy()
            new_product['model'] = str(sku)

            new_meta = response.meta.copy()
            new_meta['product'] = new_product
            new_meta['handle_httpstatus_list'] = [404]
            url = self.DETAILS_URL % sku
            reqs.append(Request(
                url,
                self._parse_skudetails,
                meta=new_meta,
                priority=1000)
            )
        if not reqs:
            return product
        return reqs

    def _gen_certona_url(self, response):
        # changed version 4.2x -> 5.3x
        # appid = response.xpath("//input[@id='certona_appId']/@value").extract()
        # if not appid:
        #     print "no appid"
        #     return
        appid = 'homedepot01'
        critemid = response.xpath(
            "//input[@id='certona_critemId']/@value").extract()
        if not critemid:
            critemid = is_empty(re.findall("\"itemId\"\:\"(\d+)\"", response.body))
        if not critemid:
            return

        payload = {
            "appid": appid,
            "tk": "62903038691729",
            "ss": "181357350200414",
            "sg": "1",
            "pg": "210528030293062",
            "vr": "4.2x",
            "bx": "true",
            "sc": "PIPHorizontal1_rr",
            "ev": "product",
            "ei": critemid,
            "storenum": "121",
            "cb": "None",
        }
        return urlparse.urljoin(
            self.SCRIPT_URL, "?" + urllib.urlencode(payload))

    def _parse_certona(self, response):
        product = response.meta['product']

        if response.status == 404:
            # No further pages were found.
            return product

        m = re.match(r'None\((.*)\);', response.body_as_unicode())
        if m:
            js = m.group(1)
            jsdata = json.loads(js)

            try:
                html = jsdata['Resonance']['Response'][0]['output']
            except (KeyError, IndexError):
                html = None
        else:
            html = response.body_as_unicode()

        if html:
            sel = Selector(text=html)

            el = sel.xpath(
                "//div[contains(@class,'pod')]/div/div"
                "/a[@class='item_description']"
            )
            prods = []
            for e in el:
                href = e.xpath("@href").extract()
                if href:
                    href = href[0]
                name = e.xpath("text()").extract()
                if name:
                    name = name[0].strip()
                prods.append(RelatedProduct(
                    name, urlparse.urljoin(product['url'], href)))

            if prods:
                product['related_products'] = {"recommended": prods}

        skus = response.meta.get('skus', None)

        if not skus:
            if product.get("model"):
                return Request(
                    url=self.REVIEWS_URL % (product.get("model"),),
                    callback=self.parse_buyer_reviews,
                    meta={"product": product},
                    dont_filter=True,
                )
            return product
        return self._gen_variants_requests(response, product, skus)

    def _parse_skudetails(self, response):
        product = response.meta['product']

        try:
            jsdata = json.loads(response.body_as_unicode())
            storeskus = jsdata['storeSkus']
            price = storeskus['storeSku']['pricing']['originalPrice']
            product['price'] = price

            if product.get('price', None):
                if not '$' in product['price']:
                    self.log('Unknown currency at' % response.url)
                else:
                    product['price'] = Price(
                        price=product['price'].replace(',', '').replace(
                            '$', '').strip(),
                        priceCurrency='USD'
                    )

            desc = jsdata['info']['description']
            product['description'] = desc

            url = jsdata['canonicalURL']
            url = urlparse.urljoin(product['url'], url)
            product['url'] = url

            image = jsdata['inlinePlayerJSON']['IMAGE'][1]['mediaUrl']
            product['image_url'] = image

            attrname = response.meta.get('attributelabel', 'Color/Finish')
            colornames = jsdata['attributeGroups']['group'][0]['entries'][
                'attribute']
            colornames = [el['value'] for el in colornames
                          if el['name'] == attrname]
            if colornames:
                product['model'] = str(colornames[0])
        except (ValueError, KeyError, IndexError):
            self.log("Failed to parse SKU details.", DEBUG)


        if product.get("model"):
            return Request(
                url=self.REVIEWS_URL % (product.get("model"),),
                callback=self.parse_buyer_reviews,
                meta={"product": product},
                dont_filter=True,
            )

        return product

    def parse_buyer_reviews(self, response):
        product = response.meta.get("product")
        data = html.fromstring(response.body_as_unicode())
        rating_by_stars = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}

        avg = float(is_empty(is_empty(
            re.findall("\"avgRating\"\:(\d+(.\d+){0,1})", 
            response.body_as_unicode()
        ), []), 0))
        total = data.xpath(
            "//span[contains(@class, 'BVRRCount')]/strong/span/text()"
        ) or 0
        alls = data.xpath("//span[contains(@class, 'BVRRHistAbsLabel')]/text()")[:5]
        alls = [x.replace("(", "").replace(")", "").strip() for x in alls]
        alls.reverse()
        for i, rev in enumerate(alls):
            rating_by_stars[str(i+1)] = rev
        if total:
            total = is_empty(re.findall(
                FLOATING_POINT_RGEX,
                is_empty(total, "")
            ), 0)
        if avg:
            avg = float("{0:.2f}".format(avg))
        if avg and total:
            product["buyer_reviews"] = BuyerReviews(
                int(total.replace(",", "")), 
                float(avg), 
                rating_by_stars
            )
        else:
            product["buyer_reviews"] = ZERO_REVIEWS_VALUE
        
        return product

    def _scrape_total_matches(self, response):
        totals = response.xpath(
            "//a[@id='all_products']/label"
            "/text()").re(r'All Products \(([\d,]+)\)')
        if totals:
            totals = totals[0]
            totals = totals.replace(",", "")
            if is_num(totals):
                return int(totals)
        no_matches = response.xpath(
            "//h1[@class='page-title']/text()").extract()
        if no_matches:
            if 'we could not find any' in no_matches[0] or \
               'we found 0 matches for' in no_matches[0]:
                return 0
        return None

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[contains(@class,'product') "
            "and contains(@class,'plp-grid')]"
            "//descendant::a[contains(@class, 'item_description')]/@href").extract()

        if not links:
            self.log("Found no product links.", DEBUG)

        for link in links:
            if link in self.product_filter:
                continue
            self.product_filter.append(link)
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath(
            "//div[@class='pagination-wrapper']/ul/li/span"
            "/a[@title='Next']/@href |"
            "//div[contains(@class, 'pagination')]/ul/li/span"
            "/a[@class='icon-next']/@href"
        ).extract()
        if next:
            return urlparse.urljoin(response.url, next[0])
