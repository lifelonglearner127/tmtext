import re

from product_ranking.items import BuyerReviews, Price
from product_ranking.spiders import cond_set, cond_set_value, \
    populate_from_open_graph, cond_replace_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider


class TopshopProductsSpider(ProductsSpider):
    """ topshop.com product ranking spider

    Takes `order` argument with following possible values:

    * `relevance` (default)
    * `price_asc`, `price_desc`
    * `new`
    * `rating`

    There are the following caveats:

    * `upc`, `model`, `is_out_of_stock`, `is_in_store_only` are not scraped
    * `related_products` not scraped as they are always random
    * `brand` is not always scraped and may be incorrect as it's taken from the product's title

    """

    name = 'topshop_products'

    allowed_domains = ['topshop.com']

    SEARCH_URL = "http://www.topshop.com/webapp/wcs/" \
                 "stores/servlet/CatalogNavigationSearchResultCmd" \
                 "?langId=-1&storeId=12556&catalogId=33057" \
                 "&beginIndex=1&viewAllFlag=false&pageSize=20" \
                 "&sort_field={sort_mode}&searchTerm={search_term}"

    SORT_MODES = {
        'default': 'Relevance',
        'relevance': 'Relevance',
        'new': 'Newness',
        'price_asc': 'Price Ascending',
        'price_desc': 'Price Descending',
        'ratting': 'Rating Descending'
    }

    OPTIONAL_REQUESTS = {
        'buyer_reviews': True
    }

    REVIEWS_API_URL = 'http://reviews.topshop.com/6025-en_gb' \
                      '/{prod_id}/reviews.htm?format=embedded&amp' \
                      ';sort=featured'

    def _total_matches_from_html(self, response):
        total = response.css('.product_total::text').extract()
        return int(re.sub(', ', '', total[0]) if total else 0)

    def _scrape_next_results_page_link(self, response):
        link = response.css('.show_next a::attr(href)').extract()
        return link[0] if link else None

    def _fetch_product_boxes(self, response):
        return response.css('ul.product')

    def _link_from_box(self, box):
        return box.css('[data-productid]::attr(href)')[0].extract()

    def _populate_from_box(self, response, box, product):
        cond_set(product, 'title',
                 box.css('[data-productid]::attr(title)').extract())
        cond_set(product, 'price', box.css('.now_price span::text').extract())
        cond_set(product, 'price', box.css('.product_price::text').extract())

    def _populate_from_html(self, response, product):
        cond_set(product, 'image_url',
                 response.css('#product_view_full::attr(href)').extract())
        xpath = '//div[@class="product_description"]/node()[normalize-space()]'
        cond_set_value(product, 'description', response.xpath(xpath).extract(),
                       ''.join)
        populate_from_open_graph(response, product)
        #price = product.get('price')
        currency = response.css('[property="og:price:currency"]'
                                '::attr(content)')
        price = response.css('[property="og:price:amount"]::attr(content)')
        if price and currency:
            price = Price(priceCurrency=currency[0].extract(),
                          price=price[0].extract())
        else:
            price = product.get('price', '')
            if price.startswith(u'\xa3'):
                price = price.replace(u'\xa3', '').replace(',', '') \
                    .replace(' ', '')
                price = Price(priceCurrency='GBP', price=price)
        cond_replace_value(product, 'price', price or None)
        cond_set(product, 'brand',
                 re.findall('.+ by (.+)', product.get('title')))


    def _request_buyer_reviews(self, response):
        product = response.meta['product']
        prod_id = response.css('.product_code span::text').extract()
        if not prod_id:
            self.log('Could not request buyer reviews')
        return self.REVIEWS_API_URL.format(prod_id=prod_id[0])

    def _parse_buyer_reviews(self, response):
        css = '.BVRRDisplayContent .BVRRRatingNumber.value::text'
        reviews = map(int, response.css(css).extract())
        total = len(reviews)
        if not total:
            return
        by_star = {value: reviews.count(value) for value in reviews}
        avg = float(response.css('.BVRRRatingNumber::text')[0].extract())
        result = BuyerReviews(num_of_reviews=total, average_rating=avg,
                              rating_by_star=by_star)
        response.meta['product']['buyer_reviews'] = result

