import itertools
import re
import string
import urllib
import json

from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from product_ranking.items import Price, SiteProductItem
from product_ranking.spiders import cond_set_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider
from scrapy import Request


def dict_product(dicts):
    products = itertools.product(*dicts.itervalues())
    return (dict(itertools.izip(dicts, x)) for x in products)


class PetcoProductsSpider(ProductsSpider):
    name = 'petco_products'
    allowed_domains = ['petco.com']

    SEARCH_URL = ("http://www.petco.com/shop/SearchDisplay?categoryId=&storeId"
                  "=10151&catalogId=10051&langId=-1&sType=SimpleSearch&"
                  "resultCatEntryType=2&showResultsPage=true&searchSource=Q&"
                  "pageView=&beginIndex=0&pageSize=48&fromPageValue=search"
                  "&searchTerm={search_term}")

    SEARCH_URL_2 = ("http://www.petco.com/shop/ProductListingView?searchType="
                    "12&filterTerm=&langId=-1&advancedSearch=&sType=Simple"
                    "Search&resultCatEntryType=2&catalogId=10051&searchTerm="
                    "{search_term}&resultsPerPage=48&emsName=&facet=&category"
                    "Id=&storeId=10151&beginIndex={begin_index}")

    REVIEW_URL = ("http://api.bazaarvoice.com/data/products.json?"
                  "passkey=dpaqzblnfzrludzy2s7v27ehz&apiversion=5.5"
                  "&filter=id:{product_id}&stats=reviews")

    PRICE_URL = "http://www.petco.com/shop/GetCatalogEntryDetailsByIDView"

    def __init__(self, *args, **kwargs):
        super(PetcoProductsSpider, self).__init__(*args, **kwargs)
        self.br = BuyerReviewsBazaarApi(called_class=self)
        self.product_last_page = 0

    def parse_buyer_reviews(self, response):
        meta = response.meta.copy()
        product = response.meta['product']
        reqs = meta.get('reqs', [])

        product['buyer_reviews'] = self.br.parse_buyer_reviews_products_json(
            response)

        if reqs:
            return self.send_next_request(reqs, response)
        else:
            return product

    def _total_matches_from_html(self, response):
        total = response.xpath(
            '//*[contains(@id,"searchTotalCount")]/text()').re('\d+')
        return int(total[0].replace(',', '')) if total else 0

    def _scrape_results_per_page(self, response):
        return 48

    def _scrape_next_results_page_link(self, response):
        # End of pagination
        if not self.product_last_page:
            return None

        begin_index = int(re.search('beginIndex=(\d+)', response.url).group(1))
        num_poduct_page = self._scrape_results_per_page(response)
        st = response.meta['search_term']
        url = self.url_formatter.format(self.SEARCH_URL_2,
                                        search_term=urllib.quote_plus(
                                            st.encode('utf-8')),
                                        begin_index=str(
                                            begin_index + num_poduct_page))
        return url

    def _scrape_product_links(self, response):
        item_urls = response.xpath(
            '//*[@class="product-display-grid"]'
            '//*[@class="product-name"]/a/@href').extract()

        self.product_last_page = len(item_urls)
        for item_url in item_urls:
            yield item_url, SiteProductItem()

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _parse_title(self, response):
        title = response.xpath('//h1/text()').extract()
        return title[0].strip() if title else None

    def _parse_categories(self, response):
        categories = response.css('.breadcrumb a::text').extract()
        return categories if categories else None

    def _parse_category(self, response):
        categories = self._parse_categories(response)
        return categories[-1] if categories else None

    def _parse_image_url(self, response):
        image_url = response.xpath(
            '//*[@property="og:image"]/@content').extract()
        return image_url[0] if image_url else None

    def _parse_brand(self, response):
        brand = response.xpath(
            '//*[@class="product-brand"]/a/text()').re('by.(.*)')

        return brand[0].strip() if brand else None

    def _parse_sku(self, response):
        sku = response.xpath("//input[@id='primarySku']/@value").extract()
        if len(sku[0]) < 1:
            sku = response.css(
                '.product-sku::text').re(u'SKU:.(\d+)')

        return sku[0] if sku else None

    def _parse_variants(self, response):
        variants = []

        try:
            variants_info = json.loads(response.xpath('//*[contains(@id,"entitledItem_")]/text()').extract()[0])
        except:
            variants_info = {}

        for attr_value in variants_info:
            attributes = {}
            variant_attribute = attr_value["Attributes"]
            attributes['price'] = attr_value["RepeatDeliveryPrice"]["price"]
            attributes['image_url'] = attr_value["ItemImage"]
            if variant_attribute:
                attr_text = attr_value["Attributes"].keys()[0].split('_')
                attributes[attr_text[0]] = attr_text[1]

            variants.append(attributes)

        return variants if variants else None

    def _parse_is_out_of_stock(self, response):
        status = response.xpath(
            '//*[@itemprop="availability" and @content="in_stock"]')
        return not bool(status)

    def _parse_shipping_included(self, response):
        pass

    def _parse_description(self, response):
        description = response.xpath(
            '//*[@id="description"]').extract()

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

        # Reseller_id
        cond_set_value(product, 'reseller_id', sku)

        # Brand
        brand = self._parse_brand(response)
        cond_set_value(product, 'brand', brand)

        product_id = response.xpath(
            '//*[@id="productPartNo"]/@value').extract()

        if product_id:
            reqs.append(
                Request(
                    url=self.REVIEW_URL.format(
                        product_id=product_id[0], index=0),
                    dont_filter=True,
                    callback=self.parse_buyer_reviews,
                    meta=response.meta
                ))

        price_id = response.xpath(
            '//*[contains(@id,"entitledItem_")]/@id').re(
            'entitledItem_(\d+)')

        cat_id = response.xpath('//script/text()').re(
            'productDisplayJS.displayAttributeInfo\("(\d+)","(\d+)"')

        if not cat_id:
            cat_id = response.xpath(
                '//*[@name="firstAvailableSkuCatentryId_avl"]/@value').extract()

        if price_id and cat_id:
            text = ("storeId=10151&langId=-1&catalogId=10051&"
                    "catalogEntryId={cat}&productId={prod_id}".format(cat=cat_id[0],
                                                                      prod_id=price_id[0]))
            reqs.append(
                Request(self.PRICE_URL,
                        body=text,
                        headers={'Content-Type': 'application/x-www-form-urlencoded',
                                 'X-Requested-With': 'XMLHttpRequest'},
                        method='POST',
                        meta=response.meta,
                        callback=self._parse_price,
                        dont_filter=True)
            )

        else:
            prices = map(float, response.xpath(
                '//*[@class="product-price"]//span/text()').re('\$([\d\.]+)'))
            product['price'] = Price(price=min(prices), priceCurrency="USD")

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_price(self, response):
        reqs = response.meta.get('reqs', [])
        product = response.meta['product']

        raw_information = re.findall(
            '\{.*\}', response.body, re.MULTILINE | re.DOTALL)[0]

        product_data = eval(raw_information)
        price = product_data["catalogEntry"]["offerPrice"]
        product['price'] = Price(price=price, priceCurrency="USD")

        if reqs:
            return self.send_next_request(reqs, response)

        return product
