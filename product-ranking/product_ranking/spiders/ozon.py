from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse
import re
import json
import urllib

from scrapy.log import ERROR, DEBUG, WARNING
from scrapy.http import FormRequest, Request

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

    RELATED_PRODS_URL = "http://www.ozon.ru/json/shelves.asmx/getitemsitems"

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
        meta = response.meta.copy()
        product = meta['product']
        reqs = []

        # Set product title
        cond_set(product, 'title', response.xpath(
            '//h1[@itemprop="name"]/text()'
        ).extract(), string.strip)

        # Set image url
        # TODO: refactor this odd piece of code too
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

        # Set if out of stock
        cond_set(product, 'is_out_of_stock', response.xpath(
            '//div[@id="PageContent"]'
            '//div[@class="bSaleColumn"]'
            '//span[@class="eSale_Info mInStock"]/text()'
        ).extract(), lambda x:
            x.strip() != u'\u041d\u0430 \u0441\u043a\u043b\u0430\u0434\u0435.'
        )

        # Set description and brand
        # TODO: refactor this odd piece of code
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

        # Set locale
        cond_set_value(product, 'locale', 'ru-RU')

        # Set recommended products
        rel_prod_sel = response.xpath('//*[@class="bUniversalShelf"]/'
                                      './/ul[@class="eUniversalShelf_Tabs"]/'
                                      'li[contains(@class, "eUniversalShelf_Tab")]/@onclick')

        if rel_prod_sel:
            rel_prod_ids = is_empty(rel_prod_sel.extract())

            rel_prod_ids = is_empty(
                re.findall(
                    r'return\s+(.+)',
                    rel_prod_ids
                )
            )

            if rel_prod_ids:
                rel_prod_ids = rel_prod_ids.replace('\'', '"').replace(' ', '').replace('Ids', 'itemsIds')
                data = json.loads(rel_prod_ids)

                reqs.append(
                    Request(
                        self.RELATED_PRODS_URL,
                        method='POST',
                        callback=self.parse_recommended_prods,
                        body=json.dumps(data),
                        headers={'Content-Type': 'application/json'},
                    )
                )

        # Set also bought products
        also_bought = is_empty(
            re.findall(
                r"dataLayer.push\({\"ecommerce\":(.+)}\);",
                response.body_as_unicode()
            )
        )

        if also_bought:
            try:
                prod_ids = []
                data = json.loads(also_bought)

                ids = data['impressions']
                for item in ids:
                    prod_ids.append(item['id'])

                form_data = {
                    "Type": "Items",
                    "itemsIds": prod_ids
                }

                reqs.append(
                    Request(
                        self.RELATED_PRODS_URL,
                        method='POST',
                        callback=self.parse_also_bought_prods,
                        body=json.dumps(form_data),
                        headers={'Content-Type': 'application/json'},
                    )
                )
            except (KeyError, ValueError):
                self.log("Impossible to get also bought products info in %r" % response.url, WARNING)

        # Set matketplaces
        marketplace_sel = response.css('#js_merchant_name ::text')

        mktplaces = []
        marketplace = {}

        if marketplace_sel:
            marketplace_name = is_empty(
                marketplace_sel.extract()
            ).strip()
            marketplace['name'] = marketplace_name
            marketplace['price'] = product['price']
            marketplace['seller_type'] = 'seller'
        else:
            marketplace['name'] = self.allowed_domains[0]
            marketplace['price'] = product['price']
            marketplace['seller_type'] = 'site'

        mktplaces.append(marketplace)
        product['marketplace'] = mktplaces

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()

        if reqs:
            new_meta["reqs"] = reqs

        return req.replace(meta=new_meta)

    def parse_recommended_prods(self, response):
        meta = response.meta.copy()
        product = meta['product']
        related_products = product.get('related_products', {})
        reqs = meta.get('reqs')
        data = self._handle_related_product(response, 'recommended')

        if data:
            related_products['recommended'] = data
            product['related_products'] = related_products

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def parse_also_bought_prods(self, response):
        meta = response.meta.copy()
        product = meta['product']
        related_products = product.get('related_products', {})
        reqs = meta.get('reqs')
        data = self._handle_related_product(response, 'also_bought')

        if data:
            related_products['also_bought'] = data
            product['related_products'] = related_products

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _handle_related_product(self, response, rel_product_type):
        related_products = []

        try:
            data = json.loads(response.body_as_unicode())
            items = data['d']['Items']

            if items:
                for item in items:
                    title = item['Name']
                    href = '{www}{domain}{url}'.format(
                        www='http://www.',
                        domain=self.allowed_domains[0],
                        url=item['Href']
                    )

                    related_products.append(RelatedProduct(
                        title=title,
                        url=href
                    ))

                return related_products
        except (KeyError, ValueError):
            self.log("Impossible to get {0} products info in {1}".format(
                rel_product_type, response.url
            ), WARNING)
            return None

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
