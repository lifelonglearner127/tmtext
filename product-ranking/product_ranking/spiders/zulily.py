# -*- coding: utf-8 -*-
import string
import urllib
import re
import json
import time
from scrapy.utils.response import open_in_browser
from scrapy import FormRequest, Request, Spider
from product_ranking.items import SiteProductItem, BuyerReviews, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    FLOATING_POINT_RGEX, cond_set_value


class KrogerProductsSpider(BaseProductsSpider):
    name = "zulily_products"
    allowed_domains = ["zulily.com"]

    use_proxies = True
    SEARCH_URL = "https://www.kroger.com/storecatalog/servlet/SearchDisplay?urlRequestType=Base&" \
                 "storeId={store_id}&searchTerm={search_term}&pageTitle=Search%20results&pageNumber={page}&sort=popularity"
    LOG_IN_URL = "https://www.kroger.com/user/authenticate"

    def __init__(self, login="", password="", *args, **kwargs):
        super(KrogerProductsSpider, self).__init__(*args, **kwargs)
        self.login = login
        self.password = password

    def start_requests(self):
            body = '{"account":{"email":"arnoldmessi777@gmail.com","password":"apple123","rememberMe":false},"location":""}'
        yield Request(self.LOG_IN_URL,
                      method='POST',
                      body=body,
                      callback=self._log_in,
                      headers={'Content-Type': 'application/json;charset=UTF-8'})

    def _log_in(self, response):
        url = "https://www.kroger.com/storecatalog/servlet/Logon?pickupStoreId=" \
              "{pickup_id}&divisionSwitch=true&catalogId=13551&langId=-1&storeId=" \
              "{store_id}&URL=https%3A%2F%2Fwww.kroger.com%2Fstorecatalog%2Fservlet%2FTopCategoriesDisplayView".format(store_id=self.store_id, pickup_id=self.pickup_id)
        yield Request(url,
                      callback=self._pick_store)

    def _pick_store(self, response):
        url = "https://www.kroger.com/storecatalog/servlet/CategoryDisplay?urlRequestType=Base&catalogId=13551&categoryId=104698" \
              "&pageView=grid&urlLangId=-1&beginIndex=0&langId=-1&top_category=104501&storeId={store_id}".format(store_id=self.store_id)
        yield Request(url,
                      callback=self._start_requests)

    def _scrape_next_results_page_link(self, response):
        # <a role="button" class="right_arrow " id = "WC_SearchBasedNavigationResults_pagination_link_right_categoryResults" href = 'javascript:dojo.publish("showResultsForPageNumber",[{pageNumber:"2",pageSize:"60", linkId:"WC_SearchBasedNavigationResults_pagination_link_right_categoryResults"}])' title="Show next page"></a>
        # pageNumber:"2",pageSize:"60",
        next_page = response.xpath('//a[@class="right_arrow "]/@href').re('pageNumber:"(\d+)"')
        if next_page:
            next_page = int(next_page[0])
        else:
            return
        url = re.sub('pageNumber=\d+', 'pageNumber={}'.format(next_page), response.url)
    def _start_requests(self, response):
        """Generate Requests from the SEARCH_URL and the search terms."""
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8'),),
                    page=1,
                    store_id=self.store_id
                ),
                meta={'search_term': st, 'remaining': self.quantity},
            )

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            prod['search_term'] = ''
            upc = self._get_upc_from_url(self.product_url)
            yield Request(self.product_url,
                          self._get_product_id,
                          meta={'product': prod,
                                'upc': upc})

    def _scrape_product_links(self, response):
        links = response.xpath('//div[@class="product_name"]/a/@href').extract()
        for no, link in enumerate(links):
            yield link, SiteProductItem()

    def _scrape_total_matches(self, response):
        matches = re.search('searchTabProdCount.innerHTML = (.+?);', response.body)
        return int(matches.group(1)) if matches else 0


    def _get_product_id(self, response):
        # https://www.kroger.com/storecatalog/clicklistbeta/#/productdetails/0007480618639?categoryId=0101400172
        upc = response.meta.get('upc')
        url = "https://www.kroger.com/storecatalog/servlet/SearchDisplay?urlRequestType=Base&storeId=" \
              "{store_id}&searchTerm={upc}".format(store_id=self.store_id, upc=upc)
        yield Request(url,
                      callback=self._get_product_page,
                      meta=response.meta)

    def _get_product_page(self, response):
        # SearchJS.updateSearchTermHistoryCookieAndRedirect("0007480618639", "https://www.kroger.com/storecatalog/servlet/ProductDisplay?urlRequestType=Base&catalogId=13551&categoryId=&productId=136183&errorViewName=ProductDisplayErrorView&urlLangId=-1&langId=-1&top_category=&parent_category_rn=&storeId=13651")
        url = re.search('SearchJS.updateSearchTermHistoryCookieAndRedirect\(\"\d+", "(.+?)"', response.body).group(1)

        yield Request(url,
                      callback=self._parse_single_product,
                      meta=response.meta)

    def _parse_single_product(self, response):
        yield self.parse_product(response)

    @staticmethod
    def _get_upc_from_url(url):
        pattern = 'productdetails\/(\d+)'
        found = re.search(pattern, url)
        return found.group(1) if found else None

    @staticmethod
    def _parse_title(response):
        # <h1 role="heading" aria-level="1" class="main_header">Daily's Bahama Mama Pouch</h1>
        title = response.xpath('//h1[@role="heading"]/text()').extract()
        return title[0] if title else ''

    @staticmethod
    def _parse_price(response):
        # <span id="offerPrice_136183" class="price offer_price" itemprop="price">
        price = response.xpath('//*[@itemprop="price"]/text()').re(FLOATING_POINT_RGEX)
        if not price:
            return None
        currency = 'USD'
        return Price(price=price[0], priceCurrency=currency)

    @staticmethod
    def _parse_upc(response):
        # <span id="product_SKU_136183" class="sku">SKU:0007480618639</span>
        upc = response.xpath('//*[@class="sku"]/text()').re('\d+')
        return upc[0] if upc else None

    @staticmethod
    def _parse_image_url(response):
        # <input type="hidden" id="ProductInfoImage_136183" value="https://www.kroger.com/product/images/140494904/large/front/0007480618639"/>
        image = response.xpath('//*[contains(@id, "ProductInfoImage_")]/@value').extract()
        return image[0] if image else None

    @staticmethod
    def _parse_no_longer_available(product_json):
        return not product_json.get('buyable')

    def parse_product(self, response):

        product = response.meta['product']

        image_url = self._parse_image_url(response)
        cond_set_value(product, 'image_url', image_url)

        # Parse title
        title = self._parse_title(response)
        cond_set_value(product, 'title', title, conv=string.strip)

        # Parse price
        price = self._parse_price(response)
        cond_set_value(product, 'price', price)

        # Parse upc
        upc = self._parse_upc(response)
        cond_set_value(product, 'upc', upc)

        # Parse url
        url = "https://www.kroger.com/storecatalog/clicklistbeta/#/productdetails/{upc}".format(upc=upc)
        product['url'] = url

        return product
