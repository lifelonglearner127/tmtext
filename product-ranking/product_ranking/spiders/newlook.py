from __future__ import division, absolute_import, unicode_literals
import string
import urllib
import urlparse

from scrapy.log import ERROR
from scrapy.http import Request

from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value, FormatterWithDefaults

is_empty = lambda x, y=None: x[0] if x else y

class NewlookProductsSpider(BaseProductsSpider):
    name = 'newlook_products'

    allowed_domains = ["newlook.com"]

    start_urls = []

    SEARCH_URL = "http://www.newlook.com/eu/spring/facetBrowse.jsp?" \
        "Ntt={search_term}&eNtt={search_term}&icCategory=" # Brogues

    SORTING = None
    SORT_MODES = {
        'default': '',
        'price_low_to_high': 'sort.price.eu|0',
        'price_high_to_low': 'sort.price.eu|1',
        'newest': 'publish.date|1',
        'best_sellers': 'sort.bestseller.score|1',
    }

    def __init__(self, sort_mode=None, *args, **kwargs):
        if sort_mode:
            if sort_mode.lower() not in self.SORT_MODES:
                self.log('"%s" not in SORT_MODES')
            else:
                self.SORTING = self.SORT_MODES[sort_mode.lower()]

        super(NewlookProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                sort_mode=self.SORTING or self.SORT_MODES['default']),
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def start_requests(self):
        """Generate Requests from the SEARCH_URL and the search terms."""
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8')),
                ),
                self.parse_302,
                meta={'search_term': st, 'remaining': self.quantity},
            )

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            prod['search_term'] = ''
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod})

        if self.products_url:
            urls = self.products_url.split('||||')
            for url in urls:
                prod = SiteProductItem()
                prod['url'] = url
                prod['search_term'] = ''
                yield Request(url,
                              self._parse_single_product,
                              meta={'product': prod})

    def parse_302(self, response):
        if not self.SORTING:
            self.SORTING = ''
        url = response.url + '&Ns=' + self.SORTING
        return Request(url,
            meta=response.meta, dont_filter=True)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(
            product,
            'title',
            response.xpath(
                "//div[contains(@class,'prod_info')]"
                "/div[contains(@class,'title_container')]/h1/text()"
            ).extract(),
            conv=string.strip)

        if not product.get('brand', None):
            brand = guess_brand_from_first_words(
                product.get('title', None).strip())
            if brand:
                product['brand'] = brand

        cond_set(
            product,
            'image_url',
            response.xpath(
                "//div[contains(@id,'image_viewer')]"
                "/img[@id='mainImage']/@src"
            ).extract(),
            lambda url: urlparse.urljoin(response.url, url)
        )

        prod_description = response.xpath(
            "//div[@id='product-info']"
            "/span[contains(@itemprop, 'description')]/p/text()"
        )
        cond_set_value(product, 'description', "\n".join(
            x.strip() for x in prod_description.extract() if x.strip()))

        cond_set(
            product,
            'sku',
            response.css(".prod_info #product-info p "
                "span[itemprop=productID]::text").extract(),
            conv=string.strip,
        )

        price_now = response.css(".prod_info span.price "
            "span.now span.promovalue::text").extract()
        if not price_now:
            price = response.css(".prod_info span.price "
                "span.promovalue::text").extract()
        else:
            price = price_now
        cond_set(
            product,
            'price', price,
            conv=string.strip,
        )
        if price:
            product['price'] = Price(
                price=product['price'].replace('\u20ac',
                                               '').replace(',', '.').strip(),
                priceCurrency='EUR')

        cond_set_value(product, 'locale', 'en_EU')

        stock_status = response.xpath('///select[@id="size_standard"]'
                                      '/option/@class').extract()
        sku_vatiants = response.xpath('//select[@id="size_standard"]'
                                      '/option[position() > 1]'
                                      '/@data-sku').extract()
        size = response.xpath('//select[@name="size_standard"]'
                              '/option/@value').extract()
        count = response.xpath('//select[@name="size_standard"]'
                               '/option[position() > 1]/@data-stock').extract()

        variant_list = []
        for index, i in enumerate(stock_status):
            variant_item = {}
            properties = {}

            variant_item['in_sock'] = True if 'in_stock' in i else False
            variant_item['price'] = price[0].replace(u'\u20ac', '').\
                replace(',', '.').strip()

            properties['size'] = size[index]
            properties['count'] = count[index]
            properties['sku'] = sku_vatiants[index]

            variant_item['properties'] = properties
            variant_list.append(variant_item)

        product['variants'] = variant_list

        return product

    def _scrape_total_matches(self, response):
        totals = response.xpath(
            "//div[contains(@class,'SortingAndPagingControls')]"
            "/div[contains(@class,'pagination')]"
            "/div[contains(@class,'totalproducts')]"
            "/span[contains(@class,'count')]/text()"
        ).extract()
        if totals:
            total = totals[0].replace(".", "")
            try:
                total_matches = int(total)
            except ValueError:
                self.log(
                    "Failed to parse number of matches: %r" % total, ERROR)
                total_matches = None
        elif "Sorry, we can't find any matches for" in response.body_as_unicode():
            total_matches = 0
        else:
            total_matches = None

        return total_matches

    def _scrape_product_links(self, response):
        links = response.xpath(
            "//div[contains(@class,'ProductListBox')]/ul/li"
            "/a[contains(@class,'mouseover-product')]"
            "/@href").extract()
        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_page_links = response.css(
            ".pagination>ul>li.next>a::attr('href')").extract()
        if next_page_links:
            return next_page_links[0]
