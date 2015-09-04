# -*- coding: utf-8 -*-#

import json
import re
import string
import itertools
import urllib

from scrapy.http import FormRequest, Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value
from product_ranking.settings import ZERO_REVIEWS_VALUE

is_empty = lambda x, y=None: x[0] if x else y


class WayfairProductSpider(BaseProductsSpider):

    name = 'wayfair_products'
    allowed_domains = ["wayfair.com"]

    SEARCH_URL = "http://www.wayfair.com/keyword.php?keyword={search_term}"

    LAST_BR_DATE_URL = "http://www.wayfair.com/a/product_review_page/get_update_reviews_json?" \
                       "_format=json&product_sku={sku}&page_number=1&sort_order=date_desc" \
                       "&filter_rating=&filter_tag=&item_per_page=10&is_nova=1&_txid=rBAZEVXcZE6pEXHr94MSAg%3D%3D"

    VARIANTS_STOCK_URL = "http://www.wayfair.com/ajax/stock_total.php?bpss=yes&" \
                         "skulist={sku}&kitmode=0&postalcode=67346&_txid=rBAZEVXca8GoynHn%2FREfAg%3D%3D"

    def __init__(self, *args, **kwargs):
        super(WayfairProductSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        # Set product primary sku
        product_sku = is_empty(
            response.xpath('//span[@class="product_breadcrumb"]/text()').extract()
        )

        if product_sku:
            product_sku = is_empty(
                re.findall(r'SKU:\s?(\w+)', product_sku)
            )
            response.meta['product_sku'] = product_sku
        else:
            self.log('No product sku in {0}'.format(
                response.url
            ), WARNING)

        # Set kitid
        # Needed to choose product own variants
        kit_id = is_empty(
            response.xpath('//input[@name="kitId"]/@value').extract(),
            '0'
        )
        response.meta['kit_id'] = int(kit_id)

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse brand
        brand = self._parse_brand(response)
        cond_set_value(product, 'brand', brand, conv=string.strip)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse special pricing
        special_pricing = self._parse_special_pricing(response)
        cond_set_value(product, 'special_pricing', special_pricing, conv=bool)

        # Parse image link
        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Parse description
        description = self._parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse variants
        variants = self._parse_variants(response)
        cond_set_value(product, 'variants', variants)

        # Parse stock status for variants
        # if variants:
        #     stock_skus = urllib.quote(response.meta['stock_skus'])
        #     reqs.append(Request(
        #         url=self.VARIANTS_STOCK_URL.format(sku=stock_skus),
        #         callback=self._parse_variants_stock,
        #         headers={
        #             'Referer': response.url,
        #             'X-Requested-With': 'XMLHttpRequest',
        #             'User-Agent': 'Mozilla/5.0 (X11; Linux i686 (x86_64)) AppleWebKit/537.36 (KHTML, '
        #                           'like Gecko) Chrome/43.0.2357.134 Safari/537.36'
        #         }
        #     ))

        # Parse categories
        category = self._parse_category(response)
        cond_set_value(product, 'category', category)

        # Parse department
        if category:
            department = category[-1]
            cond_set_value(product, 'department', department)

        # Parse stock status
        stock_status = self._parse_stock_status(response)
        if stock_status:
            product.update(stock_status)

        # Parse buyer reviews
        buyer_reviews = self._parse_buyer_reviews(response)
        cond_set_value(product, 'buyer_reviews', buyer_reviews)

        # Parse last buyer review date
        # if buyer_reviews is not ZERO_REVIEWS_VALUE:
        #     reqs.append(Request(
        #         url=self.LAST_BR_DATE_URL.format(sku=product_sku),
        #         callback=self._parse_last_buyer_review_date
        #     ))

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_title(self, response):
        """
        Parse product title
        """
        title = is_empty(
            response.xpath('//*[@class="title_name"]/text()').extract()
        )

        return title

    def _parse_brand(self, response):
        """
        Parse product brand
        """
        brand = is_empty(
            response.xpath('//*[@class="manu_name"]/a/text()').extract()
        )

        return brand

    def _parse_special_pricing(self, response):
        """
        Parse product special price
        """
        special_pricing = is_empty(
            response.xpath('//*[contains(@class, "listprice")]').extract()
        )

        return special_pricing

    def _parse_image_url(self, response):
        """
        Parse product image link
        """
        image_url = is_empty(
            response.xpath('//*[@id="zoomimg"]/.//*[contains(@class, "pdp_main_carousel_container")]/./'
                           '/a/img/@src').extract()
        )

        return image_url

    def _parse_description(self, response):
        """
        Parse product description
        """
        description = is_empty(
            response.xpath('//*[@id="information"]/div').extract()
        )

        return description

    def _parse_category(self, response):
        """
        Parse product categories
        """
        category = response.xpath('//div[contains(@class, "product__nova__breadcrumbs")]/./'
                                  '/a[contains(@class, "breadcrumb")]/text()').extract()

        return category

    def _parse_stock_status(self, response):
        """
        Parse product stock status
        """
        stock_status = is_empty(
            response.xpath('//ul[@id="ship_display"]/'
                           'li[contains(@class, "stock_count")]').extract()
        )

        if stock_status:
            return self._guess_stock_field(stock_status)
        else:
            self.log('Unable to parse stock status on {url}'.format(
                url=response.url
            ), WARNING)
            return None

    def _guess_stock_field(self, stock_status):
        """
        Selects what field to fill.
        For ex. for '+10 in Stock' --> {'is_out_of_stock': False}
        """
        stock_status = stock_status.lower()

        if 'out of stock' in stock_status:
            return {'is_out_of_stock': True}
        elif 'low' in stock_status:
            return {'is_limited': True}
        else:
            return {'is_out_of_stock': False}

    def _parse_buyer_reviews(self, response):
        """
        Parse product buyer reviews
        """
        num_of_reviews = is_empty(
            response.xpath('//span[contains(@class, "ratingcount")]/'
                           'span/text()').extract(), ''
        )

        if num_of_reviews:
            num_of_reviews = is_empty(
                re.findall(r'(\d+) reviews?', num_of_reviews)
            )

            if num_of_reviews:
                average_rating = is_empty(
                    response.xpath('//span[@itemprop="ratingValue"]/'
                                   'text()').extract(), '0'
                )

                histogram = is_empty(
                    re.findall(r'"formatted_histogram_stats":\s?\[(.[^]]+)',
                               response.body_as_unicode())
                )

                if not histogram or not average_rating:
                    return ZERO_REVIEWS_VALUE
                else:
                    histogram = "[{0}]".format(histogram)

                    try:
                        stars_data = json.loads(histogram)
                        rating_by_star = {}

                        for star in stars_data:
                            rating_by_star[star['id']] = star['he_count']

                        buyer_reviews = {
                            'average_rating': average_rating,
                            'num_of_reviews': num_of_reviews,
                            'rating_by_star': rating_by_star,
                        }
                        return BuyerReviews(**buyer_reviews)
                    except (KeyError, ValueError) as exc:
                        self.log('Unable to parse star rating from {url}: {exc}'.format(
                            url=response.url,
                            exc=exc
                        ), ERROR)
                        return ZERO_REVIEWS_VALUE
        else:
            return ZERO_REVIEWS_VALUE

    def _parse_last_buyer_review_date(self, response):
        """
        Parse product buyer reviews
        """
        meta = response.meta.copy()
        reqs = meta.get('reqs')
        product = meta['product']

        try:
            data = json.loads(response.body_as_unicode())
            last_buyer_review = data['reviews'][0]
            last_buyer_review_date = last_buyer_review['date']
            cond_set_value(product, 'last_buyer_review_date', last_buyer_review_date)
        except (KeyError, ValueError) as exc:
            self.log('Unable to get last buyer review date on {url}: {exc}'.format(
                url=response.url,
                exc=exc
            ), WARNING)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_variants(self, response):
        """
        Parse product variants from HTML body as JS var
        """
        meta = response.meta.copy()
        product = meta['product']
        variants_data = is_empty(
            re.findall(
                'wf\.appData\.product_data_%s\s?=\s?({.[^;]+)' % meta.get('product_sku'),
                response.body_as_unicode()
            )
        )

        if variants_data:
            main_price = product['price']

            try:
                data = json.loads(variants_data)
                # Contains data for all variants for all products on page
                # (ps. there also can be related prods with variants)
                option_details = data.get('option_details')
                variants = []

                if option_details:
                    final_options = {}
                    # A dict for sku accordance for every single variant.
                    # Will contain, for ex.: 'blue': '123456', 'red': '456789'
                    variants_skus = {}
                    # Will contain sku for stock status request. If the variant is {'color: 'blue', 'size':10}
                    # skus for every of them are: {'blue':'123456', 'red': '456789'} and product sku: 'QMP2470'
                    # we will get 'QMP2470-123456,456789'
                    stock_skus = []

                    for sku, option in option_details.iteritems():
                        # Getting information for every variant and push it to dict
                        if option['kit_id'] == meta['kit_id']:
                            category = option['category'].replace(' ', '_').lower()
                            value = option['name']

                            # From this data for price we get an additional price value (+ 3.00 USD, for ex.)
                            add_price = round(option['price'], 2)

                            if not final_options.get(category):
                                final_options[category] = []

                            variants_skus[value] = sku
                            final_options[category].append({category: value, 'price': add_price})

                    response.meta['variants_skus'] = variants_skus

                    for variant in itertools.product(*final_options.values()):
                        # Make a list of dictionary with variant from a list of tuples
                        # ({'color': u'Yellow', 'price': 12.99}, {'price': 15.99, 'size': u'10'}) -->
                        #     {'color': u'Yellow', 'price': 15.99, 'size': u'10'}
                        single_variant = {}
                        stock_sku = []

                        # Make a final price from additional prices for variants
                        final_price = product['price'].price.__float__()
                        for var in variant:
                            final_price += var['price']

                        properties = dict(sum(map(dict.items, variant), []))
                        del properties['price']

                        single_variant['price'] = round(final_price, 2)
                        single_variant['properties'] = properties

                        for property in properties.itervalues():
                            stock_sku.append(variants_skus[property])

                        # This argument is needed to send Req for variant stock status
                        # Ex.: BSS1567-2673193,2673179
                        stock_skus.append(
                            meta['product_sku'] + '-'
                            + ','.join(stock_sku)
                        )

                        variants.append(single_variant)
                    # This argument is needed to send Req for variant stock status
                    # Ex.: BSS1567-2673193,2673179~^~BSS1567-2673199,2673190
                    response.meta['stock_skus'] = '~^~'.join(stock_skus)

                return variants
            except Exception as exc:
                self.log('Unable to parse variants on {url}: {exc}'.format(
                    url=response.url,
                    exc=exc
                ), ERROR)
                return []

        return []

    def _parse_variants_stock(self, response):
        """
        Parse product variants from HTML body as JS var
        """
        meta = response.meta.copy()
        product = meta['product']
        reqs = meta.get('reqs')

        try:
            # Dict where stock status data is accesses by sky, for ex.: "QMP2470_14347972_14347969"
            stock_status_data = json.loads(response.body_as_unicode())
            variants = product['variants']
            skus = response.meta['variants_skus']

            for variant in variants:
                variant_sku = [meta['product_sku']]

                for property in variant['properties'].itervalues():
                    variant_sku.append(skus[property])

                variant_sku = '_'.join(variant_sku)
                stock_status = self._guess_stock_field(
                    stock_status_data[variant_sku]['QuantityDisplay']
                )

                if stock_status:
                    variant.update(stock_status)

        except Exception as exc:
            self.log('Unable to parse variants on {url}: {exc}'.format(
                url=response.url,
                exc=exc
            ), ERROR)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_price(self, response):
        """
        Parse product price
        """
        price = is_empty(
            response.xpath('//span[contains(@class, "product_price")]')
        )

        if price:
            usd = is_empty(
                price.xpath('./text()').extract(), ''
            )
            coins = is_empty(
                price.xpath('.//sup/text()').extract(), ''
            )

            if usd:
                usd = usd.strip().replace('$', '')

                if coins:
                    coins = coins.strip()
                    price = usd + coins
                else:
                    price = usd + '00'
            else:
                price = '0.00'
        else:
            self.log('No price in {0}'. format(response.url), WARNING)
            price = '0.00'

        return Price(price=price, priceCurrency='USD')

    def send_next_request(self, reqs, response):
        """
        Helps to handle several requests
        """

        req = reqs.pop(0)
        new_meta = response.meta.copy()
        if reqs:
            new_meta["reqs"] = reqs
        return req.replace(meta=new_meta)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _scrape_total_matches(self, response):
        """
        Scraping number of resulted product links
        """
        total_matches = is_empty(
            response.xpath("//span[@class='viewingItems']/text()").extract(),
        )

        if total_matches:
            total_matches = total_matches.replace(',', '')
            return int(total_matches)
        else:
            return 0

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        num = is_empty(
            response.xpath("//span[@class='js-product-range-end']/text()").extract()
        )

        if not num:
            return 0

        return int(num)

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.xpath(
            '//div[@id="sbprodgrid"]/.//a'
        )

        if items:
            for item in items:
                link = is_empty(
                    item.xpath('.//@href').extract()
                )
                res_item = SiteProductItem()
                yield link, res_item
        else:
            self.log("Found no product links in {url}".format(url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        url = response.xpath(
            '//a[contains(@class, "pages_prev_next")]/@href'
        ).extract()

        if len(url) == 1:
            return url[0]
        elif len(url) == 0:
            self.log("Found no 'next page' links", WARNING)
            return None
        else:
            return url[1]
