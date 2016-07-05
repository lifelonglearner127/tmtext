import string

from product_ranking.items import SiteProductItem, BuyerReviews, Price
from product_ranking.spiders import cond_set_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider


class RiteAidProductsSpider(ProductsSpider):
    name = 'riteaid_products'

    allowed_domains = ['riteaid.com']

    SEARCH_URL = "https://shop.riteaid.com/catalogsearch/result/"\
                 "?limit=72&q={search_term}"

    def _total_matches_from_html(self, response):
        total = response.xpath(
            '(//*[@class="pager"]//*[@class="amount"]'
            '/text())[1]').re('of (\d+)')

        return int(total[0]) if total else 0

    def _scrape_results_per_page(self, response):
        results_per_page = response.xpath(
            '//*[@class="limiter"]//option[@selected]/text()').re('\d+')
        return int(results_per_page[0]) if results_per_page else 0

    def _scrape_next_results_page_link(self, response):
        link = response.xpath('//a[@title="Next"]/@href').extract()
        return link[0] if link else None

    def _scrape_product_links(self, response):
        item_urls = response.xpath(
            '//*[@class="product-name"]/a/@href').extract()
        for item_url in item_urls:
            yield item_url, SiteProductItem()

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _parse_title(self, response):
        title = response.xpath('//*[@itemprop="name"]/text()').extract()
        return title[0] if title else None

    def _parse_category(self, response):
        categories = response.xpath(
            '(//a[@property="v:title"]/text())[position()>1]').extract()
        return categories[-1] if categories else None

    def _parse_price(self, response):
        price = response.xpath('//*[@itemprop="price"]/text()').re('[\d\.]+')
        currency = response.xpath(
            '//*[@itemprop="priceCurrency"]/@content').re('\w{2,3}') or ['USD']

        if not price:
            return None

        return Price(price=price[0], priceCurrency=currency[0])

    def _parse_image_url(self, response):
        image_url = response.xpath('//*[@itemprop="image"]/@src').extract()
        return image_url[0] if image_url else None

    def _parse_variants(self, response):
        return None

    def _parse_is_out_of_stock(self, response):
        status = response.xpath(
            '//*[@itemprop="availability" '
            'and not(@href="http://schema.org/InStock")]')
        return bool(status)

    def _parse_description(self, response):
        description = response.xpath(
            '(//*[@id="collateral-tabs"]//*[@class="tab-container"])[1]'
            '//*[self::p or self::ul or self::table] | '
            '(//*[@id="collateral-tabs"]//*[@class="tab-container"])[1]'
            '//*[@class="std"]/text()').extract()
        return ''.join(description).strip() if description else None

    def _parse_buyer_reviews(self, response):
        num_reviews = response.xpath(
            '//*[@itemprop="reviewCount"]/text()').extract()
        average_rating = response.xpath(
            '//*[@itemprop="ratingValue"]/text()').extract()

        value_rating = response.xpath(
            '//*[contains(@class,"review-summary-table")]//'
            'th[@class="label" and text()="Value"]/'
            'following-sibling::td//*[@class="rating"]/@style').re('\d+')

        quality_rating = response.xpath(
            '//*[contains(@class,"review-summary-table")]//'
            'th[@class="label" and text()="Quality"]/'
            'following-sibling::td//*[@class="rating"]/@style').re('\d+')

        if num_reviews and average_rating:
            average_rating = float(average_rating[0]) / 20
            num_reviews = int(num_reviews[0])
            rating_by_star = None
            if value_rating and quality_rating:
                rating_by_star = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
                for (a, b) in zip(value_rating, quality_rating):
                    average_vote = (int(a) + int(b)) / 2
                    over_five = average_vote / 20
                    rating_by_star[str(over_five)] += 1

            return BuyerReviews(num_of_reviews=num_reviews,
                                average_rating=average_rating,
                                rating_by_star=rating_by_star)

        return None

    def _parse_last_buyer_date(self, response):
        last_review_date = response.xpath(
            '//*[contains(@class,"box-reviews")]'
            '//*[@class="date"]/text()').re('Posted on (.*)\)')
        return last_review_date[0] if last_review_date else None

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Set locale
        product['locale'] = 'en_US'

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

        # Parse buyer reviews
        buyer_reviews = self._parse_buyer_reviews(response)
        cond_set_value(product, 'buyer_reviews', buyer_reviews)

        # Parse last buyer review date
        last_buyer_date = self._parse_last_buyer_date(response)
        cond_set_value(product, 'last_buyer_review_date', last_buyer_date)

        if reqs:
            return self.send_next_request(reqs, response)

        return product
