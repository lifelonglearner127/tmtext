# -*- coding: utf-8 -*-#
from __future__ import division, absolute_import, unicode_literals

import re
import json
import string
import urllib

from scrapy.http import Request
from scrapy.log import DEBUG
from scrapy import Selector
from urlparse import urljoin

from scrapy.conf import settings


from product_ranking.items import SiteProductItem, BuyerReviews, \
    RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import cond_set_value


class LowesProductsSpider(BaseProductsSpider):
    name = 'lowes_products'
    allowed_domains = ["lowes.com", "bazaarvoice.com", "lowes.ugc.bazaarvoice.com"]
    start_urls = []

    SEARCH_URL = "http://www.lowes.com/Search={search_term}?storeId="\
        "10151&langId=-1&catalogId=10051&N=0&newSearch=true&Ntt={search_term}"

    RATING_URL = "http://lowes.ugc.bazaarvoice.com/0534/{prodid}"\
        "/reviews.djs?format=embeddedhtml"

    STORES_JSON = "http://www.lowes.com/IntegrationServices/resources/storeLocator/json/v2_0/stores" \
                  "?langId=-1&storeId=10702&catalogId=10051&place={zip_code}&count=25"

    SELECT_STORE = "http://www.lowes.com/LowesUpdateLocalStoreCmd?storeNumber={key}"\
                   "&URL=http://www.lowes.com/?catalogId=10051&catalogId=10051&errorURL=UserAccountView"


    def __init__(self, zip_code='94117', *args, **kwargs):
        self.zip_code = zip_code
        settings.overrides['CRAWLERA_ENABLED'] = True
        super(LowesProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def start_requests(self):
        yield Request(self.STORES_JSON.format(zip_code=self.zip_code),
                      meta={'zip_code_stage': 2},
                      headers={'X-Crawlera-Cookies': 'disable'},
                      callback=self.set_zip_code)

    def set_zip_code(self, response):
        zip_code_stage = response.meta.get('zip_code_stage')
        self.log("zip code stage: %s" % zip_code_stage, DEBUG)
        if zip_code_stage == 1:
            new_meta = response.meta.copy()
            new_meta['zip_code_stage'] = 2
            request = Request(
                url=self.STORES_JSON.format(zip_code=self.zip_code),
                callback=self.set_zip_code,
                headers={'X-Crawlera-Cookies': 'disable'},
                meta=new_meta)
            yield request

        elif zip_code_stage == 2:
            stores_json = json.loads(response.body)
            near_store = stores_json['Location'][0]
            new_meta = response.meta.copy()
            new_meta['zip_code_stage'] = 3
            request = Request(
                url=self.SELECT_STORE.format(key=near_store['KEY']),
                headers={'X-Crawlera-Cookies': 'disable'},
                callback=self.set_zip_code,
                meta=new_meta)
            yield request

        else:
            for st in self.searchterms:
                yield Request(
                    self.url_formatter.format(
                        self.SEARCH_URL,
                        search_term=urllib.quote_plus(st.encode('utf-8')),
                    ),
                    headers={'X-Crawlera-Cookies': 'disable'},
                    meta={'search_term': st, 'remaining': self.quantity},
                )

            if self.product_url:
                prod = SiteProductItem()
                prod['is_single_result'] = True
                prod['url'] = self.product_url
                prod['search_term'] = ''
                yield Request(self.product_url,
                              self._parse_single_product,
                              headers={'X-Crawlera-Cookies': 'disable'},
                              meta={'product': prod})

            if self.products_url:
                urls = self.products_url.split('||||')
                for url in urls:
                    prod = SiteProductItem()
                    prod['url'] = url
                    prod['search_term'] = ''
                    yield Request(url,
                                  self._parse_single_product,
                                  headers={'X-Crawlera-Cookies': 'disable'},
                                  meta={'product': prod})

    def _parse_single_product(self, response):
        # open_in_browser(response)
        return self.parse_product(response)

    def clear_text(self, str_result):
        return str_result.replace("\t", "").replace("\n", "").replace("\r", "").replace(u'\xa0', ' ').strip()

    def _scrape_total_matches(self, response):
        # extracting total matches by calculating numbers on filter panel
        panel_values = response.xpath('.//li[contains(@class, "refinement-label") '
                                      'and contains(@data-name, "$")]//span[@id]/text()').re(r'\((\d+)\)')
        panel_values = [int(p) for p in panel_values if p.isdigit()]
        total_matches = sum(panel_values)
        return total_matches

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//*[@name="listpage_productname"]/@href').extract()
        if not links:
            links = response.xpath(
                './/*[contains(@id, "product-")]/@data-producturl').extract()
        for link in links:
            product = SiteProductItem()
            yield link, product

    def _scrape_next_results_page_link(self, response):
        next_page_url = response.xpath(
            '(//*[@title="Next Page"]/@href)[1]').extract()
        if not next_page_url:
            next_page_url= response.xpath('.//*[@class="page-next"]/a/@href').extract()

        return urljoin(response.url, next_page_url[0]) if \
            next_page_url else None

    def _parse_title(self, response):
        title = response.xpath('//h1/text()').extract()
        return title[0] if title else None

    def _parse_brand(self, response):
        brand = response.xpath('//meta[@itemprop="brand"]/@content').extract()
        return brand[0] if brand else None

    def _parse_model(self, response):
        arr = response.xpath('//p[contains(@class,"secondary-text")]//text()').extract()
        model = None
        is_model = False
        for item in arr:
            if is_model:
                model = item.strip()
                break
            if "model #" in item.lower():
                is_model = True
        return model

    def _parse_categories(self, response):
        return response.xpath(
            '//li[@itemprop="itemListElement"]//a//text()'
        ).extract() or None

    def _parse_category(self, response):
        categories = self._parse_categories(response)
        return categories[-1] if categories else None

    def _parse_reseller_id(self, response):
        reseller_id = response.xpath('.//*[contains(text(), "Item #")]/following-sibling::text()[1]').extract()
        reseller_id = reseller_id[0] if reseller_id else None
        return reseller_id

    def _parse_price(self, response):
        price = response.xpath(
            '//*[@class="price"]/text()').re('[\d\.\,]+')
        if not price:
            price = response.xpath('.//*[@itemprop="price"]/@content').re('[\d\.\,]+')

        if not price:
            return None
        price = price[0].replace(',', '')
        return Price(price=price, priceCurrency='USD')

    def _parse_image_url(self, response):
        image_url = response.xpath(
            '//*[@id="prodPrimaryImg"]/@src').extract()
        if not image_url:
            image_url = response.xpath(
                './/img[contains(@class, "product-image")]/@src').extract()
        return image_url[0] if image_url else None

    def _parse_variants(self, response):
        return None

    def _parse_is_out_of_stock(self, response):
        status = response.xpath(
            '//*[@itemprop="availability" '
            'and not(@href="http://schema.org/InStock")]')
        return bool(status)

    def _parse_description(self, response):
        description_div = response.xpath('//div[contains(@class,"panel-body")]')
        if len(description_div) > 0:
            description_div = description_div[0]
            description = description_div.xpath('.//text()').extract()
            if description:
                return self.clear_text(''.join(description).strip())
            else:
                return ''
        else:
            return ''

    def _parse_related_products(self, response):
        related_products = []
        for a in response.xpath('.//*[@class="slick-track"]/div[contains(@class, "item ")]/a[@tabindex]'):
            title = a.xpath('text()').extract()
            url = a.xpath('@href').extract()

            if title and url:
                related_products.append(
                    RelatedProduct(title=title[0],
                                   url=urljoin(response.url, url[0])))
        return related_products or None

    def _parse_no_longer_available(self, response):
        return bool(response.xpath('.//*[contains(@class, "pd-shipping-delivery")]//'
                                   'div[@class="media-body"]/p[contains(text(), "Available!")]'))

    def parse_product(self, response):
        reqs = response.meta.get('reqs',[])
        product = response.meta['product']

        # Set locale
        product['locale'] = 'en_US'

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse brand
        brand = self._parse_brand(response)
        cond_set_value(product, 'brand', brand, conv=string.strip)

        # Parse model
        model = self._parse_model(response)
        cond_set_value(product, 'model', model)

        # Parse categories
        categories = self._parse_categories(response)
        cond_set_value(product, 'categories', categories)

        # Parse category
        category = self._parse_category(response)
        cond_set_value(product, 'category', category)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse reseller_id
        reseller_id = self._parse_reseller_id(response)
        cond_set_value(product, 'reseller_id', reseller_id)

        # Parse image url
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Parse variants
        variants = self._parse_variants(response)
        cond_set_value(product, 'variants', variants)

        # Parse stock status
        out_of_stock = self._parse_is_out_of_stock(response)
        cond_set_value(product, 'is_out_of_stock', out_of_stock)

        no_longer_available = self._parse_no_longer_available(response)
        cond_set_value(product, 'no_longer_available', no_longer_available)

        related_products = self._parse_related_products(response)
        cond_set_value(product, 'related_products', related_products)

        # Reviews
        bv_product_id = response.xpath('//*[@id="bvProductId"]/@value').extract()
        bv_product_id = bv_product_id[0] if bv_product_id else None
        if not bv_product_id:
            bv_product_id = response.url.split('/')[-1]
        if bv_product_id:
            url = self.RATING_URL.format(prodid=bv_product_id)
            reqs.append(
                Request(
                    url,
                    dont_filter=True,
                    callback=self._parse_bazaarv,
                    meta={'product': product, 'reqs': reqs}
                ))
        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_bazaarv(self, response):
        reqs = response.meta.get('reqs', [])
        product = response.meta['product']
        text = response.body_as_unicode().encode('utf-8')
        if response.status == 200:
            x = re.search(
                r"var materials=(.*),\sinitializers=", text, re.M + re.S)
            if x:
                jtext = x.group(1)
                jdata = json.loads(jtext)

                html = jdata['BVRRSourceID']
                sel = Selector(text=html)
                avrg = sel.xpath(
                    "//div[contains(@id,'BVRRRatingOverall')]"
                    "/div[@class='BVRRRatingNormalOutOf']"
                    "/span[contains(@class,'BVRRRatingNumber')]"
                    "/text()").extract()
                if avrg:
                    try:
                        avrg = float(avrg[0])
                    except ValueError:
                        avrg = 0.0
                else:
                    avrg = 0.0
                total = sel.xpath(
                    "//div[@class='BVRRHistogram']"
                    "/div[@class='BVRRHistogramTitle']"
                    "/span[contains(@class,'BVRRNonZeroCount')]"
                    "/span[@class='BVRRNumber']/text()").extract()
                if total:
                    try:
                        total = int(total[0])
                    except ValueError:
                        total = 0
                else:
                    total = 0

                hist = sel.xpath(
                    "//div[@class='BVRRHistogram']"
                    "/div[@class='BVRRHistogramContent']"
                    "/div[contains(@class,'BVRRHistogramBarRow')]")
                distribution = {}
                for ih in hist:
                    name = ih.xpath(
                        "span/span[@class='BVRRHistStarLabelText']"
                        "/text()").re("(\d) star")
                    try:
                        if name:
                            name = int(name[0])
                        value = ih.xpath(
                            "span[@class='BVRRHistAbsLabel']/text()").extract()
                        if value:
                            value = int(value[0])
                        distribution[name] = value
                    except ValueError:
                        pass
                if distribution:
                    reviews = BuyerReviews(total, avrg, distribution)
                    cond_set_value(product, 'buyer_reviews', reviews)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)
