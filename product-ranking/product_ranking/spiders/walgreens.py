from __future__ import division, absolute_import, unicode_literals

import urlparse
import json
import re

from scrapy.http import Request

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value, FormatterWithDefaults


class WalGreensProductsSpider(BaseProductsSpider):
    """ walgreens.com product ranking spider

    Takes `order` argument with following possible values:

    * `relevance`
    * `top_sellers`
    * `price_asc`, `price_desc`
    * `product_name_asc`, `product_name_desc`
    * `most_reviewed`
    * `highest_rated`
    * `most_viewed`
    * `newest_arrival`

    There are the following caveats:

    * `upc`, `related_products`,`sponsored_links`  are not scraped
    * `buyer_reviews`, `price` are not always scraped

    """
    name = "walgreens_products"
    allowed_domains = ["walgreens.com", "api.bazaarvoice.com"]
    start_urls = []
    site = 'http://www.walgreens.com'
    page = 1
    SORTING = None
    SORT_MODES = {
        'relevance': 'relevance',  # default
        'top_sellers': 'Top Sellers',
        'price_asc': 'Price Low to High',
        'price_desc': 'Price High to Low',
        'product_name_asc': 'Product Name A-Z',
        'product_name_desc': 'Product Name Z-A',
        'most_reviewed': 'Most Reviewed',
        'highest_rated': 'Highest Rated',
        'most_viewed': 'Most Viewed',
        'newest_arrival': 'Newest Arrival'
    }

    SEARCH_URL = "http://www.walgreens.com/svc/products/search?" \
                 "requestType=search&" \
                 "q={search_term}&" \
                 "p={page}&" \
                 "s=60&" \
                 "deviceType=desktop&" \
                 "closeMatch=false&" \
                 "id=%5B%5D&" \
                 "sort={sort_mode}&" \
                 "view=allView"

    REVIEW_API_URL = 'http://api.bazaarvoice.com/data/batch.json?' \
                     'passkey=tpcm2y0z48bicyt0z3et5n2xf&' \
                     'apiversion=5.5&' \
                     'resource.q0=products&' \
                     'filter.q0=id%3Aeq%3A{prod_id}&' \
                     'stats.q0=reviews&' \
                     'callback=BV._internal.dataHandler0'

    PRICE_VARI_API_URL = "http://www.walgreens.com/svc/products" \
                         "/{prod_id}/(PriceInfo+Inventory)?rnd=1461679490848"

    def __init__(self, sort_mode=None, *args, **kwargs):
        if sort_mode:
            if sort_mode.lower() not in self.SORT_MODES:
                self.log('"%s" not in SORT_MODES')
            else:
                self.SORTING = self.SORT_MODES[sort_mode.lower()]

        super(WalGreensProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                page=self.page,
                sort_mode=self.SORTING or self.SORT_MODES['relevance'],),
            *args,
            **kwargs)

    def start_requests(self):
        # Specific for this website
        if self.searchterms:
            self.searchterms = [st.replace('-', ' ') for st in self.searchterms]
        return super(WalGreensProductsSpider, self).start_requests()

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _parse_price_and_variants(self, response):
        try:
            data = json.loads(response.body)
        except:
            data = {}

        prod = response.meta['product']
        reqs = response.meta.get('reqs', [])

        # Parse Price
        if "priceInfo" in data:
            if "messages" in data["priceInfo"]:
                price = None
            elif "salePrice" in data["priceInfo"]:
                price = self.parse_price_single_product(
                    data["priceInfo"], "salePrice")
            elif "regularPrice" in data["priceInfo"]:
                price = self.parse_price_single_product(
                    data["priceInfo"], "regularPrice")

            if price:
                cond_set_value(prod, 'price', Price(price=price[0],
                                                    priceCurrency='USD'))
        # UPC
        upc = data.get('inventory', {}).get('upc')
        cond_set_value(prod, 'upc', upc)

        # In Store Only
        ship_message = data.get('inventory', {}).get('shipAvailableMessage')
        is_in_store_only = (ship_message == "Not sold online")
        cond_set_value(prod, 'is_in_store_only', is_in_store_only)

        # Parse Variants
        colors_variants = data.get('inventory', {}).get(
            'relatedProducts', {}).get('color', [])

        variants = []
        for color in colors_variants:
            vr = {}
            vr['skuID'] = color.get('key', "").replace('sku', '')
            vr['in_stock'] = color.get('isavlbl') == "yes"
            color_name = color.get('value', '').split('-')[0].strip()
            vr['properties'] = {'color': color_name}
            variants.append(vr)

        if variants:
            cond_set_value(prod, 'variants', variants)

        if reqs:
            return self.send_next_request(reqs, response)
        return prod

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def parse_price_single_product(self, data, key):
        if "1/" in data[key]:
            price = re.findall("1\/.(\d+\.{0,1}\d+)", data[key])
        else:
            price = re.findall("(\d+\.{0,1}\d+)", data[key])
        return price

    def parse_product(self, response):
        prod = response.meta['product']
        reqs = response.meta.get('reqs', [])

        title = response.xpath('//*[@id="productName"]/text()'
                               '|//*[@class="wag-prod-title"]/text()').extract()
        title = [x.strip() for x in title if x.strip()]
        cond_set(prod, 'title', title)

        no_longer_available = bool(response.xpath(
            '//*[@role="alert"]/span[contains'
            '(text(),"no longer available")]'))

        cond_set_value(prod, 'no_longer_available', no_longer_available)

        img_url = response.xpath(
            '//img[@id="main-product-image"]/@data-src').extract()
        if img_url:
            img_url = urlparse.urljoin(self.site, img_url[0])
            prod['image_url'] = img_url

        prod['url'] = response.url
        prod['locale'] = 'en-US'

        cond_set_value(
            prod,
            'description',
            ''.join(
                response.xpath('//div[@id="description-content"]').extract()),
        )

        cond_set(
            prod,
            'model',
            response.xpath(
                '//section[@class="panel-body wag-colornone"]/text()'
            ).re('Item Code: (\d+)')
        )

        prod_id = re.findall('ID=(.*)-', response.url)[0]
        review_url = self.REVIEW_API_URL.format(prod_id=prod_id)
        price_variants_url = self.PRICE_VARI_API_URL.format(prod_id=prod_id)

        reqs.append(Request(review_url,
                            meta=response.meta,
                            callback=self._parse_review_api))
        reqs.append(Request(price_variants_url,
                            meta=response.meta,
                            callback=self._parse_price_and_variants))

        if reqs:
            return self.send_next_request(reqs, response)
        return prod

    def _scrape_total_matches(self, response):
        data = json.loads(response.body)
        count = int(data['summary']['productInfoCount'])
        return count

    def _scrape_product_links(self, response):
        data = json.loads(response.body)
        if 'products' in data:
            items = data['products']
            for item in items:
                full_link = urlparse.urljoin(
                    self.site,
                    item['productInfo']['productURL'])
                product = self._get_json_data(item)
                yield full_link, product

    def _scrape_next_results_page_link(self, response):
        data = json.loads(response.body)
        if 'products' in data:
            self.page += 1
            next_url = self.SEARCH_URL.format(
                search_term=response.meta['search_term'],
                page=self.page,
                sort_mode=self.SORTING or self.SORT_MODES['relevance'])
            return next_url
        else:
            return None

    def _get_json_data(self, item):
        product = SiteProductItem()
        item = item['productInfo']

        if 'salePrice' in item['priceInfo']:
            price = re.findall('(/?\d+.\d+)',
                               item['priceInfo']['salePrice'])
            if len(price) == 1:
                product['price'] = Price(price=float(price[0]),
                                         priceCurrency='USD')
            else:
                product['price'] = Price(price=float(price[-1]),
                                         priceCurrency='USD')
        elif 'regularPrice' in item['priceInfo']:
            price = re.findall('(/?\d+.\d+)',
                               item['priceInfo']['regularPrice'])
            if len(price) == 1:
                product['price'] = Price(price=float(price[0]),
                                         priceCurrency='USD')
            else:
                product['price'] = Price(price=float(price[-1]),
                                         priceCurrency='USD')

        messages = item.get('channelAvailability', [])
        for mes in messages:
            if 'displayText' in mes:
                if 'Not sold online' in mes['displayText']:
                    product['is_in_store_only'] = True
                if 'Out of stock online' in mes['displayText']:
                    product['is_out_of_stock'] = True

        upc = item.get('upc')
        cond_set_value(product, 'upc', upc)

        return product

    def _parse_review_api(self, response):
        product = response.meta['product']
        reqs = response.meta.get('reqs', [])
        res = re.findall('\{.*\}', response.body)[0]
        data = json.loads(res)

        product['brand'] = data['BatchedResults']['q0']['Results'][0]['Brand']['Name']

        by_star = {}
        stars = data['BatchedResults']['q0']['Results'][0][
            'ReviewStatistics']['RatingDistribution']
        for star in stars:
            by_star[star['RatingValue']] = star['Count']

        total = data['BatchedResults']['q0']['Results'][0][
            'ReviewStatistics']['TotalReviewCount']
        if total == 0:
            product['buyer_reviews'] = ZERO_REVIEWS_VALUE

        else:
            avg = round(data['BatchedResults']['q0']['Results'][0][
                        'ReviewStatistics']['AverageOverallRating'], 1)

            product['buyer_reviews'] = BuyerReviews(num_of_reviews=total,
                                                    average_rating=avg,
                                                    rating_by_star=by_star)
        if reqs:
            return self.send_next_request(reqs, response)

        return product
