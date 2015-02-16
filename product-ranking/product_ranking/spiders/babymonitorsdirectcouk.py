from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re
import string
import urllib
import urlparse
import collections

from scrapy.log import WARNING

from scrapy.http import Request
from product_ranking.items import SiteProductItem, RelatedProduct, \
    Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults,\
    cond_set, cond_set_value


class BabymonitorsdirectProductsSpider(BaseProductsSpider):
    """Spider for babymonitorsdirect.co.uk.

    scrapy crawl babymonitorsdirectcouk_products
    -a searchterms_str="baby monitor" [-a order=pricedesc]

    -a order=bestselling used by default.

    Note: some product where price market as 'DISCONTNUED' may
    be out of correct position during price order.
    """
    name = 'babymonitorsdirectcouk_products'
    allowed_domains = ["babymonitorsdirect.co.uk"]
    start_urls = []
    SEARCH_URL = "http://www.babymonitorsdirect.co.uk/search.php?" \
        "search_query={search_term}"\
        "&section=product&ajax=1&sortBy={order}"

    page_number = 0
    _product_on_page = 16
    count_prod = 0

    SEARCH_SORT = {
        'relevance': 'relevance',
        'featured': 'featured',
        'newest': 'newest',
        'bestselling': 'bestselling', # default
        'alphaasc': 'alphaasc',
        'alphadesc': 'alphadesc',
        'avgcustomerreview': 'avgcustomerreview',
        'priceasc': 'priceasc',
        'pricedesc': 'pricedesc',
    }

    def __init__(self, order='bestselling', *args, **kwargs):
        order = self.SEARCH_SORT.get(order, 'bestselling')
        formatter = FormatterWithDefaults(order=order)
        super(BabymonitorsdirectProductsSpider, self
            ).__init__(formatter, *args, **kwargs)

    def start_requests(self):
        print 'get products match for all terms'
        for st in self.searchterms:
            url = self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8')),
                    dont_filter=False
                )
            yield Request(
                            url, 
                            callback=self.getResponse, 
                         )

    #Function count products on last page in pagination
    def count_prod_set(self, response):
        self.count_prod = 0
        for div in response.xpath('//ul[contains(@class, "ProductList")]' \
            '/li[contains(@class, "ListView")]'):
            self.count_prod += 1

    def getResponse(self, response):
        link = response.xpath(
            '//ul[@class="PagingList"]/li[last()]/a/@href'
        ).extract()

        if link:
            page_number_loc = re.findall("\d+", re.findall("page=\d+", link[0])[0])[0]
        else:
            self.count_prod_set(response)
            for el in self.continue_parse():
               yield el
            return

        if int(page_number_loc) < int(self.page_number):
            self.count_prod_set(response)
            for el in self.continue_parse():
               yield el
            return

        self.page_number = page_number_loc

        if link:
            ajax_link = link[0].rstrip('#results')
            ajax_link += '&ajax=1'
            full_link = "http://www.babymonitorsdirect.co.uk/" + ajax_link
            yield Request(
                    full_link,
                    callback=self.getResponse,
                    dont_filter=True
                    )

    #Function which start parse products after total_matches found
    def continue_parse(self):
        for req in super(BabymonitorsdirectProductsSpider, self).start_requests():
            req.dont_filter = True
            yield req

    def parse_product(self, response):

        product = response.meta['product']

        title = response.xpath(
            '//div[@class="BlockContent"]/h1/text()').extract()
        cond_set(product, 'title', title)

        brand = response.xpath(
            '//div[@class="DetailRow"]/div[contains(text(), "Brand:")]' \
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

        #Reviews
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
            average_rating = int(re.findall("IcoRating(\d)", average_rating[0])[0])
        if not average_rating:
            num_of_reviews = None
        buyer_reviews = BuyerReviews(num_of_reviews=num_of_reviews,
                                     average_rating=int(average_rating),
                                     rating_by_star={})
        if average_rating or num_of_reviews:
            cond_set_value(product, 'buyer_reviews', buyer_reviews)

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

        return product

    def _scrape_total_matches(self, response):
        total_matches = None
        if 'No products found matching the search criteria' in response.body_as_unicode():
            total_matches = 0
        elif self.page_number != 0:
            total_matches = (int(self.page_number)-1) * \
                self._product_on_page + float(self.count_prod)
        else:
            total_matches = self.count_prod

        return int(total_matches)

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[@class="ProductDetails"]/strong/a/@href').extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath(
            '//div[@class="CategoryPagination"]' \
            '/div[@class="FloatRight"]/a/@href'
        )
        if links:
            ajax_link = links.extract()[0].strip().rstrip('#results')
            ajax_link += '&ajax=1'
            full_link = "http://www.babymonitorsdirect.co.uk/" + ajax_link
            return full_link
        return None
