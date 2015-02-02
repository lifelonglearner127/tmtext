from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re

from scrapy.log import ERROR, WARNING
from scrapy.http import Request
from scrapy import FormRequest

from scrapy.http import Request
from product_ranking.items import SiteProductItem, Price, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults,\
    cond_set, cond_set_value

is_empty = lambda x: x[0] if x else ""


class PeapodProductsSpider(BaseProductsSpider):
    """Spider for peapod.com.

    This site require authorization. For this reason we enter one time
    visitor zipcode. It should be from peapod.com coverage area.

    Not populated fields:
    -related_products
    -buyers_reviews # not available
    -upc # not available
    -is_in_store_only # not available
    -model # not available

    Note: Some products have no description populated on the site.

    Accepted order modes:
    'default'
    'best_match'
    'alphabetical'
    'size'
    'unit_price'
    'price'
    'specials'

    Example command:
    scrapy crawl -a peapod_products searchterms_str="tea" -a order="default"
    """
    name = "peapod_products"
    allowed_domains = ["peapod.com"]

    start_url = "https://www.peapod.com/site/gateway/zip-entry"\
                "/top/zipEntry_main.jsp"

    default_zip = '10024'

    formdata = {
        '_dyncharset': '',
        '/peapod/handler/iditarod/ZipHandler.continueURL': '',
        '_D:/peapod/handler/iditarod/ZipHandler.continueURL': '',
        '/peapod/handler/iditarod/ZipHandler.submitSuccessURL': '',
        '_D:/peapod/handler/iditarod/ZipHandler.submitSuccessURL': '',
        '/peapod/handler/iditarod/ZipHandler.submitFailureURL': '',
        '_D:/peapod/handler/iditarod/ZipHandler.submitFailureURL': '',
        '_D:zipcode': '',
        '/peapod/handler/iditarod/ZipHandler.collectProspectURL': '',
        '_D:/peapod/handler/iditarod/ZipHandler.collectProspectURL': '',
        '/peapod/handler/iditarod/ZipHandler.storeClosedURL': '',
        '_D:/peapod/handler/iditarod/ZipHandler.storeClosedURL': '',
        '/peapod/handler/iditarod/ZipHandler.defaultGuestParameters': '',
        '_D:/peapod/handler/iditarod/ZipHandler.defaultGuestParameters': '',
        '_DARGS': '',
    }

    # it's really horrible but it seems all this data required for correct
    # search request
    SEARCH_URL = "http://www.peapod.com/search_results.jhtml?searchText="\
                 "{search_term}&_D%3AsearchText=+&x=0&y=0&%2Fpeapod%2F"\
                 "handler%2Fiditarod%2FSearchHandler.brandId=0&_D%3A%2F"\
                 "peapod%2Fhandler%2Fiditarod%2FSearchHandler.brandId=+&%2F"\
                 "peapod%2Fhandler%2Fiditarod%2FSearchHandler.categoryId="\
                 "0&_D%3A%2Fpeapod%2Fhandler%2Fiditarod%2FSearchHandler."\
                 "categoryId=+&%2Fpeapod%2Fhandler%2Fiditarod%2FSearch"\
                 "Handler.catNodeId=0&_D%3A%2Fpeapod%2Fhandler%2Fiditarod"\
                 "%2FSearchHandler.catNodeId=+&%2Fpeapod%2Fhandler%2F"\
                 "iditarod%2FSearchHandler.brand=&_D%3A%2Fpeapod%2Fhandler"\
                 "%2Fiditarod%2FSearchHandler.brand=+&%2Fpeapod%2Fhandler%2F"\
                 "iditarod%2FSearchHandler.category=&_D%3A%2Fpeapod%2Fhandler"\
                 "%2Fiditarod%2FSearchHandler.category=+&%2Fpeapod%2Fhandler"\
                 "%2Fiditarod%2FSearchHandler.search=0&_D%3A%2Fpeapod%2F"\
                 "handler%2Fiditarod%2FSearchHandler.search=+&start=1&sort"\
                 "={search_sort}&%2Fpeapod%2Fhandler%2Fiditarod%2FSearch"\
                 "Handler.locationId=27022&_D%3A%2Fpeapod%2Fhandler%2F"\
                 "iditarod%2FSearchHandler.locationId=+&results=standard"\
                 "&typeahead=0&pagesize=100&_DARGS=%2Ffr4_top.jhtml"

    SORT_MODES = {
        'default': '-searchScore,-userFrequency,-itemsPurchased',
        'best_match': '-searchScore,-userFrequency,-itemsPurchased',
        'alphabetical': '+itemLongName',
        'size': '+itemSizeCode,+itemLongName',
        'unit_price': '+unitPrice,+scaledBestPrice',
        'price': '+scaledBestPrice,+itemLongName',
        'specials': '-specialCode,+itemLongName',
    }

    def __init__(self, order='default', *args, **kwargs):
        if order not in self.SORT_MODES.keys():
            self.log("'%s' not in SORT_MODES. Used default for this session"
                     % order, WARNING)
            order = 'default'
        search_sort = self.SORT_MODES[order]
        super(PeapodProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=search_sort,
            ), *args, **kwargs
        )

    def start_requests(self):
        yield Request(self.start_url, callback=self.login_handler)

    def login_handler(self, response):
        form = response.xpath('//form[@name="zipEntryForm"]')
        url = form.xpath('@action').extract()[0]
        main_url = 'https://peapod.com/' + url
        # extract data required for POST request from form
        new_data = {}
        for key in self.formdata.keys():
            path = './/input[@name="%s"]/@value' % key
            value = form.xpath(path).extract()
            new_data[key] = str(value[0]).strip()
        # populate static info
        new_data['zipcode'] = self.default_zip
        new_data['memberType'] = 'C'
        new_data['_D:memberType'] = ''
        return FormRequest(main_url,
                           formdata=new_data,
                           callback=self.after_login,)

    def after_login(self, response):
        return super(PeapodProductsSpider, self).start_requests()

    def parse_product(self, response):
        prod = response.meta['product']
        prodxp = response.xpath('//div[@id="product"]/dl')

        title = prodxp.xpath(
            'dt/text()').extract()
        cond_set(prod, 'title', (is_empty(title).strip(),))

        price = prodxp.xpath(
            'dd[@class="productPrice"]/text()').extract()
        price = re.findall("\d*\.?\d+", is_empty(price))
        if not price:
            price_pattern = r"tm_price: '(.*)'"
            price = re.findall(price_pattern, response.body_as_unicode())
        prod["price"] = Price(
            priceCurrency="USD", price=is_empty(price)
        )

        des = response.xpath(
            '//div[@id="productDetails-details"]').extract()
        cond_set(prod, 'description', des)

        img_url = response.xpath(
            '//div[@id="productImageHolder"]/input/@value'
        ).extract()
        cond_set(prod, 'image_url', img_url)

        cond_set(prod, 'locale', ['en-US'])

        prod['url'] = response.url

        rp = []
        r_products_dl = response.xpath(
            '//div[@id="product_rr"]/div[contains(@class, "recsContainer")]/dl'
        )

        # related_products not populated at this moment
        if r_products_dl:
            for dl in r_products_dl:
                url = dl.xpath(
                    './/div[@class="recs_info"]/dt/a/@href'
                ).extract()
                title = dl.xpath(
                    './/div[@class="recs_info"]/dt/a/text()'
                ).extract()
                if url and title:
                    rp.append(RelatedProduct(title[0], url[0]))
        prod['related_products'] = {'recommended': rp}

        brand_pattern = r"tm_brand: '(.*)'"
        brand = re.findall(brand_pattern, response.body_as_unicode())
        if brand:
            brand = brand[0].replace('\\', '').strip()
            prod['brand'] = brand

        span_out_of_stock = response.xpath(
            '//span[@class="outOfStock"]'
        ).extract()
        if span_out_of_stock:
            cond_set_value(prod, 'is_out_of_stock', True)
        else:
            cond_set_value(prod, 'is_out_of_stock', False)
        return prod

    def _scrape_total_matches(self, response):
        total_matches = response.xpath(
            '//div[@id="SRResultCount"]/text()'
        ).extract()
        if total_matches:
            total_matches = re.findall("\d+", total_matches[0])

        return int(total_matches[0])

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[@class="SRProductsGridItemDesc"]/a/@href'
        ).extract()
        for link in links:
            l1 = "http://www.peapod.com/itemDetailView.jhtml?productId="
            l2 = re.findall('ntn\((\d+)', link)
            if l2:
                yield l1+l2[0], SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        next_link = response.xpath(
            '//td[@align="right"]/a[contains(text(), "Next")]/@href'
        ).extract()
        if next_link:
            return next_link[0]
        return None
