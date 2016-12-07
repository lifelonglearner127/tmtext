# -*- coding: utf-8 -*-

import re
import string
import urlparse
import json

from scrapy import Request
from scrapy.log import ERROR

from product_ranking.spiders import cond_set, cond_set_value
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import FormatterWithDefaults, dump_url_to_file
from product_ranking.items import SiteProductItem, Price
from product_ranking.guess_brand import guess_brand_from_first_words

is_empty = lambda x, y=None: x[0] if x else y

def _inner_html(tag_str):
    return re.match('\A<[^<]+>(.+?)<[^>]+>\Z',
                    tag_str, re.DOTALL).group(1).strip(' \n\t')


class ArgosUKProductsSpider(BaseProductsSpider):
    """argos.co.uk product ranking spider.

    Due to the error on website some products may not be scraped.

    Parameters:
       searchterms_str - list of search terms. Required.

       sort_mode - Sort ordering. Possible sort orders are: relevance,
          price_asc, price_desc, promotions, rating. Default is relevance.

       fetch_related_products - should the spider scrape related products or
          not. Requires additional requests to be made, so may (and will) slow
          down the process. Default is True.
    """

    name = 'argos_uk_products'

    allowed_domains = ["www.argos.co.uk", "service.avail.net"]

    SEARCH_URL = 'http://www.argos.co.uk/static/Search/searchTerm/{search_term}.htm'

    SORT_SEARCH_URL = "http://www.argos.co.uk/webapp/wcs/stores/servlet/Search" \
                      "?s={sort_mode}&q={search_term}&storeId={store_id}" \
                      "&catalogId={catalog_id}&langId={lang_id}&authToken="

    PAGE_URL = "http://www.argos.co.uk/static/Search/fs/0/p/{start_from}/pp" \
               "/{products_per_page}/q/{search_term}/s/{sort_mode}.htm"

    SORT_MODES = {
        "relevance": "Relevance",
        "price_asc": "Price: Low - High",
        "price_desc": "Price: High - Low",
        "promotions": "Promotions",
        "rating": "Average Rating"
    }
    SORTING = None

    def __init__(self, sort_mode=None, fetch_related_products=True,
                 store_id=10151,
                 catalog_id=24551,
                 lang_id=110, *args, **kwargs):
        self.fetch_related_products = fetch_related_products
        if sort_mode in self.SORT_MODES:
            sort_mode = self.SORT_MODES[sort_mode]
            self.SEARCH_URL = self.SORT_SEARCH_URL
            self.SORTING = sort_mode
            formatter = FormatterWithDefaults(sort_mode=sort_mode,
                                              store_id=store_id,
                                              catalog_id=catalog_id,
                                              lang_id=lang_id)
        else:
            self.log('"%s" not in SORT_MODES')
            self.SORTING = self.SORT_MODES['relevance']
            formatter = FormatterWithDefaults()
        cond_set_value(kwargs, 'site_name', 'argos.co.uk')
        super(ArgosUKProductsSpider, self).__init__(formatter, *args, **kwargs)

    def _scrape_total_matches(self, response):
        if len(response.css('.sorrytext.notexact')):
            return 0
        if len(response.css('.noresultscontent')):
            return 0
        total = is_empty(re.findall('\d+', is_empty(
                response.xpath(
                    '//div[@id="categorylist"]/h2/span/text()').extract(),
                ""
            )
        ))
        if not total:
            total = is_empty(re.findall('\d+', is_empty(
                    response.css(
                      '.extrainfo.totalresults::text').extract(),
                    ""
                )
            ))
        if total:
            return int(total)
        return 0

    def _scrape_next_results_page_link_old(self, response):
        """Deprecated _scrape_next_results_page_link.

        Won't work as intended due to the website error"""
        link = response.css('a[rel=next]::attr(href)').extract()
        return link[0] if link else None

    def _scrape_next_results_page_link(self, response):
        products_per_page = response.meta['products_per_page']
        page = response.meta.get('page', 1) + products_per_page
        if page > response.meta['total_matches']:
            return None
        result = self.url_formatter.format(self.PAGE_URL, start_from=page,
                                           products_per_page=products_per_page,
                                           search_term=response.meta[
                                               'search_term'],
                                           sort_mode=self.SORTING)
        response.meta['page'] = page
        result = result.replace(' ', '%2B')
        print 'RES', result, products_per_page, page
        return result

    def _scrape_product_links(self, response):
        product_boxes = response.css('.product')
        for box in product_boxes:
            product = SiteProductItem()
            url = box.css('.title a::attr(href)').extract()[0]
            cond_set(product, 'title', box.css('.title a::text').extract())
            cond_set(
                product, 'price',
                box.css('.price .main::text').extract(), string.strip
            )
            yield url, product

    def _parse_single_product(self, response):
      return self.parse_product(response)

    def parse_product(self, response):
        product = response.meta['product']
        cond_set(
            product, 'title', response.css('#pdpProduct h1::text').extract(),
            lambda s: string.strip(s, ' \n')
        )
        if not product.get('brand', None):
            brand = guess_brand_from_first_words(product.get('title').strip() if product.get('title') else '')
            if brand:
                product['brand'] = brand

        if not product.get('brand', None):
            dump_url_to_file(response.url)

        if product.get('price') is None:
            currency = response.css('.currency::text').extract()
            currency = currency[0] if currency else ''
            price = response.css('.actualprice .price::text').re('\d+')
            price = price[0] if price else ''
            cond_set_value(product, 'price', currency + price)
        if not u'£' in product.get('price', ''):
            self.log('Invalid price at: %s' % response.url, level=ERROR)
        else:
            product['price'] = Price(
                price=product['price'].replace(u'£', '').strip(),
                priceCurrency='GBP'
            )
        cond_set(
            product, 'image_url',
            response.css('#mainimage.photo::attr(src)').extract(),
            lambda url: urlparse.urljoin(response.url, url)
        )
        cond_set(product, 'description',
                 response.css('.fullDetails').extract(), _inner_html)
        cond_set(product, 'is_out_of_stock',
                 response.css('#globalDeliveryGrey[style="display:block;"]'),
                 bool)
        reseller_id = re.findall(r'partNumber/(\d+)', response.url)
        cond_set(
            product, 'reseller_id', reseller_id[0] if reseller_id else None
        )
        # Hardcoded
        cond_set_value(product, 'locale', 'en-GB')

        cond_set(product, 'model',
                 response.xpath(
                     '//div[@class="fullDetails"]/ul/li/text()').re('EAN:\s(.*).'))

        if self.fetch_related_products:
            return self._request_related_products(response)
        else:
            return product

    def _get_recommendations_url(self, response):
        customer_id = self._get_customer_id(response)
        product_id = re.search('static/Product/partNumber/(\d+).htm',
                               response.url).group(1)
        js = json.dumps({"ret1": ["getRecommendations",
                                  {"TemplateName": "ProductPage_Alternatives",
                                   "Input": ["ProductId:%s" % product_id],
                                   "ColumnNames": ["ProductId", "ProductName"]
                                  }]})
        return "http://service.avail.net/2009-02-13/dynamic/" \
               "%s/scr?q=%s&s=2" % (customer_id, js)

    def _get_customer_id(self, response):
        return re.search(
            'AI_CUSTOMER_ID = "([a-z0-9-]+)";', response.body).group(1)

    def _request_related_products(self, response):
        url = self._get_recommendations_url(response)
        return Request(url, self._parse_related_products, meta=response.meta)

    def _parse_related_products(self, response):
        product = response.meta['product']
        json_part = response.body_as_unicode().split('=', 1)[-1].strip()
        json_part = json.loads(json_part)
        url_base = 'http://www.argos.co.uk/static/Product/partNumber/%s.htm'
        related = {'recommendations': [(name, url_base % id_)
                                       for id_, name in
                                       json_part['ret1']['values']]}
        cond_set_value(product, 'related_products', related)
        return product
