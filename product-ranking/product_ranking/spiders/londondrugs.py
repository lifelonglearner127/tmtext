from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set
from scrapy.log import ERROR


class LondondrugsProductsSpider(BaseProductsSpider):
    name = 'londondrugs_products'
    allowed_domains = ["londondrugs.com"]
    start_urls = []

    SEARCH_URL = \
        "http://www.londondrugs.com/on/demandware.store" \
        "/Sites-LondonDrugs-Site/default/Search-Show" \
        "?q={search_term}&simplesearch=Go"

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(product, 'brand', response.xpath(
            "//div[@id='product-title-bar']"
            "/h2[@itemprop='brand']/text()").extract())

        cond_set(product, 'title', map(string.strip, response.xpath(
            "//div[@id='product-title-bar']"
            "/h1[@itemprop='name']/text()").extract()))

        cond_set(product, 'price', map(string.strip, response.xpath(
            "//div[contains(@class,'price')]"
            "/div[@itemprop='price']/text()").extract()))

        cond_set(product, 'image_url', response.xpath(
            "//div[contains(@class,'productimages')]"
            "/div[@class='productimage']/img/@src").extract())

        cond_set(product, 'upc', map(int, response.xpath(
            "//div[@id='product-title-bar']"
            "/div[contains(@class,'productid')]/text()").re(r' L(\d*)')))

        j = response.xpath(
            "//div[@id='product-details-info']"
            "/div[@class='content']/div/ul"
            "/descendant::*[text()]/text()").extract()
        if j:
            info = ". ".join(j)
            product['description'] = info

        related = response.xpath(
            "//div[@class='recommendations_cross-sell']"
            "/div[contains(@class,'product')]")
        lrelated = []

        for rel in related:
            a = rel.xpath('div/div/p/a')
            link = a.xpath('@href').extract()[0]
            ltitle = a.xpath('img/@title').extract()[0]
            lrelated.append(RelatedProduct(ltitle, link))
        product['related_products'] = {"recomended": lrelated}

        cond_set(product, 'model', response.xpath(
            "//div[@class='pdp-features']/div[@class='attribute']"
            "/div[@class='label']/text()[contains(.,'Model')]"
            "/../../div[@class='value']/text()").extract())

        product['locale'] = "en-US"
        return product

    def _scrape_total_matches(self, response):
        total = response.xpath(
            "//div[@class='resultshits']"
            "/text()[contains(.,'matches')]").re(r'.*of (\d+)')
        if len(total) > 0:
            return int(total[0])
        total = response.xpath(
            "//div[@class='resultshits']/strong/text()").re(r'.*- (\d+)')
        if len(total) > 0:
            return int(total[0])
        else:
            return 0

    def parse(self, response):
        redirect_urls = response.meta.get('redirect_urls')
        if redirect_urls:
            response.meta['product'] = SiteProductItem(
                search_term=response.meta['search_term'])
            product = self.parse_product(response)
            product['site'] = self.site_name
            product['total_matches'] = 1
            product['ranking'] = 1
            return product
        else:
            return super(LondondrugsProductsSpider, self).parse(response)

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[@class='productlisting']/div[contains(@class,'product')]"
            "/div[@class='name']/a/@href")
        links = links.extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath(
            "//div[@class='pagination']/a[@class='pagenext']/@href")
        if next:
            next = next.extract()[0]
            next = urlparse.urljoin(response.url, next)
        return next
