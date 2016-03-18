# -*- coding: utf-8 -*-

import urllib
import string
import urlparse
import json
import re

import requests
from scrapy.log import INFO
from scrapy import Request
from scrapy import Selector
from scrapy.selector import HtmlXPathSelector

from product_ranking.items import SiteProductItem, RelatedProduct, \
    Price, BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import cond_set, cond_set_value, \
    FLOATING_POINT_RGEX, cond_replace
from contrib.product_spider import ProductsSpider
from product_ranking.validation import BaseValidator
from product_ranking.guess_brand import guess_brand_from_first_words
from spiders_shared_code.macys_variants import MacysVariants
from product_ranking.validators.macys_validator import MacysValidatorSettings


class MacysProductsSpider(BaseValidator, ProductsSpider):
    name = 'macys_products'
    allowed_domains = ['macys.com']
    SEARCH_URL = "http://www1.macys.com/shop/search?keyword={search_term}" \
                 "&x=0&y=0&sortBy={sort_mode}&pageIndex={page}"

    user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64)) " \
        "AppleWebKit/537.36 (KHTML, like Gecko) " \
        "Chrome/37.0.2062.120 Safari/537.36"

    SORT_MODES = {
        'default': 'ORIGINAL',
        'featured': 'ORIGINAL',
        'price_asc': 'PRICE_LOW_TO_HIGH',
        'price_desc': 'PRICE_HIGH_TO_LOW',
        'rating': 'TOP_RATED',
        'best_sellers': 'BEST_SELLERS',
        'new': 'NEW_ITEMS'
    }

    REQUIRE_PRODUCT_PAGE = False

    settings = MacysValidatorSettings

    def __init__(self, sort_mode='default', *args, **kwargs):
        super(MacysProductsSpider, self).__init__(*args, **kwargs)
        self.sort_mode = self.SORT_MODES.get(sort_mode, 'ORIGINAL')

    def start_requests(self):  # Stolen from walmart
        """Generate Requests from the SEARCH_URL and the search terms."""
        self.url_formatter.defaults['page'] = 1
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8')),
                    sort_mode=self.sort_mode
                ),
                meta={
                    'search_term': st, 'remaining': self.quantity,
                    # 'dont_redirect': True, 'handle_httpstatus_list': [302],
                    'page': 1,
                    },
                headers={"User-Agent": self.user_agent},
                dont_filter=True,
                cookies={'shippingCountry': 'US', 'currency': 'USD'}
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

    def parse(self, response):  # Stolen again
        if response.status == 302:
            yield self._create_from_redirect(response)
        else:
            for item in super(MacysProductsSpider, self).parse(response):
                if isinstance(item, Request):
                    item.meta['dont_redirect'] = True
                    item.meta['handle_httpstatus_list'] = [302]
                yield item

    def _create_from_redirect(self, response):  # Thanks walmart
        # Create comparable URL tuples.
        redirect_url = response.url
        redirect_url_split = urlparse.urlsplit(redirect_url)
        redirect_url_split = redirect_url_split._replace(
            query=urlparse.parse_qs(redirect_url_split.query))
        original_url_split = urlparse.urlsplit(response.request.url)
        original_url_split = original_url_split._replace(
            query=urlparse.parse_qs(original_url_split.query))

        if redirect_url_split == original_url_split:
            self.log("Found identical redirect!", INFO)
            request = response.request.replace(dont_filter=True)
        else:
            self.log("Found legit redirect!", INFO)
            request = response.request.replace(url=redirect_url)
        request.meta['dont_redirect'] = True
        request.meta['handle_httpstatus_list'] = [302]
        return request

    def _scrape_total_matches(self, response):
        try:
            path = '#productCount::text'
            return int(response.css(path).extract()[0].strip())
        except (ValueError, IndexError):
            return 0

    def _populate_from_box(self, response, box, product):
        cond_set(product, 'title',
                 box.css('.shortDescription a::text').extract(),
                 string.strip)

        if box.css('.priceSale::text'):
            price = box.css('.priceSale::text').re(FLOATING_POINT_RGEX)
        else:
            price = box.css('.prices span.priceSale::text').re(
                FLOATING_POINT_RGEX)
        if not price:
            price = box.css('.prices span::text').re(FLOATING_POINT_RGEX)
        if price:
            product['price'] = Price(price=price[0],
                                     priceCurrency='USD')
        path = '[id^=main_images_holder_] img[id^=image]::attr(src)'
        cond_set(product, 'image_url', box.css(path).extract())
        cond_set(product, 'is_out_of_stock', box.css('.notAvailable'), bool)

    def _fetch_product_boxes(self, response):
        return response.css('.productThumbnail')

    def _link_from_box(self, box):
        return box.css('.shortDescription a::attr(href)').extract()[0]

    def _scrape_next_results_page_link(self, response):
        anchors = response.css('#paginateTop a::text').extract()
        anchors = filter(lambda s: s.isdigit(), anchors)
        if len(anchors) >= 1:
            last_page = int(anchors[-1])
            if last_page <= response.meta['page']:
                return None
            page = response.meta['page'] + 1
            url = self.url_formatter.format(self.SEARCH_URL,
                                            search_term=urllib.quote_plus(
                                                response.meta['search_term']),
                                            page=page,
                                            sort_mode=self.sort_mode)
            meta = response.meta.copy()
            meta['page'] = page

            if re.findall("edge=hybrid", response.url):
                cat_id = re.findall("\?id=(\d+)", response.url)[0]
                url = "http://www1.macys.com/catalog/category/facetedmeta" \
                    "?edge=hybrid" \
                    "&categoryId=%s&facet=false&dynamicfacet=true" \
                    "&pageIndex=%d&sortBy=%s&productsPerPage=40&" % (
                        cat_id, page, self.sort_mode)
                r = requests.get(url)
                array = Selector(text=r.text).xpath(
                    "//div[@id='metaProductIds']/text()").extract()
                ids = json.loads(array[0])
                url = "http://www1.macys.com/shop/catalog/product/thumbnail/" \
                    "1?edge=hybrid&limit=none&suppressColorSwatches=false" \
                    "&categoryId=%s&ids=" % (cat_id,)
                for i in ids:
                    url += cat_id + "_" + str(i) + ","

            return Request(url, meta=meta)
        else:
            return None

    def _populate_from_html(self, response, product):
        """
        @returns items 1 1
        @scrapes title description locale
        """
        product = response.meta.get('product', SiteProductItem())

        if u'>this product is currently unavailable' in response.body_as_unicode().lower():
            product['no_longer_available'] = True
            return

        mv = MacysVariants()
        mv.setupSC(response)
        product['variants'] = mv._variants()

        if response.xpath('//li[@id="memberItemsTab"]').extract():
            price = response.xpath(
                "//div[@id='memberProductList']/div[1]/"
                "div[@class='productPriceSection']/div/span[last()]/text()"
            ).re(FLOATING_POINT_RGEX)
        else:
            price = response.xpath(
                "//div[@id='priceInfo']/div/span/text()"
            ).re(FLOATING_POINT_RGEX)
        if response.css('.priceSale::text'):
            price = response.css('.priceSale::text').re(FLOATING_POINT_RGEX)
        if not price:
            price = response.xpath('//*[contains(@id, "priceInfo")]').re(FLOATING_POINT_RGEX)
        if not price:
            price = response.xpath('//*[contains(@class, "singlePrice")][contains(text(), "$")]')
        if price:
                product['price'] = Price(price=price[0],
                                         priceCurrency='USD')

        if not product.get("image_url") or \
                "data:image" in product.get("image_url"):
            image_url = response.xpath(
                "//img[contains(@id, 'mainView')]/@src").extract()
            if image_url:
                product["image_url"] = image_url[0]
        if not product.get('image_url'):
            cond_set(
                product, 'image_url',
                response.xpath('//*[contains(@class,'
                               ' "productImageSection")]//img/@src').extract()
            )
        if not product.get('image_url'):
            cond_set(
                product, 'image_url',
                response.xpath('//*[contains(@class, "mainImages")]'
                               '//*[contains(@class, "imageItem")]//img/@src').extract()
            )
        if not product.get("image_url") or \
                "data:image" in product.get("image_url"):
            img_src = response.xpath('//*[contains(@class, "imageItem") '
                                 'and contains(@class, "selected")]/img/@src').extract()
            if img_src:
                product['image_url'] = img_src[0]

        title = response.css('#productTitle::text').extract()
        if not title:
            title = response.xpath('//*[contains(@class, "productTitle")]'
                                   '[contains(@itemprop, "name")]/text()').extract()
        if title:
            cond_replace(product, 'title', [title[0].strip()])
        path = '//*[@id="memberProductDetails"]/node()[normalize-space()]'
        desc = response.xpath(path).extract()
        if not desc:
            desc = response.xpath(
                '//*[@id="productDetails"]/node()[normalize-space()]'
            ).extract()
            if desc:
                desc = [d for d in desc if 'id="adPool"' not in d]
        cond_set_value(product, 'description',
                       desc, ''.join)
        if not product.get('description', ''):
            product['description'] = (
                ' '.join(response.css('#product-detail-control ::text').extract()))

        locale = response.css('#headerCountryFlag::attr(title)').extract()
        if not locale:
            locale = response.xpath(
                '//meta[@property="og:locale"]/@content'
            ).extract()
        cond_set(product, 'locale', locale)
        brand = response.css('#brandLogo img::attr(alt)').extract()
        if not brand:
            brand = guess_brand_from_first_words(product['title'].replace(u'®', ''))
            brand = [brand]
        cond_set(product, 'brand', brand)

        if product.get('brand', '').lower() == 'levis':
            product['brand'] = "Levi's"

        product_id = response.css('#productId::attr(value)').extract()
        if not product_id:
            product_id = response.xpath('//*[contains(@class,"productID")]'
                                        '[contains(text(), "Web ID:")]/text()').extract()
            if product_id:
                product_id = [''.join([c for c in product_id[0] if c.isdigit()])]

        if product_id:  # Reviews
            url = "http://macys.ugc.bazaarvoice.com/7129aa/%s" \
                "/reviews.djs?format=embeddedhtml" % (product_id[0],)

            r = requests.get(url)
            resp = r.text
            resp = re.findall("var materials=(.*)", resp)
            if resp:
                resp = resp[0]
                data = json.loads(resp[0:-1])
                hxs = HtmlXPathSelector(text=data["BVRRSourceID"])

                num_of_reviews = hxs.xpath(
                    '//div[@id="BVRRQuickTakeSummaryID"]'
                    '/div/div/div/div/div/div/div/div/span'
                    '/span[contains(@class, "BVRRNumber")]/text()'
                ).extract()
                if num_of_reviews:
                    num_of_reviews = int(num_of_reviews[0].replace(',', ''))
                    array = hxs.xpath(
                        '//div/span[@class="BVRRHistAbsLabel"]/text()'
                    ).extract()
                    if array:
                        rating_by_star = {}
                        array = list(array)
                        array.reverse()
                        count = 0
                        review_sum = 0
                        for i in range(0, 5):
                            rating_by_star[i+1] = array[i].replace(',', '')
                            count += int(array[i].replace(',', ''))
                            review_sum += (i+1) * int(array[i].replace(',',
                                                                       ''))
                        average_rating = round(
                            float(review_sum) / float(count), 2)

                        br = BuyerReviews(
                            num_of_reviews,
                            average_rating,
                            rating_by_star
                        )

                        cond_set_value(product, 'buyer_reviews', br)
        cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
        # Related Products
        if product_id:
            aj_url = "http://www1.macys.com/sdp/rto/request/recommendations"
            headers = {
                'Content-type': 'application/x-www-form-urlencoded',
            }
            aj_body = {
                'productId': product_id[0],
                'visitorId': '0',
                'requester': 'MCOM-NAVAPP',
                'context': 'PDP_ZONE_A'
            }

            r = requests.post(
                aj_url,
                data=urllib.urlencode(aj_body),
                headers=headers
            )
            data = json.loads(r.text)

            rp = []
            rel_prod_links = []
            if data.get('recommendedItems'):
                for el in data["recommendedItems"]:
                    url, title = "", ""
                    link = "http://www1.macys.com/shop/catalog/" \
                        "product/newthumbnail/json?" \
                        "productId=%s&source=118" % (el["productId"],)
                    rel_prod_links.append(link)

                    r = requests.get(link)
                    data = json.loads(r.text)

                    try:
                        title = data["productThumbnail"]["productDescription"]
                        url = "http://www1.macys.com/" + \
                            data["productThumbnail"]["semanticURL"]
                    except Exception:
                        pass

                    if title or url:
                        rp.append(RelatedProduct(title, url))
            if rp:
                recomm = {'Customers Also Shopped': rp}
                product["related_products"] = recomm

    def _scrape_product_links(self, response):
        # redefine this method cause site may return for some search
        # terms products with the same links
        result = super(MacysProductsSpider,
                       self)._scrape_product_links(response)
        result = list(result)
        result = [(req_and_prod[0].replace(dont_filter=True), req_and_prod[1])
                  if req_and_prod[0] else req_and_prod for req_and_prod
                  in result]
        return result
