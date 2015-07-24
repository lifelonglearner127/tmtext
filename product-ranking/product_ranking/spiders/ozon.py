from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse
import re

from scrapy.log import ERROR, DEBUG

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import (BaseProductsSpider, cond_set,
                                     FormatterWithDefaults, cond_set_value,
                                    _extract_open_graph_metadata, FLOATING_POINT_RGEX)


def clear_text(l):
    """
    useful for  clearing sel.xpath('.//text()').explode() expressions
    """
    return " ".join(
        [it for it in map(string.strip, l) if it])

is_empty = lambda x, y=None: x[0] if x else y


class OzonProductsSpider(BaseProductsSpider):
    name = 'ozon_products'
    allowed_domains = ["ozon.ru"]
    start_urls = []

    SEARCH_URL = ("http://www.ozon.ru/?context=search&text={search_term}"
                  "&sort={search_sort}")

    SEARCH_SORT = {
        'default': '',
        'price': 'price',
        'year': 'year',
        'rate': 'rate',
        'new': 'new',
        'best_sellers': 'bests'
    }

    def __init__(self, search_sort='default', *args, **kwargs):

        super(OzonProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort]
            ),
            *args, **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(product, 'title', response.xpath(
            '//h1[@itemprop="name"]/text()'
        ).extract(), string.strip)

        cond_set(product, 'image_url', response.xpath(
            '//div[@id="PageContent"]'
            '//img[@class="eBigGallery_ImageView"]/@src'
        ).extract())
        cond_set(product, 'image_url', response.xpath(
            '//div[@id="PageContent"]'
            '//*[@itemprop="image"]/@src'
        ).extract())
        if product.get('image_url'):
            product['image_url'] = urlparse.urljoin(
                response.url,
                product.get('image_url'))

        # Set price
        price_main = response.xpath(
            '//div[contains(@class, "bSaleBlock")]/'
            './/span[@class="eOzonPrice_main"]/text()'
        )
        price_submain = response.xpath(
            '//div[contains(@class, "bSaleBlock")]/'
            './/span[@class="eOzonPrice_submain"]/text()'
        )

        if price_submain:
            price_submain = is_empty(
                price_submain.extract()
            )
        else:
            price_submain = '00'

        if price_main:
            price_main = is_empty(
                price_main.extract()
            ).replace('\xa0', '')
            price = '{0}.{1}'.format(
                price_main.strip(),
                price_submain.strip()
            )
            product['price'] = Price(price=price,
                                     priceCurrency='RUB')

        cond_set(product, 'is_out_of_stock', response.xpath(
            '//div[@id="PageContent"]'
            '//div[@class="bSaleColumn"]'
            '//span[@class="eSale_Info mInStock"]/text()'
        ).extract(), lambda x:
            x.strip() != u'\u041d\u0430 \u0441\u043a\u043b\u0430\u0434\u0435.'
        )

        desc = ''
        desc1 = response.xpath('//div[@class="bDetailLogoBlock"]/node()')
        brand = desc1.xpath(
            './/a[contains(@href, "/brand/")]/text()').extract()

        if brand:
            cond_set_value(product, 'brand', ', '.join(brand))

        if desc1:
            desc = clear_text(desc1.extract())
            m = re.search(r'{model}:([^,<\n]+)'.format(
                model=u'\u041c\u043e\u0434\u0435\u043b\u044c'
            ), desc)
            if m:
                cond_set_value(product, 'model', m.group(1).strip())

        desc2 = response.xpath(
            '//div[@id="js_additional_properties"]'
            '/div[@class="bTechDescription"]/node()')
        brand = desc2.xpath(
            './/a[contains(@href, "/brand/")]/text()').extract()

        if brand:
            cond_set_value(product, 'brand', ', '.join(brand))

        if desc2:
            desc = '\n'.join([desc, clear_text(desc2.extract())])

        desc3 = response.xpath(
            '//div[@itemprop="description"]/div/table//td/node()'
        ).extract()
        if desc3:
            desc = '\n'.join([desc, clear_text(desc3)])

        cond_set_value(product, 'description', desc)
        cond_set_value(product, 'locale', 'ru-RU')

        return product

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _parse_related(self, response, link_selectors):
        related_products = []
        # for related_link in link_selectors:
        #     title = related_link.xpath('@title').extract()
        #     url = related_link.xpath('@href').extract()
        #
        #     if not url or not title or url[0] in response.url:
        #         continue
        #
        #     related_products.append(RelatedProduct(
        #         title[0],
        #         urlparse.urljoin(response.url, url[0])
        #     ))
        return related_products

    def _scrape_total_matches(self, response):
        total = None

        totals = response.xpath('//*[@class="bAlsoSearch"]/span[1]/text()') \
                         .re('\u041d\u0430\u0448\u043b\u0438 ([\d\s]+)')

        if totals:
            total = int(''.join(totals[0].split()))

        elif not response.xpath("//div[@calss='bEmptSearch']"):
            self.log(
                "Failed to find 'total matches' for %s" % response.url,
                ERROR
            )

        return total

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[@itemprop="itemListElement"]/a[@itemprop="url"]/@href'
        ).extract()

        if not links:
            self.log("Found no product links.", DEBUG)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):

        next = response.css('.SearchPager .Active') \
                       .xpath('following-sibling::a[1]/@href') \
                       .extract()

        if not next:
            link = None
        else:
            link = urlparse.urljoin(response.url, next[0])
        return link
