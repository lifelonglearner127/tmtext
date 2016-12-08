from __future__ import division, absolute_import, unicode_literals
from future_builtins import filter, map

import re

from scrapy.log import ERROR
from scrapy import Request

from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value


class CostcoProductsSpider(BaseProductsSpider):
    name = "costco_products"
    allowed_domains = ["costco.com"]
    start_urls = []

    SEARCH_URL = "http://www.costco.com/CatalogSearch?pageSize=96" \
        "&catalogId=10701&langId=-1&storeId=10301" \
        "&currentPage=1&keyword={search_term}"

    DEFAULT_CURRENCY = u'USD'

    REVIEW_URL = 'http://api.bazaarvoice.com/data/products.json?passkey=bai25xto36hkl5erybga10t99&apiversion=5.5&filter=id:{product_id}&stats=reviews'

    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)

        super(CostcoProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        prod = response.meta['product']

        meta = response.meta.copy()
        reqs = []
        meta['reqs'] = reqs

        # not longer available
        no_longer_available = response.xpath(
            '//*[@class="server-error" and contains(text(),'
            '"out of stock and cannot be added to your cart at this time")]')
        cond_set_value(prod, 'no_longer_available', 1 if no_longer_available else 0)

        if not no_longer_available and response.xpath('//h1[text()="Product Not Found"]'):
            prod['not_found'] = True
            return prod

        model = response.xpath('//div[@id="product-tab1"]//text()').re(
            'Model[\W\w\s]*')
        if len(model) > 0:
            cond_set(prod, 'model', model)
            if 'model' in prod:
                prod['model'] = re.sub(r'Model\W*', '', prod['model'].strip())

        title = response.xpath('//h1[@itemprop="name"]/text()').extract()
        cond_set(prod, 'title', title)

        # Title key must be present even if it is blank
        cond_set_value(prod, 'title', "")

        tab2 = ''.join(
            response.xpath('//div[@id="product-tab2"]//text()').extract()
        ).strip()
        brand = ''
        for i in tab2.split('\n'):
            if 'Brand' in i.strip():
                brand = i.strip()
        brand = re.sub(r'Brand\W*', '', brand)
        if brand:
            prod['brand'] = brand


        merchandising_price = response.xpath('//*[@class="top_review_panel"]/*[@class="merchandisingText"]/text()').re('\$([\d\.\,]+) OFF')
        price_value = ''.join(response.xpath('//input[contains(@name,"price")]/@value').re('[\d.]+')).strip()
        configured_price_html = response.xpath(
            '//span[contains(text(),"Configured Price")]')

        if configured_price_html:
            configured_price = configured_price_html.xpath(
                'following-sibling::span[@class="currency"]'
                '/text()').re('[\d\.\,]+')
            if configured_price:
                cond_set_value(prod, 'price', Price(priceCurrency=self.DEFAULT_CURRENCY,
                                                    price=configured_price[0]))

        elif merchandising_price:
            diff_price = str(float(price_value) + float(merchandising_price[0].replace(',','')))
            cond_set_value(prod, 'price', Price(priceCurrency=self.DEFAULT_CURRENCY,
                                                    price=diff_price))

            cond_set_value(prod, 'price_with_discount', Price(priceCurrency=self.DEFAULT_CURRENCY,
                                                                    price=price_value))
        else:
            price_without_discount = ''.join(response.xpath('//*[@class="online-price"]/span[@class="currency"]/text()').re('[\d\.\,]+')).strip().replace(',','')
            if price_value:
                if price_without_discount:
                    cond_set_value(prod, 'price', Price(priceCurrency=self.DEFAULT_CURRENCY,
                                                        price=price_without_discount))
                    cond_set_value(prod, 'price_with_discount', Price(priceCurrency=self.DEFAULT_CURRENCY,
                                                                        price=price_value))
                else:
                    cond_set_value(prod, 'price', Price(priceCurrency=self.DEFAULT_CURRENCY,
                                                        price=price_value))


        des = response.xpath('//div[@id="product-tab1"]//text()').extract()
        des = ' '.join(i.strip() for i in des)
        if '[ProductDetailsESpot_Tab1]' in des.strip():
            des = response.xpath("//div[@id='product-tab1']/*[position()>1]//text()").extract()
            des = ' '.join(i.strip() for i in des)
            if des.strip():
                prod['description'] = des.strip()

        elif des:
            prod['description'] = des.strip()

        img_url = response.xpath('//img[@itemprop="image"]/@src').extract()
        cond_set(prod, 'image_url', img_url)

        cond_set_value(prod, 'locale', 'en-US')
        prod['url'] = response.url

        # Categories
        categorie_filters = ['home']
        # Clean and filter categories names from breadcrumb
        categories = list(filter((lambda x: x.lower() not in categorie_filters),
                        map((lambda x: x.strip()), response.xpath('//*[@itemprop="breadcrumb"]//a/text()').extract())))

        category = categories[-1] if categories else None

        cond_set_value(prod, 'categories', categories)
        cond_set_value(prod, 'category', category)

        # Minimum Order Quantity
        try:
            minium_order_quantity = re.search('Minimum Order Quantity: (\d+)', response.body_as_unicode()).group(1)
            cond_set_value(prod, 'minimum_order_quantity', minium_order_quantity)
        except:
            pass

        shipping = ''.join(response.xpath(
            '//*[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
            ' "abcdefghijklmnopqrstuvwxyz"), "shipping & handling:")]'
        ).re('[\d\.\,]+')).strip().replace(',', '')
        if not shipping:
            shipping = ''.join(response.xpath(
            '//*[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
            ' "abcdefghijklmnopqrstuvwxyz"), "shipping and handling:")]'
        ).re('[\d\.\,]+')).strip().replace(',', '')

        if shipping:
            cond_set_value(prod, 'shipping_cost', Price(priceCurrency=self.DEFAULT_CURRENCY,
                                                        price=shipping))

        shipping_included = ''.join(response.xpath(
            '//*[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
            ' "abcdefghijklmnopqrstuvwxyz"),"shipping & handling included")]'
        ).extract()).strip().replace(',', '') or \
            response.xpath(
                '//*[@class="merchandisingText" and '
                'contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", '
                '"abcdefghijklmnopqrstuvwxyz"), "free shipping")]') or \
            ''.join(response.xpath(
                '//p[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
                ' "abcdefghijklmnopqrstuvwxyz"),"shipping and handling included")]'
            ).extract()).strip().replace(',', '')

        cond_set_value(prod, 'shipping_included', 1 if shipping_included or shipping == "0.00" else 0)

        available_store = re.search('Item may be available in your local warehouse', response.body_as_unicode())
        cond_set_value(prod, 'available_store', 1 if available_store else 0)

        not_available_store = re.search('Not available for purchase on Costco.com', response.body_as_unicode())
        cond_set_value(prod, 'available_online', 0 if not_available_store else 1)

        if str(prod.get('available_online', None)) == '0' and str(prod.get('available_store', None)) == '0':
            prod['is_out_of_stock'] = True

        count_review = response.xpath('//meta[contains(@itemprop, "reviewCount")]/@content').extract()
        product_id = re.findall(r'var bvProductId = \'(.+)\';', response.body_as_unicode())

        if product_id and count_review:
            reqs.append(
                Request(
                    url=self.REVIEW_URL.format(product_id=product_id[0], index=0),
                    dont_filter=True,
                    callback=self.parse_buyer_reviews,
                    meta=meta
                ))

        if reqs:
            return self.send_next_request(reqs, response)

        return prod

    def parse_buyer_reviews(self, response):
        meta = response.meta.copy()
        product = response.meta['product']
        reqs = meta.get('reqs', [])

        product['buyer_reviews'] = self.br.parse_buyer_reviews_products_json(response)

        if reqs:
            return self.send_next_request(reqs, response)
        else:
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

    def _search_page_error(self, response):
        if not self._scrape_total_matches(response):
            self.log("Costco: unable to find a match", ERROR)
            return True
        return False

    def _scrape_total_matches(self, response):
        count = response.xpath(
            '//*[@id="secondary_content_wrapper"]/div/p/span/text()'
        ).re('(\d+)')
        count = int(count[-1]) if count else None
        if not count:
            count = response.xpath(
                '//*[@id="secondary_content_wrapper"]'
                '//span[contains(text(), "Showing results")]/text()'
            ).extract()
            count = int(count[0].split(' of ')[1].replace('.', '').strip()) if count else None
        if not count:
            count = response.css(".table-cell.results.hidden-xs.hidden-sm.hidden-md>span").re(
                r"Showing\s\d+-\d+\s?of\s?([\d.,]+)")
            count = int(count[0].replace('.', '').replace(',', '')) if count else None
        return count

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[contains(@class,"product-list grid")]//a[contains(@class,"thumbnail")]/@href'
        ).extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath(
            "//*[@class='pagination']"
            "/ul[2]"  # [1] is for the Items Per Page section which has .active.
            "/li[@class='active']"
            "/following-sibling::li[1]"  # [1] is to get just the next sibling.
            "/a/@href"
        ).extract()
        if links:
            link = links[0]
        else:
            link = None

        return link
