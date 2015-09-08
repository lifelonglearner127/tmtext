from __future__ import division, absolute_import, unicode_literals

import re
import urllib

from scrapy.http import Request

from product_ranking.items import SiteProductItem, RelatedProduct, \
    Price, BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults,\
    cond_set, cond_set_value

is_empty = lambda x, y=None: x[0] if x else y

class BabymonitorsdirectProductsSpider(BaseProductsSpider):
    """Spider for babymonitorsdirect.co.uk.

    scrapy crawl babymonitorsdirectcouk_products
    -a searchterms_str="baby monitor" [-a order=pricedesc]

    Note: some product where price market as 'DISCONTNUED' may
    be out of correct position during price order search.
    Note: This type of spider need first to crawl through all
    pagination page to count total_matches.
    """
    name = 'babymonitorsdirectcouk_products'
    allowed_domains = ["babymonitorsdirect.co.uk"]
    start_urls = []
    SEARCH_URL = "http://www.babymonitorsdirect.co.uk/catalogsearch/" \
                 "result/index/?dir={sort}&order={order}&q={search_term}"

    SEARCH_SORT = {
        'ASC': 'asc',
        'DESC': 'desc'
    }

    SEARCH_ORDER = {
        'relevance': 'relevance',
        'name': 'name',
        'price': 'price'
    }

    def __init__(self, order='relevance', *args, **kwargs):
        order = self.SEARCH_ORDER.get(order, 'relevance')
        formatter = FormatterWithDefaults(order=order, sort='asc')
        super(BabymonitorsdirectProductsSpider,
              self).__init__(formatter, *args, **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        product = response.meta['product']

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title)

        brand = response.xpath(
            '//div[@class="DetailRow"]/div[contains(text(), "Brand:")]'
            '/../div[@class="Value"]/a/text()'
        ).extract()
        cond_set(product, 'brand', brand)

        price = response.xpath(
            '//em[contains(@class, "ProductPrice")]/text()'
        ).extract()
        if not price:
            price = response.xpath(
                '//em[contains(@class, "ProductPrice")]/span/text()'
            ).extract()
        if price and 'DISCONTNUED' in price[0]:
            price = response.xpath(
                '//div[contains(@class, "RetailPrice")]'
                '/div[@class="Value"]/text()'
            ).extract()
            cond_set_value(product, 'is_out_of_stock', True)
        if price:
            price = re.findall("\d+", price[0])
            if len(price) >= 2:
                price = price[0] + "." + price[1]
            else:
                price = price[0]

            product["price"] = Price(
                price=price,
                priceCurrency="GBP"
            )

        is_out_of_stock = response.xpath(
            '//div[@class="DetailRow"]/div[contains(text(), "Availability:")]'
            '/../div[@class="Value"]/text()'
        ).extract()
        if is_out_of_stock:
            is_out_of_stock = is_out_of_stock[0]
        if "In Stock" in is_out_of_stock:
            cond_set(product, 'is_out_of_stock', ("False",))
        elif "Out of Stock" in is_out_of_stock:
            cond_set(product, 'is_out_of_stock', ("True",))
        else:
            is_out_of_stock = response.xpath(
                '//div[@class="CurrentlySoldOut"]/p[1]/text()'
            ).extract()
            if is_out_of_stock:
                is_out_of_stock = is_out_of_stock[0]
            if "this item is currently unavailable" in is_out_of_stock:
                cond_set(product, 'is_out_of_stock', ("False",))

        img_url = response.xpath(
            '//div[@class="ProductThumbImage"]/a/img/@src').extract()
        cond_set(product, 'image_url', img_url)

        des = response.xpath(
            '//div[@class="ProductDescriptionContainer"]').extract()
        cond_set(product, 'description', des)

        rp = []
        for prod in response.xpath('//ul[@class="ProductList"]/li'):
            prod_all = prod.xpath('div[@class="ProductDetails"]/strong/a')
            title = prod_all.xpath('text()').extract()
            url = prod_all.xpath('@href').extract()
            if title:
                title = title[0]
            if url:
                url = url[0]
            rp.append(RelatedProduct(title, url))
        cond_set_value(product, 'related_products', rp)

        cond_set_value(product, 'locale', 'en_GB')

        product["url"] = response.url

        # Reviews
        num_of_reviews = response.xpath(
            '//div[@class="DetailRow"]/div[contains(text(), "Rating:")]'
            '/../div[@class="Value"]/span/a/text()'
        ).extract()
        if num_of_reviews:
            num_of_reviews = re.findall("\d+", num_of_reviews[0])
            if num_of_reviews:
                num_of_reviews = int(num_of_reviews[0])
            if not num_of_reviews:
                num_of_reviews = None
        average_rating = response.xpath(
            '//div[@class="DetailRow"]/div[contains(text(), "Rating:")]'
            '/../div[@class="Value"]/img/@src'
        ).extract()
        if average_rating:
            average_rating = int(re.findall("IcoRating(\d)",
                                 average_rating[0])[0])
        if not average_rating:
            average_rating = 0
            num_of_reviews = 0
        buyer_reviews = BuyerReviews(num_of_reviews=int(num_of_reviews),
                                     average_rating=float(average_rating),
                                     rating_by_star={1: 0, 2: 0, 3: 0,
                                                     4: 0, 5: 0})
        if average_rating or num_of_reviews:
            cond_set_value(product, 'buyer_reviews', buyer_reviews)
            new_meta = response.meta.copy()
            new_meta['product'] = product
            return Request(url=response.url,
                           meta=new_meta,
                           callback=self._extract_reviews,
                           dont_filter=True)
        else:
            cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
            return product

    def _parse_title(self, response):
        title = is_empty(
            response.xpath(
                '//div[@class="BlockContent"]/'
                'h1/text() |'
                '//h1[@itemprop="name"]/text()').extract()
        )
        if title:
            title = title.strip()

        return title

    def _extract_reviews(self, response):
        product = response.meta['product']
        num, avg, by_star = product.get('buyer_reviews')

        stars = response.xpath('//ol[@class="ProductReviewList"]/'
                               'li/h4/img/@src').re('IcoRating(\d)')

        for i in stars:
            by_star[int(i)] += 1

        buyer_reviews = BuyerReviews(num_of_reviews=num,
                                     average_rating=avg,
                                     rating_by_star=by_star)

        cond_set_value(product, 'buyer_reviews', buyer_reviews)
        next_page = response.xpath('//p[@class="ProductReviewPaging"]/span'
                                   '/a[contains(text(),"Next")]/@href')\
            .extract()

        if next_page:
            new_meta = response.meta.copy()
            new_meta['product'] = product
            return Request(url=next_page[1], meta=new_meta,
                           callback=self._extract_reviews,
                           dont_filter=True)
        else:
            return product

    def _scrape_total_matches(self, response):
        if 'No products found' in \
                response.body_as_unicode():
            total_matches = 0
        else:
            total_matches = is_empty(
                response.xpath('//div[@class="sorter"]'
                               '/p[@class="amount"]'
                               '/text()').extract(), 0
            )
            if total_matches:
                total_matches = is_empty(
                    re.findall(
                        r'of (\d+) total',
                        total_matches
                    ), 0
                )

        return int(total_matches)

    def _scrape_results_per_page(self, response):
        num = is_empty(
            response.xpath('//div[@class="limiter"]'
                           '/select/option[@selected="selected"]'
                           '/text()').extract(), '0'
        )
        num = num.strip()

        return int(num)

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//ul[contains(@class, "products-grid")]/li[@class="item"]'
            '/h2[@class="product-name"]/a/@href').extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath(
            '//div[@class="CategoryPagination"]'
            '/div[@class="FloatRight"]/a/@href'
        )
        if links:
            ajax_link = links.extract()[0].strip().rstrip('#results')
            ajax_link += '&ajax=1'
            full_link = "http://www.babymonitorsdirect.co.uk/" + ajax_link
            return full_link
        return None
