from __future__ import division, absolute_import, unicode_literals

import urlparse
import urllib
import json
import re

from scrapy import FormRequest
from scrapy.log import WARNING
from scrapy.http import Request

from product_ranking.items import SiteProductItem, Price, RelatedProduct,\
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider, \
    FormatterWithDefaults, FLOATING_POINT_RGEX, dump_url_to_file


class EBuyerProductSpider(BaseProductsSpider):
    """Spider for ebuyer.com.

    Allowed search orders:
    -'rating'
    -'price_asc'
    -'price_desc'
    -'default'

    Fields limited_stock, is_in_store_only, upc not provided.

    When related_products provided site server return 4*2 recommended
    products. But on page site randomly display only 3*2. Spider
    parse all 4*2 products.
    Also when cookies wasn't cleared at browser ebuyer may display
    category "Items Related to Your Recent Searches". Spider don't
    see this category.
    """
    name = 'ebuyer_products'
    allowed_domains = ["ebuyer.com",  "recs.richrelevance.com",
                       "mark.reevoo.com"]

    SEARCH_URL = "http://www.ebuyer.com/search?q={search_term}"

    SEARCH_SORT = {
        'rating': 'rating descending',
        'price_asc': 'price ascending',
        'price_desc': 'price descending',
        'default': 'relevancy descending',
    }

    SCRIPT_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js?"

    RECOMM_AJAX_URL = "http://www.ebuyer.com/rich-relevance-ajax"

    REVIEW_URL = "http://mark.reevoo.com/reevoomark/en-GB/product"\
                 "?trkref=EBU&sku={sku}"

    POPULATE_REVIEWS = True

    def __init__(self, search_sort='default', *args, **kwargs):
        self.order = self.SEARCH_SORT[search_sort]
        super(EBuyerProductSpider, self).__init__(
            url_formatter=FormatterWithDefaults(),
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def start_requests(self):
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8')),
                ),
                callback=self.sort_handling,
                meta={'search_term': st, 'remaining': self.quantity},
            )

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod})

    def sort_handling(self, response):
        parsed = urlparse.urlparse(response.url)
        qs = urlparse.parse_qs(parsed.query)
        qs['sort'] = [self.order]
        new_query = urllib.urlencode(qs, doseq=True)
        new_parsed = parsed._replace(query=new_query)
        sorted_url = urlparse.urlunparse(new_parsed)
        return Request(sorted_url, callback=self.parse,
                       meta=response.meta.copy())

    def _scrape_total_matches(self, response):
        num_results = response.xpath(
            '//li[@class="listing-count"]/text()').re('(\d+)')
        if num_results and num_results[1]:
            total = int(num_results[1])
            if total == 1000:
                # Get approximate number of total matches.
                # Since the site doesn't provide it for search
                # result with number bigger than 1000
                total = 15*int(num_results[0])
            return total
        else:
            return 0

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//h3[@class="listing-product-title"]/a/@href').extract()
        if not links:
            self.log("Found no product links.", WARNING)
        for link in links:
            link = urlparse.urljoin(response.url, link)
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath(
            '//li[@class="next-page"]/a/@href').extract()
        if next and next[0]:
            next_url = next[0] + '&sort=' + self.order
            return urlparse.urljoin(response.url, next_url)
        else:
            return None

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        prod = response.meta['product']

        prod['url'] = response.url
        prod['locale'] = 'en_GB'

        title = response.xpath(
            '//h1[@class="product-title"]/text()').extract()
        if title:
            prod['title'] = title[0].strip()

        img = response.xpath(
            '//img[@itemprop="image"]/@src').extract()
        if img:
            prod['image_url'] = urlparse.urljoin(response.url, img[0])

        price = response.xpath(
            '//span[@itemprop="price"]/text()').re(FLOATING_POINT_RGEX)
        if price:
            prod['price'] = Price(price=price[0],
                                  priceCurrency='GBP')

        description = response.xpath(
            '//div[@class="product-description"]').extract()
        if not description:
            description = response.xpath(
                '//ul[@itemprop="description"]'
            ).extract()
        if description:
            prod['description'] = description[0].strip()

        brand = response.xpath(
            '//img[@itemprop="logo"]/@alt').extract()
        if brand:
            prod['brand'] = brand[0]

        if not prod.get('brand', None):
            dump_url_to_file(response.url)

        in_stock = response.xpath(
            '//p[@itemprop="availability"]/@content').extract()
        if in_stock:
            if in_stock[0] == 'in_stock':
                prod['is_out_of_stock'] = False
            else:
                prod['is_out_of_stock'] = True

        sku = response.xpath(
            '//strong[@itemprop="sku"]/text()'
        ).extract()
        if sku:
            prod['model'] = sku[0]

        d = re.findall(r'window.ebuyer.config\s=\s(.*);',
                       response.body_as_unicode())
        if d:
            data = json.loads(d[0])
            a = data['richRelevance']['apiKey']
            p = data['product']['id']
            s = data['sessionId']
            pt = '|item_page.recs_1|item_page.recs_2'
            l = 1
            get_dict = {
                'a': a,
                'p': p,
                's': s,
                'pt': pt,
                'l': l
            }
            converted_get = urllib.urlencode(get_dict)
            related_link = self.SCRIPT_URL + converted_get
            meta = response.meta.copy()
            meta['item_id'] = p
            yield Request(related_link, callback=self.get_recommended_id,
                          meta=meta)
        yield prod

    def get_recommended_id(self, response):
        placements = re.findall(
            'rr_call_after_flush=function\(\){(.*)};rr_flush=function',
            response.body
        )
        if not placements:
            return None
        splited = placements[0].split('json = ')
        splited = splited[1:]
        ids_data = {}
        for placement in splited:
            strategy = re.findall(
                '{\s*"strategy_message":"(.*)",\s*"items".*};', placement)
            if strategy:
                strategy = strategy[0]
                ids = re.findall(r'"id":"(\d+)",', placement)
                ids_data[strategy] = ids
        if not ids_data:
            return response.meta['product']
        data = []
        for value in ids_data.values():
            for item in value:
                post_data = ('productIds[]', '%s' % item)
                data.append(post_data)
        meta = response.meta.copy()
        meta['ids_data'] = ids_data
        return FormRequest(self.RECOMM_AJAX_URL,
                           callback=self.populate_recommendations,
                           formdata=data,
                           dont_filter=True,
                           meta=meta)

    def populate_recommendations(self, response):
        ids_data = response.meta['ids_data']
        product = response.meta['product']
        related = product.get('related_products', {})
        # ids = ids_data[ids_data.keys()[0]]
        for key in ids_data.keys():
            recomm = []
            ids = ids_data[key]
            body = json.loads(response.body)
            for item_id in ids:
                try:
                    name = body['recommendedProducts'][item_id]['name']
                    url = body['recommendedProducts'][item_id]['canonicalUrl']
                except KeyError:
                    pass
                else:
                    full_url = "http://www.ebuyer.com/" + url
                    recomm.append(RelatedProduct(name, full_url))
            related[key] = recomm
        # pls note that server return to spider and site 8 products,
        # but displayed by javascript only 6.
        product['related_products'] = related
        sku = response.meta['item_id']
        url = self.REVIEW_URL.format(sku=sku)
        if self.POPULATE_REVIEWS:
            meta = response.meta.copy()
            meta['handle_httpstatus_list'] = [404]
            return Request(url, callback=self.populate_reviews,
                           meta=meta)
        return product

    def populate_reviews(self, response):
        product = response.meta['product']
        if response.status == 404:
            return product
        avg_total = response.xpath(
            '//div[@class="average_score"]/@title'
        ).extract()
        if not avg_total:
            product['buyer_reviews'] = ZERO_REVIEWS_VALUE
            return product
        return self.populate_by_star(response)

    def populate_by_star(self, response):
        # maybe some optimisation will required for this method
        total_scores = response.meta.get('total_scores', [])
        scores = response.xpath(
            '//article[contains(@id, "review")]'
            '//span[contains(@class, "overall_score")]/@title'
        ).extract()
        total_scores.extend(scores)
        next_url = response.xpath('//a[@class="next_page"]/@href').extract()
        if next_url:
            url = 'http://mark.reevoo.com' + next_url[0]
            meta = response.meta.copy()
            meta['total_scores'] = total_scores
            return Request(url, callback=self.populate_by_star,
                           meta=meta)
        stars = {}
        for number in range(1, 11):
            pattern = '%s out of 10' % number
            counted = total_scores.count(pattern)
            stars[number] = counted

        avg_total = response.xpath(
            '//div[@class="average_score"]/@title'
        ).extract()
        avg = re.findall(r'is\s(.*)\sout', avg_total[0])
        avg = float(avg[0])
        total = re.findall(r'from\s(\d+)\sreview', avg_total[0])
        total = int(total[0])

        product = response.meta['product']
        if total:
            product['buyer_reviews'] = BuyerReviews(total, avg, stars)
        else:
            product['buyer_reviews'] = ZERO_REVIEWS_VALUE
        return product
