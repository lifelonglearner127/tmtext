from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import string
import urllib

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider
from product_ranking.spiders import cond_set, cond_set_value
from scrapy.http import Request, FormRequest
from scrapy.log import DEBUG, ERROR


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

    def __init__(self, clubno='4704', *args, **kwargs):
        self.clubno = clubno
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
            st = self.searchterms[0]
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
        cond_set_value(product, 'brand', 'NO BRAND')

        cond_set(
            product,
            'title',
            response.xpath(
                "//div[contains(@class,'prodTitle')]/h1/span[@itemprop='name']"
                "/text()"
            ).extract())

        cond_set(product, 'image_url', response.xpath(
            "//div[@id='plImageHolder']/img/@src").extract())

        cond_set(
            product,
            'price',
            response.xpath(
                "//div[@class='moneyBoxBtn']/a"
                "/span[contains(@class,'onlinePrice')]/text()"
            ).extract())

        pr = response.xpath(
            "//div[contains(@class,'pricingInfo')]"
            "/ul/li/span/text()").extract()
        if not pr:
            pr = response.xpath(
                "//div[contains(@class,'pricingInfo')]"
                "/div/ul/li/span/text()").extract()
        if pr:
            price = "".join(pr[:-1]) + "." + pr[-1]
            cond_set_value(product, 'price', price)

        cond_set(
            product,
            'price',
            response.xpath(
                "//span[contains(@class,'onlinePrice')]/text()").extract())

        cond_set(
            product,
            'description',
            response.xpath(
                "//div[@itemprop='description']").extract(),
        )

        productid = response.xpath(
            "//span[@itemprop='productID']/text()").extract()
        if productid:
            productid = productid[0].strip().replace('#:', '', 1)
            try:
                product['upc'] = int(productid)
            except ValueError:
                self.log("Failed to parse upc number of matches: %r" % (
                    productid), ERROR)

        cond_set(product, 'model', response.xpath(
            "//span[@itemprop='model']/text()").extract(),
            conv=string.strip)

        product['locale'] = "en-US"

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
            links = response.xpath("//body/li/a/@href").extract()
        else:
            links = response.xpath(
                "//ul[contains(@class,'shelfItems')]"
                "/li[contains(@class,'item')]/a/@href"
            ).extract()

        if not links:
            self.log("Found no product links.", ERROR)

        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        # If the total number of matches cannot be scrapped it will not be set.
        num_items = min(response.meta.get('total_matches', 0), self.quantity)
        if num_items:
            return SamsclubProductsSpider._NEXT_PAGE_URL.format(
                search_term=response.meta['search_term'],
                offset=response.meta['products_per_page'] + 1,
                prods_per_page=num_items,
            )
        return None
