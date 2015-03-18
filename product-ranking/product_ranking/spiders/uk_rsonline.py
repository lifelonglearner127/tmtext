# -*- coding: utf-8 -*-


import re
import urlparse

from product_ranking.items import RelatedProduct, BuyerReviews, Price
from product_ranking.spiders import cond_set, cond_set_value, \
    cond_replace_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider


def _itemprop(response, prop, extract=True):
    result = response.css('[itemprop="%s"]::text' % prop)
    return result.extract() if extract else result


class UkRsOnlineProductsSpider(ProductsSpider):
    """ uk.rs-online.com product ranking spider

    There are following caveats:

    - sorting not implemented because of different sorting mechanism for different search terms
    - upc, model, is_in_store_only, limited_stock, sponsored_links fields are not scraped
    """

    name = 'uk_rsonline_products'

    allowed_domains = [
        'uk.rs-online.com'
    ]

    SEARCH_URL = "http://uk.rs-online.com/web/c/?searchTerm={search_term}" \
                 "&sra=oss&r=t&vn=1"

    def _is_product_page(self, response):
        return response.url.startswith('http://uk.rs-online.com/web/p')

    def _total_matches_from_html(self, response):
        matches = response.css('.viewProdDiv::text').re('f ([\d, ]+) products')
        return int(re.sub('[, ]', '', matches[0])) if matches else 0

    def _scrape_results_per_page(self, response):
        results = response.css('.defaultItem div::text').re('\d+')
        return int(results[0]) if results else None

    def _scrape_next_results_page_link(self, response):
        url = response.css('.checkoutPaginationContent noscript a::attr(href)')
        return url[-2].extract() if len(url) > 1 else None

    def _fetch_product_boxes(self, response):
        if self._is_product_page(response):
            return [response]
        return response.css('.resultRow')

    def _link_from_box(self, box):
        return box.css('.srDescDiv a::attr(href), '
                       '.tnProdDesc::attr(href)')[0].extract()

    def _populate_from_box(self, response, box, product):
        if self._is_product_page(response):
            self._populate_from_html(response, product)
            cond_set_value(product, 'is_single_result', True)
            cond_set_value(product, 'url', response.url)
        else:
            cond_set(product, 'price', box.css('.price::text').re(
                u'\u00a3([\d, .]+)'))
            cond_set(product, 'title', box.css('.tnProdDesc::text').extract(),
                     unicode.strip)
            xpath = '//li/span[text()="Brand"]/../a/text()'
            cond_set(product, 'brand', box.xpath(xpath).extract(),
                     unicode.strip)


    def _populate_from_html(self, response, product):
        cond_set(product, 'price', response.css('.price span::text').re(
            u'\u00a3([\d, .]+)'))
        cond_set(product, 'title', _itemprop(response, 'model'), unicode.strip)
        cond_set(product, 'brand',
                 _itemprop(_itemprop(response, 'brand', False), 'name'),
                 unicode.strip)
        cond_set(product, 'image_url', _itemprop(response, 'image', False)
                 .css('img::attr(src)').extract())
        image = product.get('image_url')
        if image and image.endswith('noImage.gif'):
            del (product['image_url'])
        cond_set_value(product, 'is_out_of_stock',
                       response.css('.stockMessaging::text').re(
                           'out of stock|Discontinued product'),
                       bool)
        details = response.css('.prodDetailsContainer').xpath(
            'node()[normalize-space()]')
        details = [d.extract() for d in details if not d.css(
            '.heading , form')]
        if details:
            cond_set_value(product, 'description', details, ''.join)
        self._populate_related_products(response, product)
        self._populate_buyer_reviews(response, product)
        price = product.get('price', None)
        if price == 0:
            del (product['price'])
        elif price:
            price = re.sub(', ', '', price)
            cond_replace_value(product, 'price', Price(priceCurrency='GBP',
                                                       price=price))

    def _populate_related_products(self, response, product):
        related_products = {}
        for panel in response.css('.relProPanel'):
            relation = panel.css('h2::text').extract()[0]
            products = []
            for link in panel.css('a.productDesc'):
                url = urlparse.urljoin(response.url, link.css(
                    '::attr(href)')[0].extract())
                title = link.css('::text')[0].extract()
                products.append(RelatedProduct(title=title, url=url))
            related_products[relation] = products
        cond_set_value(product, 'related_products', related_products)

    def _populate_buyer_reviews(self, response, product):
        regexp = '"http://img-europe.electrocomponents.com/siteImages/browse' \
                 '/stars-(\d+-\d+).gif'
        stars = response.css('img::attr(src)').re(regexp)
        if not stars:
            return
        stars = map(float, (s.replace('-', '') for s in stars))
        by_star = {star: stars.count(star) for star in stars}
        total = len(stars)
        average = sum(stars) / total
        cond_set_value(product, 'buyer_reviews',
                       BuyerReviews(num_of_reviews=total,
                                    average_rating=average,
                                    rating_by_star=by_star))