from __future__ import division, absolute_import, unicode_literals

import json
import urllib
import urlparse

from scrapy import Request
from scrapy.log import ERROR, WARNING

from product_ranking.items import RelatedProduct, BuyerReviews
from product_ranking.items import SiteProductItem, Price
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set
from product_ranking.spiders import FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set_value, populate_from_open_graph



# From PowerReview.groupPath()
def groupPath(groupId):
    b = groupId
    for x in range(0, 6 - len(b)):
        b = "0" + b
    b = b[0:2] + "/" + b[2:4] + "/" + b[4:]
    return b


class SoapProductSpider(BaseProductsSpider):
    name = 'soap_products'
    allowed_domains = ["soap.com"]

    SEARCH_URL = "http://www.soap.com/buy?s={search_term}&ref=srbr_so_unav"
    ADD_SEARCH = (
        "http://www.soap.com/SearchSite/ProductLoader.qs"
        "?IsPLPAjax=Y&originUrl={origin}&sectionIndex=1")
    SORT_MODES = {
        'relevance': "&SortExpression=Relevance",
        'highestrating': "&SortExpression=MergedRating%20(Descending)",
        'pricelh': "&SortExpression=Price%20(Ascending)",
        'pricehl': "&SortExpression=Price%20(Descending)",
        'nameaz': "&SortExpression=Name%20(Ascending)",
        'nameza': "&SortExpression=Name%20(Descending)",
        'bestselling': "&SortExpression=Bestselling%20(Descending)",
        'newest': "&SortExpression=New%20(Descending)",
    }

    SORTING = None

    def __init__(self, sort_mode=None, *args, **kwargs):
        from scrapy.conf import settings
        settings.overrides['DEPTH_PRIORITY'] = 1
        settings.overrides['SCHEDULER_DISK_QUEUE'] = 'scrapy.squeue.PickleFifoDiskQueue'
        settings.overrides['SCHEDULER_MEMORY_QUEUE'] = 'scrapy.squeue.FifoMemoryQueue'

        if sort_mode:
            if sort_mode.lower() not in self.SORT_MODES:
                self.log('"%s" not in SORT_MODES')
            else:
                self.SORTING = self.SORT_MODES[sort_mode.lower()]
                self.SEARCH_URL += self.SORTING
        self.urls = set()
        super(SoapProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def start_requests(self):
        for request in super(SoapProductSpider, self).start_requests():
            yield Request(
                url='http://www.soap.com', 
                meta=request.meta.copy(),
                callback=self._start_search
            )

    def _start_search(self, response):
        if "search_term" in response.meta:
            return Request(
                self.SEARCH_URL.format(search_term=response.meta['search_term']),
                meta=response.meta.copy())
        elif self.product_url:
            return Request(
                url=self.product_url, 
                meta=response.meta.copy(), 
                callback=self._parse_single_product
            )

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse(self, response):
        purl = urlparse.urlparse(response.url)
        purl = purl._replace(scheme='', netloc='')
        ref = urllib.quote(urlparse.urlunparse(purl))

        url = self.ADD_SEARCH.format(origin=ref)

        new_meta = response.meta.copy()
        new_meta['prev_response'] = response
        return Request(
            url,
            callback=self._parse_additional_links,
            meta=new_meta
        )

    def _parse_additional_links(self, response):
        prev_response = response.meta['prev_response']
        links = response.xpath(
            "//*[contains(concat( ' ', @class, ' ' ), "
            "concat( ' ', 'pdpLinkable', ' '))]/a/@href").extract()
        prev_response.meta['additional_links'] = links
        return super(SoapProductSpider, self).parse(prev_response)

    def parse_product(self, response):
        prod = response.meta['product']

        populate_from_open_graph(response, prod)

        self._populate_from_html(response, prod)

        cond_set_value(prod, 'locale', 'en-US')  # Default locale.
        plist = response.xpath(
            "//table[contains(@class,'gridItemList')]/tr[@id]")
        variants = []
        for pi in plist:
            inp = pi.xpath("*//input[@class='skuHidden']")
            if inp:
                inp = inp[0]
                value = inp.xpath("@value").extract()
                if value:
                    value = value[0]
                name = inp.xpath("@skuname").extract()
                if name:
                    name = name[0]
                pid = inp.xpath("@productid").extract()
                if pid:
                    pid = pid[0]
                price = inp.xpath("@displayprice").extract()
                if price:
                    price = price[0]
                outofstock = inp.xpath("@isoutofstock").extract()
                if outofstock:
                    outofstock = outofstock[0]
                variants.append(
                    {'name': name, 'price': price, 
                    'productid': pid, 'outofstock': outofstock, 
                    'value': value
                    }
                )
        response.meta['variants'] = variants

        json_link = response.xpath(
            "//*[@id='soapcom']/head/link[@type='application/json+oembed']"
            "/@href"
        ).extract()[0]

        # This additional request is necessary to get the brand.
        new_meta = response.meta.copy()
        new_meta['handle_httpstatus_list'] = [404]

        productid = response.xpath(
            "//input[@id='productIDTextBox']/@value").extract()

        #Reviews
        num_of_reviews = response.xpath(
            '//p[@class="pr-snapshot-average-based-on-text"]/span/text()'
        ).re(FLOATING_POINT_RGEX)
        average_rating = response.xpath(
            '//span[contains(@class, "average")]/text()'
        ).re(FLOATING_POINT_RGEX)
        rating_by_star = {1:0, 2:0, 3:0, 4:0, 5:0}
        all_marks = response.xpath(
            '//span[@class="pr-rating pr-rounded"]/text()').extract()
        for review in all_marks:
            rating_by_star[int(float(review))] += 1
        if average_rating and num_of_reviews:
            prod["buyer_reviews"] = BuyerReviews(
                num_of_reviews=int(num_of_reviews[0]), 
                average_rating=float(average_rating[0]), 
                rating_by_star=rating_by_star
            )
        else:
            prod["buyer_reviews"] = ZERO_REVIEWS_VALUE

        if productid:
            productid = productid[0]
            prodpath = groupPath(productid)

            new_meta['url_related'] = "http://www.soap.com" \
                "/qaps/BehaviorData!GetPageSlots.qs?" \
                "ProductId={pid}&PersonalizationMode=C&SkuCode={upc}".format(
                    pid=productid,
                    upc=prod['upc']
                )
            new_meta['url_reviews_detail'] = "http://www.soap.com" \
                "/amazon_reviews/{prodpath}/" \
                "mosthelpful_Default.html".format(
                    prodpath=prodpath
                )

        return Request(
            json_link, 
            self._parse_brand_json, 
            meta=new_meta, 
            dont_filter=True
        )

    def _parse_brand_json(self, response):
        product = response.meta['product']
        if response.status == 200:
            data = json.loads(response.body_as_unicode())

            cond_set_value(product, 'brand', data.get('brand'))
            # cond_set_value(product, 'model', data.get('title'))

        rel_url = response.meta.get('url_related')
        if rel_url:
            new_meta = response.meta.copy()
            new_meta['handle_httpstatus_list'] = [404]
            return Request(
                rel_url, self._parse_related, 
                meta=new_meta, dont_filter=True
            )

        del product["upc"]
        return product
        #return self._gen_variants(response)

    def _parse_related(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        product = response.meta['product']
        if response.status == 200:
            lfb = response.xpath(
                "//div[@class='frequentlyBought']"
                "/ul/li/a")
            frel = []
            for irel in lfb:
                name = irel.xpath('@title').extract()
                if name:
                    name = name[0]
                    href = irel.xpath('@href').extract()
                    if href:
                        href = full_url(href[0])
                        frel.append(RelatedProduct(url=href, title=name))
            rel = []
            lrel = response.xpath(
                "//div[@id='youMayAlsoLikeContainer']/div/div/ul/li"
                "/h2[@class='showName']/a")
            for irel in lrel:
                name = irel.xpath('@title').extract()
                if name:
                    name = name[0]
                    href = irel.xpath('@href').extract()
                    if href:
                        href = full_url(href[0])
                        rel.append(RelatedProduct(url=href, title=name))
            if rel:
                product['related_products'] = {"recommended": frel,
                                               "also_bought": rel}
        rurl = response.meta['url_reviews_detail']
        new_meta = response.meta.copy()
        new_meta['handle_httpstatus_list'] = [404]

        del product["upc"]
        return product
        #return Request(rurl, self._parse_reviews_mosthelpful, meta=new_meta, dont_filter=True)

    # def _parse_reviews_mosthelpful(self, response):
    #     product = response.meta['product']
    #     if response.status == 200:

    #         total = response.xpath(
    #             "//span[@class='pr-review-num']/text()").re(
    #             r"(\d+) REVIEWS")
    #         if total:
    #             try:
    #                 total = int(total[0])
    #             except ValueError:
    #                 total = 0

    #         avrg = response.xpath(
    #             "//span[contains(@class,'average')]/text()").extract()
    #         if avrg:
    #             avrg = float(avrg[0])

    #         stars = response.xpath("//div[@class='pr-info-graphic-amazon']/dl")
    #         distribution = {}
    #         for star in stars:
    #             starno = star.xpath(
    #                 "dd[contains(text(),'star')]/text()").re(
    #                 r"(\d+) star")
    #             if starno:
    #                 try:
    #                     starno = int(starno[0])
    #                 except ValueError:
    #                     starno = 0
    #                 revno = star.xpath("dd/text()").re(r"\((\d+)\)")
    #                 if revno:
    #                     try:
    #                         revno = int(revno[0])
    #                     except ValueError:
    #                         revno = 0
    #                     distribution[starno] = revno
    #         reviews = BuyerReviews(total, avrg, distribution)
    #         product['buyer_reviews'] = reviews
    #     return product
        #return self._gen_variants(response)

    # def _gen_variants(self, response):
    #     product = response.meta['product']
    #     variants = response.meta['variants']

    #     if not variants:
    #         raise AssertionError("NO VARIANTS FOR %s", product)

    #     varp = []
    #     for ivar in variants:
    #         vprod = product.copy()
    #         vprod['title'] = ivar['name']
    #         vprod['upc'] = ivar['productid']
    #         pricex = FLOATING_POINT_RGEX.search(ivar['price'])
    #         if pricex:
    #             price = pricex.group(0)
    #             vprod['price'] = Price(
    #                 price=price, priceCurrency='USD')
    #         if ivar['outofstock'] == 'Y':
    #             vprod['is_out_of_stock'] = True
    #         varp.append(vprod)
    #     return varp

    def _populate_from_html(self, response, product):
        prices = response.xpath(
            "//*[@id='priceDivClass']/span/text()").extract()
        cond_set(product, 'price', prices)

        # The description is a possible <p> or just the text of the class,
        # each page is different.
        desc = response.xpath("//*[@class='pIdDesContent']").extract()
        cond_set_value(product, 'description', desc, conv=''.join)

        if not desc:
            desc = response.xpath("//div[@class='descriptContent']").extract()
            if desc:
                del product['description']
                cond_set(product, 'description', desc)

        upcs = response.xpath("//*[@class='skuHidden']/@value").extract()
        cond_set(product, 'upc', upcs)

        # Override the title from other sources. This is the one we want.
        cond_set(
            product, 'title', response.css(
                '.productTitle h1 ::text').extract())
        self._unify_price(product)
        image_url = response.xpath(
            "//div[contains(@class,'productDetailPic')]"
            "/div/a/img/@src").extract()
        if image_url:
            image_url = image_url[0]
            if image_url.startswith("//"):
                image_url = 'http:' + image_url
            product['image_url'] = image_url

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//*[contains(concat( ' ', @class, ' ' ), "
            "concat( ' ', 'pdpLinkable', ' '))]/a/@href"
        ).extract()

        if links:
           links.extend(response.meta['additional_links'])
        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, response):
        num_results = response.xpath(
            "//*[@class='result-pageNum-info']/span/text()").extract()
        if num_results and num_results[0]:
            try:
                num_results = int(num_results[0])
            except:
                num_results = 0
            return num_results
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_next_results_page_link(self, response):
        next_pages = response.css(
            "a:nth-child(3).result-pageNum-iconWrap::attr(href)").extract()
        #next_page = None
        if next_pages:
            next_page = next_pages[0]
            if len(next_pages) > 2:
                self.log("Found more than two 'next page' links.", WARNING)
            return next_page
        return None

    def _unify_price(self, product):
        price = product.get('price')
        if price is None:
            return
        is_usd = not price.find('$')
        price = price[1:].replace(',', '')
        if is_usd and price.replace('.', '').isdigit():
            product['price'] = Price('USD', price)
