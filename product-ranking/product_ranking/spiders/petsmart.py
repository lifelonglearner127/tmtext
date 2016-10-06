import re
import string
import urllib

from scrapy import Request

from product_ranking.items import SiteProductItem, Price, BuyerReviews, RelatedProduct
from product_ranking.spiders.contrib.product_spider import ProductsSpider



def _populate(item, key, value, first=False):
    if not value:
        return
    value = filter(None, map(string.strip, value))
    if value:
        if first:
            item[key] = value[0]
        else:
            item[key] = value



class PetsmartProductsSpider(ProductsSpider):
    name = 'petsmart_products'
    allowed_domains = ['petsmart.com']

    SEARCH_URL = 'http://www.petsmart.com/search?SearchTerm={search_term}'

    XPATH = {
        'product': {
            'title': '//h1[contains(@class, "ws-product-title")]/text()',
            'categories': '//li[@class="ws-breadcrumbs-list-item"]/a/text()',
            'description': '//div[@class="ws-product-long-description"]',
            'price': '//form//span[contains(@class, "price-value")]/text()',
            'image_url': '//div[contains(@class, "ws-product-photo")]/@data-zoom-image',
            'out_of_stock_button': '//button[contains(@class, "ws-add-to-cart-inactive")]',
            'not_available_online': '//div[contains(@class, "shopoption") and text()="Not Sold Online"]',
            'not_available_store': '//div[contains(@class, "shopoption") and text()="Not Sold In Stores"]',
            'sku': '//input[@name="SKU"]/@value',
            'size': '//input[@name="SizeCode"]/@value',
            'color': '//input[@name="ColorCode"]/@value',
            'variants': '//li[contains(@class, "ws-variation-list-item")]/@data-sku',
            'average_rating': '//span[@itemprop="aggregateRating"]//span[@itemprop="ratingValue"]/text()',
            'reviews_count': '//span[@itemprop="aggregateRating"]//span[@itemprop="reviewCount"]/text()',
        },
        'search': {
            'total_matches': '//h1[@class="ws-heading"]',
            'next_page': '//li[contains(@class, "pagination-list-next-page")]/a/@href',
            'prod_links': '//li[@data-product]//a[contains(@class, "url") and h4]/@href',
        },
    }



    def _parse_single_product(self, response):
        return self.parse_product(response)


    def parse_product(self, response):
        product = response.meta['product']

        # locale
        product['locale'] = 'en_US'

        # title
        title = response.xpath(self.XPATH['product']['title']).extract()
        _populate(product, 'title', title, first=True)

        # categories
        categories = response.xpath(self.XPATH['product']['categories']).extract()
        _populate(product, 'categories', categories)
        if product.get('categories'):
            product['category'] = product['categories'][-1]

        # description
        description = response.xpath(self.XPATH['product']['description']).extract()
        _populate(product, 'description', description, first=True)

        # buyer reviews
        average_rating = response.xpath(self.XPATH['product']['average_rating']).re(r'([\d.]+)')
        reviews_count = response.xpath(self.XPATH['product']['reviews_count']).re(r'(\d+)')
        if average_rating and reviews_count:
            product['buyer_reviews'] = BuyerReviews(
                num_of_reviews=int(reviews_count[0]),
                average_rating=float(average_rating[0]),
                rating_by_star={}
            )

        # variants
        variants = set(response.xpath(self.XPATH['product']['variants']).extract())

        if len(variants) > 1:
            product['variants'] = []
            response.meta['product'] = product
            variant_sku = variants.pop()
            response.meta['variants'] = variants
            return Request(
                response.url.split('?')[0].split(';')[0] + '?var_id=' + variant_sku,
                meta=response.meta,
                callback=self._parse_variants,
                # dont_filter=True
            ) 
        else:
            product['variants'] = [self._parse_variant_data(response)]
            return product


    def _parse_variants(self, response):
        response.meta['product']['variants'].append(
            self._parse_variant_data(response)
        )
        if response.meta.get('variants'):
            variant_sku = response.meta['variants'].pop()
            return Request(
                response.url.split('?')[0] + '?var_id=' + variant_sku,
                meta=response.meta,
                callback=self._parse_variants,
                # dont_filter=True
            )
        else:
            return response.meta['product'] 
 

    def _parse_variant_data(self, response):
        data = {}

        # image url
        image_url = response.xpath(self.XPATH['product']['image_url']).extract()
        _populate(data, 'image_url', image_url, first=True)

        # in stock?
        stock = response.xpath(self.XPATH['product']['out_of_stock_button']).extract()
        data['is_out_of_stock'] = bool(stock)

        if data['is_out_of_stock']:
            data['available_online'] = False
            data['available_store'] = False
        else:
            if response.xpath(self.XPATH['product']['not_available_online']):
                data['is_in_store_only'] = True
                data['available_online'] = False
                data['available_store'] = True
            elif response.xpath(self.XPATH['product']['not_available_store']):
                data['is_in_store_only'] = False
                data['available_online'] = True
                data['available_store'] = False
                
        # sku
        sku = response.xpath(self.XPATH['product']['sku']).extract()
        _populate(data, 'sku', sku, first=True)

        # price
        price = response.xpath(self.XPATH['product']['price']).extract()
        if price:
            price = price[0].strip('$ ')
            data['price'] = Price(price=price, priceCurrency='USD')

        # size
        size = response.xpath(self.XPATH['product']['size']).extract()
        _populate(data, 'size', size, first=True)

        # color
        color = response.xpath(self.XPATH['product']['color']).extract()
        _populate(data, 'color', color, first=True)

        return data
        

    def _total_matches_from_html(self, response):
        total_matches = response.xpath(self.XPATH['search']['total_matches']).re(r'\d+')
        if total_matches:
            return int(total_matches[0])


    def _scrape_next_results_page_link(self, response):
       next_page = response.xpath(self.XPATH['search']['next_page']).extract()
       if next_page:
           return next_page[0] 


    def _scrape_product_links(self, response):
        for link in response.xpath(self.XPATH['search']['prod_links']).extract():
            yield link.split('?')[0].split(';')[0], SiteProductItem()



