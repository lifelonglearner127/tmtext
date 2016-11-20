# -*- coding: utf-8 -*-

import re
import json
import urllib

from scrapy import Request

from scrapy.selector import HtmlXPathSelector
import requests

from product_ranking.items import SiteProductItem, RelatedProduct, \
    Price, BuyerReviews
from product_ranking.spiders import cond_set, cond_set_value, \
    FLOATING_POINT_RGEX, cond_replace
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.guess_brand import guess_brand_from_first_words
from spiders_shared_code.macys_variants import MacysVariants
from .macys import MacysProductsSpider

is_empty = lambda x: x[0] if x else None


class MacysShelfPagesSpider(MacysProductsSpider):
    name = 'macys_shelf_urls_products'
    allowed_domains = ['macys.com', 'www1.macys.com', 'www.macys.com']

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = 99999
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.zip_code = '12345'
        self.current_page = 1

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': 99999, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        super(MacysShelfPagesSpider, self).__init__(*args, **kwargs)
        self.product_url = kwargs['product_url']
        self._setup_class_compatibility()

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
                          " AppleWebKit/537.36 (KHTML, like Gecko)" \
                          " Chrome/37.0.2062.120 Safari/537.36"

        # variants are switched off by default, see Bugzilla 3982#c11
        self.scrape_variants_with_extra_requests = False
        if 'scrape_variants_with_extra_requests' in kwargs:
            scrape_variants_with_extra_requests = kwargs['scrape_variants_with_extra_requests']
            if scrape_variants_with_extra_requests in (1, '1', 'true', 'True', True):
                self.scrape_variants_with_extra_requests = True

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility(),
                      dont_filter=True)

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def _scrape_product_links(self, response):
        urls = response.xpath(
            '//span[contains(@id, "main_images_holder")]/../../a/@href'
        ).extract()

        urls = ['http://www1.macys.com' + i for i in urls]

        shelf_categories = response.xpath(
            './/*[@id="nav_category"]//*[@id="viewAllInCategory" or @id="currentCatNavHeading"]/text()').extract()
        shelf_categories = [i.replace('View All','').strip() for i in shelf_categories if i.strip()]
        shelf_category = shelf_categories[-1] if shelf_categories else None

        for url in urls:
            item = SiteProductItem()
            if shelf_category:
                item['shelf_name'] = shelf_category
            if shelf_categories:
                item['shelf_path'] = shelf_categories
            yield url, item

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        return super(MacysShelfPagesSpider,
                     self)._scrape_next_results_page_link(response)

    # def parse_product(self, response):
    #     is_collection = response.xpath(".//*[@id='memberItemsTab']/a[@href='#collectionItems']"
    #                                    "/*[contains(text(),'Choose Your Items')]")
    #     if is_collection:
    #         self.log("{} - item is collection, dropping the item".format(response.url), INFO)
    #         return None
    #     else:
    #         return super(MacysShelfPagesSpider, self).parse_product(response)

    def _populate_from_html(self, response, product):
        """
        @returns items 1 1
        @scrapes title description locale
        """
        product = response.meta.get('product', SiteProductItem())

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
            price = [p.strip() for p in
                     response.xpath('//*[@id="priceInfo"]//text()').extract()
                     if p.strip()]
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
            title = title[0].strip() if title else ''
        if not product.get('title', None):
            title = response.xpath('//h1[contains(@class,"productName")]//text()').extract()
            title = title[0].strip() if title else ''

        if title:
            cond_replace(product, 'title', [''.join(title).strip()])

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
        locale = response.css('#headerCountryFlag::attr(title)').extract()
        if not locale:
            locale = response.xpath(
                '//meta[@property="og:locale"]/@content'
            ).extract()
        cond_set(product, 'locale', locale)
        brand = response.css('#brandLogo img::attr(alt)').extract()
        if not brand:
            brand = response.xpath('.//*[@class="productTitle"]/a[@class="brandNameLink"]/text()').extract()
        if not brand:
            brand = guess_brand_from_first_words(product['title'].replace(u'®', ''))
            brand = [brand]
        cond_set(product, 'brand', brand)

        if product.get('brand', '').lower() == 'levis':
            product['brand'] = "Levi's"

        product_id = response.css('#productId::attr(value)').extract()

        self._parse_reviews(response, product)

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

    def _parse_reviews(self, response, product):
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
                            rating_by_star[i + 1] = array[i].replace(',', '')
                            count += int(array[i].replace(',', ''))
                            review_sum += (i + 1) * int(array[i].replace(',',
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
