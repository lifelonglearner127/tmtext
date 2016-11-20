# -*- coding: utf-8 -*-
import re
import string
import urllib
import urlparse

from contrib.product_spider import ProductsSpider

from lxml import etree

from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.items import Price, SiteProductItem
from product_ranking.spiders import FLOATING_POINT_RGEX, cond_set, \
    cond_set_value
from product_ranking.validation import BaseValidator

from scrapy import Request
from scrapy.contrib.linkextractors import LinkExtractor

from StringIO import StringIO


class BJSProductsSpider(BaseValidator, ProductsSpider):
    name = 'bjs_products'
    allowed_domains = ['bjs.com']
    SEARCH_URL = "http://www.bjs.com/webapp/wcs/stores/servlet/Search?" \
                 "catalogId=10201&storeId=10201&langId=-1&sortBy=&" \
                 "searchKeywords={search_term_upper}&state=all" \
                 "&currentPage={page_no}&clubId=00&" \
                 "originalSearchKeywords={search_term}&x=0&y=0"

    def start_requests(self):
        """Generate Requests from the SEARCH_URL and the search terms."""
        self.url_formatter.defaults['page_no'] = 1
        for st in self.searchterms:
            search_term, search_term_upper = self.generate_search_terms(st)
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=search_term,
                    search_term_upper=search_term_upper,
                ),
                meta={
                    'search_term': st,
                    'remaining': self.quantity,
                    'page': 1},
                dont_filter=True,
            )

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod}, dont_filter=True)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _scrape_total_matches(self, response):
        text_quantity = response.xpath(
            '//div[@id="catTab_1"]/input[@type="button"]/@value'
        ).extract()
        if not text_quantity:
            return 0
        int_quantity = int(re.findall(r'\d+', text_quantity[0])[0])
        return int_quantity

    def _scrape_next_results_page_link(self, response):
        prod_links = self._scrape_product_links(response)
        if not prod_links:
            return None
        current_page = response.meta['page']
        next_page = current_page + 1
        st = response.meta['search_term']
        search_term, search_term_upper = self.generate_search_terms(st)
        return Request(
            self.url_formatter.format(
                self.SEARCH_URL,
                search_term=search_term,
                search_term_upper=search_term_upper,
                page_no=next_page,
            ),
            meta={
                'search_term': st,
                'remaining': self.quantity,
                'page': next_page},)

    def generate_search_terms(self, st):
        search_term = urllib.quote_plus(st.encode('utf-8'))
        search_term_upper = search_term.upper()
        return search_term, search_term_upper

    def _scrape_product_links(self, response):
        link_extractor = LinkExtractor(
            restrict_xpaths='//div[@id="prodtitle"]')
        links = link_extractor.extract_links(response)
        links = [(l.url, SiteProductItem()) for l in links]
        return links

    def _scrape_results_per_page(self, response):
        prod_links = self._scrape_product_links(response)
        return len(prod_links)

    def _clean_empty_tags(self, html_tree):
        childs = html_tree.xpath("*")
        if not len(childs) and html_tree.text and not html_tree.text.strip():
            html_tree.getparent().remove(html_tree)
        if html_tree.text:
            html_tree.text = html_tree.text.strip()
        for child in childs:
            self._clean_empty_tags(child)

    def parse_product(self, response):
        product = response.meta.get('product', SiteProductItem())
        reqs = []
        cond_set(product,
                 'title',
                 response.xpath(
                     '//h1[@id="itemNameID"]/text()').extract(),
                 string.strip)

        # Title key must be present even if it is blank
        cond_set_value(product, 'title', '')

        # Price handling
        # this field may exist and contain full price if product have discount
        full_price = response.xpath(
            '//div[@class="price5"]/span/text()').extract()
        if full_price:
            try:
                full_price = re.findall(FLOATING_POINT_RGEX, full_price[1])
            except IndexError:
                full_price = response.xpath(
                    '//div[@class="price5"]/p/span/text()').extract()
                full_price = re.findall(FLOATING_POINT_RGEX, full_price[0])
            if full_price:
                product['price'] = Price(price=full_price[0],
                                         priceCurrency='USD')

        # this price may contain price with discount or original if discount
        # is not present
        string_price = response.xpath('//div[@class="price4"]/p/span/text() |'
                                      '//div[@class="price4"]/span/text()'
                                      ).extract()
        if string_price:
            price_value = re.findall(FLOATING_POINT_RGEX, string_price[0])
            if price_value:
                price_obj = Price(price=price_value[0], priceCurrency='USD')
                if full_price:
                    product['price_with_discount'] = price_obj
                else:
                    product['price'] = price_obj

        description = response.xpath('//div[@id="tab-1"]').extract()
        if description:
            parser = etree.HTMLParser()
            tree = etree.parse(StringIO(description[0]), parser)
            if tree:
                self._clean_empty_tags(tree.xpath('*')[0])
                if tree.xpath('//body/*'):
                    description_clened = etree.tostring(
                        tree.xpath('//body/*')[0])
                    # Description
                    cond_set_value(product, 'description', description_clened)

        # Image
        image_list = response.xpath('//img[@id="productImage"]/@src').extract()
        if image_list:
            image_url = image_list[0]
            # this required to get image with max resolution
            parsed_url = urlparse.urlparse(image_url)
            parsed_query = urlparse.parse_qs(parsed_url.query)
            parsed_query.pop('recipeName', None)
            new_query = urllib.urlencode(parsed_query, doseq=True)
            url_parts = list(parsed_url)
            url_parts[4] = new_query
            image_url = urlparse.urlunparse(url_parts)
            cond_set_value(product, 'image_url', image_url)
        cond_set_value(product, 'locale', 'en_US')

        # Model
        models_list = re.findall(r'Model: (.*)', response.body)
        if not models_list:
            # for some products we can find model only from description
            models_list = re.findall(r'\(Model (.*)\)<', response.body)
        cond_set(product, 'model', models_list, string.strip)

        # Category
        category_path = filter(None, map((lambda x: x.strip()),
            response.xpath('//li[@id="pagepath"]//a/text()').extract()))

        if category_path:
            category = category_path[-1]
            cond_set_value(product, 'category', category)

        cond_set_value(product, 'categories', category_path)

        # Available Online: 1 or 0 (1 = yes, 0 = no)
        online_not_avail = response.xpath('//div[@id="onlineItemNotAvail"]')
        product['available_online'] = 1 if not online_not_avail else 0

        # Available In-club(store): 1 or 0 (1 = yes, 0 = no)
        club_avail = response.xpath('//div[@class="avail"]')
        product['available_store'] = 1 if club_avail else 0

        if str(product.get('available_online', None)) == '0' and str(product.get('available_store', None)) == '0':
            product['is_out_of_stock'] = True

        # Shipping & Handling Included: 1 or 0 (1 = yes, 0 = no)
        shipping_included = response.xpath('//div[@id="freeShipping"]/p')
        product['shipping_included'] = 1 if shipping_included else 0

        # Out of stock
        out_stock_text = response.xpath(
            '//span[@id="clubInvStatus_0"]/text()').extract()
        if out_stock_text and 'out of' in out_stock_text[0].lower():
            cond_set_value(product, 'is_out_of_stock', True)
        else:
            cond_set_value(product, 'is_out_of_stock', False)

        # Guessing brand
        brand = guess_brand_from_first_words(
            product['title'].replace(u'®', ''))
        cond_set_value(product, 'brand', brand)

        # is_out_of_stock
        oos = response.xpath('//*[@id="stockinfo"]//text()').re('Out Of Stock')
        product['is_out_of_stock'] = True if oos else False

        # buyer_reviews
        avg_review = response.xpath(
            '//*[@class="pr-rating pr-rounded average"]/text()').extract()
        num_of_reviews = response.xpath(
            '//*[@class="pr-snapshot-rating rating"]'
            '//*[@class="count"]/text()').extract()

        num_of_reviews = num_of_reviews[0] if num_of_reviews else 0

        product['buyer_reviews'] = {
            'num_of_reviews': num_of_reviews,
            'average_rating': avg_review[0] if avg_review else 0.0,
            'rating_by_star': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        }

        # To Do: Discover the values of P1 and P2 for each product
        if num_of_reviews:
            part_number = response.xpath(
                '//*[@id="partNumber"]/@value').extract()[0]
            review_url_part = self.get_review_url_part(part_number)
            review_url = "http://www.bjs.com/pwr/content/" \
                "%s/%s-en_US-meta.js" % (review_url_part, part_number)

            reqs.append(Request(review_url,
                                self._parse_reviews,
                                meta={'product': product, 'reqs': reqs}))

        last_buyer_review_date = response.xpath(
            '(//*[@class="pr-review-author-date pr-rounded"]'
            '/text())[1]').extract()
        if last_buyer_review_date:
            product['last_buyer_review_date'] = last_buyer_review_date[0]

        # not longer available
        no_longer_available = response.xpath(
            '//*[@class="ProdInact_ErrTxt" and'
            ' contains(text(),"item is no longer available")]')
        product['no_longer_available'] = 1 if no_longer_available else 0

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

    def _parse_reviews(self, response):
        product = response.meta['product']
        reqs = response.meta.get('reqs', [])
        rating_by_star = product['buyer_reviews']['rating_by_star']
        for vote in re.findall('rating:(\d),', response.body):
            rating_by_star[vote] = rating_by_star[vote] + 1

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    @staticmethod
    def get_review_url_part(product_model):
        """This method was created as copy of javascript function g(c4) from
        full.js. It will generate numerical part of url for reviews.
        example: 06/54 for url
        http://www.bjs.com/pwr/content/06/54/P_159308793-en_US-meta.js

        I use the same variables names as in js, but feel free to change them
        """
        c4 = product_model
        c3 = 0
        for letter in c4:
            c7 = ord(letter)
            c7 = c7 * abs(255 - c7)
            c3 += c7

        c3 = c3 % 1023
        c3 = str(c3)

        cz = 4
        c6 = list(c3)

        c2 = 0
        while c2 < (cz - len(c3)):
            c2 += 1
            c6.insert(0, "0")

        c3 = ''.join(c6)
        c3 = c3[0: 2] + '/' + c3[2: 4]
        return c3
