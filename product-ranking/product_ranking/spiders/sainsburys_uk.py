from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urlparse
import urllib

from scrapy.log import ERROR, DEBUG, INFO
from scrapy.http import Request

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults
from product_ranking.spiders import (cond_set, cond_set_value,
                                     _extract_open_graph_metadata)


def clear_text(l):
    """
    usefull for  clearing sel.xpath('.//text()').explode() expressions
    """
    return " ".join(
        [it for it in map(string.strip, l) if it])


class SainsburysUkProductsSpider(BaseProductsSpider):
    name = 'sainsburys_uk_products'
    allowed_domains = ["sainsburys.co.uk"]
    start_urls = []

    SEARCH_URL = ("http://www.sainsburys.co.uk/sol/global_search/"
                  "global_result.jsp?bmForm=global_search"
                  "&GLOBAL_DATA._search_term1={search_term}"
                  "&GLOBAL_DATA._searchType=0")

    class GroceryCategory:
        url = ("http://www.sainsburys.co.uk/"
               "webapp/wcs/stores/servlet/SearchDisplayView?"
               "langId=44&storeId=10151&catalogId=10122&pageSize=30&"
               "orderBy={sort_order}&searchTerm={search_term}&beginIndex=0")

        sort_orders = {
            'default': 'RELEVANCE',
            'low_price': 'PRICE_ASC',
            'high_price': 'PRICE_DESC',
            'name_asc': 'NAME_ASC',
            'name_desc': 'NAME_DESC',
            'best_sellers': 'TOP_SELLERS',
            'rating': 'RATINGS_DESC',
        }

        def _scrape_product_links(self, response):
            return response.css(
                '#productLister ul.productLister '
                '.productNameAndPromotions h3 a::attr(href)'
            ).extract()

        def _scrape_next_results_page_link(self, response):
            return response.css(
                '#productLister .pagination li.next a::attr(href)'
            ).extract()

        def parse_product(self, response):
            prod = response.meta['product']

            cond_set(prod, 'title', response.xpath(
                '//div[@class="productSummary"]/h1/text()'
            ).extract(), string.strip)

            cond_set(prod, 'price', response.xpath(
                '//p[@class="pricePerUnit"]/text()'
            ).extract(), string.strip)

            img_url = response.xpath(
                '//div[@class="productSummary"]/img/@src'
            ).extract()
            if img_url:
                img_url = urlparse.urljoin(response.url, img_url[0])
                cond_set_value(prod, 'image_url', img_url)

            desc = response.xpath(
                '//div[@id="information"]'
                '/h2[@class="access"]/following-sibling::*'
            ).extract()
            if desc:
                cond_set_value(prod, 'description', clear_text(desc))

            return prod

    class ProductsCategory:
        url = None
        url_template = ("http://www.sainsburys.co.uk/"
                        "sol/shop/{slug}/list.html?search={{search_term}}"
                        "&sort={{sort_order}}")
        sort_orders = {
            'default': 'default',
            'newest': 'newest_first',
            'rating': 'avg_rating',
            'name_asc': ' price_asc',
            'high_price': 'price_desc',
            'offers': 'great_offers'
        }

        def __init__(self, slug):
            self.url = self.url_template.format(slug=slug)

        def _scrape_product_links(self, response):
            return response.xpath(
                '(//ul[@class="itemList"])[1]'
                '//h3[@class="listItemDesc"]//a/@href'
            ).extract()

        def _scrape_next_results_page_link(self, response):
            return response.css(
                '.paging li.next a::attr(href)'
            ).extract()

        def parse_product(self, response):
            prod = response.meta['product']
            cond_set(prod, 'title', response.xpath(
                '//div[@class="productHeaderTextInner"]/h3/text()'
            ).extract(), string.strip)
            cond_set(
                prod, 'price', response.css(
                    'div.productContent'
                ).xpath('string(.//div[@class="priceNow"])').extract(),
                string.strip
            )
            cond_set(prod, 'image_url', response.xpath(
                '//img[@id="bigImage"]/@src'
            ).extract())
            desc = response.xpath(
                '//div[@class="productOverviewPanel"]/node()'
            ).extract()

            if desc:
                cond_set_value(prod, 'description', clear_text(desc))

            in_stock = response.xpath(
                '//span[@id="stockStatus"]/text()').extract()
            if in_stock and in_stock[0] != 'In stock':
                cond_set_value(prod, 'is_out_of_stock', True)

            cond_set(prod, 'brand', response.xpath(
                '//li/label[@for="Brand1"]/text()'
            ).extract())

            consider = response.xpath('//div[@class="consideredPanelInner"]//a')
            recommend = response.xpath(
                '//div[@class="recommendationPanel clearFloat"]//a')
            rel = []
            for link in consider + recommend:
                href = link.xpath('@href').extract()
                title = link.xpath('text()').extract()
                if title and href:
                    url = urlparse.urljoin(response.url, href[0])
                    title = title[0].strip()
                    rel.append(RelatedProduct(title=title, url=url))
            cond_set_value(prod, 'related_products', {'recommended': rel})
            return prod

    CATEGORIES = {
        'Groceries': GroceryCategory(),
        'Home & garden': ProductsCategory("home_and_garden"),
        'Appliances': ProductsCategory("appliances"),
        'Technology': ProductsCategory("technology"),
        'Toys': ProductsCategory("toys_and_nursery"),
        'Sport & leisure': ProductsCategory("sport_and_leisure"),
        'Baby': ProductsCategory("baby"),
        'Events': ProductsCategory("events"),
    }

    def __init__(self, search_sort='default', *args, **kwargs):
        super(SainsburysUkProductsSpider, self).__init__(*args, **kwargs)
        self.search_sort = search_sort

    def start_requests(self):

        for request in super(SainsburysUkProductsSpider, self).start_requests():
            request.callback = self.parse_global_search
            yield request

    def parse_global_search(self, response):
        total_matches = self._scrape_total_matches(response)
        if total_matches is not None:
            response.meta['total_matches'] = total_matches
            self.log("Found %d total matches." % total_matches, INFO)

            categories = []

            groceries = response.xpath(
                '//div[@class="sectionResult foodnDrink"]'
                '//div[@class="sectionResult groceries"]')
            if groceries:
                categories.append('Groceries')
                self.log("Groceries found.", INFO)
            products = response.xpath(
                '//div[@class="sectionResult gmproductcatagory"]'
                '/div[@class="containerBoxHeader"]/h4/text()') \
                .extract()
            for product in products:
                self.log("{} found.".format(product), INFO)
                if product in self.CATEGORIES:
                    categories.append(product)

            if categories:
                response.meta['categories'] = iter(categories)
                return self._next_category(response)
        else:
            self.log("No products found.", INFO)

    def _next_category(self, response):

        try:
            cat = next(response.meta['categories'])
        except StopIteration:
            return
        cat_obj = self.CATEGORIES[cat]
        st = response.meta['search_term']
        sort = cat_obj.sort_orders.get(
            self.search_sort,
            cat_obj.sort_orders['default'])

        url = cat_obj.url.format(
            search_term=urllib.quote_plus(st),
            sort_order=sort
        )
        new_meta = response.meta.copy()
        new_meta['cat'] = cat
        new_meta['products_per_page'] = None
        return Request(
            url,
            meta=new_meta)

    def parse_product(self, response):
        cat = self.CATEGORIES[response.meta['cat']]
        cat.parse_product(response)
        product = cat.parse_product(response)
        cond_set_value(product, 'locale', 'en-GB')
        return product

    def _scrape_total_matches(self, response):
        total = None
        totals = response.css('.panelContentHeader strong::text').extract()
        if totals:
            total = int(totals[0].strip())
        else:
            self.log(
                "Failed to find 'total matches' for %s" % response.url,
                ERROR)
        return total

    def _scrape_product_links(self, response):
        cat = self.CATEGORIES[response.meta['cat']]
        items = cat._scrape_product_links(response)

        self.log("Found {} links.".format(len(items)), DEBUG)

        for link in items:
            prod_item = SiteProductItem()
            url = urlparse.urljoin(response.url, link)
            yield Request(
                url,
                callback=self.parse_product,
                meta={'product': prod_item, 'cat': response.meta['cat']},
            ), prod_item

    def _scrape_next_results_page_link(self, response):
        cat = self.CATEGORIES[response.meta['cat']]

        next = cat._scrape_next_results_page_link(response)
        if next:
            link = urlparse.urljoin(response.url, next[0])
        else:
            link = self._next_category(response)
        return link