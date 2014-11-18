# -*- coding: utf-8 -*-

import urlparse
import re

from product_ranking.spiders import cond_replace
from product_ranking.spiders import cond_set_value, cond_set
from contrib.product_spider import ProductsSpider


class SainsburysProductSpider(ProductsSpider):
    """ sainsburys.co.uk product ranking spider

    Spider takes `order` argument.

    Allowed sorting orders are:

    * `relevance`: relevance. This is default.
    * `price_asc`: price per unit (ascending).
    * `price_desc`: price per unit (descending).
    * `name_asc`: product title (ascending).
    * `name_desc`: product title (descending).
    * `best`: best sellers first.
    * `rating`: average user rating (descending).

    There are following caveats:

    * if price per unit is not found, the spider will try other pricing
      variants.
    * `brand` might not be scraped for some products, or scraped incorrectly,
       but this is very unlikely.
    * `model`, `is_out_of_stock`, `is_in_store_only` and `upc` fields are not
       scraped
    """

    name = "sainsburys_uk_products"

    allowed_domains = [
        "sainsburys.co.uk",
    ]

    SEARCH_URL = "http://www.sainsburys.co.uk/" \
                 "webapp/wcs/stores/servlet/SearchDisplayView" \
                 "?catalogId=10122&langId=44&storeId=10151" \
                 "&categoryId=&parent_category_rn=&top_category=" \
                 "&pageSize=30&orderBy={sort_mode}" \
                 "&searchTerm={search_term}" \
                 "&beginIndex=0&categoryFacetId1="

    SORT_MODES = {
        'default': 'RELEVANCE',
        'relevance': 'RELEVANCE',
        'price_asc': 'PRICE_ASC',
        'price_desc': 'PRICE_DESC',
        'name_asc': 'NAME_ASC',
        'name_desc': 'NAME_DESC',
        'best': 'TOP_SELLERS',
        'rating': 'RATINGS_DESC'
    }

    def _total_matches_from_html(self, response):
        try:
            text = response.css('#resultsHeading::text').extract()[0]
            matches = re.search('We found (\d+)', text).group(1)
        except (IndexError, AttributeError):
            matches = 0
        return int(matches)

    def _scrape_next_results_page_link(self, response):
        link = response.css('.next a::attr(href)')
        return link.extract()[0] if link else None

    def _fetch_product_boxes(self, response):
        # Collect brand names before scraping products
        if 'brands' not in response.meta:
            css = 'label[for*=topBrands]::text'
            response.meta['brands'] = response.css(css).extract()

        return response.css('.product')

    def _link_from_box(self, box):
        url = box.css('.productInfo h3 a::attr(href)').extract()[0]
        return url

    def _populate_from_box(self, response, box, product):
        cond_set(product, 'title',
                 box.css('.productInfo h3 a::text').extract(),
                 unicode.strip)
        cond_set(product, 'price', box.css('.pricePerUnit::text').extract(),
                 unicode.strip)
        cond_set(product, 'price',
                 box.css('.pricing [class*=pricePer]').extract(),
                 unicode.strip)
        cond_set(product, 'image_url',
                 box.css('.productInfo h3 a img::attr(src)').extract(),
                 lambda url: urlparse.urljoin(response.url, url))

        # Try to find brand name in a title
        brands = response.meta.get('brands', [])
        brand = next((brand for brand in brands
                      if product.get('title', '').find(brand) == 0), None)
        cond_set_value(product, 'brand', brand)

    def _populate_from_html(self, response, product):
        cond_set(product, 'title',
                 response.css('.productSummary h1::text').extract())
        cond_set(product, 'price',
                 response.css('.pricePerUnit::text').extract(),
                 unicode.strip)
        cond_set(product, 'price',
                 response.css('.pricing [class*=pricePer]').extract(),
                 unicode.strip)
        xpath = '//*[@id="information"]' \
                '/node()[not(@class="access")][normalize-space()]'
        cond_set_value(product, 'description', response.xpath(xpath).extract(),
                       ''.join)
        cond_replace(product, 'image_url',
                     response.css('#productImageHolder img::attr(src)')
                     .extract(),
                     lambda url: urlparse.urljoin(response.url, url))


