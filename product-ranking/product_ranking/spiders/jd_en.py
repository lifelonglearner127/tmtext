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
    DESCRIPTION_URL = ('http://en.jd.com/product/getDescription.html?callback='
                       'descriptionCallback&wareid={prod_id}')

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
        sku = response.css('#summary-price::attr(skuid)').extract()[0]
        prod_id = response.css('#summary::attr(data-ware-id)').extract()[0]
        cond_set_value(prod, 'sku', sku)
        self._parse_variants(response)

        reqs = list()
        reqs.append(Request(self.PRICE_URL.format(prod_id=sku),
                            callback=self._parse_price))
        reqs.append(Request(self.DESCRIPTION_URL.format(prod_id=prod_id),
                            callback=self._parse_description))
        return self.send_next_request(reqs, response)

    def _parse_variants(self, response):
        prod = response.meta['product']
        options = response.css('ul.saleAttr')
        variants = []
        for option in options:
            option_name = option.xpath('../preceding-sibling::'
                                       'div[@class="dt"]/text()').extract()[0]
            values = option.xpath('li/a/@title').extract()
            variants.append({option_name: [value for value in values]})
        print '@' * 50
        print variants

    def _parse_price(self, response):
        prod = response.meta['product']
        try:
            str_data = re.findall('curJdPriceCallBack\((\{.*\})\)',
                                  response.body_as_unicode())
            data = json.loads(str_data[0])
            price_json = data['priceList'][0]
            price_discount = price_json.get('discountPrice')
            price_orig = price_json.get('jdPrice')
            if price_discount:
                prod['price_original'] = price_orig
            price = Price(
                price=price_discount or price_orig,
                priceCurrency=price_json['currency']
            )
            prod['price'] = price
        except Exception as e:
            self.log("Get price error: %s" % e, ERROR)
        reqs = response.meta.get('reqs')
        return self.send_next_request(reqs, response)

    def _parse_description(self, response):
        prod = response.meta['product']
        try:
            str_data = re.findall('descriptionCallback\((.+)\)',
                                  response.body_as_unicode())
            data = json.loads(str_data[0])
            descr = data['descriptionVO']['description']
            prod['description'] = descr
        except Exception as e:
            self.log("Get description error: %s" % e, ERROR)
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
# todo: variants, reviews