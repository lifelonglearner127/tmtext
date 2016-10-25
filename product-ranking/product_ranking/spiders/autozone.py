from __future__ import division, absolute_import, unicode_literals

import re
import urllib

from scrapy.selector import Selector
from scrapy.log import ERROR
from scrapy.http import Request
from scrapy.conf import settings
from product_ranking.items import SiteProductItem, Price, RelatedProduct, \
    BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import BaseProductsSpider,FormatterWithDefaults, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX


class AutozoneProductsSpider(BaseProductsSpider):
    name = 'autozone_products'
    allowed_domains = ["autozone.com", "api.bazaarvoice.com"]
    start_urls = []

    SEARCH_URL = "http://www.autozone.com/searchresult?" \
                 "searchText={search_term}&vehicleSetFromSearch=false&keywords={search_term}"

    SEARCH_SORT = {
        'best_match': '',
        'best_selling': 'performanceRank%7c0',
        'new_to_store': 'newToStoreDate%7c1',
        'a-z': 'Brand+Line%7c0%7c%7cname%7c0%7c%7cgroupDistinction%7c0',
        'z-a': 'Brand+Line%7c1%7c%7cname%7c1%7c%7cgroupDistinction%7c1',
        'customer_rating': 'avgRating%7c1%7c%7cratingCount%7c1',
        'low_to_high_price': 'price%7c0',
        'high_to_low_price': 'price%7c1',
        'saving_dollars': 'savingsAmount%7c1',
        'saving_percent': 'savingsPercent%7c1',
    }

    REVIEW_URL = 'https://pluck.autozone.com/ver1.0/sys/jsonp?' \
                  'widget_path=pluck/reviews/rollup&' \
                  'plckReviewOnKey={product_id}&' \
                  'plckReviewOnKeyType=article&' \
                  'plckReviewShowAttributes=true&' \
                  'plckDiscoveryCategories=&' \
                  'plckArticleUrl={product_url}&' \
                  'clientUrl={product_url}'

    def __init__(self, search_sort='best_match', *args, **kwargs):
        if "search_modes" in kwargs:
            search_sort = kwargs["search_modes"]
        super(AutozoneProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.SEARCH_SORT[search_sort]
            ),
            site_name="autozone.com",
            *args, **kwargs)
        #settings.overrides['CRAWLERA_ENABLED'] = True

    def start_requests(self):
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8')),
                ).replace("%2B", "+"),
                meta={'search_term': st, 'remaining': self.quantity},
            )
        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod, 'handle_httpstatus_list': [404, 503, 500]})

    def parse_product(self, response):
        product = response.meta['product']
        reqs = []

        if response.status == 404:
            product['not_found'] = True
            return product

        cond_set(product, 'title', response.xpath(
            "//h3[@property='name']//text()").extract(), lambda y: y.strip())

        cond_set(product, 'image_url', response.xpath(
            "//div[contains(@class,'productThumbsblock')]//li//a//img/@src").extract())

        price = response.xpath("//td[@class='pricing-description']").extract()
        if price:
            if not '$' in price[0]:
                self.log('Unknown currency at' % response.url)
            else:
                product['price'] = Price(
                    price=price[0].replace(',', '').replace(
                        '$', '').strip(),
                    priceCurrency='USD'
                )

        cond_set_value(product,
                       'description',
                       response.xpath("//div[@id='features']").extract(),
                       conv=''.join)

        brand = 'Autozone'
        cond_set_value(product, 'brand', brand)

        is_out_of_stock = response.xpath(
            '//div[@id="divAvailablity"]/text()').extract()
        if is_out_of_stock:
            if is_out_of_stock[0] == "in stock":
                is_out_of_stock = False
            else:
                is_out_of_stock = True
            cond_set(product, 'is_out_of_stock', (is_out_of_stock,))
        else:
            is_out_of_stock = response.xpath(
                '//div[@id="ReplacementReasonDiv"]/span/text()'
            ).extract()
            if is_out_of_stock:
                if "item is temporarily out of stock" in is_out_of_stock[0]:
                    is_out_of_stock = True
                else:
                    is_out_of_stock = False
                cond_set(product, 'is_out_of_stock', (is_out_of_stock,))

        product['locale'] = "en-US"

        #Buyer reviews
        product_id = response.xpath("//div[@id='product-data']//div[@id='SkuId']//text()").extract()
        if len(product_id) > 0:
            product_id = product_id[0].strip()
            review_url = self.REVIEW_URL.format(product_id=product_id, product_url=response.url)
            reqs.append(Request(review_url,
                                self._parse_review,
                                meta=response.meta))


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

    def _parse_review(self, response):
        product = response.meta['product']
        reqs = response.meta.get('reqs', [])

       # review_html = html.fromstring(
       #      re.search('(<div id="pluck_reviews_rollup.+?\'\))', contents).group(1)
       #  )

        arr = response.xpath(
            "//div[contains(@class,'pluck-dialog-middle')]"
            "//span[contains(@class,'pluck-review-full-attributes-name-post')]/text()"
        ).extract()
        review_list = []
        if len(arr) >= 5:
            review_list = [[5 - i, int(re.findall('\d+', mark)[0])]
                           for i, mark in enumerate(arr)]
        if review_list:
            # average score
            sum = 0
            cnt = 0
            for i, review in review_list:
                sum += review*i
                cnt += review
            average_rating = float(sum)/cnt
            # number of reviews
            num_of_reviews = 0
            for i, review in review_list:
                num_of_reviews += review
        else:
            pass

        rating_by_star = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for i, review in review_list:
            rating_by_star[i] = review
        if average_rating and num_of_reviews:
            product["buyer_reviews"] = BuyerReviews(
                num_of_reviews=int(num_of_reviews),
                average_rating=float(average_rating),
                rating_by_star=rating_by_star,
            )
        else:
            product["buyer_reviews"] = ZERO_REVIEWS_VALUE

        if reqs:
            return self.send_next_request(reqs, response)

        return product

    def get_related_products(self, resp):
        rp = []
        product = resp.meta['product']
        all_inf = Selector(text=resp.body).xpath(
            '//td[@class="weRecommend"]/a')
        if all_inf:
            urls = all_inf.xpath('@href').extract()
            titles = all_inf.xpath(
                'div[@class="weRecommendSubText"]/text()').extract()
            titles = [x.strip() for x in titles]
            for i in range(0, len(titles)):
                rp.append(
                    RelatedProduct(
                        title=titles[i],
                        url=urls[i]
                    )
                )
        if rp:
            product["related_products"] = {"recommend": rp}
        return product

    def _scrape_total_matches(self, response):
        total_matches = response.xpath(
            '//h2[@class="SrchMsgHeader"]/text()'
        ).re(FLOATING_POINT_RGEX)

        if total_matches:
            return int(total_matches[0].replace(',', ''))
        return 0

    def _scrape_product_links(self, response):
        items = response.css('div.itemGrid div.info')
        if not items:
            self.log("Found no product links.", ERROR)
        for item in items:
            link = item.xpath('.//a/@href').extract()[0]
            brand = item.xpath('.//span[@class="name"]/text()').extract()[0]
            yield link, SiteProductItem(brand=brand.strip(' -'))

    def _scrape_next_results_page_link(self, response):
        link = response.xpath(
            '//table[@class="srdSrchNavigation"]'
            '//a[@class="nextpage"]/@href'
        ).extract()
        if link:
            return link[0]
        return None

    def _parse_single_product(self, response):
        return self.parse_product(response)
