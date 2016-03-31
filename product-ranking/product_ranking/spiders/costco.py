from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re

from scrapy.log import ERROR
from scrapy import Request

from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value


class CostcoProductsSpider(BaseProductsSpider):
    name = "costco_products"
    allowed_domains = ["costco.com"]
    start_urls = []

    SEARCH_URL = "http://www.costco.com/CatalogSearch?pageSize=96" \
        "&catalogId=10701&langId=-1&storeId=10301" \
        "&currentPage=1&keyword={search_term}"

    DEFAULT_CURRENCY = u'USD'

    REVIEW_URL = 'http://api.bazaarvoice.com/data/batch.json?passkey=bai25xto36hkl5erybga10t99&apiversion=5.5' \
                 '&displaycode=2070-en_us&resource.q0=products&filter.q0=id%3Aeq%3A{product_id}&stats.q0=reviews' \
                 '&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_CA%2Cen_US' \
                 '&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_CA%2Cen_US&resource.q1=reviews' \
                 '&filter.q1=isratingsonly%3Aeq%3Afalse&filter.q1=productid%3Aeq%3A{product_id}' \
                 '&filter.q1=contentlocale%3Aeq%3Aen_CA%2Cen_US&sort.q1=submissiontime%3Adesc&stats.q1=reviews' \
                 '&filteredstats.q1=reviews&include.q1=authors%2Cproducts%2Ccomments' \
                 '&filter_reviews.q1=contentlocale%3Aeq%3Aen_CA%2Cen_US' \
                 '&filter_reviewcomments.q1=contentlocale%3Aeq%3Aen_CA%2Cen_US' \
                 '&filter_comments.q1=contentlocale%3Aeq%3Aen_CA%2Cen_US&limit.q1=8&offset.q1=0' \
                 '&limit_comments.q1=3&resource.q2=reviews&filter.q2=productid%3Aeq%3A{product_id}' \
                 '&filter.q2=contentlocale%3Aeq%3Aen_CA%2Cen_US&limit.q2=1&resource.q3=reviews' \
                 '&filter.q3=productid%3Aeq%3A{product_id}&filter.q3=isratingsonly%3Aeq%3Afalse' \
                 '&filter.q3=rating%3Agt%3A3&filter.q3=totalpositivefeedbackcount%3Agte%3A3' \
                 '&filter.q3=contentlocale%3Aeq%3Aen_CA%2Cen_US&sort.q3=totalpositivefeedbackcount%3Adesc' \
                 '&include.q3=authors%2Creviews%2Cproducts&filter_reviews.q3=contentlocale%3Aeq%3Aen_CA%2Cen_US' \
                 '&limit.q3=1&resource.q4=reviews&filter.q4=productid%3Aeq%3A{product_id}' \
                 '&filter.q4=isratingsonly%3Aeq%3Afalse&filter.q4=rating%3Alte%3A3' \
                 '&filter.q4=totalpositivefeedbackcount%3Agte%3A3&filter.q4=contentlocale%3Aeq%3Aen_CA%2Cen_US' \
                 '&sort.q4=totalpositivefeedbackcount%3Adesc&include.q4=authors%2Creviews%2Cproducts' \
                 '&filter_reviews.q4=contentlocale%3Aeq%3Aen_CA%2Cen_US&limit.q4=1&callback=BV._internal.dataHandler0'

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

        if response.xpath('//h1[text()="Product Not Found"]'):
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

        if merchandising_price:
            diff_price = str(float(price_value) - float(merchandising_price[0].replace(',','')))
            cond_set_value(prod, 'price', Price(priceCurrency=self.DEFAULT_CURRENCY,
                                                    price=price_value))

            cond_set_value(prod, 'price_with_discount', Price(priceCurrency=self.DEFAULT_CURRENCY,
                                                                    price=diff_price))
        else:
            price_without_discount = ''.join(response.xpath('//*[@class="online-price"]/span[@class="currency"]/text()').re('[\d\.\,]+')).strip().replace(',','')
            if price_value and price_value != '0.00':
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
                        map((lambda x: x.strip()),response.xpath('//*[@itemprop="breadcrumb"]//a/text()').extract())))

        category = categories[-1] if categories else None
        
        cond_set_value(prod, 'categories', categories)
        cond_set_value(prod, 'category', category)

        # Minimum Order Quantity
        try:
            minium_order_quantity = re.search('Minimum Order Quantity: (\d+)', response.body_as_unicode()).group(1)
            cond_set_value(prod, 'minimum_order_quantity', minium_order_quantity)
        except:
            pass

        shipping = ''.join(response.xpath('//p[contains(text(),"Shipping & Handling:")]').re('[\d\.\,]+')).strip().replace(',','')
        
        if shipping and shipping != "0.00":
            cond_set_value(prod, 'shipping_cost', Price(priceCurrency=self.DEFAULT_CURRENCY,
                                                    price=shipping))

        shipping_included = ''.join(response.xpath('//p[contains(text(),"Shipping & Handling Included")]').extract()).strip().replace(',','')
        cond_set_value(prod, 'shipping_included', 1 if shipping_included else 0)
        
        available_store = re.search('Item may be available in your local warehouse', response.body_as_unicode())
        cond_set_value(prod, 'available_store', 1 if available_store else 0)

        not_available_store = re.search('Not available for purchase on Costco.com', response.body_as_unicode())
        cond_set_value(prod, 'available_online', 0 if not_available_store else 1)


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

        product['buyer_reviews'] = self.br.parse_buyer_reviews_batch_json(response)

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
        try:
            count = response.xpath(
                '//*[@id="secondary_content_wrapper"]/div/p/span/text()'
            ).re('(\d+)')[-1]
            if count:
                return int(count)
            return 0
        except IndexError:
            count = response.xpath(
                '//*[@id="secondary_content_wrapper"]'
                '//span[contains(text(), "Showing results")]/text()'
            ).extract()
            return int(count[0].split(' of ')[1].replace('.', '').strip())

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[contains(@class,"product-tile-image-container")]/a/@href'
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
