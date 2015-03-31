from __future__ import division, absolute_import, unicode_literals
import json
import re

from scrapy.http import HtmlResponse

from product_ranking.items import Price, BuyerReviews
from product_ranking.spiders import cond_set, \
    cond_set_value

# scrapy crawl amazoncouk_products -a searchterms_str="iPhone"


from product_ranking.spiders.contrib.product_spider import ProductsSpider


# TODO: related_products


class GandermountainProductsSpider(ProductsSpider):
    name = "gandermountain_products"
    allowed_domains = ["www.gandermountain.com"]
    start_urls = []

    SEARCH_URL = "http://www.gandermountain.com/modperl/wbsrvcs" \
                 "/adobeSearch.cgi?do=json&q={search_term}&sort={sort_mode}" \
                 "&page={page}"

    SORT_MODES = {
        'default': ''
    }

    def __init__(self, *args, **kwargs):
        super(GandermountainProductsSpider, self).__init__(*args, **kwargs)
        self.url_formatter.defaults['page'] = 1

    def parse(self, response):
        json_data = json.loads(response.body_as_unicode())
        resp = HtmlResponse(response.url, response.status, response.headers,
                            ''.join([chunk for chunk in json_data.itervalues()
                                     if isinstance(chunk, unicode)]),
                            response.flags, response.request,
                            encoding=response.encoding)

        return list(super(GandermountainProductsSpider, self).parse(resp))

    def _scrape_next_results_page_link(self, response):
        next_link = response.css('[alt=arrow-r-blue]')
        if not next_link:
            return
        page = int(re.findall('page=(\d+)', response.url)[0]) + 1
        search_term = response.meta['search_term']
        return self.url_formatter.format(self.SEARCH_URL, page=page,
                                         search_term=search_term)

    def _total_matches_from_html(self, response):
        matches = response.xpath(
            '//p[@class="page-numbers"]/strong/text()').re('\d+')
        return int(matches[0]) if matches else 0

    def _fetch_product_boxes(self, response):
        return response.css('[id*=bItem]')

    def _link_from_box(self, box):
        return box.css('a[title]::attr(href)')[0].extract()

    def _populate_from_box(self, response, box, product):
        cond_set(product, 'title',
                 box.css('a[data-item-number]::attr(title)').extract())
        cond_set(product, 'price',
                 box.css('.red-message.price-point::text').re('\$([\d ,.]+)'))
        cond_set(product, 'price',
                 box.css('.price-point::text').re('\$([\d ,.]+)'))

    def _populate_from_html(self, response, product):
        cond_set(product, 'title', response.css('.product-title h1::text'),
                 unicode.strip)
        cond_set(product, 'price',
                 response.css('.saleprice span::text').re('\$([\d ,.]+)'))
        cond_set(product, 'price',
                 response.css('.regprice span::text').re('\$([\d ,.]+)'))
        cond_set(product, 'image_url',
                 response.css('.jqzoom img::attr(src)').extract())
        cond_set_value(product, 'is_out_of_stock', not (response.css(
            '.stockstatus .info::text').re('In Stock|Low Stock')))
        cond_set(product, 'brand',
                 response.css('.alignBrandImageSpec::attr(alt)').extract(),
                 lambda brand: brand.replace('_', ' '))
        xpath = '//td[@class="detailsText"]/node()[normalize-space()]'
        cond_set_value(product, 'description',
                       response.xpath(xpath).extract(), u''.join)
        price = product.get('price', None)
        if price == 0:
            del product['price']
        elif price:
            product['price'] = Price(priceCurrency='USD',
                                     price=re.sub('[ ,]', '', price))
        self._populate_buyer_reviews(response, product)

    def _populate_buyer_reviews(self, response, product):
        total = response.css(
            '.pr-snapshot-average-based-on-text .count::text').re('[\d ,]+')
        if not total:
            return
        total = int(re.sub('[ ,]', '', total[0]))
        avg = response.css('.pr-rating.pr-rounded.average::text')[0].extract()
        avg = float(avg)
        by_star = response.css('.pr-histogram-count span::text')
        by_star = by_star.re('\(([\d, ]+)\)')
        by_star = {i + 1: int(re.sub('[ ,]', '', c))
                   for i, c in enumerate(reversed(by_star))}
        cond_set_value(product, 'buyer_reviews',
                       BuyerReviews(num_of_reviews=total,
                                    average_rating=avg,
                                    rating_by_star=by_star))

