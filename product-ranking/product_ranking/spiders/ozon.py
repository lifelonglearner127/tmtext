from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse
import re
import json
import urllib

from scrapy.log import ERROR, DEBUG, WARNING
from scrapy.http import FormRequest, Request

from product_ranking.items import SiteProductItem, RelatedProduct, \
                                    Price, BuyerReviews
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

    BUYER_REVIEWS_URL = "http://www.ozon.ru/DetailLoader.aspx?module=comments&" \
                        "id={product_id}&sort=&perPage={per_page}&page={page}&loadForm=true"

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

        # Product ID
        product_id = is_empty(
            re.findall(r'id\/(\d+)\/', response.url)
        )
        response.meta['product_id'] = product_id

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
        else:
            product['price'] = None

        # Set if out of stock
        is_out_of_stock = is_empty(
            response.xpath(
                '//div[@id="PageContent"]'
                '//div[@class="bSaleColumn"]'
                '//span[@class="eSale_Info mInStock"]/text()'
            ).extract(), ''
        )

        if is_out_of_stock.strip() != u'\u041d\u0430 \u0441\u043a\u043b\u0430\u0434\u0435.':
            product['is_out_of_stock'] = True
        else:
            product['is_out_of_stock'] = False

        # Set description and brand
        # TODO: refactor this odd piece of code
        desc = response.xpath('//div[@class="bDetailLogoBlock"]/node() |'
                              '//div[@id="js_additional_properties"]'
                              '/div[@class="bTechDescription"]/node() |'
                              '//div[@itemprop="description"] |'
                              '//div[@id="detail_description"]')

        if desc:
            # m = re.search(r'{model}:([^,<\n]+)'.format(
            #     model=u'\u041c\u043e\u0434\u0435\u043b\u044c'
            # ), desc)
            # if m:
            #     cond_set_value(product, 'model', m.group(1).strip())

            product['description'] = is_empty(
                desc.extract()
            ).strip()

        # TODO: refactor brand
        # Set brand
        brand = is_empty(
            response.xpath(
                '//a[contains(@href, "/brand/")]/text()'
            ).extract(), ''
        ).strip()

        if brand:
            product['brand'] = brand
        else:
            brand = is_empty(
                response.xpath(
                    '//a[@class="eItemBrand_logo"]/img/@alt |'
                    '//div[contains(@class, "bDetailLogoBlock")]/./'
                    '/a[contains(@href, "/brand/")]/text()'
                ).extract(), ''
            ).strip()
            product['brand'] = brand

        # Set locale
        product['locale'] = 'ru-RU'

        # Set category
        category_sel = response.xpath('//div[contains(@class, "bBreadCrumbs")]/'
                                      'a[contains(@class, "eBreadCrumbs_link")]/text()')
        if category_sel:
            category = category_sel[0].extract()
            product['category'] = category.strip()

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
                        url=self.RELATED_PRODS_URL,
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
                        url=self.RELATED_PRODS_URL,
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
            marketplace['price'] = product.get('price', None)
            marketplace['seller_type'] = 'site'

        mktplaces.append(marketplace)
        product['marketplace'] = mktplaces

        # Set buyer reviews
        reviews_url = self.BUYER_REVIEWS_URL.format(
            product_id=product_id,
            per_page=1000000,
            page=1
        )

        num_of_reviews_sel = response.xpath(
            '//a[contains(@class, "bProductRating_Stars")]/./'
            '/span/text() |'
            '//span[@class="eItemRatingStars_text"]/text()'
        )

        if num_of_reviews_sel:
            num_of_reviews = is_empty(
                re.findall(
                    r'(\d+)',
                    is_empty(num_of_reviews_sel.extract())
                ), 0
            )

            if num_of_reviews:
                response.meta['num_of_reviews'] = num_of_reviews
                reqs.append(
                    Request(
                        url=reviews_url,
                        callback=self.parse_buyer_reviews
                    )
                )
            else:
                product['buyer_reviews'] = BuyerReviews(
                    num_of_reviews=0,
                    average_rating=0,
                    rating_by_star={'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
                )

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

    def parse_buyer_reviews(self, response):
        meta = response.meta.copy()
        reqs = meta.get('reqs')
        product = meta.get('product')

        rating_by_star = {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
        num_of_reviews = int(meta['num_of_reviews'])
        star_sum = 0

        for star in rating_by_star.iterkeys():
            reviews_sel = response.xpath(
                '//meta[@itemprop="ratingValue"][@content={star}]'.format(
                    star=star
                )
            )

            if reviews_sel:
                num_of_star = len(reviews_sel)
                rating_by_star[star] = num_of_star
                star_sum += num_of_star * int(star)

        average_rating = round(star_sum / num_of_reviews)

        product['buyer_reviews'] = BuyerReviews(
            average_rating=average_rating,
            num_of_reviews=num_of_reviews,
            rating_by_star=rating_by_star
        )

        if reqs:
            self.send_next_request(reqs, response)

        return product

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
