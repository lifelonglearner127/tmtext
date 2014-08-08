from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function
from future_builtins import *

import urlparse

from scrapy.log import ERROR
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FormatterWithDefaults


class AmazonFreshProductsSpider(BaseProductsSpider):
    name = "amazonfresh_products"
    allowed_domains = ["fresh.amazon.com"]
    start_urls = []

    SEARCH_URL = "https://fresh.amazon.com/Search?browseMP={market_place_id}" \
        "&resultsPerPage=50&predictiveSearchFlag=false&recipeSearchFlag=false" \
        "&comNow=&input={search_term}"

    def __init__(self, location='southern_cali', *args, **kwargs):
        settings = get_project_settings()
        locations = settings.get('AMAZONFRESH_LOCATION')
        loc = locations.get(location, '')
        super(AmazonFreshProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(market_place_id=loc),
            *args,
            **kwargs
        )

    def parse_product(self, response):
        prod = response.meta['product']

        query_string = urlparse.parse_qs(urlparse.urlsplit(response.url).query)
        cond_set(prod, 'model', query_string['asin'])
        title = response.xpath('//div[@class="buying"]/h1/text()').extract()
        cond_set(prod, 'title', title)
        brand = response.xpath('//div[@class="byline"]/a/text()').extract()
        cond_set(prod, 'brand', brand)
        price = response.xpath(
            '//div[@class="price"]/span[@class="value"]/text()').extract()
        cond_set(prod, 'price', price)
        des = response.xpath('//*[@id="productDescription"]/p/text()').extract()
        cond_set(prod, 'description', des)
        img_url = response.xpath(
            '//div[@id="mainImgWrapper"]/img/@src').extract()
        cond_set(prod, 'image_url', img_url)
        cond_set(prod, 'locale', ['en-US'])
        prod['url'] = response.url
        return prod

    def _search_page_error(self, response):
        sel = Selector(response)

        try:
            found1 = sel.xpath('//div[@class="warning"]/p/text()').extract()[0]
            found2 = sel.xpath(
                '//div[@class="warning"]/p/strong/text()'
            ).extract()[0]
            found = found1 + " " + found2
            if 'did not match any products' in found:
                self.log(found, ERROR)
                return True
            return False
        except IndexError:
            return False

    def _scrape_total_matches(self, response):
        count = response.xpath('//div[@class="numberOfResults"]/text()').re(
            '(\d+)')[-1]
        if count:
            return int(count)
        return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[@class="itemDetails"]/h4/a/@href').extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        link = response.xpath(
            '//div[@class="pagination"]/a/@href').extract()[-1]
        return link
