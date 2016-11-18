import re
import string
import urlparse

from itertools import islice
from scrapy import Request
from scrapy.log import ERROR, INFO

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import cond_set_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi



class ChewyProductsSpider(ProductsSpider):
    name = 'chewy_products'
    allowed_domains = ['chewy.com']

    SEARCH_URL = "http://www.chewy.com/s?query={search_term}"

    BUYER_REVIEWS_URL = ("http://chewy.ugc.bazaarvoice.com/0090-en_us"
                         "/{product_id}/reviews.djs?format=embeddedhtml")

    def __init__(self, *args, **kwargs):
        super(ChewyProductsSpider, self).__init__(*args, **kwargs)
        self.br = BuyerReviewsBazaarApi(called_class=self)

    def _total_matches_from_html(self, response):
        total = response.css('.resultCount::text').re('of (\d+) Result')
        return int(total[0].replace(',', '')) if total else 0

    def _scrape_results_per_page(self, response):
        return 39

    def _scrape_next_results_page_link(self, response):
        link = response.xpath('//a[@class="next"]/@href').extract()
        return link[0] if link else None

    def _scrape_product_links(self, response):
        item_urls = response.xpath(
            '//*[@class="product"]/a[1]/@href').extract()
        for item_url in item_urls:
            yield item_url, SiteProductItem()

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _parse_title(self, response):
        title = response.xpath('//h1/text()').extract()
        return title[0].strip() if title else None

    def _parse_categories(self, response):
        categories = response.css('.breadcrumbs a::text').extract()
        return categories if categories else None

    def _parse_category(self, response):
        categories = self._parse_categories(response)
        return categories[-1] if categories else None

    def _parse_price(self, response):
        price = response.css('.our-price::text').re('[\d\.]+')

        if not price:
            return None

        return Price(price=price[0], priceCurrency='USD')

    def _parse_image_url(self, response):
        image_url = response.xpath(
            '//a[@class="MagicZoomPlus"]/@href').extract()
        return 'http:' + image_url[0] if image_url else None

    def _parse_brand(self, response):
        brand = response.xpath(
            '//*[@id="brand"]//a/text()').extract()
        return brand[0].strip() if brand else None

    def _parse_sku(self, response):
        sku = response.xpath('//*[@itemprop="sku"]/@content').extract()
        return sku[0] if sku else None

    def _parse_variants(self, response):
        variants_data = response.xpath(
            '//script[contains(text(),"itemData")]').extract()
        if not variants_data:
            return None

        variants_data = variants_data[0].replace('\n', '')

        skus = re.findall('\'(\d+)\' : {', variants_data)
        prices = re.findall('price: \'\$([\d\.]+)', variants_data)
        urls = re.findall('canonicalURL: \'(.*?)\'', variants_data)
        imgs_raw = re.findall('images: \[(.*?)\]', variants_data)
        imgs = []
        for img in imgs_raw:
            imgs.append(["http:" + x.replace('\'', '').strip() for x in img.split(',') if x.strip()])

        variants = []
        for item in zip(skus, prices, urls, imgs):
            vr = {}
            cond_set_value(vr, 'price', item[1])
            cond_set_value(vr, 'url', urlparse.urljoin(response.url, item[2]))
            cond_set_value(vr, 'image_urls', item[3])
            vr['selected'] = True if item[0] in response.url else False

            if vr:
                variants.append(vr)

        return variants if variants and len(variants) > 1 else None

    def _parse_is_out_of_stock(self, response):
        status = response.xpath(
            '//*[@id="availability"]/span[text()="In Stock"]')

        return not bool(status)

    def _parse_shipping_included(self, response):
        shipping_text = ''.join(
            response.xpath('//span[@class="free-shipping"]//text()').extract())

        return shipping_text == ' & FREE Shipping'

    def _parse_description(self, response):
        description = response.xpath(
            '//*[@class="longDescription"]').extract()

        return ''.join(description).strip() if description else None

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def parse_product(self, response):
        reqs = []
        product = response.meta['product']
        response.meta['product_response'] = response
        # Set locale
        product['locale'] = 'en_US'

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse category
        category = self._parse_category(response)
        cond_set_value(product, 'category', category)

        # Parse categories
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

        # Parse variants
        variants = self._parse_variants(response)
        cond_set_value(product, 'variants', variants)

        # Parse stock status
        out_of_stock = self._parse_is_out_of_stock(response)
        cond_set_value(product, 'is_out_of_stock', out_of_stock)

        # Sku
        sku = self._parse_sku(response)
        cond_set_value(product, 'sku', sku)

        # Brand
        brand = self._parse_brand(response)
        cond_set_value(product, 'brand', brand)

        # Shipping included
        shipping_included = self._parse_shipping_included(response)
        cond_set_value(product, 'shipping_included', shipping_included)

        product_id = response.xpath(
            '//script[contains(text(),"show_reviews")]').re(
            'productId: "(\d+)"')

        if product_id:
            # Parse buyer reviews
            reqs.append(
                Request(
                    url=self.BUYER_REVIEWS_URL.format(
                        product_id=product_id[0]),
                    dont_filter=True,
                    callback=self.br.parse_buyer_reviews
                )
            )

        if reqs:
            return self.send_next_request(reqs, response)

        return product


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
                    meta={'product': prod_item},
                    # Remove Referer field on searchs to make the
                    # website display the breadcrumbs
                    headers={'referer': ''},
                )
