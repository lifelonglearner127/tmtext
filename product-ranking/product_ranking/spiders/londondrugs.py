from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import cond_set, cond_set_value
from scrapy.log import DEBUG


class LondondrugsProductsSpider(BaseProductsSpider):
    name = 'londondrugs_products'
    allowed_domains = ["londondrugs.com"]
    start_urls = []

    SEARCH_URL = \
        "http://www.londondrugs.com/on/demandware.store" \
        "/Sites-LondonDrugs-Site/default/Search-Show" \
        "?q={search_term}&simplesearch=Go"

    SORT_MODES = {
        "default": "&srule=Default",
        "az": '&srule=Name%20A-Z',
        "za": '&srule=Name%20Z-A',
        "pricelh": "&srule=Price%20-%20Low%20to%20High",
        "pricehl": "&srule=Price%20-%20High%20to%20Low",
        "brandaz": "&srule=Brand%20A-Z",
        "brandza": "&srule=Brand%20Z-A",
        "bestsellers": "&srule=Bestsellers",
    }

    def __init__(self, sort_mode="default", *args, **kwargs):
        if sort_mode not in self.SORT_MODES:
            self.log('"%s" not in SORT_MODES')
            sort_mode = 'default'
        formatter = None
        self.SEARCH_URL = self.SEARCH_URL + self.SORT_MODES[sort_mode]
        super(LondondrugsProductsSpider, self).__init__(
            formatter,
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(
            product,
            'brand',
            response.xpath(
                "//div[@id='product-title-bar']"
                "/h2[@itemprop='brand']/text()").extract()
        )
        cond_set(
            product,
            'brand',
            response.xpath(
                "//div[contains(@id,'subProduct')]/div"
                "/div[contains(@class,'productinfo')]"
                "/div[@class='brand']/text()").extract()
        )
        cond_set_value(product, 'brand', 'NO BRAND')

        cond_set(
            product,
            'title',
            response.xpath(
                "//div[@id='product-title-bar']"
                "/h1[@itemprop='name']/text()").extract(),
            conv=string.strip
        )

        cond_set(
            product,
            'price',
            response.xpath(
                "//div[contains(@class,'price')]"
                "/div[@itemprop='price']/text()").extract(),
            conv=string.strip
        )

        cond_set(
            product,
            'image_url',
            response.xpath(
                "//div[contains(@class,'productimages')]"
                "/div[@class='productimage']/img/@src").extract()
        )

        cond_set(
            product,
            'upc',
            response.xpath(
                "//div[@id='product-title-bar']"
                "/div[contains(@class,'productid')]/text()").re(r' L(\d*)'),
            conv=int
        )

        cond_set(
            product,
            'description',
            response.xpath(
                "//div[@id='product-details-info']"
                "/div[@class='content']"
                "/div[@itemprop='description']").extract(),
        )
        cond_set(
            product,
            'description',
            response.xpath(
                "//div[@id='product-details-info']"
                "/div[@class='content']"
                "/div[@class='more-less-text']").extract(),
        )

        related = response.xpath(
            "//div[@class='recommendations_cross-sell']"
            "/div[contains(@class,'product')]")
        lrelated = []

        for rel in related:
            a = rel.xpath('div/div/p/a')
            link = a.xpath('@href').extract()[0]
            ltitle = a.xpath('img/@title').extract()[0]
            lrelated.append(RelatedProduct(ltitle, link))

        if lrelated:
            product['related_products'] = {"recommended": lrelated}

        cond_set(
            product,
            'model',
            response.xpath(
                "//div[@class='pdp-features']/div[@class='attribute']"
                "/div[@class='label']/text()[contains(.,'Model')]"
                "/../../div[@class='value']/text()").extract()
        )
        cond_set_value(product, 'url', response.url)
        product['locale'] = "en-US"
        return product

    def _scrape_total_matches(self, response):
        nohitsmessage = response.xpath(
            "//div[@id='search']/div[@class='nohits']"
            "/div[@class='nohitsmessage']"
            "/text()").re(
                "We're sorry, no products were found for your search:")
        if nohitsmessage:
            return 0
        total = response.xpath(
            "//div[@class='resultshits']"
            "/text()[contains(.,'matches')]").re(r'.*of ([\d,]+)')
        if total:
            total = total[0].replace(",", "")
            return int(total)

        total = response.xpath(
            "//div[@class='resultshits']/strong/text()").re(r'.*- ([\d,]+)')
        if total:
            total = total[0].replace(",", "")
            try:
                return int(total)
            except ValueError:
                return
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
        nohitsmessage = response.xpath(
            "//div[@id='search']/div[@class='nohits']"
            "/div[@class='nohitsmessage']"
            "/text()").re(
                "We're sorry, no products were found for your search:")
        if nohitsmessage:
            return
        links = response.xpath(
            "//div[@class='productlisting']/div[contains(@class,'product')]"
            "/div[@class='name']/a/@href")
        links = links.extract()

        if not links:
            self.log("Found no product links.", DEBUG)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        nohitsmessage = response.xpath(
            "//div[@id='search']/div[@class='nohits']"
            "/div[@class='nohitsmessage']"
            "/text()").re(
                "We're sorry, no products were found for your search:")
        if nohitsmessage:
            return
        next = response.xpath(
            "//div[@class='pagination']/a[@class='pagenext']/@href")
        if next:
            next = next.extract()[0]
            next = urlparse.urljoin(response.url, next)
            return next
