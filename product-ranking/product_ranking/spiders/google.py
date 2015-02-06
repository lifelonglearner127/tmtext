from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urllib
import urlparse
import json
import re

from scrapy.log import ERROR, WARNING, DEBUG
from scrapy.selector import Selector
from scrapy.http import Request

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults
from product_ranking.spiders import cond_set, cond_set_value
from product_ranking.guess_brand import guess_brand_from_first_words


def clear_text(l):
    """
    useful for clearing sel.xpath('.//text()').explode() expressions
    """
    return " ".join(
        [it for it in map(string.strip, l) if it])


def get_price(elements):
    """ Returns content of element that looks like the price block """
    for e in elements:
        e_text = e.css('::text').extract()[0]
        if '$' in e_text:
            return e_text.strip()


def get_upc(response):
    """ Returns the UPC code (if any) """
    upc = response.xpath(
        './/*[contains(text(), "GTIN")]/following-sibling'
        '::*[contains(@class, "specs-value")]/text()'
    ).extract()
    if not upc:
        return
    upc = upc[0]
    if re.match(r'^\d{12}$', upc.strip()):
        return upc


class GoogleProductsSpider(BaseProductsSpider):
    name = 'google_products'
    allowed_domains = ["www.google.com"]
    start_urls = []
    user_agent = ('Mozilla/5.0 (X11; Linux i686; rv:25.0)'
                  ' Gecko/20100101 Firefox/25.0')
    download_delay = 1

    SEARCH_URL = ("https://www.google.com/search?tbm=shop"
                  "&q={search_term}&num=100")

    SEARCH_SORT = {
        'default': 'p_ord:r',
        'rating': 'p_ord:rv',
        'low_price': 'p_ord:p',
        'high_price': 'p_ord:pd',
    }

    def __init__(self, search_sort=None, *args, **kwargs):
        super(GoogleProductsSpider, self).__init__(*args, **kwargs)
        if search_sort in self.SEARCH_SORT:
            self.sort = search_sort
        else:
            self.sort = None

    def start_requests(self):
        yield Request(
            url="https://www.google.com/shopping",
            callback=self.parse_init)

    def parse_init(self, response):
        for request in super(GoogleProductsSpider, self).start_requests():
            if self.sort:
                request.callback = self.sort_request
                if self.sort == 'default':
                    request.callback = self.parse
            yield request

    def sort_request(self, response):

        url = response.request.url

        if self.sort:
            pattern = r'\,{}[\&$]'.format(self.SEARCH_SORT[self.sort])
            sort_urls = response.xpath(
                '//div[@id="stt__ps-sort-m"]/div/@data-url').extract()

            for sort_url in sort_urls:
                m = re.search(pattern, sort_url)
                if m:
                    url = urlparse.urljoin(response.url, sort_url)
                    break

        request = response.request.replace(
            callback=self.parse,
            url=url
        )
        yield request

    def parse_product(self, response):
        product = response.meta['product']
        desc = response.xpath(
            '//div[@id="product-description-full"]/text()'
        ).extract()
        if desc:
            product['description'] = desc[0]

        cond_set(product, 'upc', get_upc(response))

        cond_set(product, 'brand', response.xpath(
            '//div[@id="specs"]'
            '//div[@class="specs-row"]'
            '[contains(./*[@class="specs-name"]/text(), "Brand")]'
            '/*[@class="specs-value"]/text()'
        ).extract())

        if not product.get('brand', None):
            brand = guess_brand_from_first_words(product['title'])
            if brand:
                product['brand'] = brand

        related = response.css('#related li.rel-item .rel-title a')
        r = []
        for rel in related:
            title = rel.xpath('text()').extract()
            url = rel.xpath('@href').extract()
            if title and url:
                r.append(RelatedProduct(
                    title=title[0],
                    url=urlparse.urljoin(response.url, url[0])
                ))
        product['related_products'] = {'recommended': r}

        # get right url if it redirect url
        # TODO: this pattern neems should be checked
        redirect_pattern = r'&adurl=(.*)'
        res = re.findall(redirect_pattern, product['url'])
        if res:
            req_url = urllib.unquote(res[0])
            res = urllib.urlopen(req_url)
            url_not_stripped = res.geturl()
            product['url'] = url_not_stripped

        # strip GET data from only google urls
        if 'www.google.com/shopping/product' in product['url']:
            pattern = r'(.*)\?'
            result = re.findall(pattern, product['url'])
            if result:
                product['url'] = result[0]
                product['google_source_site'] = []
                stores_link = result[0] + '/online'
                return Request(stores_link, callback=self.populate_stores,
                               meta={'product': product})
        return product

    def populate_stores(self, response):
        product = response.meta['product']
        sellers = response.xpath(
            '//tr[@class="os-row"]/td[@class="os-seller-name"]/span/a/text()'
        ).extract()
        source_list = product['google_source_site']
        source_list.extend(sellers)
        product['google_source_site'] = source_list
        next_link = response.xpath(
            '//div[@id="online-pagination"]/div[contains(@class,'
            '"jfk-button-collapse-left")]/@data-reload'
        ).extract()
        if next_link:
            url = "https://www.google.com" + next_link[0]
            return Request(url, callback=self.populate_stores,
                           meta={'product': product})
        product['google_source_site'] = '; '.join(source_list)
        return product

    def _scrape_total_matches(self, response):
        self.log("Impossible to scrape total matches for this spider",
                 DEBUG)
        return 0

    def _scrape_product_links(self, response):

        items = response.css('ol.product-results li.psli')
        if not items:
            items = response.css('ol.product-results li.psgi')

        if not items:
            self.log("Found no product links.", DEBUG)
        # try to get data from json
        script = response.xpath(
            '//div[@id="xjsi"]/script/text()').extract()
        script = script[0] if script else ''

        json_data = {}
        start = script.find(u'google.pmc=')
        if start < 0:
            start = 0
        else:
            start = start + len(u'google.pmc=')

        end = script.find(u';google.y.first.push')
        if end < 0:
            end = None

        cleansed = script[start:end]

        if cleansed:
            try:
                json_data = json.loads(cleansed)
            except:
                self.log('Failed to process json data', ERROR)

            try:
                json_data = json_data['spop']['r']
            except:
                self.log('JSON structure changed', ERROR)

        for item in items:
            url = title = description = price = image_url = None
            try:
                id = item.xpath('@data-docid').extract()[0]
                link = item.xpath('.//div[@class="pslmain"]/h3[@class="r"]/a')
                if not link:
                    link = item.xpath('.//a[@class="psgiimg"]')
                title = link.xpath('string(.)').extract()[0]
                url = link.xpath('@href').extract()[0]
                source_site = item.xpath('.//div[@class="_tyb"]/text()'
                    ).extract()
                if source_site:
                    source_site = source_site[0].replace('from ', '').strip()
            except IndexError:
                self.log('Index error at {url}'.format(url=response.url),
                         WARNING)
                continue

            _prices = item.xpath('.//*[contains(@class, "price")]')
            price = get_price(_prices)

            # TODO: support more currencies? we have to detect the website
            #  (google.au, google.br etc.) and use the appropriate currency
            # See https://support.google.com/merchants/answer/160637?hl=en
            if '$' not in price:  # TODO: only USD is supported now
                self.log('Unrecognized currency sign at %s' % response.url,
                         level=ERROR)
            else:
                price = Price(
                    price=price.replace('$', '').replace(',', '').strip(),
                    priceCurrency='USD'
                )

            # fill from json
            l = json_data.get(id)
            if l:
                try:
                    if not title:
                        title = Selector(
                            text=l[1]).xpath('string(.)').extract()[0]
                    if not url:
                        url = l[2]
                    description = l[3]
                    image_url = l[8][0][0]
                except IndexError:
                    self.log('Invalid JSON on {url}'.format(url=response.url),
                             WARNING)

            redirect = url
            url = urlparse.urljoin(response.url, url)

            yield redirect, SiteProductItem(
                url=url,
                title=title,
                price=price,
                image_url=image_url,
                description=description,
                google_source_site=source_site,
                locale='en-US')

    def _scrape_next_results_page_link(self, response):
        next = response.css('table#nav td.cur') \
                       .xpath('following-sibling::td[1]/a/@href') \
                       .extract()

        if not next:
            link = None
            self.log('Next page link not found', ERROR)
        else:
            link = urlparse.urljoin(response.url, next[0])
        return link
