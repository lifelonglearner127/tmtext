from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re

from scrapy.selector import Selector
from scrapy.log import ERROR
from scrapy.http import Request

from product_ranking.items import SiteProductItem, Price, RelatedProduct, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider,FormatterWithDefaults, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX


class DrugstoreProductsSpider(BaseProductsSpider):
    name = 'drugstore_products'
    allowed_domains = ["drugstore.com",
        "recs.richrelevance.com"]
    start_urls = []

    SEARCH_URL = "http://www.drugstore.com/search/search_results.asp?"\
        "Ns={search_sort}&N=0&Ntx=mode%2Bmatchallpartial&Ntk=All" \
        "&srchtree=5&Ntt={search_term}"

    SEARCH_SORT = {
        'best_match': '',
        'best_selling': 'performanceRank%7c0',
        'new_to_store': 'newToStoreDate%7c1',
        'a-z': 'Brand+Line%7c0%7c%7cname%7c0%7c%7cgroupDistinction%7c0',
        'z-a' : 'Brand+Line%7c1%7c%7cname%7c1%7c%7cgroupDistinction%7c1',
        'customer_rating': 'avgRating%7c1%7c%7cratingCount%7c1',
        'low_to_high_price': 'price%7c0',
        'high_to_low_price': 'price%7c1',
        'saving_dollars': 'savingsAmount%7c1',
        'saving_percent': 'savingsPercent%7c1',
    }

    def __init__(self, search_sort='best_match', *args, **kwargs):
        if "search_modes" in kwargs:
            search_sort = kwargs["search_modes"]
        super(DrugstoreProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort]
            ),
            site_name="drugstore.com",
            *args, **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(product, 'title', response.xpath(
            "string(//div[@id='divCaption']/h1[1])").extract())

        cond_set(product, 'image_url', response.xpath(
            "//div[@id='divPImage']//img/@src").extract())

        cond_set(product, 'price', response.xpath(
            "//div[@id='productprice']/*[@class='price']/text()").extract())

        if product.get('price', None):
            if not '$' in product['price']:
                self.log('Unknown currency at' % response.url)
            else:
                product['price'] = Price(
                    price=product['price'].replace(',', '').replace(
                        '$', '').strip(),
                    priceCurrency='USD'
                )

        cond_set_value(product, 'description', response.xpath(
            "//div[@id='divPromosPDetail']/table/tr/td").extract())

        brand = response.xpath('//div[@id="brandStoreLink"]/a/text()').extract()
        if brand:
            brand = re.findall('see more from (.*)', brand[0])
            cond_set_value(product, 'brand', brand)

        is_out_of_stock = response.xpath(
            '//div[@id="divAvailablity"]/text()').extract()
        if is_out_of_stock:
            if is_out_of_stock[0] == "in stock":
                is_out_of_stock = False
            else:
                is_out_of_stock = True
            cond_set(product, 'is_out_of_stock', (is_out_of_stock,))

        product['locale'] = "en-US"

        #Buyer reviews
        average_rating = response.xpath(
            '//span[contains(@class, "average")]/text()'
        ).re(FLOATING_POINT_RGEX)

        num_of_reviews = response.xpath(
            '//p[@class="pr-review-count"]/text()').re(FLOATING_POINT_RGEX)

        rating_by_star = {1:0, 2:0, 3:0, 4:0, 5:0}
        for li in response.xpath('//ul[@class="pr-ratings-histogram-content"]/li'):
            i = li.xpath(
                'p[@class="pr-histogram-label"]/span/text()'
            ).re(FLOATING_POINT_RGEX)
            count = li.xpath(
                'p[@class="pr-histogram-count"]/span/text()'
            ).re(FLOATING_POINT_RGEX)
            if i and count:
                rating_by_star[int(i[0])] = int(count[0])
        
        if average_rating and num_of_reviews:
            product["buyer_reviews"] = BuyerReviews(
                num_of_reviews=num_of_reviews[0],
                average_rating=average_rating[0],
                rating_by_star=rating_by_star,
            )

        #related_products
        prod_id = re.findall('var dtmProductId\s+\=\s+\'(\d+)\'', response.body)
        if prod_id:
            url = "http://recs.richrelevance.com/rrserver/p13n_generated.js?" \
                "a=bc4f2197c160e3dd&ts=1422951881817" \
                "&cs=%7C195861%3Amassage%20tables%20%26%20accessories" \
                "&re=True&pt=%7Citem_page.rr1" \
                "&u=1EAFA20B71FE47DABCF769FC97F93858" \
                "&s=EA668A065C864DCEAE8919DF1868FAA8" \
                "&cv=0&l=1&p="+ prod_id[0]
            return Request(
                url,
                meta={'product': product, 'remaining': self.quantity},
                callback=self.get_related_products,
            )
        else:
            return product

    def get_related_products(self, resp):
        rp = []
        product = resp.meta['product']
        all_inf = Selector(text=resp.body).xpath(
            '//td[@class="weRecommend"]/a')
        if all_inf:
            urls = all_inf.xpath('@href').extract()
            titles = all_inf.xpath(
                'div[@class="weRecommendSubText"]/text()').extract()
            titles = [x.strip() for x in titles]
            for i in range(0, len(titles)):
                rp.append(
                    RelatedProduct(
                        title=titles[i],
                        url=urls[i]
                    )
                )
        if rp:
            product["related_products"] = {"recommend": rp}
        return product

    def _scrape_total_matches(self, response):
        total_matches = response.xpath(
            '//h2[@class="SrchMsgHeader"]/text()'
        ).re(FLOATING_POINT_RGEX)

        if total_matches:
            return int(total_matches[0].replace(',', ''))        
        return 0

    def _scrape_product_links(self, response):
        items = response.css('div.itemGrid div.info')
        if not items:
            self.log("Found no product links.", ERROR)
            
        for item in items:
            link = item.xpath('.//a/@href').extract()[0]
            brand = item.xpath('.//span[@class="name"]/text()').extract()[0]
            yield link, SiteProductItem(brand=brand.strip(' -'))

    def _scrape_next_results_page_link(self, response):
        link = response.xpath(
            '//table[@class="srdSrchNavigation"]'
            '//a[@class="nextpage"]/@href'
        ).extract()
        
        if link:
            return link[0]
        return None
