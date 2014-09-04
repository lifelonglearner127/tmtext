from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import string
import urllib
import urlparse
import re

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value
from scrapy import Request
from scrapy.log import DEBUG, ERROR


class CanadiantireProductsSpider(BaseProductsSpider):
    name = 'canadiantire_products'
    allowed_domains = ["canadiantire.ca"]
    start_urls = []

    SEARCH_URL = "http://www.canadiantire.ca/en/search-results.html" \
        "?searchByTerm=true&q={search_term}"

    SEARCH_URL2 = "http://tires.canadiantire.ca/en/search/?searchterm={search_term}"

    _PROD_DATA_RELATIVE_URL = "{load_url}?productCodes={product_code}" \
        "&locale={locale}&storeId=&showAdSkus={show_ad}"

    def __init__(self, *args, **kwargs):
        super(CanadiantireProductsSpider, self).__init__(*args, **kwargs)
        self.force_tires = False

    def parse(self, response):
        redirect_urls = response.meta.get('redirect_urls')

        if response.meta.get('redirect_urls') and \
                urlparse.urlsplit(redirect_urls[0]).netloc == 'www.canadiantire.ca' and \
                urlparse.urlsplit(response.url).netloc == 'tires.canadiantire.ca':

            self.force_tires = True
            self.allowed_domains = ["tires.canadiantire.ca"]
            self.log("Redirect to tires.canadiantire.ca site.", DEBUG)

            rlist = []
            for st in self.searchterms:
                rlist.append(Request(
                    self.url_formatter.format(self.SEARCH_URL2,
                        search_term=urllib.quote_plus(st)),
                        meta={'search_term': st, 'remaining': self.quantity}
                ))
            return rlist
        else:
            return super(CanadiantireProductsSpider, self).parse(response)

    def parse_product(self, response):
        if self.force_tires:
            return self._tires_parse_product(response)

        product = response.meta['product']

        cond_set(product, 'title', response.xpath(
            "//div[contains(@class,'product-title')]/div/h1/text()").extract())

        cond_set(product, 'brand', response.xpath(
            "//div[contains(@class,'product-title')]/img/@title").extract())

        cond_set(product, 'image_url', response.xpath(
            "//link[@rel='image_src']/@href").extract())

        productid = response.xpath("//span[@class='displaySkuCode']/text()")
        if productid:
            productid = productid.extract()[0].strip().replace(
                '#', '', 1
            ).replace('-', '')
            product['upc'] = int(productid)

        info = response.xpath("//div[@class='features_wrap']/descendant::*[text()]/text()")
        cond_set_value(product, 'description', ''.join(info.extract()), conv=''.join)

        related = response.xpath(
            "//div[@class='sr-cross-sell__wrapper']/*/*/*/a")
        lrelated = []
        for sel in related:
            link = sel.xpath('@href')
            link = link.extract()[0]
            link = urlparse.urljoin(response.url, link)

            ltitle = sel.xpath('img/@title')
            ltitle = ltitle.extract()[0]

            lrelated.append(RelatedProduct(ltitle, link))
        product['related_products'] = {"recommended": lrelated}

        price = response.xpath(
            "//div[contains(@class,'product-price')]/@data-load-params")
        if not price:
            ret = product
        else:
            load_params = json.loads(price.extract()[0])

            locale = load_params.get('lang')
            cond_set_value(product, 'locale', locale)

            prod_data_rel_url = self._PROD_DATA_RELATIVE_URL.format(
                load_url=load_params.get('loadUrl'),
                product_code=load_params.get('productCode'),
                locale=locale,
                show_ad="false",  # Fetch only what's necessary.
            )
            prod_data_url = urlparse.urljoin(response.url, prod_data_rel_url)
            ret = Request(
                prod_data_url, self._parse_json, meta=response.meta.copy())

        cond_set_value(product, 'locale', "en-US")

        return ret

    def _tires_parse_product(self, response):
        product = response.meta['product']

        cond_set(product, 'title', map(string.strip, response.xpath(
            "//div[@class='productContent']/h1/div[@id='productName']/text()").extract()))

        cond_set(product, 'brand', response.xpath(
            "//script[contains(text(),'dim7')]/text()").re(r'.*"dim7":"([^"]*)"}.*'))

        productid = response.xpath("//p[@id='prodNo']/span[@id='metaProductID']/text()")
        if productid:
            productid = productid.extract()[0].strip().replace('P', '')
            try:
                product['upc'] = int(productid)
            except ValueError:
                self.log(
                    "Failed to parse upc number : %r" % productid, ERROR)

        cond_set(product, 'image_url', response.xpath(
            "//div[@class='bigImage']/img[@id='mainProductImage']/@src").extract())

        price = response.xpath(
            "//div[contains(@class,'bigPrice')]/div[@class='price']/descendant::*[text()]/text()")
        price = [x.strip() for x in price.extract()]
        price = "".join(price)
        m = re.match(r'\$(.*)\*.*', price)
        if m:
            price = m.group(1)
        cond_set_value(product, 'price', price)

        info = response.xpath("//div[@id='features']/div[@class='tabContent']/descendant::*[text()]/text()")
        if info:
            cond_set_value(product, 'description', " ".join(info.extract()))

        cond_set_value(product, 'locale', "en-US")
        return product

    def _parse_json(self, response):
        product = response.meta['product']

        data = json.loads(response.body_as_unicode())
        prod_data = data[0]

        cond_set_value(product, 'price', prod_data.get('regularPrice'))
        cond_set_value(product, 'title', prod_data.get('name'))

        return product

    def _scrape_total_matches(self, response):
        if self.force_tires:
            return self._tires_scrape_total_matches(response)
        total = response.xpath(
            "//span[@class='search_results_filter__hilite-count']/text()")
        if total:
            return int(total.extract()[0])
        else:
            return 0

    def _tires_scrape_total_matches(self, response):
        total = response.xpath(
            "//div[@id='productListing']/strong/h2/text()").re(r'.* returned (\d+) results:')
        if total:
            return int(total[0])
        else:
            return 0

    def _scrape_product_links(self, response):
        if self.force_tires:
            links = response.xpath(
                "//ul[@id='productList']/li/div[@class='productImage']/a/@href"
            ).extract()
        else:
            links = response.xpath(
                "//div[@id='search_results']/*/*/*"
                "/div[contains(@class,'product_result')]/a/@href"
            ).extract()
        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        if self.force_tires:
            next_page_links = response.xpath(
                "//div[@class='pageNumbering']/a[contains(@class,'pageNext')]/@href")
        else:
            next_page_links = response.xpath(
                "//li[@class='pagination']/ul/li/a[contains(text(),'Next')]/@href")

        if next_page_links:
            next_page_link = urlparse.urljoin(
                response.url, next_page_links.extract()[0])
        else:
            next_page_link = None
        return next_page_link
