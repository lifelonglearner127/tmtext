<<<<<<< HEAD
# -*- coding: utf-8 -*-#
=======
from itertools import starmap
>>>>>>> 594b76f... Fix: staples_product - spider did not scrape reviews for some products
import re
import urlparse
import string
import operator

from contrib.product_spider import ProductsSpider
from product_ranking.items import RelatedProduct, Price, BuyerReviews
from product_ranking.spiders import cond_set, cond_set_value, \
    _populate_from_open_graph_product
from product_ranking.guess_brand import guess_brand_from_first_words


def _strip_non_ascii(s):
    return filter(lambda x: x in string.printable, s)


class StaplesProductsSpider(ProductsSpider):
    """ staples.com product ranking spider

    Spider takes `order` argument with following possible sorting modes:

    * `relevance` (default)
    * `price_asc`, `price_desc`
    * `name_asc`, `name_desc`
    * `rating`
    * `new`

    Note: when price_desc/price_asc order was chosed, some misorder
    out_of_store items may occure due to staples.com own server
    logic.

    Following fields are not scraped:

    * `upc`, `is_in_store_only`
    """

    name = 'staples_products'

    SEARCH_URL = "http://www.staples.com/{search_term}" \
                 "/directory_{search_term}?sby={sort_mode}&pn={page}"

    allowed_domains = [
        'staples.com'
    ]

    SORT_MODES = {
        'default': 0,
        'relevance': 0,
        'price_asc': 1,
        'price_desc': 2,
        'name_asc': 3,
        'name_desc': 4,
        'rating': 5,
        'new': 6
    }

    HARDCODED_FIELDS = {
        'locale': 'en-US'
    }

    def __init__(self, *args, **kwargs):
        super(StaplesProductsSpider, self).__init__(*args, **kwargs)
        self.url_formatter.defaults['page'] = 1

    def _total_matches_from_html(self, response):
        matches = response.css('.c00Wrapper .details p::text').extract()
        matches = map(int,
                      re.findall("(\d+)[\xa0 ]+items found", ''.join(matches),
                                 re.UNICODE | re.MULTILINE))
        return max(matches) if matches else 0

    def _scrape_next_results_page_link(self, response):
        current = self._get_page(response)
        total = self._get_pages(response)
        if current < total:
            return self._get_page_url(response, current + 1)

    def _get_page(self, response):
        current = response.css('.perpage .active a::text').extract()
        return int(current[0]) if current else 1

    def _get_pages(self, response):
        pages = response.css('.perpage ul li a::text').extract()
        pages = map(int, filter(unicode.isdigit, pages))
        return max(pages) if pages else 0

    def _get_page_url(self, response, page):
        search_term = response.meta['search_term']
        url = self.url_formatter.format(self.SEARCH_URL,
                                        search_term=search_term, page=page)
        return url

    def _fetch_product_boxes(self, response):
        return response.css('#productDetail li.prd')

    def _link_from_box(self, box):
        return box.css('.name h3 a::attr(href)')[0].extract()

    def _populate_from_box(self, response, box, product):
        cond_set(product, 'title',
                 box.css('.name h3 a::attr(title)').extract())
        product['title'] = _strip_non_ascii(product.get('title', ''))
        cond_set(product, 'model', box.css('.model::text').extract(),
                 lambda text: text.replace('Model ', ''))
        cond_set(product, 'is_out_of_stock',
                 box.css('#stockMessage::text').extract(),
                 "Out of Stock Online".startswith)
        cond_set_value(product, 'is_out_of_stock', False)

    def _populate_from_html(self, response, product):
        cond_set(product, 'title',
                 response.css('.productDetails h1::text').extract())
        product['title'] = _strip_non_ascii(product.get('title', ''))
        desc = response.css('#subdesc_content')
        headline = desc.css('.skuHeadline').extract()
        description = desc.css('.layoutWidth06').extract()
        cond_set_value(product, 'description',
                       (headline or [''])[0] + (description or [''])[0])
<<<<<<< HEAD
        #_populate_from_open_graph_product(response, product)
=======
        _populate_from_open_graph_product(response, product,
                                          metadata={'type': 'product'})
>>>>>>> 594b76f... Fix: staples_product - spider did not scrape reviews for some products
        cond_set(product, 'image_url',
                 response.css('#largeProductImage::attr(src)').extract())
        brand = response.xpath(
            '//productcatalog/product/@brandname'
        ).extract()
        if not brand:
            brand = response.css('product::attr(brandname)').extract()
        cond_set(product, 'brand', brand)
        if not brand:
            brand = guess_brand_from_first_words(product['title'])
            cond_set_value(product, 'brand', brand)

        price = response.css('.finalPrice::text').extract()
        if not price:
            price = response.xpath(
                '//dd[@class="finalPrice"]/b/i/text()'
            ).extract()
        if price:
            price = re.search('[ ,.0-9]+', price[0])
        if not price:
            price = response.css('product .price::text').extract()
        else:
            price = [price.group().replace(' ', '').replace(',', '')]
        currency = response.css('product .currency::text').extract()
        if price and currency:
            cond_set_value(product, 'price', Price(currency[0], price[0]))
        self._populate_related_products(self, response, product)
        buyer_reviews = self._buyer_reviews_from_html(response)
        if buyer_reviews:
            cond_set_value(product, 'buyer_reviews', buyer_reviews)

    def _populate_related_products(self, self1, response, product):
        xpath = '//*[@class="a200" and text()="Related Products"]' \
                '/../div[@class="b201"]//a[@id="carouselitem"]'
        products = []
        for link in response.xpath(xpath):
            url = link.css('::attr(href)').extract()
            title = link.css('::text').extract()
            if url and title:
                products.append(
                    RelatedProduct(url=urlparse.urljoin(response.url, url[0]),
                                   title=_strip_non_ascii(title[0])))
        cond_set_value(product, 'related_products',
                       {'Related Products': products})

    def _buyer_reviews_from_html(self, response):
        rarea = response.xpath(
<<<<<<< HEAD
            "//div[contains(@class,'yotpo-regular-box') and contains(@class,'yotpo-bottomline')]")
=======
            "//div[@id='reviews_inline']")
        if not rarea:
            return self._buyer_reviews_from_html_yotpo(response)
>>>>>>> 594b76f... Fix: staples_product - spider did not scrape reviews for some products
        if rarea:
            rarea = rarea[0]
        else:
            return
        avrg = rarea.xpath(
            "//div[@class='yotpo-stars-and-sum-reviews']"
            "/span[@class='yotpo-star-digits']/text()").extract()
        if avrg:
            avrg = avrg[0].strip()
            try:
                avrg = float(avrg)
            except ValueError:
                avrg = 0.0
        else:
            return
        total = rarea.xpath(
            "//div[@class='yotpo-stars-and-sum-reviews']"
            "/span[@class='yotpo-sum-reviews']/span/text()").re("(\d+) Reviews")
        if total:
            total = total[0].strip()
            try:
                total = int(total)
            except ValueError:
                total = 0
        else:
            return

        ratings = {}
        rat = rarea.xpath(
            "//div[@class='yotpo-star-distribution']"
            "/div[@class='yotpo-star-distribution-content']"
            "/div[@class='yotpo-distibutions-sum-reviews']/span")
        for irat in rat:
            label = irat.xpath(
                "@data-score-distribution").extract()
            if label:
                label = label[0]
            val = irat.xpath(
                "text()").re("\((\d+)\)")
            try:
                val = int(val[0])
            except ValueError:
                val = 0
            ratings[label] = val
        return BuyerReviews(
            num_of_reviews=total,
            average_rating=avrg,
            rating_by_star=ratings)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _buyer_reviews_from_html_yotpo(self, response):
        int_convert = lambda lst: int(re.sub('[, ]', '', lst[0]))
        total = response.css('.yotpo-sum-reviews span::text').re('\d[\d ,]*')
        if not total:
            return
        total = int_convert(total)
        if not total:
            return
        avg = response.css('.yotpo-star-digits::text').re('[\d.]+')
        avg = float(avg[0]) if avg else None
        distribution = response.css('.yotpo-distibutions-sum-reviews '
                                    '.yotpo-sum-reviews')
        distribution = {
            int(elt.css('::attr(data-score-distribution)').extract()[0]):
                int_convert(elt.css('::text').re('\d[\d ,]*'))
            for elt in distribution}
        if not avg:
            star_sum = sum(starmap(operator.__mul__, distribution.iteritems()))
            avg = float(star_sum) / total
        result = BuyerReviews(num_of_reviews=total,
                              average_rating=avg,
                              rating_by_star=distribution)
        return result
