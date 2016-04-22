import json
import string
import re

from urlparse import urljoin

from product_ranking.items import SiteProductItem, BuyerReviews, Price
from product_ranking.spiders import cond_set_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider


class VerizonwirelessProductsSpider(ProductsSpider):
    handle_httpstatus_list = [404]
    name = 'verizonwireless_products'

    allowed_domains = ['verizonwireless.com']

    SEARCH_URL = "http://www.verizonwireless.com/search/" \
                 "vzwSearch?Ntt={search_term}&nav=Global&gTab="

    def _total_matches_from_html(self, response):
        total = response.xpath(
            '//*[@id="total-results-source-div"]//strong/text()').re('\d+')

        return int(total[0]) if total else 0

    def _scrape_results_per_page(self, response):
        return 24

    def _scrape_next_results_page_link(self, response):
        link = response.xpath('//a[text()="Next"]/@href').extract()
        return link[0] if link else None

    def _scrape_product_links(self, response):
        item_urls = response.xpath(
            '//div[@itemtype="https://schema.org/Product" and '
            'not(contains(@class,"Device-SpecificInstructions") or '
            'contains(@class,"allother"))]'
            '/a/@href').extract()
        for item_url in item_urls:
            yield item_url, SiteProductItem()

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _parse_title(self, response):
        title = response.xpath('//*[@itemprop="name"]/text()').extract()
        return title[0] if title else None

    def _parse_categories(self, response):
        categories = response.xpath(
            '//*[@itemtype="https://data-vocabulary.org/Breadcrumb"]'
            '//span[@itemprop="title"]/text()').extract()
        return categories

    def _parse_category(self, response):
        categories = self._parse_categories(response)
        return categories[-1] if categories else None

    def _parse_price(self, response):
        price = ''.join(response.xpath(
            '//*[@itemprop="price"]//span/text()').re('[\d\.]+'))
        currency = response.xpath(
            '//*[@itemprop="priceCurrency"]/@content').re('\w{2,3}') or ['USD']

        if not price:
            return None

        return Price(price=price, priceCurrency=currency[0])

    def _parse_image_url(self, response):
        image_url = response.xpath(
            '//*[@property="og:image"]/@content').extract()
        return image_url[0].split('?')[0] if image_url else None

    def _parse_sku(self, response):
        sku = re.findall('selectedSkuId":"(.*?)"', response.body)
        return sku[0] if sku else None

    def _parse_variants(self, response):
        return None

    def _parse_is_out_of_stock(self, response):
        status = response.xpath(
            '//*[@itemprop="availability" '
            'and not(@href="http://schema.org/InStock")]')
        return bool(status)

    def _parse_description(self, response):
        description = response.xpath(
            '//*[@data-tabname="overview"]'
            '//div[@id="pdp-two-thirds"]').extract()

        return ''.join(description).strip() if description else None

    def _parse_buyer_reviews(self, response):
        value_list = response.xpath(
            '//*[@id="pdp-review-link"]/span/text()').extract()
        if len(value_list) is 3:
            num_reviews = value_list[2]
            average_rating = value_list[0]
            rating_by_star = None

            return BuyerReviews(num_of_reviews=num_reviews,
                                average_rating=average_rating,
                                rating_by_star=rating_by_star or None)
        return None

    def _parse_last_buyer_date(self, response):
        return None

    def _parse_price_json(self, data):
        return data.get('mboxInfo', {}).get(
            'priceBreakDownFullRetailPrice', None)

    def _parse_sku_price_json(self, data):
        return data.get('priceBreakDown', {}).get(
            'fullRetailPriceListId', {}).get('RETAIL PRICE', None) or \
            data.get('price', {}).get('retailPrice')

    def _parse_variants_json(self, sku_list):
        if not sku_list:
            return None
        variants = []
        for sku in sku_list:
            vr = {}
            vr['skuID'] = sku.get('id')
            properties = {}
            color = sku.get('colorName')
            if color:
                properties['color'] = color
            capacity = sku.get('capacity')
            if capacity:
                properties['capacity'] = capacity

            if properties:
                vr['properties'] = properties

            price = self._parse_sku_price_json(sku)
            if price and float(price) != 0.00:
                vr['price'] = price
            variants.append(vr)

        return variants

    def _parse_reviews_json(self, product_data):
        num_reviews = product_data.get(
            'numberOfReviews', None)
        average_rating = product_data.get(
            'productRating', None)

        rating_by_star = None

        return BuyerReviews(num_of_reviews=num_reviews,
                            average_rating=average_rating,
                            rating_by_star=rating_by_star or None)

    def parse_404(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Set locale
        product['locale'] = 'en_US'

        pdp_data = response.xpath('//script/text()').re('pdpJSON = ({.*})')
        if pdp_data:
            pdp_json = json.loads(pdp_data[0])

            product_data = pdp_json.get('devices', {}) or \
                pdp_json.get('accessory', {})

            price = self._parse_price_json(pdp_json)
            cond_set_value(product, 'price', price)

            sku_list = product_data.get('skus', [])

            variants = self._parse_variants_json(sku_list)
            cond_set_value(product, 'variants', variants)

            reviews = self._parse_reviews_json(product_data)
            cond_set_value(product, 'buyer_reviews', reviews)

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse category
        category = self._parse_category(response)
        cond_set_value(product, 'category', category)

        # Parse category
        categories = self._parse_categories(response)
        cond_set_value(product, 'categories', categories)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse image url
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Parse sku
        sku = self._parse_sku(response)
        cond_set_value(product, 'sku', sku)

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
