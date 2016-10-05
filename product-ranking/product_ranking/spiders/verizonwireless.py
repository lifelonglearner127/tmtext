# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals
import json
import string
import re
import urlparse

from itertools import islice

from scrapy import Request
from scrapy.conf import settings
from scrapy.log import ERROR, INFO

from product_ranking.items import SiteProductItem, BuyerReviews, Price
from product_ranking.spiders import cond_set_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider
from spiders_shared_code.verizonwireless_variants import VerizonWirelessVariants
from product_ranking.guess_brand import guess_brand_from_first_words

class VerizonwirelessProductsSpider(ProductsSpider):
    handle_httpstatus_list = [404]
    name = 'verizonwireless_products'

    allowed_domains = ['verizonwireless.com', 'bazaarvoice.com']

    SEARCH_URL = "http://www.verizonwireless.com/search/" \
                 "vzwSearch?Ntt={search_term}&nav=Global&gTab="

    REVIEW_URL = "http://api.bazaarvoice.com/data/batch.json?passkey=e8bg3vobqj42squnih3a60fui&apiversion=5.5&displaycode=6543-en_us&resource.q0=products&filter.q0=id%3Aeq%3A{0}&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews"

    def __init__(self, *args, **kwargs):
        settings.overrides[
            'RETRY_HTTP_CODES'] = [500, 502, 503, 504, 400, 403, 408]
        middlewares = settings.get('DOWNLOADER_MIDDLEWARES')
        middlewares['product_ranking.custom_middlewares.VerizonMetaRefreshMiddleware'] = 700
        middlewares['product_ranking.custom_middlewares.VerizonRedirectMiddleware'] = 800

        settings.overrides['DOWNLOADER_MIDDLEWARES'] = middlewares

        super(VerizonwirelessProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def _total_matches_from_html(self, response):
        total = response.xpath(
            '//*[@id="total-results-source-div"]//strong/text()').re('\d+') or \
            re.findall('totalNumRecs":(\d+)}', response.body)

        return int(total[0]) if total else 0

    def _scrape_results_per_page(self, response):
        return 24

    def _scrape_next_results_page_link(self, response):
        link = response.xpath('//a[text()="Next"]/@href').extract()
        return link[0] if link else None

    def _scrape_product_links(self, response):
        item_urls = response.xpath(
            '//div[@itemtype="https://schema.org/Product" and '
            'not(contains(@class,"Device-SpecificInstructions") or '
            'contains(@class,"allother"))]'
            '/a/@href').extract()


        for item_url in item_urls:
            yield urlparse.urljoin(
                response.url, item_url), SiteProductItem()

        # Search Special Case
        if not item_urls:
            urls = set()
            item_urls = [x.split('#')[0] for x in re.findall(
                'pdpUrl":\["(.*?)\"]', response.body)]
            for url in item_urls:
                if url not in urls:
                    urls.add(url)
                    yield urlparse.urljoin(response.url, url), SiteProductItem()

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _parse_title(self, response):
        title = response.xpath('//*[@itemprop="name"]/text()').extract()
        return title[0] if title else None

    def _parse_categories(self, response):
        devices = ['/tablets/', '/smartphones/', '/basic-phones/']
        categories = response.xpath(
            '//*[@itemtype="https://data-vocabulary.org/Breadcrumb"]'
            '//span[@itemprop="title"]/text()').extract()
        if categories and any([x in response.url for x in devices]):
            categories.insert(1, 'Devices')

        return categories

    def _parse_category(self, response):
        categories = self._parse_categories(response)
        return categories[-1] if categories else None

    def _parse_price(self, response):
        price = ''.join(response.xpath(
            '//*[@itemprop="price"]//span/text()').re('[\d\.]+'))
        currency = response.xpath(
            '//*[@itemprop="priceCurrency"]/@content').re('\w{2,3}') or ['USD']

        if not price:
            return None

        return Price(price=price, priceCurrency=currency[0])

    def _parse_image_url(self, response):
        image_url = response.xpath(
            '//*[@property="og:image"]/@content').extract()
        if image_url and image_url[0]:
            return image_url[0].split('?')[0]

        inits7_img = response.xpath(
            '//*[@id="PDPContainer"]/script').re(
            'initS7Viewer\(\'(.*)\'\)')
        if inits7_img:
            return "https://ss7.vzw.com/is/image/VerizonWireless/%s" % inits7_img[0]

        return None

    def _parse_brand(self, response, product):
        brand = response.xpath(".//*[@id='product-brand-field']/text()").extract()
        if not brand:
            brand = response.xpath('.//*[@itemprop="brand"]/text()').extract()
            brand = brand[0].strip() if brand else ''
        if not brand:
            brand = guess_brand_from_first_words(product['title'].replace(u'®', ''))

        return brand

    def _parse_sku(self, response):
        sku = re.findall('selectedSkuId":"(.*?)"', response.body)
        return sku[0] if sku else None

    def _parse_variants(self, response):
        self.av = VerizonWirelessVariants()
        self.av.setupSC(response)
        variants = self.av._variants()

        if variants and len(variants) == 1:
            print "%s only 1 variant" % response.url
        return variants

    def _parse_is_out_of_stock(self, response, variants):
        if variants:
            stocked_variants = [x for x in variants if x.get('in_stock')]
            return not bool(len(stocked_variants))

        out_of_stock = response.xpath(
            '//*[@id="pdp-outOfStock-cart"]|'
            '//*[@class="outOfStockBar" and contains(text(), "out of stock")]')
        return bool(out_of_stock)

    def _parse_description(self, response):
        description = response.xpath(
            '//*[@data-tabname="overview"]'
            '//div[@id="pdp-two-thirds"]').extract()

        return ''.join(description).strip() if description else None

    def _parse_price_json(self, data):
        return data.get('mboxInfo', {}).get(
            'priceBreakDownFullRetailPrice', None)

    def _get_products(self, response):
        remaining = response.meta['remaining']
        search_term = response.meta['search_term']
        prods_per_page = response.meta.get('products_per_page')
        total_matches = response.meta.get('total_matches')
        scraped_results_per_page = response.meta.get('scraped_results_per_page')

        prods = self._scrape_product_links(response)

        if prods_per_page is None:
            # Materialize prods to get its size.
            prods = list(prods)
            prods_per_page = len(prods)
            response.meta['products_per_page'] = prods_per_page

        if scraped_results_per_page is None:
            scraped_results_per_page = self._scrape_results_per_page(response)
            if scraped_results_per_page:
                self.log(
                    "Found %s products at the first page" %scraped_results_per_page
                    , INFO)
            else:
                scraped_results_per_page = prods_per_page
                if hasattr(self, 'is_nothing_found'):
                    if not self.is_nothing_found(response):
                        self.log(
                            "Failed to scrape number of products per page", ERROR)
            response.meta['scraped_results_per_page'] = scraped_results_per_page

        if total_matches is None:
            total_matches = self._scrape_total_matches(response)
            if total_matches is not None:
                response.meta['total_matches'] = total_matches
                self.log("Found %d total matches." % total_matches, INFO)
            else:
                if hasattr(self, 'is_nothing_found'):
                    if not self.is_nothing_found(response):
                        self.log(
                            "Failed to parse total matches for %s" % response.url,ERROR)

        if total_matches and not prods_per_page:
            # Parsing the page failed. Give up.
            self.log("Failed to get products for %s" % response.url, ERROR)
            return

        for i, (prod_url, prod_item) in enumerate(islice(prods, 0, remaining)):
            # Initialize the product as much as possible.
            prod_item['site'] = self.site_name
            prod_item['search_term'] = search_term
            prod_item['total_matches'] = total_matches
            prod_item['results_per_page'] = prods_per_page
            prod_item['scraped_results_per_page'] = scraped_results_per_page
            # The ranking is the position in this page plus the number of
            # products from other pages.
            prod_item['ranking'] = (i + 1) + (self.quantity - remaining)
            if self.user_agent_key not in ["desktop", "default"]:
                prod_item['is_mobile_agent'] = True

            if prod_url is None:
                # The product is complete, no need for another request.
                yield prod_item
            elif isinstance(prod_url, Request):
                cond_set_value(prod_item, 'url', prod_url.url)  # Tentative.
                yield prod_url
            else:
                # Another request is necessary to complete the product.
                url = urlparse.urljoin(response.url, prod_url)
                cond_set_value(prod_item, 'url', url)  # Tentative.
                yield Request(
                    url,
                    callback=self.parse_product,
                    errback=self.parse_404,
                    meta={'product': prod_item},
                )

    def parse_404(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Set locale
        product['locale'] = 'en_US'

        pdp_data = response.xpath('//script/text()').re('pdpJSON = ({.*})')
        if pdp_data:
            pdp_json = json.loads(pdp_data[0])

            price = self._parse_price_json(pdp_json)
            if price:
                cond_set_value(product, 'price', Price(price=price,
                                                       priceCurrency="USD"))

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse brand
        brand = self._parse_brand(response, product)
        cond_set_value(product, 'brand', brand)

        # Parse category
        category = self._parse_category(response)
        cond_set_value(product, 'category', category)

        # Parse category
        categories = self._parse_categories(response)
        cond_set_value(product, 'categories', categories)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse image url
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Parse sku
        sku = self._parse_sku(response)
        cond_set_value(product, 'sku', sku)

        # Parse variants
        variants = self._parse_variants(response)
        cond_set_value(product, 'variants', variants)

        # Parse stock status
        out_of_stock = self._parse_is_out_of_stock(response, variants)
        cond_set_value(product, 'is_out_of_stock', out_of_stock)

        # Default Reviews Values
        review_list = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        reviews = BuyerReviews(0, 0.0, review_list)
        product['buyer_reviews'] = reviews

        id = None
        device_prod_id_search = re.search('deviceProdId=(.*?)&', response.body)

        if device_prod_id_search:
            id = device_prod_id_search.group(1)

        else:
            is_product_id = response.xpath(
                '//input[@id="isProductId"]/@value').extract()
            if is_product_id:
                id = is_product_id[0]
        if id:
            reqs.append(Request(self.REVIEW_URL.format(id),
                        meta=response.meta,
                        callback=self._parse_reviews))

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_reviews(self, response):
        product = response.meta['product']
        reqs = response.meta.get('reqs', [])

        review_json = json.loads(response.body_as_unicode())

        review_count = self._review_count(review_json)
        average = self._average_review(review_json)
        fdist = self._reviews(review_json)
        reviews = BuyerReviews(review_count, average, fdist)
        product['buyer_reviews'] = reviews

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """
        req = reqs.pop(0)
        new_meta = response.meta

        if reqs:
            new_meta["reqs"] = reqs

        return req.replace(meta=new_meta)

    def _average_review(self, review_json):
        average_review = 0.0
        try:
            average_review = float(review_json["BatchedResults"]["q0"][
                "Results"][0]["FilteredReviewStatistics"][
                "AverageOverallRating"])
        except:
            pass
        return round(average_review, 1)

    def _review_count(self, review_json):
        review_count = 0
        try:
            review_count = review_json["BatchedResults"]["q0"]["Results"][0][
                "FilteredReviewStatistics"]["TotalReviewCount"]
        except:
            pass
        return review_count

    def _reviews(self, review_json):
        review_list = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        try:
            for review in review_json["BatchedResults"]["q0"]["Results"][0][
                    "FilteredReviewStatistics"]["RatingDistribution"]:
                review_list[str(review["RatingValue"])] = int(review["Count"])
        except:
            pass

        return review_list