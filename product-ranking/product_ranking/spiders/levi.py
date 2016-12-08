from __future__ import division, absolute_import, unicode_literals

import json
import re

from scrapy import Request

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value
from product_ranking.validation import BaseValidator
from product_ranking.br_bazaarvoice_api_script import BuyerReviewsBazaarApi
from scrapy import Selector
from spiders_shared_code.levi_variants import LeviVariants
from product_ranking.validators.levi_validator import LeviValidatorSettings

is_empty =lambda x,y=None: x[0] if x else y

def is_num(s):
    try:
        int(s.strip())
        return True
    except ValueError:
        return False


class LeviProductsSpider(BaseValidator, BaseProductsSpider):
    name = 'levi_products'
    allowed_domains = ["levi.com", "www.levi.com"]
    start_urls = []

    settings = LeviValidatorSettings

    SEARCH_URL = "http://www.levi.com/US/en_US/search?Ntt={search_term}"  # TODO: ordering

    PAGINATE_URL = ('http://www.levi.com/US/en_US/includes/searchResultsScroll/?nao={nao}'
                    '&url=%2FUS%2Fen_US%2Fsearch%3FD%3D{search_term}%26Dx'
                    '%3Dmode%2Bmatchall%26N%3D4294960840%2B4294961101%2B4294965619%26Ntk'
                    '%3DAll%26Ntt%3Ddress%26Ntx%3Dmode%2Bmatchall')

    CURRENT_NAO = 0
    PAGINATE_BY = 12  # 12 products
    TOTAL_MATCHES = None  # for pagination

    REVIEW_URL = "http://levistrauss.ugc.bazaarvoice.com/9090-en_us/" \
                 "{product_id}/reviews.djs?format=embeddedhtml&page={index}&"

    RELATED_PRODUCT = "http://www.res-x.com/ws/r2/Resonance.aspx?" \
                      "appid=levi01&tk=811541814822703" \
                      "&ss=544367773691192" \
                      "&sg=1&" \
                      "&vr=5.3x&bx=true" \
                      "&sc=product4_rr" \
                      "&sc=product3_rr" \
                      "&sc=product1_r" \
                      "r&sc=product2_rr" \
                      "&ev=product&ei={product_id}" \
                      "&no=20" \
                      "&language=en_US" \
                      "&cb=certonaResx.showResponse" \
                      "&ur=http%3A%2F%2Fwww.levi.com%2FUS%2Fen_US%" \
                      "2Fwomens-jeans%2Fp%2F095450043&plk=&"

    handle_httpstatus_list = [404]

    use_proxies = True

    def __init__(self, *args, **kwargs):
        self.br = BuyerReviewsBazaarApi(called_class=self)

        super(LeviProductsSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product(self, response):
        product = response.meta.get('product', SiteProductItem())

        if response.status == 404 or 'This product is no longer available' in response.body_as_unicode() \
                or "www.levi.com/US/en_US/error" in response.url:
            product.update({"not_found": True})
            product.update({"no_longer_available": True})
            return product

        reqs = []

        # product id
        self.product_id = is_empty(response.xpath('//meta[@itemprop="model"]/@content').extract())

        # product data in json
        self.js_data = self.parse_data(response)

        # Parse locate
        locale = 'en_US'
        cond_set_value(product, 'locale', locale)

        # Parse model
        cond_set_value(product, 'model', self.product_id)

        # Parse title
        title = self.parse_title(response)
        cond_set(product, 'title', title)

        # Parse image
        image = self.parse_image(response)
        cond_set_value(product, 'image_url', image)

        # Parse brand
        brand = self.parse_brand(response)
        cond_set_value(product, 'brand', brand)

        # Parse upc
        upc = self.parse_upc(response)
        cond_set_value(product, 'upc', upc)

        # Parse sku
        sku = self.parse_sku(response)
        cond_set_value(product, 'sku', sku)

        # Parse description
        description = self.parse_description(response)
        cond_set_value(product, 'description', description)

        # Parse price
        price = self.parse_price(response)
        cond_set_value(product, 'price', price)

        try:
            variants = self._parse_variants(response)
        except KeyError:
            product['not_found'] = True
            return product

        product['variants'] = variants

        response.meta['marks'] = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
        real_count = is_empty(re.findall(r'<span itemprop="reviewCount">(\d+)<\/span>',
                                response.body_as_unicode()))
        if real_count:
            # Parse buyer reviews
            if int(real_count) > 8:
                for index, i in enumerate(xrange(9, int(real_count) + 1, 30)):
                    reqs.append(
                        Request(
                            url=self.REVIEW_URL.format(product_id=self.product_id, index=index+2),
                            dont_filter=True,
                            callback=self.parse_buyer_reviews
                        )
            )

        reqs.append(
            Request(
                url=self.REVIEW_URL.format(product_id=self.product_id, index=0),
                dont_filter=True,
                callback=self.parse_buyer_reviews
            ))

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def _parse_variants(self, response):
        """
        Parses product variants.
        """
        lv = LeviVariants()
        lv.setupSC(response)
        variants = lv._variants()

        return variants

    def parse_buyer_reviews(self, response):
        meta = response.meta.copy()
        buyer_reviews_per_page = self.br.parse_buyer_reviews_per_page(response)

        for k, v in buyer_reviews_per_page['rating_by_star'].iteritems():
            response.meta['marks'][k] += v

        product = response.meta['product']
        reqs = meta.get('reqs')

        product['buyer_reviews'] = BuyerReviews(
            num_of_reviews=buyer_reviews_per_page['num_of_reviews'],
            average_rating=buyer_reviews_per_page['average_rating'],
            rating_by_star=response.meta['marks']
            )
        if reqs:
            reqs.append(
                Request(
                    url=self.RELATED_PRODUCT.format(product_id=self.product_id, index=0),
                    dont_filter=True,
                    callback=self.parse_related_product
                ))

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

    def parse_brand(self, response):
        brand = is_empty(response.xpath(
            '//meta[@itemprop="brand"]/@content').extract())

        return brand

    def parse_title(self, response):
        title = response.xpath(
                '//meta[contains(@property, "og:title")]/@content').extract()
        if title:
            title = [title[0].replace('&trade;', '').replace('\u2122', '')]
        else:
            title = response.xpath(
                '//h1[contains(@class, "title")]/text()').extract()
        return title

    def parse_data(self, response):
        data = re.findall(r'var buyStackJSON = \'(.+)\'; ', response.body_as_unicode())
        if data:
            data = re.sub(r'\\(.)', r'\g<1>', data[0])
            try:
                js_data = json.loads(data)
            except:
                return
            return js_data

    def parse_image(self, response):
        if self.js_data:
            try:
                image = self.js_data['colorid'][self.product_id]['gridUrl']
            except:
                return

            return image

    def parse_related_product(self, response):
        related_prods = []
        product = response.meta['product']
        sample = response.body_as_unicode()
        try:
            sample = sample.replace(u'certonaResx.showResponse(', '')
            sample = sample[:-2]
            data = json.loads(sample)
            html = data['Resonance']['Response'][2]['output']
        except Exception as e:
            self.log('Error during parsing related products page: {}'.format(e))
            return product
        else:
            s = Selector(text=html)
            titles = s.xpath('//h4/text()').extract()  # Title
            urls = s.xpath('//img/@src').extract()  # Img url
            for title, url in zip(titles, urls):
                if url and title:
                    related_prods.append(
                                RelatedProduct(
                                    title=title,
                                    url=url
                                )
                            )
            product['related_products'] = {}
            if related_prods:
                product['related_products']['buyers_also_bought'] = related_prods
            return product

    def parse_description(self, response):
        if self.js_data:
            try:
                description = self.js_data['colorid'][self.product_id]['name']
            except:
                return
            return description

    def parse_upc(self, response):
        if self.js_data:
            for v in self.js_data['sku'].values():
                upc = v['upc']
            upc = upc[-12:]

            return upc

    def parse_sku(self, response):
        if self.js_data:
            for v in self.js_data['sku'].values():
                skuid = v['skuid']

            return skuid

    def parse_price(self, response):
        if self.js_data:
            price = self.js_data['colorid'][self.product_id]['price']
            for price_data in price:
                if price_data['il8n'] == 'now':
                    price = price_data['amount']
            currency = is_empty(re.findall(r'currency":"(\w+)"', response.body_as_unicode()))

            if price and currency:
                price = Price(price=price, priceCurrency=currency)
            else:
                price = Price(price=0.00, priceCurrency="USD")

            return price

    def _scrape_total_matches(self, response):
        totals = response.css('.productCount ::text').extract()
        if totals:
            totals = totals[0].replace(',', '').replace('.', '').strip()
            if totals.isdigit():
                if not self.TOTAL_MATCHES:
                    self.TOTAL_MATCHES = int(totals)
                return int(totals)

    def _scrape_product_links(self, response):
        for link in response.xpath(
            '//li[contains(@class, "product-tile")]'
            '//a[contains(@rel, "product")]/@href'
        ).extract():
            yield link, SiteProductItem()

    def _get_nao(self, url):
        nao = re.search(r'nao=(\d+)', url)
        if not nao:
            return
        return int(nao.group(1))

    def _replace_nao(self, url, new_nao):
        current_nao = self._get_nao(url)
        if current_nao:
            return re.sub(r'nao=\d+', 'nao='+str(new_nao), url)
        else:
            return url+'&nao='+str(new_nao)

    def _scrape_next_results_page_link(self, response):
        if self.TOTAL_MATCHES is None:
            self.log('No "next result page" link!')
            return
        if self.CURRENT_NAO > self.TOTAL_MATCHES+self.PAGINATE_BY:
            return  # it's over
        self.CURRENT_NAO += self.PAGINATE_BY
        return Request(
            self.PAGINATE_URL.format(
                search_term=response.meta['search_term'],
                nao=str(self.CURRENT_NAO)),
            callback=self.parse, meta=response.meta
        )

