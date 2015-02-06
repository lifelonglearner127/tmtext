from __future__ import division, absolute_import, unicode_literals

import json

from scrapy.log import ERROR, WARNING
from scrapy import Request
import urlparse
import urllib

from product_ranking.items import SiteProductItem, Price
from product_ranking.items import RelatedProduct, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value, \
    populate_from_open_graph


class SoapProductSpider(BaseProductsSpider):
    name = 'soap_products'
    allowed_domains = ["soap.com"]

    SEARCH_URL = "http://www.soap.com/buy?s={search_term}"
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
        'bestselling': "SortExpression=Bestselling%20(Descending)",
        'newest': "&SortExpression=New%20(Descending)",
    }

    SORTING = None

    def __init__(self, sort_mode=None, *args, **kwargs):
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
            meta=new_meta)

    def _parse_additional_links(self, response):
        prev_response = response.meta['prev_response']
        links = response.xpath(
            "//*[contains(concat( ' ', @class, ' ' ), "
            "concat( ' ', 'pdpLinkable', ' '))]/a/@href").extract()
        prev_response.meta['additional_links'] = links
        return super(SoapProductSpider, self).parse(prev_response)

    def parse_product(self, response):
        # with open("/tmp/soap-item.html", "w") as f:
        #     f.write(response.body_as_unicode().encode('utf-8'))
        prod = response.meta['product']

        populate_from_open_graph(response, prod)

        self._populate_from_html(response, prod)

        cond_set_value(prod, 'locale', 'en-US')  # Default locale.

        json_link = response.xpath(
            "//*[@id='soapcom']/head/link[@type='application/json+oembed']"
            "/@href"
        ).extract()[0]

        # This additional request is necessary to get the brand.
        new_meta = response.meta.copy()
        new_meta['handle_httpstatus_list'] = [404]

        # FIXME: generate urls from productid
        new_meta['url_related'] = "http://www.soap.com/qaps/BehaviorData!GetPageSlots.qs?ProductId=44480&PersonalizationMode=C&SkuCode=AUN-218"
        new_meta['url_reviews_detail'] = "http://www.soap.com/amazon_reviews/04/44/80/mosthelpful_Default.html"
        return Request(json_link, self._parse_brand_json, meta=new_meta)

    def _parse_brand_json(self, response):
        product = response.meta['product']
        if response.status == 200:
            data = json.loads(response.body_as_unicode())

            cond_set_value(product, 'brand', data.get('brand'))
            cond_set_value(product, 'model', data.get('title'))

        rel_url = response.meta['url_related']
        new_meta = response.meta.copy()
        new_meta['handle_httpstatus_list'] = [404]
        return Request(rel_url, self._parse_related, meta=new_meta)

    def _parse_related(self, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        product = response.meta['product']
        if response.status == 200:
            print "RELATED", response.url
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
                product['related_products'] = {"recommended": rel}

        rurl = response.meta['url_reviews_detail']
        new_meta = response.meta.copy()
        new_meta['handle_httpstatus_list'] = [404]
        return Request(rurl, self._parse_reviews_mosthelpful, meta=new_meta)

    def _parse_reviews_mosthelpful(self, response):
        product = response.meta['product']
        if response.status == 200:

            total = response.xpath(
                "//span[@class='pr-review-num']/text()").re(
                r"(\d+) REVIEWS")
            if total:
                try:
                    total = int(total[0])
                except ValueError:
                    total = 0

            avrg = response.xpath(
                "//span[contains(@class,'average')]/text()").extract()
            if avrg:
                avrg = float(avrg[0])

            stars = response.xpath("//div[@class='pr-info-graphic-amazon']/dl")
            distribution = {}
            for star in stars:
                starno = star.xpath(
                    "dd[contains(text(),'star')]/text()").re(
                    r"(\d+) star")
                if starno:
                    try:
                        starno = int(starno[0])
                    except ValueError:
                        starno = 0
                    revno = star.xpath("dd/text()").re(r"\((\d+)\)")
                    if revno:
                        try:
                            revno = int(revno[0])
                        except ValueError:
                            revno = 0
                        distribution[starno] = revno
            reviews = BuyerReviews(total, avrg, distribution)
            product['buyer_reviews'] = reviews
        return product

    def _populate_from_html(self, response, product):
        prices = response.xpath(
            "//*[@id='priceDivClass']/span/text()").extract()
        cond_set(product, 'price', prices)

        # The description is a possible <p> or just the text of the class,
        # each page is different.
        desc = response.xpath("//*[@class='pIdDesContent']").extract()
        cond_set_value(product, 'description', desc, conv=''.join)

        upcs = response.xpath("//*[@class='skuHidden']/@value").extract()
        cond_set(product, 'upc', upcs)

        # Override the title from other sources. This is the one we want.
        cond_set(
            product, 'title', response.css(
                '.productTitle h1 ::text').extract())
        self._unify_price(product)

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//*[contains(concat( ' ', @class, ' ' ), "
            "concat( ' ', 'pdpLinkable', ' '))]/a/@href"
        ).extract()

        if links:
            links.extend(response.meta['additional_links'])
        # print "LINKS=", len(links),len(self.urls)
        # for link in links:
        #     if link in self.urls:
        #         raise ValueError("DUPLICATE %s" % link)
        #     self.urls.add(link)

        if not links:
            self.log("Found no product links.", ERROR)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_total_matches(self, response):
        num_results = response.xpath(
            "//*[@class='result-pageNum-info']/span/text()").extract()
        # with open("/tmp/soap-links.html", "w") as f:
        #     f.write(response.body_as_unicode().encode('utf-8'))
        # print "NUM_RESULTS=", num_results
        if num_results and num_results[0]:
            return int(num_results[0])
        else:
            self.log("Failed to parse total number of matches.", level=ERROR)

    def _scrape_next_results_page_link(self, response):
        next_pages = response.css(
            "a:nth-child(3).result-pageNum-iconWrap::attr(href)").extract()
        # print "NEXT_PAGES=",next_pages
        next_page = None
        if next_pages:
            next_page = next_pages[0]
            if len(next_pages) > 2:
                self.log("Found more than two 'next page' links.", WARNING)
        return next_page

    def _unify_price(self, product):
        price = product.get('price')
        if price is None:
            return
        is_usd = not price.find('$')
        price = price[1:].replace(',', '')
        if is_usd and price.replace('.', '').isdigit():
            product['price'] = Price('USD', price)
