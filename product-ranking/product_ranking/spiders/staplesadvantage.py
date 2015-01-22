import json
import re
from urlparse import urljoin

from scrapy import Request

from .contrib.product_spider import ProductsSpider
from product_ranking.items import RelatedProduct, BuyerReviews
from product_ranking.spiders import cond_set, cond_set_value


class StaplesadvantageProductsSpider(ProductsSpider):
    """" staplesadvantage.com product ranking spider

    Takes `order` argument with following possible values:

    * `relevance` (default)
    * `rating` - user rating from low to high
    * `best` - best sellers

    Following fields are not scraped:

    * `price`, `is_out_of_stock`, `is_in_store_only`, `upc`
    """

    name = "staplesadvantage_products"

    allowed_domains = ['staplesadvantage.com']

    SEARCH_URL = "http://www.staplesadvantage.com/webapp/wcs/stores/servlet" \
                 "/StplCategoryDisplay" \
                 "?act=8&filetersrch=N&filterSearchNoResults=false" \
                 "&selSortOption=Top%20Rated" \
                 "&sortId={sort_mode}&src=SRCH&term={search_term}" \
                 "&tpvBrowse=false&pg={page}"

    START_URL = 'http://www.staplesadvantage.com/learn?storeId=10101'

    SORT_MODES = {
        'default': 'Rel|descending',
        'relevance': 'Rel|descending',
        'rating': 'top_rated|descending',
        'best': 'best_selling|descending'
    }

    OPTIONAL_REQUESTS = {
        'buyer_reviews': True
    }

    def __init__(self, *args, **kwargs):
        super(StaplesadvantageProductsSpider, self).__init__(*args, **kwargs)
        self.url_formatter.defaults['page'] = 1

    def start_requests(self):
        requests = super(StaplesadvantageProductsSpider, self).start_requests()
        return [Request(self.START_URL, self._begin_search,
                        meta={'requests': requests})]

    def _begin_search(self, response):
        return response.meta['requests']

    def _total_matches_from_html(self, response):
        total = response.css('.didYouMeanNoOfItems').extract()
        if not total: return 0
        total = re.search('[\d,]+', total[0])
        return int(total.group().replace(',', '')) if total else 0

    def _scrape_next_results_page_link(self, response):
        if not self._fetch_product_boxes(response):
            return None
        page = response.meta.get('page', 1)
        search_term = response.meta['search_term']
        response.meta['page'] = page + 1
        return self.url_formatter.format(self.SEARCH_URL,
                                         search_term=search_term,
                                         page=page + 1)

    def _fetch_product_boxes(self, response):
        return response.css('.productdescription')

    def _link_from_box(self, box):
        return box.css('.plainlink::attr(href)')[0].extract()

    def _populate_from_box(self, response, box, product):
        cond_set(product, 'title', box.css('.plainlink::text')[0].extract(),
                 unicode.strip)

    def _populate_from_html(self, response, product):
        xpath = '//div[@id="dotcombrand"]/../preceding-sibling::li[1]/text()'
        cond_set(product, 'brand', response.xpath(xpath).extract())
        xpath = '//div[@class="tabs_instead_title" and text()="Description"]' \
                '/following-sibling::*/node()[normalize-space()]'
        cond_set_value(product, 'description', response.xpath(xpath).extract(),
                       ''.join)
        cond_set(product, 'image_url',
                 response.css('#enlImage::attr(src)').extract(),
                 lambda url: urljoin(response.url, url))
        self._populate_related_products(response, product)

    def _populate_related_products(self, response, product):
        products = []
        for item in response.css('#moreproducts_id .productdescription h4 a'):
            url = item.css('::attr(href)')
            text = item.css('::text')
            if url and text:
                products.append(
                    RelatedProduct(url=url[0].extract(),
                                   title=text[0].extract().strip()))
        cond_set_value(product, 'related_products',
                       {'More product options': products})


    def _request_buyer_reviews(self, response):
        prod_id = re.search('var pr_page_id="(\d+)"', response.body)
        if not prod_id:
            return
        prod_id = prod_id.group(1)
        CH = sum((ord(c) * abs(255 - ord(c)) for c in str(prod_id)))
        CH = str(CH % 1023).rjust(4, '0')
        CH = '%s/%s' % (CH[:2], CH[2:])
        url = "http://www.staplesadvantage.com/pwr/content/%s/contents.js" % CH
        meta = response.meta.copy()
        meta['prod_id'] = prod_id
        meta['field'] = 'buyer_reviews'
        return Request(url, callback=self._parse_buyer_reviews, meta=meta,
                       errback=self._handle_option_error, dont_filter=True)

    def _parse_buyer_reviews(self, response):
        json_str = re.search("POWERREVIEWS\.common\.gResult"
                             "\['content/\d+/\d+/contents.js'\] = (.+);",
                             response.body)
        if not json_str:
            return
        data = json.loads(json_str.group(1))
        try:
            data = data['locales']['en_US'][
                'p' + str(response.meta['prod_id'])]
            data = data['reviews']
        except KeyError:
            return
        ratings = {i + 1: val for i, val in enumerate(data['review_ratings'])}
        avg = data['avg']
        total = data['review_count']
        cond_set_value(response.meta['product'], 'buyer_reviews',
                       BuyerReviews(total, avg, ratings))
