from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import json
import urlparse

from scrapy.log import ERROR
from scrapy import Request

from product_ranking.items import SiteProductItem, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set


class CanadiantireProductsSpider(BaseProductsSpider):
    name = 'canadiantire_products'
    allowed_domains = ["canadiantire.ca"]
    start_urls = []

    SEARCH_URL = "http://www.canadiantire.ca/en/search-results.html?searchByTerm=true&q={search_term}"

    def __init__(self, *args, **kwargs):
        super(CanadiantireProductsSpider, self).__init__(
            #url_formatter=FormatterWithDefaults(pagenum=1, prods_per_page=32),
            *args, **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        title = response.xpath("//div[contains(@class,'product-title')]/div/h1/text()")
        if title:
            title = title.extract()[0]
            product['title'] = title

        brand = response.xpath("//div[contains(@class,'product-title')]/img/@title")
        try:
            brand = brand.extract()[0]
        except:
            brand = 'NO BRAND'
        product['brand'] = brand

        image_url = response.xpath("//link[@rel='image_src']/@href")
        if image_url:
            image_url = image_url.extract()[0]
            product['image_url'] = image_url

        productid = response.xpath("//span[@class='displaySkuCode']/text()")
        if productid:
            productid = productid.extract()[0].strip().replace('#', '', 1).replace('-', '')
            product['upc'] = int(productid)

        j = response.xpath("//div[@class='features_wrap']/descendant::*[text()]/text()")
        if j:
            info = " ".join(j.extract())
            product['description'] = info

        related = response.xpath("//div[@class='sr-cross-sell__wrapper']/*/*/*/a")
        lrelated = []

        for sel in related:
            link = sel.xpath('@href')
            link = link.extract()[0]
            link = urlparse.urljoin(response.url, link)

            ltitle = sel.xpath('img/@title')
            ltitle = ltitle.extract()[0]

            lrelated.append(RelatedProduct(ltitle, link))

        product['related_products'] = {"recomended": lrelated}

        product['locale'] = "en-US"
        product['model'] = ''

        #json_link0 ="http://www.canadiantire.ca/services/canadian-tire/product-load?productCodes=0548347P&locale=en&storeId=&showAdSkus=true&_=1407800196416"
        price = response.xpath("//div[contains(@class,'product-price')]/@data-load-params")
        if price:
            load_params = json.loads(price.extract()[0])
            json_link = "{load_url}?productCodes={product_code}&locale={locale}&storeId=&showAdSkus={show_ad}".format(
                load_url=load_params.get('loadUrl'),
                product_code=load_params.get('productCode'),
                locale=load_params.get('lang'),
                show_ad=load_params.get('showAdSkus'),
                )
            json_link = urlparse.urljoin(response.url, json_link)

            return Request(json_link, self._parse_json, meta=response.meta.copy(), )
        else:
            return product

    def _parse_json(self, response):
        product = response.meta['product']
        data = json.loads(response.body)
        price = data[0].get('regularPrice')
        cond_set(product, 'price', [price])
        return product

    def _scrape_total_matches(self, response):
        total = response.xpath("//span[@class='search_results_filter__hilite-count']/text()")
        if len(total) > 0:
            return int(total.extract()[0])
        else:
            return 0

        total = total.extract()[0]
        return int(total)

    def _scrape_product_links(self, response):
        links = response.xpath("//div[@id='search_results']/*/*/*/div[contains(@class,'product_result')]/a/@href")
        links = links.extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next = response.xpath("//li[@class='pagination']/ul/li/a[contains(text(),'Next')]/@href")
        if next:
            next = next.extract()[0]
            next = urlparse.urljoin(response.url, next)
        return next
