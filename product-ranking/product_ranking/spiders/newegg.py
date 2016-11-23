# -*- coding: utf-8 -*-#

import json
import re
import itertools
import math
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.log import INFO
from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider, cond_set_value
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.settings import ZERO_REVIEWS_VALUE

is_empty = lambda x, y=None: x[0] if x else y


class NeweggProductSpider(BaseProductsSpider):
    name = 'newegg_products'
    allowed_domains = ["www.newegg.com"]

    TOTAL_MATCHES = None
    CURRENT_NAO = 0
    PAGINATE_BY = 30
    TOTAL_PAGE = 0

    SEARCH_URL = "http://www.newegg.com/Product/ProductList.aspx" \
                 "?Submit=ENE&DEPA=0&Order=BESTMATCH" \
                 "&Description={search_term}&N=-1&isNodeId=1"

    PAGINATE_URL = 'http://www.newegg.com/Product/ProductList.aspx?' \
                   'Submit=ENE&DEPA=0&Order=BESTMATCH&Description={search_term}' \
                   '&N=-1&isNodeId=1&Page={index}'

    MARKETPLACE_URL = 'http://www.newegg.com/LandingPage/' \
                      'ItemInfo4ProductDetail2015.aspx?Item={product_id}&v2=2012'

    RELATED_PRODUCTS = 'http://content.newegg.com/Common/Ajax/' \
                       'RelationItemInfo2015.aspx?type=Seller' \
                       '&item={product_id}&v2=2012' \
                       '&parentItem={seller_id}' \
                       '&action=Biz.Product.ItemRelationInfoManager.JsonpCallBack'

    PRICE_IN_CARD_URL = 'http://www.newegg.com/Product/MappingPrice2012.aspx?Item={SellerItem}'

    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)
        self.index = 1
        self.error_pagin = 0
        self.pages_pagin = []
        self.count_pagin_page = 0
        self.count_pagin_links = 0
        super(NeweggProductSpider, self).__init__(*args, **kwargs)

    def parse_product(self, response):
        reqs = []
        meta = response.meta
        product = meta['product']

        product_id = is_empty(response.xpath('//script[contains(text(), "product_id")]').re(r"product_id:\['(.*)']"))
        meta['product_id'] = product_id

        seller_list_id = response.xpath('//table[@class="gridSellerList"]/tbody/script[2]/text()').re(
            r'SellerList\["(\d+\-?\d+\-?\d+)"]')
        if seller_list_id:
            meta['seller_id'] = seller_list_id[-1]

        # Set locale
        product['locale'] = 'en_US'

        # Parse title
        title = self.parse_title(response)
        cond_set_value(product, 'title', title)

        # Parse brand
        brand = self.parse_brand(response)
        cond_set_value(product, 'brand', brand)

        # Parse model
        model = self.parse_model(response)
        cond_set_value(product, 'model', model)

        # Parse price
        price = self.parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse image url
        image_url = self.parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Parse description
        description = self.parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse stock status
        is_out_of_stock = self.parse_stock_status(response)
        cond_set_value(product, 'is_out_of_stock', is_out_of_stock)

        # Parse variants
        variants = self.parse_variant(response)
        cond_set_value(product, 'variants', variants)

        # Parse review
        review = self.parse_buyer_review(response)
        cond_set_value(product, 'buyer_reviews', review)

        # Parse buyer marketplace
        reqs.append(
            Request(
                url=self.MARKETPLACE_URL.format(product_id=product_id),
                dont_filter=True,
                callback=self.parse_marketplace_json,
                meta=meta
            )
        )

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def remove_duplicate(self, full_list):
        new_list = []
        for item in full_list:
            if not item in new_list:
                new_list.append(item)
        return new_list

    def parse_variant(self, response):
        variants = []

        vars = is_empty(response.xpath(
            '//script[contains(text(), "Biz.Product.GroupItemSwitcher")]').extract())
        try:
            properties_vars = re.findall(r'properties:(\[.*\]\}])', vars)
            availableMap = re.findall(r'availableMap:(\[.*\]\}])', vars)
            if properties_vars:
                data = json.loads(properties_vars[0])
            else:
                return
            price_js = json.loads(availableMap[0])
        except Exception as e:
            print e

        all = list()
        for group in data:
            group_variants = list()
            for prop in group['data']:
                if prop['displayInfo']:
                    group_variants.append([prop['description'], prop['value'], group['name'], group['description']])
            if group_variants:
                all.append(group_variants)
        result = list(itertools.product(*all))

        price_all = list()
        for group in price_js:
            group_variants = list()
            for prop in group['map']:
                group_variants.append(prop['value'])
                group_variants.append(prop['name'])
            group_variants.append(group['info']['price'])
            price_all.append(group_variants)
        for r in result:
            id_result = []
            properties = {}
            variant = {}
            for item in r:
                id_result.append(item[1])
                id_result.append(item[2])
                properties[str(item[3])] = item[0]
            for price_item in price_all:
                rez = list(set(id_result) - set(price_item))
                if not rez:
                    price = price_item[-1]
                    in_stock = True
                    break
                else:
                    price = None
                    in_stock = False

            if price:
                variant['price'] = price
            else:
                variant['price'] = None
            if str(variant.get('price', '')) == '999999':
                variant['price'] = None  # price available in cart only
            variant['in_stock'] = in_stock
            variant['properties'] = properties
            variants.append(variant)

        return variants

    def parse_marketplace_json(self, response):
        marketplaces = []
        meta = response.meta
        product = meta['product']
        data = response.body_as_unicode()
        seller_id = meta.get('seller_id')
        product_id = meta.get('product_id')
        try:
            data = is_empty(re.findall(r'parentItem":"{0}"(.*)?'.format(seller_id), data)).replace('\\', '')
            marketplace = Selector(text=data)
        except:
            return product

        sellers_noline = list(set(marketplace.xpath("//tr[contains(@class, featured)]/td/img/@alt").extract()))
        sellers_line = marketplace.xpath("//tr/td[@class='seller']/a[1]/@title").extract()
        new_sellers_line = self.remove_duplicate(sellers_line)
        sellers = sellers_noline + new_sellers_line
        price_int = marketplace.xpath(
            "//ul[contains(@class, 'price')]/li[@class='price-current ']/strong/text()").extract()
        price_sup = marketplace.xpath(
            "//ul[contains(@class, 'price')]/li[@class='price-current ']/sup/text()").extract()
        for i, item in enumerate(sellers):
            try:
                price = price_int[i] + price_sup[i]
            except:
                price = 0.0
            if price:
                price = Price(price=price, priceCurrency="USD")
            else:
                price = Price(price=0.0, priceCurrency="USD")
            marketplaces.append({
                "price": price,
                "name": item
            })

            if marketplaces:
                product["marketplace"] = marketplaces

        reqs = meta.get('reqs', [])
        reqs.append(
            Request(
                url=self.RELATED_PRODUCTS.format(product_id=product_id, seller_id=seller_id),
                dont_filter=True,
                callback=self.parse_related_product,
                meta=meta
            ))

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def parse_related_product(self, response):
        meta = response.meta
        product = meta['product']
        related_products = {
            'customers_also_bought': [],
            'recommended': []
        }
        data = response.body_as_unicode().replace('\\', '')
        if data:
            sel = Selector(text=data)

            # Customers Also Bought
            customers_products = sel.xpath('//div[contains(@class, "descSideSell")]')
            for item in customers_products:
                title = is_empty(item.xpath('a/text()').extract())
                url = is_empty(item.xpath('a/@href').extract())
                if title and url:
                    prod = RelatedProduct(url=url, title=title)
                    related_products['customers_also_bought'].append(prod)

            customers_products = sel.xpath('//div[contains(@class,"imgSideSell")]/img')
            for item in customers_products:
                title = is_empty(item.xpath('@title').extract())
                url = is_empty(item.xpath('@src').extract())
                if title and url:
                    prod = RelatedProduct(url=url, title=title)
                    related_products['customers_also_bought'].append(prod)

            # Recommended
            recommended_products = sel.xpath('//div[contains(@class, "wrap_description")]')
            for item in recommended_products:
                title = is_empty(item.xpath('a/span/text()').extract())
                url = is_empty(item.xpath('a/@href').extract())
                if title and url:
                    prod = RelatedProduct(url=url, title=title)
                    related_products['recommended'].append(prod)

            if related_products:
                product['related_products'] = related_products

        return product

    def parse_price(self, response):
        price = is_empty(response.xpath('//script[contains(text(), "product_instock")]/text()').re(
            r"product_sale_price:\['(\d+\.?\d+)']"))

        currency = is_empty(
            response.xpath('//script[contains(text(), "product_instock")]/text()').re(r"site_currency:'(\w+)'"))

        if not price:
            price = is_empty(response.xpath('//script[contains(text(), "product_instock")]/text()').re(
                r"product_unit_price:\['(\d+\.?\d+)']"))
        if price and currency:
            price = Price(price=price, priceCurrency=currency)
        else:
            price = Price(price=0.0, priceCurrency='USD')

        return price

    def parse_buyer_review(self, response):
        num_of_review = is_empty(response.xpath('//*[@id="linkSumRangeAll"]/span//text()').re(r'\d+'))
        res = []
        rating_by_star = {}
        for i in range(1, 6):
            rvm = response.xpath('//span[@id="reviewNumber%s"]//text()' % i).extract()
            if len(rvm) > 0 and (rvm[0]) > 0:
                res.append([i, (rvm[0])])
        if len(res) > 0:
            for item in res:
                rating_by_star[item[0]] = item[1]
        if rating_by_star:
            s = n = 0
            for k, v in rating_by_star.iteritems():
                s += int(k) * int(v)
                n += int(v)
            if n > 0:
                average_rating = round(s / float(n), 2)
        try:
            buyer_reviws = {'num_of_reviews': int(num_of_review),
                            'average_rating': float(average_rating),
                            'rating_by_star': rating_by_star}
        except:
            return ZERO_REVIEWS_VALUE

        return buyer_reviws

    def parse_stock_status(self, response):
        stock_status = response.xpath('//script[contains(text(), "product_instock")]/text()').re(
            r"product_instock:\['(\d+)']")

        if stock_status[0] == '1':
            in_stock = True
        elif stock_status[0] == '0':
            in_stock = False

        return in_stock

    def parse_description(self, response):
        description = response.xpath('//div[@class="grpBullet"]').extract()
        description = [i.strip() for i in description]
        if description:
            return description

    def parse_title(self, response):
        title = is_empty(response.xpath('//h1/span[@itemprop="name"]/text()').extract())

        if title:
            return title

    def parse_brand(self, response):
        brand = is_empty(response.xpath('//dl/dt[contains(text(), "Brand")]/following-sibling::*/text()').extract())

        if brand:
            return brand

    def parse_model(self, response):
        model = is_empty(response.xpath('//dl/dt[contains(text(), "Model")]/following-sibling::*/text()').extract())

        if model:
            return model

    def parse_image_url(self, response):
        image = is_empty(response.xpath('//div[@class="objImages"]/'
                                        'a[@name="gallery"]/'
                                        'span[@class="mainSlide"]'
                                        '/img/@src').extract())

        if image:
            return image

        return None

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
            response.xpath(
                '//div[@class="recordCount"]/span[@id="RecordCount_1"]/text()').extract())
        if total_matches:
            if total_matches.isdigit():
                if not self.TOTAL_MATCHES:
                    self.TOTAL_MATCHES = int(total_matches)
                    self.TOTAL_PAGE = int(math.ceil(self.TOTAL_MATCHES / self.PAGINATE_BY)) + 1
        return int(total_matches)

    def _scrape_results_per_page(self, response):
        """
        Number of results on page
        """
        links = response.xpath(
            '//div[@class="itemCell itemCell-ProductList itemCell-ProductGridList"]/'
            'div[@class="itemText"]/div/a/@href'
        ).extract()
        if links:
            per_page = int(len(links))
            if per_page:
                return per_page
        return 0

    def _scrape_product_links(self, response):
        """
        Scraping product links from search page
        """
        links = response.xpath(
            '//div[@class="itemCell itemCell-ProductList itemCell-ProductGridList"]/'
            'div[@class="itemText"]/div/a/@href'
        ).extract()

        if links:
            for link in links:
                yield link, SiteProductItem()
        else:
            self.log("Found no product links in {url}".format(url=response.url), INFO)

    def _scrape_next_results_page_link(self, response):
        self.index += 1
        if self.index <= self.TOTAL_PAGE:
            return self.PAGINATE_URL.format(
                search_term=response.meta['search_term'],
                index=self.index,
                meta=response.meta.copy(),
            )
