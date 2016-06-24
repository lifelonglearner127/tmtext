# -*- coding: utf-8 -*-#

from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re
import string
import urllib
import urlparse

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import FLOATING_POINT_RGEX
from product_ranking.spiders import cond_set, cond_set_value
from scrapy.http import Request, FormRequest
from scrapy.log import DEBUG, ERROR, WARNING


class SamsclubProductsSpider(BaseProductsSpider):
    name = 'samsclub_products'
    allowed_domains = ["samsclub.com"]
    start_urls = []

    SEARCH_URL = "http://www.samsclub.com/sams/search/searchResults.jsp" \
        "?searchCategoryId=all&searchTerm={search_term}&fromHome=no" \
        "&_requestid=29417"

    _NEXT_PAGE_URL = "http://www.samsclub.com/sams/shop/common" \
        "/ajaxSearchPageLazyLoad.jsp?sortKey=relevance&searchCategoryId=all" \
        "&searchTerm={search_term}&noOfRecordsPerPage={prods_per_page}" \
        "&sortOrder=0&offset={offset}&rootDimension=0&tireSearch=" \
        "&selectedFilter=null&pageView=list&servDesc=null&_=1407437029456"
    CLUB_SET_URL = (
        "http://www.samsclub.com/sams/search/wizard/common"
        "/displayClubs.jsp?_DARGS=/sams/search/wizard/common"
        "/displayClubs.jsp.selectId")

    def __init__(self, clubno='4704', zip_code='94117', *args, **kwargs):
        self.clubno = clubno
        self.zip_code = zip_code
        # if sort_mode not in self.SORT_MODES:
        #     self.log('"%s" not in SORT_MODES')
        #     sort_mode = 'default'
        # formatter = FormatterWithDefaults(sort_by=self.SORT_MODES[sort_mode])
        formatter = None
        super(SamsclubProductsSpider, self).__init__(
            formatter,
            site_name=self.allowed_domains[0],
            *args,
            **kwargs)

    def start_requests(self):
        yield Request(
            url="http://www.samsclub.com/",
            meta={'club': 1})

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            yield Request(self.product_url,
                          self._parse_single_product,
                          cookies={'myPreferredClub': self.clubno},
                          meta={'product': prod})

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse(self, response):
        club = response.meta.get('club')
        self.log("Club stage: %s" % club, DEBUG)
        if club == 1:
            c = response.xpath(
                "//div[@id='headerClubLocation']/text()").extract()
            self.log("Club mark: %s" % c, DEBUG)
            data = {'/sams_dyncharset': 'ISO-8859-1',
                    '_dynSessConf': '-7856921515575376948',
                    '/com/walmart/ecommerce/samsclub/shoppingfilter/handler/ShoppingFilterFormHandler.selectedClub': self.clubno,
                    '_D:/com/walmart/ecommerce/samsclub/shoppingfilter/handler/ShoppingFilterFormHandler.selectedClub': '',
                    'selectClub': 'null',
                    '/com/walmart/ecommerce/samsclub/shoppingfilter/handler/ShoppingFilterFormHandler.neighboringClubs': self.clubno,
                    '_D:/com/walmart/ecommerce/samsclub/shoppingfilter/handler/ShoppingFilterFormHandler.neighboringClubs': '',
                    '/com/walmart/ecommerce/samsclub/shoppingfilter/handler/ShoppingFilterFormHandler.wizardClubSelection': 'submit',
                    '_D:/com/walmart/ecommerce/samsclub/shoppingfilter/handler/ShoppingFilterFormHandler.wizardClubSelection': '',
                    '_DARGS:/sams/search/wizard/common/displayClubs.jsp.selectId': ''
                    }

            new_meta = response.meta.copy()
            new_meta['club'] = 2
            request = FormRequest.from_response(
                response=response,
                url=self.CLUB_SET_URL,
                method='POST',
                formdata=data,
                callback=self.parse,
                meta=new_meta)
            return request

        elif club == 2:
            self.log("Select club '%s'' response: %s " % (
                self.clubno,
                response.body_as_unicode().encode('utf-8')), DEBUG)
            new_meta = response.meta.copy()
            new_meta['club'] = 3
            return Request(
                url="http://www.samsclub.com/",
                meta=new_meta,
                dont_filter=True)

        elif club == 3:
            c = response.xpath(
                "//a[@class='shopYourClubLink']/descendant::text()").extract()
            c = " ".join(x.strip() for x in c if len(x.strip()) > 0)
            self.log("Selected club: '%s' '%s'" % (
                self.clubno, " ".join(c.split())), DEBUG)
            for st in self.searchterms:
                return Request(
                    self.url_formatter.format(
                        self.SEARCH_URL,
                        search_term=urllib.quote_plus(st.encode('utf-8')),
                    ),
                    meta={'search_term': st,
                          'remaining': self.quantity,
                          'club': 4})

        elif club == 4:
            return super(SamsclubProductsSpider, self).parse(response)

    def parse_product(self, response):
        product = response.meta['product']

        cond_set(
            product,
            'brand',
            response.xpath(
                "//div[contains(@class,'prodTitlePlus')]"
                "/span[@itemprop='brand']/text()"
            ).extract())
        if not product.get('brand', None):
            cond_set(
                product,
                'brand',
                response.xpath(
                    '//*[@itemprop="brand"]//span/text()').extract())

        cond_set(
            product,
            'title',
            response.xpath(
                "//div[contains(@class,'prodTitle')]/h1/span[@itemprop='name']"
                "/text()"
            ).extract())

        # Title key must be present even if it is blank
        cond_set_value(product, 'title', "")
        sold_out = response.xpath('//*[@itemprop="availability" and @href="http://schema.org/SoldOut"]')
        cond_set_value(product, 'no_longer_available', 1 if (not response.body or sold_out) else 0)

        cond_set(product, 'image_url', response.xpath(
            "//div[@id='plImageHolder']/img/@src").extract())

        old_price = ''.join(response.xpath(
            '//li[@class="wasPrice"]//span[@class="striked strikedPrice"]'
            '/text()').re('[\d\.\,]+')) or \
            ''.join(response.xpath(
                '//*[@class="ltGray" and contains(text(),"Everyday Price")]/'
                'following-sibling::span[@class="striked '
                'strikedPrice"]/text()').re('[\d\.\,]+'))
        old_price = old_price.strip().replace(',', '')

        if not product.get("price"):
            price = response.xpath("//li/span[@itemprop='price']/text()").extract()

            if old_price:
                cond_set_value(product, 'price', Price(price=old_price,
                                                   priceCurrency='USD'))
                if not price:
                    price = response.xpath(
                        ".//div[contains(@class, 'pricingInfo')]//*[@class='lgFont']/li/span[@class='price' or "\
                        "@class='superscript' and position()>1]/text()").extract()
                    price = ['.'.join(price)]
                cond_set_value(product, 'price_with_discount', Price(price=price[0],
                                                                     priceCurrency='USD'))

            elif price:
                cond_set_value(product, 'price', Price(price=price[0],
                                                       priceCurrency='USD'))

        price = response.xpath(
            "//div[@class='moneyBoxBtn']/a"
            "/span[contains(@class,'onlinePrice')]"
            "/text()").re(FLOATING_POINT_RGEX)

        if not price and not product.get("price"):
            oos_pr = '.'.join(response.xpath(
                '//*[contains(@class,"pricingInfo oos")]'
                '/ul[@class="lgFont"]//span/text()').re('\d+'))

            if oos_pr:
                price = [float(oss_pr)]

            pr = response.xpath(
                "//div[contains(@class,'pricingInfo')]//li"
                "/span/text()").extract()
            if pr and not price:
                price = "".join(pr[:-1]) + "." + pr[-1]
                member_price, discounted_price = None, None
                if 'too low to show' in price.lower():
                    # price is visible only after you add the product in cart
                    product['price_details_in_cart'] = True
                    price = re.search("'item_price':'([\d\.]+)',",
                                      response.body_as_unicode()).group(1)
                    price = [float(price)]
                elif 'was' in price.lower():
                    discounted_price = '.'.join(response.xpath(
                        '//div[contains(@class,"pricingInfo")]'
                        '//li[@class="nowOnly"]/following-sibling::li[1]'
                        '/span/text()').re('[\d]+')).replace(',', '').strip()

                    member_price = '.'.join(response.xpath(
                        '//*[contains(@class,"pricingInfo")]'
                        '//*[@class="dkGray"]/*[@itemprop="price"]'
                        '/text()').re('[\d\.\,]+')).replace(',', '').strip()

                elif 'tech savings' in price.lower():
                    discounted_price = '.'.join(response.xpath(
                        '//*[contains(@class,"pricingInfo")]'
                        '/*[@class="lgFont"]'
                        '//text()').re('[\d\.\,]+')).replace(',', '').strip()

                    member_price = '.'.join(response.xpath(
                        '//*[contains(@class,"pricingInfo")]'
                        '//*[@class="dkGray"]/*[@itemprop="price"]'
                        '/text()').re('[\d\.\,]+')).replace(',', '').strip()

                else:
                    m = re.search(FLOATING_POINT_RGEX, price)
                    if m:
                        price = [m.group(0).strip('.')]
                    else:
                        price = None

                if member_price and discounted_price:
                        cond_set_value(product,
                                       'price',
                                       Price(price=member_price,
                                             priceCurrency='USD'))
                        cond_set_value(product,
                                       'price_with_discount',
                                       Price(price=discounted_price,
                                             priceCurrency='USD'))
                        price = None
                elif discounted_price:
                        cond_set_value(product,
                                       'price',
                                       Price(price=discounted_price,
                                             priceCurrency='USD'))
                        price = None

            if not price:
                price = response.xpath(
                    "//span[contains(@class,'onlinePrice')]"
                    "/text()").re(FLOATING_POINT_RGEX)

        if price:
            cond_set_value(product, 'price', Price(price=price[0], priceCurrency='USD'))

        cond_set(
            product,
            'description',
            response.xpath(
                "//div[@itemprop='description']").extract(),
        )

        cond_set(product, 'model', response.xpath(
            "//span[@itemprop='model']/text()").extract(),
            conv=string.strip)
        if product.get('model', '').strip().lower() == 'null':
            product['model'] = ''

        product['locale'] = "en-US"

        # Categories
        categorie_filters = [u'sam\u2019s club']
        # Clean and filter categories names from breadcrumb
        bc = response.xpath('//*[@id="breadcrumb"]//a/text()').extract()
        bc = [b.strip() for b in bc if b.strip()]
        if not bc or len(bc)==1:
            bc = response.xpath(".//*[@id='breadcrumb']//text()").extract()
        bc = [b.strip() for b in bc if b.strip()]
        if not bc:
            bc = response.xpath('//*[@id="breadcrumb"]//a//*[@itemprop="title"]/text()').extract()
        bc = [b.strip() for b in bc if b.strip()]

        categories = list(filter((lambda x: x.lower() not in categorie_filters),
                                 map((lambda x: x.strip()), bc)))
        category = categories[-1] if categories else None
        cond_set_value(product, 'categories', categories)
        cond_set_value(product, 'category', category)

        # Subscribe and save
        subscribe_and_save = response.xpath('//*[@class="subscriptionDiv" and \
                not(@style="display: none;")]/input[@id="pdpSubCheckBox"]')
        cond_set_value(product,
                       'subscribe_and_save',
                       1 if subscribe_and_save else 0)

        # Shpping
        shipping_included = response.xpath('//*[@class="freeDelvryTxt"]')
        cond_set_value(product,
                       'shipping_included',
                       1 if shipping_included else 0)

        oos_in_both = response.xpath(
            '//*[@class="biggraybtn" and'
            ' text()="Out of stock online and in club"]')

        # Available in Store
        available_store = response.xpath(
            '//*[(@id="addtocartsingleajaxclub" or'
            '@id="variantMoneyBoxButtonInitialLoadClub")'
            'and contains(text(),"Pick up in Club")]') or \
            response.xpath(
                '//li[contains(@class,"pickupIcon")]'
                '/following-sibling::li[contains'
                '(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ",'
                ' "abcdefghijklmnopqrstuvwxyz"),"ready as soon as")]')

        cond_set_value(product,
                       'available_store',
                       1 if available_store and not oos_in_both else 0)

        # Available Online
        available_online = response.xpath('//*[(@id="addtocartsingleajaxonline" \
                or @id="variantMoneyBoxButtonInitialLoadOnline")]')
        cond_set_value(product,
                       'available_online',
                       1 if available_online and not oos_in_both else 0)

        if not shipping_included and not product.get('no_longer_available'):
            productId = ''.join(response.xpath('//*[@id="mbxProductId"]/@value').extract())
            pSkuId = ''.join(response.xpath('//*[@id="mbxSkuId"]/@value').extract())
            shipping_prices_url = "http://www.samsclub.com/sams/shop/product/moneybox/shippingDeliveryInfo.jsp?zipCode=%s&productId=%s&skuId=%s" % (self.zip_code, productId, pSkuId)
            return Request(shipping_prices_url, 
                           meta={'product': product}, 
                           callback=self._parse_shipping_cost)

        return product

    def _parse_shipping_cost(self, response):
        product = response.meta['product']
        product['shipping'] = []
        shipping_names = response.xpath('//tr/td[1]/span/text()').extract()
        shipping_prices = response.xpath('//tr/td[2]/text()').re('[\d\.\,]+')

        for shipping in zip(shipping_names, shipping_prices):
            product['shipping'].append({'name': shipping[0], 'cost': shipping[1]})

        return product

    def _scrape_total_matches(self, response):
        if response.url.find('ajaxSearch') > 0:
            items = response.xpath("//body/li[contains(@class,'item')]")
            return len(items)

        totals = response.xpath(
            "//div[contains(@class,'shelfSearchRelMsg2')]"
            "/span/span[@class='gray3']/text()"
        ).extract()
        if totals:
            total = int(totals[0])
        elif response.css('.nullSearchShelfZeroResults'):
            total = 0
        else:
            total = None
        return total

    def _scrape_product_links(self, response):
        if response.url.find('ajaxSearch') > 0:
            links = response.xpath("//body/ul/li/a/@href").extract()
        else:
            links = response.xpath(
                "//ul[contains(@class,'shelfItems')]"
                "/li[contains(@class,'item')]/a/@href"
            ).extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _get_next_products_page(self, response, prods_found):
        link_page_attempt = response.meta.get('link_page_attempt', 1)

        result = None
        if prods_found is not None:
            # This was a real product listing page.
            remaining = response.meta['remaining']
            remaining -= prods_found
            if remaining > 0:
                next_page = self._scrape_next_results_page_link(response, remaining)
                if next_page is None:
                    pass
                elif isinstance(next_page, Request):
                    next_page.meta['remaining'] = remaining
                    result = next_page
                else:
                    url = urlparse.urljoin(response.url, next_page)
                    new_meta = dict(response.meta)
                    new_meta['remaining'] = remaining
                    result = Request(url, self.parse, meta=new_meta, priority=1)
        elif link_page_attempt > self.MAX_RETRIES:
            self.log(
                "Giving up on results page after %d attempts: %s" % (
                    link_page_attempt, response.request.url),
                ERROR
            )
        else:
            self.log(
                "Will retry to get results page (attempt %d): %s" % (
                    link_page_attempt, response.request.url),
                WARNING
            )

            # Found no product links. Probably a transient error, lets retry.
            new_meta = response.meta.copy()
            new_meta['link_page_attempt'] = link_page_attempt + 1
            result = response.request.replace(
                meta=new_meta, cookies={}, dont_filter=True)

        return result

    def _scrape_next_results_page_link(self, response, remaining):
        # If the total number of matches cannot be scrapped it will not be set.
        num_items = min(response.meta.get('total_matches', 0), self.quantity)
        if num_items:
            return SamsclubProductsSpider._NEXT_PAGE_URL.format(
                search_term=response.meta['search_term'],
                offset=num_items - remaining,
                prods_per_page=min(200, num_items))
        return None
