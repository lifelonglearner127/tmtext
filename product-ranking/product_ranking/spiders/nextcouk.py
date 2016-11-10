# -*- coding: utf-8 -*-#

import json
import re
import hjson
import urlparse

from scrapy.http import Request
from scrapy.log import ERROR, INFO, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value

is_empty = lambda x, y=None: x[0] if x else y

def product_id_format(product_id, product_target=None):
    """
    Formats product id 123456 to 123-456-X56
    """
    result = '{0}-{1}'.format(
        product_id[:3],
        product_id[3:]
    )
    if product_target:
        result = '{0}-{1}'.format(
            result,
            product_target
        )
    return result

class NextCoUkProductSpider(BaseProductsSpider):

    name = 'nextcouk_products'
    allowed_domains = ["www.next.co.uk",
                       "next.ugc.bazaarvoice.com"]

    SEARCH_URL = "http://www.next.co.uk/search?w={search_term}&isort={search_sort}"

    NEXT_PAGE_URL = "http://www.next.co.uk/search?w=jeans&isort=score&srt={start_pos}"

    REVIEWS_URL = "http://next.ugc.bazaarvoice.com/data/products.json?apiversion=5.3&" \
                  "passkey=2l72hgc4hdkhcc1bqwyj1dt6d&" \
                  "Filter=Id:{product_id}&stats=reviews&callback=bvGetReviewSummaries"

    _SORT_MODES = {
        "RELEVANT": "score",
        "POPULAR": "popular",
        "ALPHABETICAL": "title",
        "LOW_HIGH": "price",
        "HIGH_LOW": "price%20rev",
        "RATING": "rating",
    }

    def __init__(self, search_sort='POPULAR', *args, **kwargs):
        self.start_pos = 0
        super(NextCoUkProductSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                search_sort=self._SORT_MODES[search_sort]
            ),
            *args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta.copy()
        product = meta['product']

        product_ids = is_empty(
            re.findall(r'#(\d+)(\D\w+)', product['url']),
            None
        )

        if not product_ids:
            product_ids = response.xpath('//input[@id="idList"]/'
                                         '@value').extract()[0]
            product_ids = product_ids.split(',')
            product_id = product_ids[0]
            product_target = is_empty(
                re.findall(r'#(\w+)', product['url']),
                ''
            )
            product_target = product_target.replace(
                product_id.lower(), ''
            ).upper()
        else:
            product_id = product_ids[0]
            product_target = product_ids[1].upper()

        response.meta['product_id'] = product_id
        response.meta['product_target'] = product_target

        product['locale'] = 'en_GB'

        # Set category
        self._parse_category(response)

        # Get StyleID to choose current item
        style_id_data = re.findall(
            r'\s*(StyleID|ItemNumber)\s*:\s*"?([^\n",]+)"?',
            response.body_as_unicode()
        )

        tree = {}
        last_id = None
        for (key, val) in style_id_data:
            if key == 'StyleID':
                last_id = val
            elif key == 'ItemNumber':
                val = is_empty(
                    re.findall(r'(\d+-\d+)', val)
                )
                tree[val] = last_id

        try:
            style_id = tree[product_id_format(product_id)]
        except (KeyError, ValueError) as exc:
            self.log('Error parsing style_id:{0}'.format(exc), ERROR)
            return product

        # Format product id to get proper section from html body
        item = response.xpath(
            '//article[@id="Style{id}"]'.format(
                id=style_id
            )
        )

        if item:
            #  Set title
            self._parse_title(response, item)

            # Set description
            self._parse_description(response, item)

            # Get variants. Method returns list of requests
            reqs = self._parse_variants(response, style_id)

            # Get price
            self._parse_price(response, item)

            # Get image url
            self._parse_image(response, item)

        else:
            self.log(
                "Failed to extract product info from {url}".format(response.url), ERROR
            )

        # Get related products
        self._parse_related_products(response, style_id)

        # Get buyer reviews
        prod_info_js = self.REVIEWS_URL.format(product_id=product_id)
        reviews_request = Request(
            url=prod_info_js,
            callback=self._parse_prod_info_js,
            dont_filter=True,
        )
        reqs.append(reviews_request)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_category(self, response):
        """
        Parses list of categories for product
        """
        product = response.meta['product']

        try:
            category = response.xpath(
                '//div[@class="BreadcrumbsHolder"]/./'
                '/li[@class="Breadcrumb"][not(contains(@class, "bcHome"))]'
                '/a/text()'
            ).extract()[:-1]
            cond_set_value(product, 'category', category, conv=list)
        except ValueError as exc:
            self.log(
                "Failed to get category from {url}: {exc}".format(
                    response.url, exc
                ), WARNING
            )

    def _parse_title(self, response, item):
        product = response.meta['product']

        title = item.xpath('.//div[@class="Title"]//h1/text() |'
                           './/div[@class="Title"]//h2/text()')
        title = is_empty(
            title.extract(), ''
        )

        if title:
            product['title'] = title.strip()

    def _parse_description(self, response, item):
        product = response.meta['product']

        description = is_empty(
            item.css('.StyleContent').extract(), ''
        )

        if description:
            product['description'] = description.strip().replace('\r', '').replace('\n', '').replace('\t', '')

    def _parse_variants(self, response, style_id):
        """
        Returns remaining requests to send
        """

        meta = response.meta.copy()
        product_target = meta['product_target']
        product_id = meta['product_id']
        reqs = meta.get('reqs', [])

        variants_data = is_empty(
            re.findall(
                r'var\s*itemData\s*=\s*(\[[^;]+)',
                response.body_as_unicode()
            ), ''
        )
        variants = {}

        if variants_data:
            variants_data = hjson.loads(
                variants_data.replace(': ', ':'),
                object_pairs_hook=dict
            )

            try:
                # Get variants data for current product
                for var in variants_data:
                    if str(var['StyleID']) == style_id:
                        data = var['Fits']
                        break

                for variant_data in data:
                    name = variant_data['Name'].strip()
                    vars_items = variant_data['Items']

                    if vars_items:
                        for variant_item in vars_items:
                            variant = dict()
                            item_number = variant_item['ItemNumber'].replace('-', '')
                            item_number_id = item_number.replace(product_target.upper(), '')
                            variant['properties'] = {}

                            if name:
                                variant['properties']['fit'] = name

                            colour_name = variant_item['Colour'].strip()
                            if colour_name:
                                variant['properties']['color'] = colour_name

                            variant['image_url'] = 'http://cdn2.next.co.uk/Common/Items/Default/' \
                                                   'Default/ItemImages/AltItemShot/315x472/{id}.jpg'.format(
                                id=item_number_id
                            )

                            variants[item_number] = variant

                            reqs.append(
                                Request(
                                    url='http://www.next.co.uk/item/{0}?CTRL=select'.format(item_number),
                                    dont_filter=True,
                                    callback=self._parse_size_variants
                                )
                            )
                response.meta['variants'] = variants
            except (KeyError, ValueError) as exc:
                self.log(
                    "Failed to extract variants from {url}: {exc}".format(
                        url=response.url, exc=exc
                    ), ERROR
                )

        return reqs

    def _parse_price(self, response, item):
        product = response.meta['product']

        price_sel = item.css('.Price')

        if price_sel:
            price = is_empty(
                price_sel.extract()
            ).strip()
            price = is_empty(
                re.findall(r'(\d+)', price)
            )
            product['price'] = Price(
                priceCurrency="GBP",
                price=price
            )
        else:
            product['price'] = None

    def _parse_image(self, response, item):
        product = response.meta['product']

        image_sel = item.xpath('.//div[@class="StyleThumb"]//img/@src')

        if image_sel:
            image = is_empty(image_sel.extract())
            product['image_url'] = image.replace('Thumb', 'Shot')

    def _parse_size_variants(self, response):
        """
        Callback - gets sizes for every single variant
        """

        meta = response.meta.copy()
        reqs = meta.get('reqs')
        product = meta['product']
        product_variants = product.get('variants', [])
        product_target = meta['product_target']
        product_id = meta['product_id']
        variants = meta['variants']

        final_vars = []

        item_number = is_empty(
            re.findall(
                r'item/(.+)\?CTRL',
                response.url
            ), ''
        )
        item_number_id = item_number.replace(product_target.upper(), '')

        # Get data of current variant from meta
        var = variants[item_number]

        size_values = response.xpath('.//select/option[@value != ""]/text()').extract()

        if size_values:
            for size in size_values:
                final_var = var.copy()
                sizes_var = dict()
                properties = var['properties']
                fit = properties.get('fit', '')
                colour = properties.get('color', '')

                sizes_var['properties'] = {}
                if fit:
                    sizes_var['properties']['fit'] = fit

                if colour:
                    sizes_var['properties']['color'] = colour

                if '- Sold Out' in size:
                    size = size.replace('- Sold Out', '')
                    sizes_var['in_stock'] = False
                else:
                    sizes_var['in_stock'] = True

                if '\\xa' in repr(size):
                    price = is_empty(
                        re.findall(
                            r'\\xa(\d+.\d{2})',
                            repr(size)
                        ), '0.00'
                    )
                    sizes_var['price'] = price
                    size = is_empty(
                        re.findall(
                            r'([^-]+)',
                            size
                        ), ''
                    )
                else:
                    sizes_var['price'] = format(
                        product['price'].price.__float__(),
                        '.2f'
                    )
                size = size.strip()
                if size != "ONE":
                    sizes_var['properties']['size'] = size

                # Set selected property
                if (fit or colour) and item_number_id == product_id and len(size_values) == 1:
                    sizes_var['selected'] = True
                else:
                    sizes_var['selected'] = False

                if sizes_var['properties']:
                    final_var.update(sizes_var)
                    final_vars.append(final_var)

        product_variants += final_vars
        product['variants'] = product_variants

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_related_products(self, response, style_id):
        product = response.meta['product']

        items = response.xpath(
            '//section[@class="ProductDetail"]/article[not(@id="Style{id}")]'.format(
                id=style_id
            )
        )

        if items:
            related_prods = []

            for item in items:
                # Get title
                title = item.xpath('.//div[@class="Title"]//h1/text() |'
                                   './/div[@class="Title"]//h2/text()')
                if title:
                    title = is_empty(
                        title.extract()
                    ).strip()

                # Get url
                targetitem = item.xpath('.//@data-targetitem')
                url = item.xpath('.//div[@class="StyleThumb"]/a/@href')
                if targetitem and url:
                    targetitem = is_empty(
                        targetitem.extract()
                    )
                    url = '{url}#{id}'.format(
                        url=response.url,
                        id=targetitem.replace('-', '')
                    )

                if url and title:
                    related_prods.append(
                        RelatedProduct(
                            title=title,
                            url=url
                        )
                    )

            product['related_products'] = related_prods

    def _parse_prod_info_js(self, response):
        meta = response.meta.copy()
        reqs = meta.get("reqs")
        product = meta['product']
        data = response.body_as_unicode()
        data = is_empty(
            re.findall(
                r'bvGetReviewSummaries\((.+)\)',
                data
            )
        )

        if data:
            data = json.loads(data)
            results = is_empty(
                data.get('Results', [])
            )

            if results:
                # Buyer reviews
                buyer_reviews = self._parse_buyer_reviews(results, response)
                product['buyer_reviews'] = BuyerReviews(**buyer_reviews)

                # Get brand
                self._parse_brand(response, results)

                # Get department
                self._parse_department(response, results)

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_brand(self, response, data):
        product = response.meta['product']

        try:
            brand = data['Brand']['Name']
            product['brand'] = brand
        except (KeyError, ValueError) as exc:
            self.log(
                "Failed to get brand from {url}: {exc}".format(
                    response.url, exc
                ), WARNING
            )

    def _parse_department(self, response, data):
        product = response.meta['product']

        try:
            departments = is_empty(
                data['Attributes']['department']['Values']
            )
            department = departments['Value']
            product['department'] = department
        except (KeyError, ValueError) as exc:
            self.log(
                "Failed to get department from {url}: {exc}".format(
                    response.url, exc
                ), WARNING
            )

    def _parse_buyer_reviews(self, data, response):
        buyer_review = dict(
            num_of_reviews=0,
            average_rating=0.0,
            rating_by_star={'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        )

        try:
            buyer_reviews_data = data['ReviewStatistics']
            buyer_review['num_of_reviews'] = buyer_reviews_data['TotalReviewCount']

            if buyer_review['num_of_reviews']:
                buyer_review['average_rating'] = float(
                    round(buyer_reviews_data['AverageOverallRating'], 1)
                )

                ratings = buyer_reviews_data['RatingDistribution']
                for rate in ratings:
                    star = str(rate['RatingValue'])
                    buyer_review['rating_by_star'][star] = rate['Count']
        except (KeyError, ValueError) as exc:
            self.log(
                "Failed to get buyer reviews from {url}: {exc}".format(
                    response.url, exc
                ), WARNING
            )

        return buyer_review

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

        total_matches = response.css("#filters .ResultCount .Count ::text")
        try:
            matches_re = re.compile('(\d+) PRODUCTS')
            total_matches = re.findall(
                matches_re,
                is_empty(
                    total_matches.extract()
                )
            )
            return int(
                is_empty(total_matches, '0')
            )
        except (KeyError, ValueError) as exc:
            total_matches = None
            self.log(
                "Failed to extract total matches from {url}: {exc}".format(
                    response.url, exc
                ), ERROR
            )

        return total_matches

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """

        num = len(
            response.css('[data-pagenumber="1"] article.Item')
        )
        self.items_per_page = num

        if not num:
            num = None
            self.items_per_page = 0
            self.log(
                "Failed to extract results per page from {url}".format(response.url), ERROR
            )

        return num

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """

        items = response.css(
            'div.Page article.Item'
        )

        if items:
            for item in items:
                link = is_empty(
                    item.css('.Details .Title a ::attr(href)').extract()
                )
                res_item = SiteProductItem()

                link = urlparse.urljoin(response.url, link)
                yield Request(
                    link,
                    dont_filter=True,
                    meta={'product': res_item},
                    callback=self.parse_product,
                ), res_item
        else:
            self.log("Found no product links in {url}".format(response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        url = self.NEXT_PAGE_URL.format(start_pos=self.start_pos)
        self.start_pos += self.items_per_page
        return url
