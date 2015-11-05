from __future__ import division, absolute_import, unicode_literals

import urlparse
import json
import re
import string

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
        'relevance':         'relevance',  # default
        'top_sellers':       'Top Sellers',
        'price_asc':         'Price Low to High',
        'price_desc':        'Price High to Low',
        'product_name_asc':  'Product Name A-Z',
        'product_name_desc': 'Product Name Z-A',
        'most_reviewed':     'Most Reviewed',
        'highest_rated':     'Highest Rated',
        'most_viewed':       'Most Viewed',
        'newest_arrival':    'Newest Arrival'
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

    def _parse_single_product(self, response):
        pId = re.findall("ID=prod(\d+)", response.url)
        if pId:
            url = "http://www.walgreens.com/svc/products" \
                "/prod%s/(PriceInfo+Inventory)?rnd=1428572592049" % (pId[0],)
            meta = response.meta.copy()
            meta.update({"response": response})
            return Request(
                url=url, 
                callback=self.get_price_single_product, 
                meta=meta
            )
        return self.parse_product(response)

    def get_price_single_product(self, response):
        try:
            data = json.loads(response.body)
        except:
            data = {}

        result = self.parse_product(response.meta["response"])
        meta = result.meta.copy()
        
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
                price = price[0]
                meta["product"]["price"] = Price(
                    price=price,
                    priceCurrency='USD'
                )       
        return result.replace(meta=meta)

    def parse_price_single_product(self, data, key):
        if "1/" in data[key]:
            price = re.findall("1\/.(\d+\.{0,1}\d+)", data[key])
        else:
            price = re.findall("(\d+\.{0,1}\d+)", data[key])
        return price

    def parse_product(self, response):
        prod = response.meta['product']

        title = response.xpath('//h2[@id="productName"]/text()').extract()
        if title:
            prod['title'] = title[0].strip()
        else:
            #title = response.css('h1#productName ::text').extract()
            title = response.xpath('//h1[@id="productName"]').extract()
            cond_set(prod, 'title', title)

        if prod['title']:
            prod['title'] = ''.join([c for c in prod['title']
                                     if c in string.printable and c != '\n'])

        img_url = response.xpath(
            '//img[@id="main-product-image"]/@src').extract()
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
        url = self.REVIEW_API_URL.format(prod_id=prod_id)
        new_meta = response.meta.copy()
        new_meta['product'] = prod
        return Request(url, meta=new_meta, callback=self._parse_review_api)

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

        return product

    def _parse_review_api(self, response):
        product = response.meta['product']
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
            return product

        avg = round(data['BatchedResults']['q0']['Results'][0][
                    'ReviewStatistics']['AverageOverallRating'], 1)

        product['buyer_reviews'] = BuyerReviews(num_of_reviews=total,
                                                average_rating=avg,
                                                rating_by_star=by_star)

        return product