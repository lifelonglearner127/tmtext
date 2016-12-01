import re
import string

from scrapy.log import INFO, WARNING
from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set_value
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi

is_empty = lambda x, y=None: x[0] if x else y


class ToysrusProductsSpider(BaseProductsSpider):

    name = 'toysrus_products'
    allowed_domains = ["toysrus.com"]

    SEARCH_URL = "http://www.toysrus.com/search/index.jsp?kwCatId=&" \
                 "kw={search_term}&keywords={search_term}&" \
                 "origkw={search_term}&sr=1"

    items_per_page = 24
    start_links = 'http://www.toysrus.com'

    def __init__(self, *args, **kwargs):
        super(ToysrusProductsSpider, self).__init__(site_name=self.allowed_domains[0], *args, **kwargs)
        self.br = BuyerReviewsBazaarApi(called_class=self)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Set locale
        product['locale'] = 'en_GB'

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse brand
        brand = self._parse_brand(response)
        cond_set_value(product, 'brand', brand)

        # Parse department
        department = self._parse_department(response)
        cond_set_value(product, 'department', department)

        # Parse categories
        categories = self._parse_categories(response)
        cond_set_value(product, 'categories', categories)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse special pricing
        special_pricing = self._parse_special_pricing(response)
        cond_set_value(product, 'special_pricing', special_pricing, conv=bool)

        # Parse image url
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url, conv=string.strip)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description, conv=string.strip)

        # Parse stock status
        is_out_of_stock = self._parse_stock_status(response)
        cond_set_value(product, 'is_out_of_stock', is_out_of_stock)

        # Parse upc
        upc = self._parse_upc(response)
        cond_set_value(product, 'upc', upc)

        # Parse sku
        sku = self._parse_sku(response)
        cond_set_value(product, 'sku', sku)

        # reseller_id
        cond_set_value(product, 'reseller_id', sku)

        # # Parse buyer reviews
        buyer_reviews = self._parse_buyer_reviews(response)
        cond_set_value(product, 'buyer_reviews', buyer_reviews)

        # # Parse related products
        related_products = self._parse_related_products(response)
        cond_set_value(product, 'related_products', related_products)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_title(self, response):
        title = is_empty(response.xpath('//meta[@property="og:title"]'
                                        '/@content').extract())
        return title

    def _parse_brand(self, response):
        brand = is_empty(response.xpath('//li[@class="first"]//label'
                                        '/text()').extract())
        return brand

    def _parse_department(self, response):
        department = self._parse_categories(response)
        return department[len(department)-1]

    def _parse_categories(self, response):
        categories = []
        categories_sel = response.xpath('//div[@id="breadCrumbs"]'
                                             '/a/text()').extract()
        for i in categories_sel:
            categories.append(i.strip())

        return categories

    def _parse_price(self, response):
        price = is_empty(response.xpath('//li[contains(@class, "retail fl")]'
                                        '/span/text()').re(r'\d+.\d+'), 0.00)

        currency = is_empty(response.xpath(
            '//script[contains(text(), '
            '"storeCurrencyCode")]').re(r"storeCurrencyCode = '(\w+)'"))

        return Price(price=float(price), priceCurrency=currency)

    def _parse_special_pricing(self, response):
        special_price = is_empty(response.xpath(
            '//li[contains(@class, "list fl")]'
            '/span/text()').extract(), False)

        return special_price

    def _parse_image_url(self, response):
        image_url = is_empty(response.xpath('//meta[@property="og:image"]'
                                            '/@content').extract())
        return image_url

    def _parse_description(self, response):
        desc = is_empty(response.xpath('//meta[@property="og:description"]'
                                       '/@content').extract())
        if desc:
            desc = desc.replace("<br>", "")

        return desc

    def _parse_stock_status(self, response):
        stock_status = is_empty(response.xpath(
            '//script[contains(text(), "inStock")]').re(r'"inStock", "(\d+)"'))

        if stock_status == "1":
            return False
        else:
            return True

    def _parse_upc(self, response):
        upc = is_empty(response.xpath('//p[@class="upc"]/span'
                                      '/text()').extract())
        return upc

    def _parse_sku(self, response):
        sku = is_empty(response.xpath('//p[@class="skuText"]/span'
                                      '/text()').extract())
        return sku

    def _parse_buyer_reviews(self, response):
        average_rating = is_empty(response.xpath(
            '//div[@id="prod_ratings"]//span[@class="pr-rating '
            'pr-rounded average"]/text()').extract(), 0.0)

        num_of_reviews = is_empty(response.xpath(
            '//div[@id="prod_ratings"]//span[@class="count"]'
            '/text()').extract(), 0)

        evaluetion = response.xpath(
            '//p[@class="pr-histogram-count"]/span/text()').re(r'\d+')[:5]

        if average_rating:
            average_rating = float(average_rating)

        if num_of_reviews:
            num_of_reviews = int(num_of_reviews)

        if evaluetion:
            evaluetion.reverse()

        rating_by_star = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        if num_of_reviews > 0:
            for index, i in enumerate(evaluetion):
                rating_by_star[index + 1] = int(i)

        return BuyerReviews(num_of_reviews, average_rating, rating_by_star)


    def _parse_related_products(self, response):
        titles = response.xpath('//div[@id="relatedItems"]'
                                '//div[@class="titleReviewPrice"]'
                                '/label/b/a/text()').extract()
        links_data = response.xpath('//div[@id="relatedItems"]'
                               '//div[@class="titleReviewPrice"]'
                               '/label/b/a/@href').extract()

        links = []
        for link in links_data:
            links.append(re.sub(r'&prodFindSrc=prodCrossSell', r'', link))

        related = []
        if titles and links:
            for index, link in enumerate(links):
                related.append(RelatedProduct(title=titles[index],
                               url=self.start_links + link))

        return related

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _scrape_total_matches(self, response):
        """
        Scraping number of resulted product links
        """
        total_matches = is_empty(
            response.xpath('//h1[@id="search"]/strong/text()').re(r'\d+'), 0
        )

        if total_matches:
            return int(total_matches)
        else:
            return 0

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        return self.items_per_page

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.xpath('//div[contains(@class, '
                               '"clearfix prodloop_row_cont")]'
                               '//div[@class="varHeightTop"]')

        if items:
            for item in items:
                link = is_empty(
                    item.xpath('a/@href').extract()
                )
                link = self.start_links + link
                res_item = SiteProductItem()
                yield link, res_item
        else:
            self.log("Found no product links in {url}".format(url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        url = is_empty(
            response.xpath('//*[@id="pagination_bot"]//a'
                           '/span[contains(@class,"next")]'
                           '/parent::*/@href').extract()

        )
        url = self.start_links + url.replace('..', '')
        if url:
            return url
        else:
            self.log("Found no 'next page' links", WARNING)
            return None
