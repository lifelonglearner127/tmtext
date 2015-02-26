from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from datetime import datetime
import json
import re
import string
import urlparse

from product_ranking.items import Price
from product_ranking.items import SiteProductItem, RelatedProduct, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set, cond_set_value
from scrapy import Selector
from scrapy.http import Request
from scrapy.log import DEBUG


class SaksfifthavenueProductsSpider(BaseProductsSpider):
    # TODO: add brand-shop,sorting
    name = 'saksfifthavenue_products'
    allowed_domains = [
        "saksfifthavenue.com", "recs.richrelevance.com",
        "saksfifthavenue.ugc.bazaarvoice.com"]
    start_urls = []
    SEARCH_URL = (
        "http://www.saksfifthavenue.com/search/EndecaSearch.jsp"
        "?bmForm=endeca_search_form_one"
        "&bmIsForm=true&bmText=SearchString&SearchString={search_term}"
        "&submit-search=&bmSingle=N_Dim&N_Dim=0&bmHidden=Ntk&Ntk=Entire+Site")

    def __init__(self, sort_mode=None, *args, **kwargs):
        # if sort_mode:
        #     if sort_mode not in self.SORT_MODES:
        #         self.log('"%s" not in SORT_MODES')
        #         sort_mode = 'default'
        #     self.SEARCH_URL += self.SORT_MODES[sort_mode]

        super(SaksfifthavenueProductsSpider, self).__init__(
            None,
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def parse_product(self, response):
        with open("/tmp/saks-item.html", "w") as f:
            f.write(response.body_as_unicode().encode('utf-8'))

        product = response.meta['product']

        cond_set(product, 'title', response.xpath(
            "//header/h2[contains(@class,'short-description')]"
            "/text()").extract())
        cond_set(product, 'brand', response.xpath(
            "//header/h1[contains(@class,'brand-name')]/a/text()").extract(),
            conv=string.strip)
        jtext = response.xpath(
            "//script[contains(text(),'var mlrs =')]"
            "/text()").re('var mlrs = (.*)')
        jdata = json.loads(jtext[0])
        # pprint(jdata)

        tprice = jdata['response']['body'][
            'main_products'][0]['price']['sale_price']
        price = re.search(FLOATING_POINT_RGEX, tprice)
        if price:
            price = price.group(0)
            product['price'] = Price(
                price=price, priceCurrency='USD')

        upc = jdata['response']['body']['main_products'][0]['product_code']
        cond_set_value(product, 'upc', upc)

        description = jdata['response']['body'][
            'main_products'][0]['description']
        cond_set_value(product, 'description', description)

        media = jdata['response']['body']['main_products'][0]['media']
        image_url = "http:" + media['images_server_url'] + media['images_path'] + \
            media['images']['product_detail_image']
        cond_set_value(product, 'image_url', image_url)
        cond_set_value(product, 'locale', "en-US")

        bvurl = self._gen_bv_url(response)
        response.meta['bvurl'] = bvurl

        url = self._gen_rr_request(response)

        if url:
            return Request(
                url, meta=response.meta.copy(),
                callback=self._parse_rr)
        return product

    def _gen_rr_request(self, response):
        def jsGetTime():
            diff = datetime(1970, 1, 1)
            return (datetime.utcnow() - diff).total_seconds() * 1000
        product = response.meta['product']
        api = response.xpath(
            "//script[contains(text(),'R3_COMMON.setApiKey')]"
            "/text()").re(r"R3_COMMON\.setApiKey\('(.*)'\)")
        if api:
            api = api[0]
            # http://recs.richrelevance.com/rrserver/p13n_generated.js?a=a92d0e9f58f55a71&ts=1424835239426&cs=%7C0%3Atest&p=0432947704503&pt=%7Citem_page.content2&s=1424776912650O-T93NqpG6x9gPJTzIt99osOmThlw-hhk8mgFUElH3Byu8AJM7iXzur1&rcs=eF4FwbsNgDAMBcAmFaMgPSnPn9jZgD1wCgo6YH7u2nZ_z1V7OmhiqZY5ZCiE6O09D_O5unuBqgHrGWDVhIUL5yIj6wc0SBAV&l=1
            url = (
                "http://recs.richrelevance.com/rrserver/p13n_generated.js"
                "?a={api}"
                "&ts={ts}"
                "&cs=%7C0%3Atest"
                "&p={prodno}"
                "&pt=%7Citem_page.content2"
                "&l=1").format(
                    api=api, prodno=product['upc'],
                    ts=int(jsGetTime()))
            return url

    def _parse_rr(self, response):
        product = response.meta['product']
        text = response.body_as_unicode().encode('utf-8')
        rr_data = self._parse_rr_js(text)
        if rr_data:
            placements = {'item_page.content2': 'recommendation'}
            product['related_products'] = {}
            for place, value in rr_data.items():
                items = value['items']
                prodlist = []
                for item_name, item_url in items:
                    prodlist.append(RelatedProduct(item_name, item_url))
                pp_key = placements.get(place)
                if pp_key:
                    product['related_products'][pp_key] = prodlist
        bvurl = response.meta.get('bvurl')
        if bvurl:
            return Request(
                bvurl, meta=response.meta.copy(),
                callback=self._parse_bv)
        return product

    def _parse_rr_js(self, text):
        m = re.match(
            r"^.*var rr_recs=\{placements:\[\{(.*)\}\]\}",
            text, re.DOTALL)
        if m:
            data = m.group(1)
            m2 = re.findall(
                r"placementType:'([^']*)',html:'(([^\\']+|\\.)*)'",
                data, re.DOTALL)
            if m2:
                results = {}
                for pt in m2:
                    html = pt[1]
                    placementtype = pt[0]
                    results[placementtype] = {}

                    sel = Selector(text=html)
                    ilist = sel.xpath("//td[@class='rr_item']")
                    results[placementtype]['items'] = []
                    for iitem in ilist:
                        ilink = iitem.xpath("a/@href").extract()
                        if ilink:
                            ilink = ilink[0]
                            url_split = urlparse.urlsplit(ilink)
                            query = urlparse.parse_qs(url_split.query)
                            original_url = query.get('ct')[0]
                            iname = iitem.xpath(
                                "a/div[@class='rr_item_text']"
                                "/div[@class='medium']"
                                "/text()").extract()
                            if iname:
                                iname = iname[0]
                                iname = iname.encode('utf-8').decode('utf-8')
                                iname = iname.replace(u"\\'", u"'")
                                results[placementtype]['items'].append(
                                    (iname, original_url))
                    return results

    def _gen_bv_url(self, response):
        product = response.meta['product']
        url = (
            "http://saksfifthavenue.ugc.bazaarvoice.com/5000-en_us"
            "/{prodno}/reviews.djs"
            "?format=embeddedhtml").format(prodno=product['upc'])
        return url

    def _parse_bv(self, response):
        product = response.meta['product']
        text = response.body_as_unicode().encode('utf-8')
        if response.status == 200:
            x = re.search(
                r"var materials=(.*),\sinitializers=", text, re.M + re.S)
            if x:
                jtext = x.group(1)
                jdata = json.loads(jtext)
                html = jdata['BVRRRatingSummarySourceID']
                sel = Selector(text=html.encode('utf-8'))
                m = re.search(r'"avgRating":(.*?),', text, re.M)
                if m:
                    avrg = m.group(1)
                    try:
                        avrg = float(avrg)
                    except ValueError:
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
                        "/text()").re("(\d) star")
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
        return product

    def check_alert(self, response):
        alert = response.xpath("//span[@id='no-results-msg']").extract()
        print "ALERT=", alert
        return alert

    def _scrape_total_matches(self, response):
        if self.check_alert(response):
            return
        total = response.xpath(
            "//div[@class='pa-gination']"
            "/span[contains(@class,'totalRecords')]"
            "/text()").extract()
        # print "TOTAL=", total
        if total:
            total = total[0].replace(",", "")
            try:
                return int(total)
            except ValueError:
                return
        return 0

    def _scrape_product_links(self, response):
        with open("/tmp/saks-links.html", "w") as f:
            f.write(response.body_as_unicode().encode('utf-8'))
        if self.check_alert(response):
            return
        links = response.xpath(
            "//div[@id='product-container']"
            "/div[contains(@id,'product-')]"
            "/div[@class='product-text']/a/@href").extract()
        print "LINKS=", len(links), links[0], "..."
        if not links:
            self.log("Found no product links.", DEBUG)
        for link in links:
            yield link, SiteProductItem()
            # yield None, SiteProductItem(url=link)

    def _scrape_next_results_page_link(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        if self.check_alert(response):
            return
        next_page_links = response.xpath(
            "//ol[@class='pa-page-number']"
            "/li/a/img[@alt='next']"
            "/../@href").extract()
        # print "NEXT=", len(next_page_links), next_page_links
        if next_page_links:
            return full_url(next_page_links[0])
        else:
            return
