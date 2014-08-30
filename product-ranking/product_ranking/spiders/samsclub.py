from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


class SamsclubProductsSpider(BaseProductsSpider):
    name = 'samsclub_products'
    allowed_domains = ["samsclub.com"]
    start_urls = []

    SEARCH_URL = "http://www.samsclub.com/sams/search/searchResults.jsp" \
        "?searchCategoryId=all&searchTerm={search_term}&fromHome=no" \
        "&_requestid=29417"

    _NEXT_PAGE_URL = "http://www.samsclub.com/sams/shop/common" \
        "/ajaxSearchPageLazyLoad.jsp?sortKey=relevance&searchCategoryId=all" \
        "&searchTerm={search_term}&noOfRecordsPerPage={prods_per_page}" \
        "&sortOrder=0&offset={offset}&rootDimension=0&tireSearch=" \
        "&selectedFilter=null&pageView=list&servDesc=null&_=1407437029456"

    def parse_product(self, response):
        product = response.meta['product']

        # FIXME: This spider uses Schema.org data without considering the tree.
        cond_set(
            product,
            'brand',
            response.xpath(
                "//div[contains(@class,'prodTitlePlus')]"
                "/span[@itemprop='brand']/text()"
            ).extract())

        cond_set(
            product,
            'title',
            response.xpath(
                "//div[contains(@class,'prodTitle')]/h1/span[@itemprop='name']"
                "/text()"
            ).extract())

        cond_set(product, 'image_url', response.xpath(
            "//div[@id='plImageHolder']/img/@src").extract())

        cond_set(
            product,
            'price',
            response.xpath(
                "//div[@class='moneyBoxBtn']/a"
                "/span[contains(@class,'onlinePrice')]/text()"
            ).extract())

        cond_set(
            product,
            'description', [' '.join(
                response.xpath("//div[@itemprop='description']/descendant::*[text()]/text()").extract())
            ],
            conv=''.join,
        )

        productid = response.xpath("//span[@itemprop='productID']/text()").extract()
        if productid:
            productid = productid[0].strip().replace('#:', '', 1)
            try:
                product['upc'] = int(productid)
            except ValueError:
                self.log("Failed to parse upc number of matches: %r" % productid, ERROR)

        cond_set(product, 'model', response.xpath(
            "//span[@itemprop='model']/text()").extract())

        product['locale'] = "en-US"

        return product

    def _scrape_total_matches(self, response):
        if response.url.find('ajaxSearch') > 0:
            items = response.xpath("//body/li[contains(@class,'item')]")
            return len(items)

        totals = response.xpath(
            "//div[contains(@class,'shelfSearchRelMsg2')]"
            "/span/span[@class='gray3']/text()"
        ).extract()
        if totals:
            total = int(totals[0])
        elif response.css('.nullSearchShelfZeroResults'):
            total = 0
        else:
            total = None
        return total

    def _scrape_product_links(self, response):
        if response.url.find('ajaxSearch') > 0:
            links = response.xpath("//body/li/a/@href").extract()
        else:
            links = response.xpath(
                "//ul[contains(@class,'shelfItems')]"
                "/li[contains(@class,'item')]/a/@href"
            ).extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        # If the total number of matches cannot be scrapped it will not be set.
        num_items = min(response.meta.get('total_matches', 0), self.quantity)
        if num_items:
            return SamsclubProductsSpider._NEXT_PAGE_URL.format(
                search_term=response.meta['search_term'],
                offset=response.meta['products_per_page'] + 1,
                prods_per_page=num_items,
            )
        return None
