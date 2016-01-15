import json
import re
from scrapy import Request
from scrapy.log import ERROR
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set, cond_set_value, populate_from_open_graph
from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews


class JdProductsSpider(BaseProductsSpider):
    name = 'jden_products'
    allowed_domains = ['en.jd.com', 'ipromo.jd.com']
    SEARCH_URL = ('http://en.jd.com/search?'
                  'keywords={search_term}&'
                  'sortType={search_sort}&'
                  'showType=grid')
    PRICE_URL = ('http://ipromo.jd.com/api/promoinfo/getCurJdPrice.html?'
                 'json={{"sid":"{prod_id}","curList":["USD"]}}&'
                 'callback=curJdPriceCallBack')

    SEARCH_SORT = {
        'default': 'relevance_desc',
        'best_match': 'relevance_desc',
        'newest': 'sort_by_onlinetime_desc',
        'popular': 'sort_total_sale_amount_desc',
        'price_asc': 'sort_lowprice_asc',
        'price_desc': 'sort_highprice_desc'
    }

    def __init__(self, search_sort='default', *args, **kwargs):
        super(JdProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort],
            ),
            site_name=self.allowed_domains[0],
            *args, **kwargs)

    def _scrape_total_matches(self, response):
        total = response.css('.total::text').extract()
        if total:
            return int(total[0])
        return 0

    def _scrape_product_links(self, response):
        items = response.css('.list-products-t > ul > li > '
                             '.p-pic > a::attr(href)').extract()
        if not items:
            self.log("Found no product links.", ERROR)
        response.meta['prods_per_page'] = len(items)

        for link in items:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_link = response.css('.p-turn.p-next::attr(href)').extract()
        if next_link:
            return next_link[0]
        return None

    def parse_product(self, response):
        prod = response.meta['product']

        prod['locale'] = 'en-GB'  # ?
        prod['is_out_of_stock'] = False  # ?
        cond_set(prod, 'title', response.css('h1.tit::text').extract())
        cond_set(prod, 'image_url', response.xpath(
            '//meta[property="og:image"]/@content').extract())
        prod_id = response.css('#summary-price::attr(skuid)').extract()[0]
        cond_set_value(prod, 'sku', prod_id)

        reqs = list()
        reqs.append(Request(self.PRICE_URL.format(prod_id=prod_id),
                            callback=self._parse_price))
        return self.send_next_request(reqs, response)

    def _parse_price(self, response):
        prod = response.meta['product']
        str_data = re.findall('curJdPriceCallBack\((\{.*\})\)',
                              response.body_as_unicode())
        data = json.loads(str_data[0])
        price_json = data['priceList'][0]
        price = Price(
            price=price_json.get('discountPrice', price_json.get('jdPrice')),
            priceCurrency=price_json['currency']
        )
        prod['price'] = price
        reqs = response.meta.get('reqs')
        return self.send_next_request(reqs, response)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """
        if not reqs:
            return response.meta['product']
        req = reqs.pop(0)
        new_meta = response.meta.copy()

        if reqs:
            new_meta["reqs"] = reqs

        return req.replace(meta=new_meta)