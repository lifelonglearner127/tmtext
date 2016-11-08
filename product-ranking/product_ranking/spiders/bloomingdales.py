# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals
from datetime import datetime
import json
import random
import re
import string
import urllib
import urlparse

from scrapy.http import Request
from scrapy.log import DEBUG
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem, RelatedProduct, \
    BuyerReviews, Price
from product_ranking.spiders import BaseProductsSpider, FLOATING_POINT_RGEX, \
    cond_set, cond_set_value


# from http://assets.bloomingdales.com/navapp/web20/assets/combo
# /catalog.productDetail.member.responsive_head_script-min-17.js
class RTD(object):
    def __init__(self):
        self.rtd = self.a()

    def getRTD(self):
        return self.rtd

    @staticmethod
    def jsGetTime(dtime):
        diff = datetime(1970, 1, 1)
        return (dtime - diff).total_seconds() * 1000

    def h(self):
        return hex(int(self.jsGetTime(
            datetime.utcnow()) + random.random() * 65536))[2:]

    def a(self):
        return (
            self.h() + self.h() + self.h() + self.h()
            + self.h() + self.h() + self.h() + self.h())


class BloomingdalesProductsSpider(BaseProductsSpider):
    name = 'bloomingdales_products'
    allowed_domains = [
        "bloomingdales.com", "bloomingdales.ugc.bazaarvoice.com"]
    start_urls = []
    SEARCH_URL = (
        "http://www1.bloomingdales.com/shop/search"
        "?keyword={search_term}&x=0&y=0")
    SEARCH_SORTED_URL = (
        "http://www1.bloomingdales.com/shop/search/facetedmeta"
        "?edge=hybrid&keyword={search}"
        "&facet=false&pageIndex={pageno}&sortBy={sorting}&productsPerPage=96"
        "&bopsZipcode=10001&BopsRadius=0&")
    PRODUCT_URL = (
        "http://www1.bloomingdales.com/shop/catalog/product/newthumbnail"
        "/json?productId={id}&source=118")
    RATING_URL = (
        "http://bloomingdales.ugc.bazaarvoice.com/7130aa/{prodid}"
        "/reviews.djs?format=embeddedhtml")
    MULTIIDS_URL = (
        "http://www1.bloomingdales.com/shop/search/product/thumbnail"
        "?edge=hybrid&limit=none&keyword={search}&ids={ids}")

    SORT_MODES = {
        'default': 'ORIGINAL',
        'news': 'NEW_ITEMS',
        'best': 'BEST_SELLERS',
        'toprated': 'TOP_RATED',
        'pricelh': 'PRICE_LOW_TO_HIGH',
        'pricehl': 'PRICE_HIGH_TO_LOW'}
    SORTING = None

    def __init__(self, sort_mode='default', *args, **kwargs):
        if sort_mode:
            if sort_mode not in self.SORT_MODES:
                self.log('"%s" not in SORT_MODES')
                sort_mode = 'default'
            self.SORTING = self.SORT_MODES[sort_mode]

        self.pageno = 1
        self.prodnos = set()
        self.rtd = RTD()
        super(BloomingdalesProductsSpider, self).__init__(
            None,
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def start_requests(self):
        for request in super(BloomingdalesProductsSpider, self).start_requests():
            request.meta['dont_redirect'] = True
            request.meta['handle_httpstatus_list'] = [302, 301]
            if self.product_url:
                prod = SiteProductItem()
                prod['is_single_result'] = True
                prod['url'] = self.product_url
                yield Request(self.product_url,
                              self._parse_single_product,
                              meta={'product': prod})
            yield request.replace(callback=self.start1)

    def start1(self, response):
        if response.status == 302:
            return Request(response.url, self.start1, dont_filter=True,
                           meta=response.meta)
        if self._check_alert(response):
            return
        total = self._scrape_total_matches(response)
        response.meta['total_matches'] = total
        url = self._gen_req_url(response)
        return Request(
            url, meta=response.meta.copy(), callback=self._parse_next)

    def _gen_req_url(self, response):
        term = response.meta.get("search_term")
        term = urllib.quote(term)
        url = self.SEARCH_SORTED_URL.format(
            pageno=self.pageno, sorting=self.SORTING, search=term)
        return url

    def parse_product(self, response):
        product = response.meta['product']
        cond_set(product, 'title', response.xpath(
            '//div[@id="productName"]/text()').extract(),
            conv=string.strip)
        price = response.xpath(
            "//div[@class='singleTierPrice']/span[@itemprop='price']"
            "/text()").re(FLOATING_POINT_RGEX)
        if not price:
            price = product.get('price')
        if price:
            price = price[0].replace(',', '')
            product['price'] = Price(
                price=price, priceCurrency='USD')
        cond_set(product, 'image_url', response.xpath(
            "//div[@id='pdp_left_image']/div[@id='zoomerDiv']"
            "/img/@src").extract())
        cond_set(product, 'description', response.xpath(
            "//div[@id='pdp_tabs_body_left']").extract())
        cond_set(product, 'description',
                 response.css(
                     '.pdp_longDescription[itemprop=description]').extract())
        cond_set_value(product, 'locale', "en-US")

        productid = response.xpath(
            "//div[@id='productContainer']/input[@id='productId']"
            "/@value").extract() or response.css(
            '#productId::attr(value)').extract()
        catid = response.xpath(
            "//script[contains(text(),'BLOOMIES.pdp.categoryId = ')]").re(
            r"BLOOMIES.pdp.categoryId = \"(.*)\";")
        if not catid:
            catid = re.findall('CategoryID=(\d+)', response.url)
        if catid:
            catid = catid[0]
            response.meta['catid'] = catid
        ptype = response.xpath(
            "//script[contains(text(),'BLOOMIES.pdp.productType = ')]").re(
            r"BLOOMIES.pdp.productType = \"(.*)\";")
        if ptype:
            ptype = ptype[0]
            response.meta['ptype'] = ptype
        if productid:
            productid = productid[0]
            cond_set_value(product, 'model', productid)

            def cb(self, response):
                text = response.body_as_unicode().encode('utf-8')
                jdata = json.loads(text)
                try:
                    brand = jdata['productThumbnail']['brand']
                except KeyError:
                    brand = None
                except TypeError:
                    brand = None
                if brand:
                    cond_set_value(product, 'brand', brand)

                url = self.RATING_URL.format(prodid=product['model'])
                return Request(
                    url,
                    meta=response.meta.copy(),
                    callback=self._parse_bazaarv)
            return self._gen_product_request(response, productid, cb)
        return product

    def _gen_product_request(self, response, prodno, callback):
        url = self.PRODUCT_URL.format(id=prodno)
        new_meta = response.meta.copy()
        new_meta['prodcallback'] = callback
        return Request(url, meta=new_meta, callback=self._parse_prodjson, dont_filter=True)

    def _parse_prodjson(self, response):
        callback = response.meta.get('prodcallback')
        if callback:
            #return self._parse_bazaarv(response)
            return callback(self, response)
        raise AssertionError("_parse_prodjson")

    def _parse_bazaarv(self, response):
        product = response.meta['product']
        text = response.body_as_unicode().encode('utf-8')
        if response.status == 200:
            x = re.search(
                r"var materials=(.*),\sinitializers=", text, re.M + re.S)
            if x:
                jtext = x.group(1)
                jdata = json.loads(jtext)

                html = jdata['BVRRSourceID']
                sel = Selector(text=html)
                avrg = sel.xpath(
                    "//div[@id='BVRRRatingOverall_']"
                    "/div[@class='BVRRRatingNormalOutOf']"
                    "/span[contains(@class,'BVRRRatingNumber')]"
                    "/text()").extract()
                if avrg:
                    try:
                        avrg = float(avrg[0])
                    except ValueError:
                        avrg = 0.0
                else:
                    avrg = 0.0
                total = sel.xpath(
                    "//div[@class='BVRRHistogram']"
                    "/div[@class='BVRRHistogramTitle']"
                    "/span[contains(@class,'BVRRNonZeroCount')]"
                    "/span[@class='BVRRNumber']/text()").extract()
                if total:
                    try:
                        total = int(total[0])
                    except ValueError:
                        total = 0
                else:
                    total = 0

                hist = sel.xpath(
                    "//div[@class='BVRRHistogram']"
                    "/div[@class='BVRRHistogramContent']"
                    "/div[contains(@class,'BVRRHistogramBarRow')]")
                distribution = {}
                for ih in hist:
                    name = ih.xpath(
                        "span/span[@class='BVRRHistStarLabelText']"
                        "/text()").re("(\d) Heart")
                    try:
                        if name:
                            name = int(name[0])
                        value = ih.xpath(
                            "span[@class='BVRRHistAbsLabel']/text()").extract()
                        if value:
                            value = int(value[0])
                        distribution[name] = value
                    except ValueError:
                        pass
                if distribution:
                    reviews = BuyerReviews(total, avrg, distribution)
                    cond_set_value(product, 'buyer_reviews', reviews)
        productid = product['model']
        vertical = self._gen_rel_request(response, productid, 'PDP_ZONE_A',
                                         'Customers Also Viewed')
        return self._gen_rel_request(response, productid, 'PDP_ZONE_B',
                                     'You Might Also Like', vertical)

    def _gen_rel_request(self, response, productid, context, relation,
                         follow=None):
        url = "http://www1.bloomingdales.com/sdp/rto/request/recommendations"
        ptype = response.meta['ptype']
        catid = response.meta['catid']
        body = {
            'productId': productid,
            'categoryId': catid,
            'context': context,
            # 'context': 'PDP_ZONE_B',   # YOU MIGHT ALSO LIKE hor.
            # 'context': 'PDP_ZONE_A',    # CUSTOMERS ALSO VIEWED - vertical
            'requester': 'BCOM-NAVAPP',
            'visitorId': self.rtd.getRTD(),
            'isInternationalMode': 'No',
            'countryCode': 'US',
            'zipCode': '',
            'isRegistryMode': 'No',
            'maxRecommendations': 10,
            'productType': ptype
        }

        new_meta = response.meta.copy()
        new_meta['relation'] = relation
        new_meta['handle_httpstatus_list'] = [404, 415]
        new_meta['follow'] = follow
        req = Request(
            url, body=urllib.urlencode(body),
            method='POST',
            meta=new_meta,
            callback=self._parse_related,
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
        )
        return req

    def _parse_related(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        product = response.meta['product']
        text = response.body_as_unicode().encode('utf-8')
        if response.status == 200:
            jdata = json.loads(text)
            reqs = []
            rel = []
            if jdata.get('recommendedItems'):
                for el in jdata.get('recommendedItems'):
                    itemno = el.get('productId')

                    def cb(self, response):
                        text = response.body_as_unicode().encode('utf-8')
                        jdata = json.loads(text)
                        try:
                            title = jdata['productThumbnail']['shortDescription']
                            url = jdata['productThumbnail']['siteSemanticURL']
                            rel.append(RelatedProduct(title, full_url(url)))
                        except TypeError:
                            pass
                        if reqs:
                            req = reqs.pop(0)
                            return req
                        if rel:
                            relation = response.meta['relation']
                            related_products = product.get('related_products',
                                {})
                            related_products[relation] = rel
                            product['related_products'] = related_products
                        return response.meta['follow'] or product

                    reqs.append(self._gen_product_request(
                        response, itemno, cb))
                if reqs:
                    req = reqs.pop(0)
                    return req
        return response.meta['follow'] or product

    def _check_alert(self, response):
        alert = response.xpath(
            "//div[@id='breadcrumbs']/text()").re(
            r"We couldn't find a match for")
        return alert

    def _scrape_total_matches(self, response):
        total = response.xpath(
            "//h2[@id='productCount']/span/text()").extract()
        if total:
            try:
                return int(total[0])
            except ValueError:
                return
        return 0

    def _scrape_product_links(self, response):
        boxes = response.css('#thumbnails .thumbnailItem')
        boxes = boxes or response.css('div[class*=productThumbnail]')
        if not boxes:
            self.log("Found no product links.", DEBUG)
        for box in boxes:
            link = box.css('.shortDescription a::attr(href)')[0].extract()
            product = SiteProductItem()
            cond_set_value(product, 'price',
                           box.css('.priceBig::text').re('([\d,.]+)'))
            yield link, product

    def _scrape_next_results_page_link(self, response):
        if self._check_alert(response):
            return
        self.pageno += 1
        url = self._gen_req_url(response)
        return Request(
            url, meta=response.meta.copy(), callback=self._parse_next)

    def _parse_next(self, response):
        text = response.body_as_unicode().encode('utf-8')
        sel = Selector(text=text)
        plist = sel.xpath("//div[@id='metaProductIds']/text()").extract()
        if plist:
            jdata = json.loads(plist[0])
        else:
            jdata = []
            self.log("Sorry it part of site not implemented in spider")
        remaining = response.meta.get('remaining')
        if (len(jdata) > remaining):
            jdata = jdata[:remaining]
        for no in jdata:
            if no in self.prodnos:
                raise ValueError("DUPLICATE %s " % no)
            self.prodnos.add(no)
        jdata = [str(x) for x in jdata]
        ids = ",".join(jdata)
        term = response.meta.get("search_term")
        term = urllib.quote(term)
        url = self.MULTIIDS_URL.format(ids=ids, search=term)
        return Request(url, meta=response.meta.copy(), callback=self.parse)
