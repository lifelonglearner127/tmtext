import json
import string
import re

from urlparse import urljoin

from scrapy import Request

from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.items import SiteProductItem, BuyerReviews, Price
from product_ranking.spiders import cond_set_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider


class VerizonwirelessProductsSpider(ProductsSpider):
    handle_httpstatus_list = [404]
    name = 'verizonwireless_products'

    custom_settings = {'RETRY_HTTP_CODES':[500, 502, 503, 504, 400, 403, 408]}

    allowed_domains = ['verizonwireless.com','bazaarvoice.com']

    SEARCH_URL = "http://www.verizonwireless.com/search/" \
                 "vzwSearch?Ntt={search_term}&nav=Global&gTab="

    REVIEW_URL = 'http://api.bazaarvoice.com/data/products.json?' \
                 'passkey=e8bg3vobqj42squnih3a60fui&apiversion=' \
                 '5.5&filter=id:{product_id}&stats=reviews'

    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)

        super(VerizonwirelessProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

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
        meta = response.meta.copy()
        product = response.meta['product']
        reqs = meta.get('reqs', [])

        product['buyer_reviews'] = self.br.parse_buyer_reviews_products_json(response)

        if reqs:
            return self.send_next_request(reqs, response)
        else:
            return product

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

        # Parse stock status
        out_of_stock = self._parse_is_out_of_stock(response)
        cond_set_value(product, 'is_out_of_stock', out_of_stock)

        try:
            device_prod_id_search = re.search('deviceProdId=(.*?)&', response.body)
            if device_prod_id_search:
                product_id = device_prod_id_search.group(1)

            else:
                product_id = response.xpath('//input[@id="isProductId"]/@value').extract()[0]

            reqs.append(
                Request(
                    url=self.REVIEW_URL.format(product_id=product_id),
                    dont_filter=True,
                    callback=self._parse_buyer_reviews,
                    meta=meta
                ))
        except:
            pass


        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """
        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs

        return req.replace(meta=new_meta)

