import re
import string
import time
import urllib
import requests
from lxml import html

from scrapy import Request
from scrapy.conf import settings

from product_ranking.items import SiteProductItem, BuyerReviews, Price
from product_ranking.spiders import cond_set_value, cond_set
from product_ranking.spiders.contrib.product_spider import ProductsSpider


class WagProductsSpider(ProductsSpider):
    name = 'wag_products'
    handle_httpstatus_list = [404]
    allowed_domains = ['wag.com']
    body_redirected = None

    SEARCH_URL = ("https://www.wag.com/search/{search_term}?s={search_term}"
                  "&ref=srbr_wa_unav#fromSearch=Y")

    def __init__(self, *args, **kwargs):
        super(WagProductsSpider, self).__init__(*args, **kwargs)
        settings.overrides[
            'RETRY_HTTP_CODES'] = [500, 502, 503, 504, 400, 403, 408]

    def parse_404_reviews(self, response):
        return self._parse_reviews(response)

    def start_requests(self):
        """Generate Requests from the SEARCH_URL and the search terms."""
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8')),
                ),
                meta={'search_term': st, 'remaining': self.quantity},
                dont_filter=True)

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            prod['search_term'] = ''
            yield Request(self.product_url,
                          self._parse_single_product,
                          dont_filter=True,
                          meta={'product': prod})

        if self.products_url:
            urls = self.products_url.split('||||')
            for url in urls:
                prod = SiteProductItem()
                prod['url'] = url
                prod['search_term'] = ''
                yield Request(url,
                              self._parse_single_product,
                              dont_filter=True,
                              meta={'product': prod})

    def _total_matches_from_html(self, response):
        if len(response.body) == 0:
            if self.body_redirected is None:
                self.body_redirected = requests.get(response.url).text
            tree = html.fromstring(self.body_redirected)
            total = tree.xpath("//span[@class='searched-stats']/text()")[0]
            return int(total[0].replace(',', '')) if total else 0
        total = response.css('.searched-stats::text').re('of ([\d\,]+)')
        return int(total[0].replace(',', '')) if total else 0

    @staticmethod
    def _scrape_results_per_page(response):
        return 60

    @staticmethod
    def _scrape_next_results_page_link(response):
        link = response.xpath('//a[@class="next"]/@href').extract()
        return link[0] if link else None

    @staticmethod
    def _scrape_product_links(response):
        item_urls = response.xpath(
            '//a[@class="product-box-link"]/@href').extract()
        for item_url in item_urls:
            yield item_url, SiteProductItem()

    def _parse_single_product(self, response):
        return self.parse_product(response)

    @staticmethod
    def _parse_title(response):
        title = response.xpath('//h1[@itemprop="name"]/text()').extract()
        return title[0] if title else None

    @staticmethod
    def _parse_categories(response):
        categories = response.xpath(
            '//*[@class="positionNav "]/a/text()').extract()
        return categories if categories else None

    def _parse_category(self, response):
        categories = self._parse_categories(response)
        return categories[-1] if categories else None

    @staticmethod
    def _parse_price(response):
        price = response.xpath('//*[@itemprop="price"]/@content').re('[\d\.]+')
        currency = response.xpath(
            '//*[@itemprop="priceCurrency"]/@content').re('\w{2,3}') or ['USD']

        if not price:
            return None

        return Price(price=price[0], priceCurrency=currency[0])

    @staticmethod
    def _parse_image_url(response):
        image_url = response.xpath(
            '//a[@class="MagicZoomPlus"]/@href').extract()
        return 'http:' + image_url[0] if image_url else None

    @staticmethod
    def _parse_sku(response):
        sku = response.xpath('//*[@itemprop="sku"]/@content').extract()
        return sku[0] if sku else None

    @staticmethod
    def _parse_variants(response):
        variants = []
        for item in response.xpath('//*[contains(@class, "diaperItemTR")]'):
            vr = {}
            vr['in_stock'] = not bool(
                item.xpath('./td[@class="outOfStockQty"]'))
            price = item.xpath('*//input[@class="skuHidden"]/@displayprice').re('[\d\.]+')
            cond_set(vr, 'price', price)
            images = ['http:' + x for x in item.xpath('.//img/@src').extract()]
            cond_set(vr, 'image_url', images)
            sku = item.xpath('*//input[@class="skuHidden"]/@value').extract()
            cond_set(vr, 'skuId', sku)
            cond_set(vr, 'reseller_id', sku)
            selected = bool(item.xpath('@isprimarysku').re('Y'))
            cond_set_value(vr, 'selected', selected)
            if sku:
                url = re.sub('(sku=)(.+?)&', '\g<1>%s&' % sku[0], response.url)
                cond_set_value(vr, 'url', url)

            variants.append(vr)

        return variants if variants and len(variants) > 1 else None

    @staticmethod
    def _parse_is_out_of_stock(response):
        status = response.xpath(
            '//*[@itemprop="offers"]/meta[@itemprop="availability" '
            'and @content="OutOfStock"]').extract()
        return bool(status)

    def _parse_description(self, response):
        sku = self._parse_sku(response)
        description = response.xpath(
            '//*[@id="Tab1DetailInfo"]/div/div[@sku="%s"]' % sku.upper()).extract()

        if not description:
            description = response.xpath(
                '//*[@id="Tab1DetailInfo"]//div[@class="pIdDesContent"]').extract()

        return ''.join(description).strip() if description else None

    @staticmethod
    def _parse_buyer_review(response, product_response):
        num_reviews = product_response.xpath(
            '//*[@itemprop="reviewCount"]/@content').extract()[0]
        average_rating = product_response.xpath(
            '//*[@itemprop="ratingValue"]/@content').extract()[0]

        rating_by_star = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}

        stars = product_response.xpath(
            '//*[@class="pr-ratings-histogram-content"]'
            '//p[@class="pr-histogram-label"]//span/text()').re('\d+')
        values = product_response.xpath(
            '//*[@class="pr-ratings-histogram-content"]'
            '//p[@class="pr-histogram-count"]//span/text()').re('\d+')

        for (star, value) in zip(stars, map(int, values)):
            rating_by_star[star] += value

        stars = response.xpath(
            '//*[@class="pr-info-graphic-amazon"]'
            '//dd/text()').re('(\d+) star')

        values = response.xpath(
            '//*[@class="pr-info-graphic-amazon"]'
            '//dd/text()').re('\((\d+)\)')

        for (star, value) in zip(stars, map(int, values)):
            rating_by_star[star] += value

        buyer_reviews = BuyerReviews(num_of_reviews=num_reviews,
                                     average_rating=average_rating,
                                     rating_by_star=rating_by_star)

        return buyer_reviews or None

    @staticmethod
    def _parse_last_buyer_date(response, product_response):
        last_comment_date_amazon = response.xpath(
            '//*[@class="pr-review-author-date'
            ' pr-rounded"]/text()').extract()
        last_comment_date_amazon = (last_comment_date_amazon[0]
                                    if last_comment_date_amazon else None)
        last_comment_date_wag = product_response.xpath(
            '//*[@class="pr-review-author-date'
            ' pr-rounded"]/text()').extract()

        last_comment_date_wag = (last_comment_date_wag[0]
                                 if last_comment_date_wag else None)

        if last_comment_date_amazon and last_comment_date_wag:
            date_amazon = time.strptime(last_comment_date_amazon,
                                        "%m/%d/%y")
            date_wag = time.strptime(last_comment_date_wag,
                                     "%m/%d/%Y")

            last_buyer_date = time.strftime("%m/%d/%Y",
                                            max(date_amazon, date_wag))

        else:
            last_buyer_date = (last_comment_date_amazon or
                               last_comment_date_wag)

        return last_buyer_date

    def _parse_reviews(self, response):
        product_response = response.meta['product_response']
        product = response.meta['product']

        # Parse buyer reviews
        buyer_reviews = self._parse_buyer_review(response,
                                                 product_response)
        cond_set_value(product, 'buyer_reviews', buyer_reviews)

        # Parse last buyer review date
        last_buyer_date = self._parse_last_buyer_date(response,
                                                      product_response)
        cond_set_value(product, 'last_buyer_review_date', last_buyer_date)

        return product

    @staticmethod
    def _parse_availability(response):
        return not bool(response.xpath('//div[@class="discontinuedBanner"]'))

    @staticmethod
    def send_next_request(reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def parse_product(self, response):
        reqs = []
        product = response.meta['product']
        response.meta['product_response'] = response
        # Set locale
        product['locale'] = 'en_US'

        # Parse availability
        if not self._parse_availability(response):
            cond_set_value(product, 'no_longer_available', True)
            return product

        cond_set_value(product, 'no_longer_available', False)

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse category
        category = self._parse_category(response)
        cond_set_value(product, 'category', category)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse image url
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Parse variants
        variants = self._parse_variants(response)
        cond_set_value(product, 'variants', variants)

        # Parse stock status
        out_of_stock = self._parse_is_out_of_stock(response)
        cond_set_value(product, 'is_out_of_stock', out_of_stock)

        # Sku
        sku = self._parse_sku(response)
        cond_set_value(product, 'sku', sku)

        # reseller_id
        reseller_id = sku.upper() if sku else None
        cond_set_value(product, 'reseller_id', reseller_id)

        review_id = response.xpath(
            '//*[@class="pr-review-engine"]/@id').re('pr-review-engine-(\d+)')

        if review_id:
            review_id = review_id[0]
            review_id = [x + y for (x, y) in
                         zip(review_id[::2], review_id[1::2])]

            review_url = ("https://www.wag.com/amazon_reviews/%s"
                          "/mostrecent_default.html" % '/'.join(review_id))

            reqs.append(Request(review_url,
                                dont_filter=True,
                                meta=response.meta,
                                errback=self.parse_404_reviews,
                                callback=self._parse_reviews))

        if reqs:
            return self.send_next_request(reqs, response)

        return product
