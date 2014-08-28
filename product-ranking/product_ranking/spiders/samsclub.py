from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set


class SamsclubProductsSpider(BaseProductsSpider):
    name = 'samsclub_products'
    allowed_domains = ["samsclub.com"]
    start_urls = []
    SEARCH_URL = "http://www.samsclub.com/sams/search/searchResults.jsp?searchCategoryId=all&searchTerm={search_term}&fromHome=no&_requestid=29417"

    def __init__(self, *args, **kwargs):
        super(SamsclubProductsSpider, self).__init__(
            #url_formatter=FormatterWithDefaults(pagenum=1, prods_per_page=32),
            *args, **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(product, 'brand', response.xpath(
            "//div[contains(@class,'prodTitlePlus')]/span[@itemprop='brand']/text()").extract())

        cond_set(product, 'title', response.xpath(
            "//div[contains(@class,'prodTitle')]/h1/span[@itemprop='name']/text()").extract())

        cond_set(product, 'image_url', response.xpath(
            "//div[@id='plImageHolder']/img/@src").extract())

        cond_set(product, 'price', response.xpath(
            "//div[@class='moneyBoxBtn']/a/span[contains(@class,'onlinePrice')]/text()").extract())

        j = response.xpath("//div[@itemprop='description']/descendant::*[text()]/text()")
        info = " ".join(j.extract())
        product['description'] = info

        productid = response.xpath("//span[@itemprop='productID']/text()")
        productid = productid.extract()[0].strip().replace('#:', '', 1)
        product['upc'] = int(productid)

        cond_set(product, 'model', response.xpath(
            "//span[@itemprop='model']/text()").extract())

        product['locale'] = "en-US"
        product['related_products'] = {}
        return product

    def _scrape_total_matches(self, response):
        if response.url.find('ajaxSearch') > 0:
            total = response.xpath("//body/li[contains(@class,'item')]")
            return len(total)
        total = response.xpath("//div[contains(@class,'shelfSearchRelMsg2')]/span/span[@class='gray3']/text()").extract()
        if total:
            return int(total[0])
        return None

    def _scrape_product_links(self, response):
        if response.url.find('ajaxSearch') > 0:
            links = response.xpath("//body/li/a/@href").extract()
        else:
            links = response.xpath("//ul[contains(@class,'shelfItems')]/li[contains(@class,'item')]/a/@href").extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        link = "http://www.samsclub.com/sams/shop/common/ajaxSearchPageLazyLoad.jsp" \
            "?sortKey=relevance&searchCategoryId=all&searchTerm={0}&noOfRecordsPerPage={1}" \
            "&sortOrder=0&offset=0&rootDimension=0&tireSearch=&selectedFilter=null" \
            "&pageView=list&servDesc=null&_=1407437029456"

        max_item = int(self._scrape_total_matches(response))
        search_term = response.meta['search_term']
        link = link.format(search_term, max_item + 11)
        return link
