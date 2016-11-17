from __future__ import division, absolute_import, unicode_literals

import re

from scrapy.log import WARNING
from scrapy.http import Request
from scrapy import FormRequest

from product_ranking.items import SiteProductItem, Price, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults,\
    cond_set, cond_set_value
from product_ranking.guess_brand import guess_brand_from_first_words

is_empty = lambda x: x[0] if x else ""


class PeapodProductsSpider(BaseProductsSpider):
    """Spider for peapod.com.

    This site require authorization. For this reason we enter one time
    visitor zipcode. It should be from peapod.com coverage area.

    Not populated fields:
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
    'aisle/dept'
    'most_popular'
    'calories'
    'fat'
    'trans_fat'
    'carbohydrates'
    'cholesterol'
    'dietary_fiber'
    'gluten_free'
    'kosher'
    'organic'
    'protein'
    'sodium'
    'sugar'

    Example command:
    scrapy crawl -a peapod_products searchterms_str="tea"
    [-a order="default"] [-a fetch_related_products=True]
    """
    name = "peapod_products"
    allowed_domains = ["peapod.com",
                       "res-x.com"]

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
                 "&typeahead=0&pagesize=200&_DARGS=%2Ffr4_top.jhtml"

    SORT_MODES = {
        'default': '-searchScore,-userFrequency,-itemsPurchased',
        'best_match': '-searchScore,-userFrequency,-itemsPurchased',
        'alphabetical': '+itemLongName',
        'size': '+itemSizeCode,+itemLongName',
        'unit_price': '+unitPrice,+scaledBestPrice',
        'price': '+scaledBestPrice,+itemLongName',
        'specials': '-specialCode,+itemLongName',
        'aisle/dept': '+consumProdCategoryId,+itemLongName',
        'most_popular': '-itemsPurchased,+itemLongName',
        'calories': '+totalCalories,+itemLongName',
        'fat': '+totalFat,+itemLongName',
        'trans_fat': '+transFatQy,+itemLongName',
        'carbohydrates': '+totalCarbohydrates,+itemLongName',
        'cholesterol': '+cholesterol,+itemLongName',
        'dietary_fiber': '-dietaryFiber,+itemLongName',
        'gluten_free': '-glutenFlag,+itemLongName',
        'kosher': '-kosher,+kshr1Id,+itemLongName',
        'organic': '-organic,+itemLongName',
        'protein': '-protein,+itemLongName',
        'sodium': '+sodium,+itemLongName',
        'sugar': '+sugar,+itemLongName',
    }

    def __init__(self, order='default', fetch_related_products=True,
                 zip_code=None, *args, **kwargs):
        from scrapy.conf import settings
        settings.overrides['DEPTH_PRIORITY'] = 1
        settings.overrides[
            'SCHEDULER_DISK_QUEUE'] = 'scrapy.squeue.PickleFifoDiskQueue'
        settings.overrides[
            'SCHEDULER_MEMORY_QUEUE'] = 'scrapy.squeue.FifoMemoryQueue'

        if zip_code and zip_code != 'default':
            self.default_zip = zip_code

        if fetch_related_products == "False":
            self.fetch_related_products = False
        else:
            self.fetch_related_products = True
        if order not in self.SORT_MODES.keys():
            self.log("'%s' not in SORT_MODES. Used default for this session"
                     % order, WARNING)
            order = 'default'
        search_sort = self.SORT_MODES[order]
        super(PeapodProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
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
        new_data['zip_code'] = self.default_zip
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

        brand_pattern = r"tm_brand: '(.*)'"
        brand = re.findall(brand_pattern, response.body_as_unicode())
        if not brand:
            brand = guess_brand_from_first_words(prod['title'])
        if brand and brand[0]:
            brand = brand[0].replace('\\', '').strip()
            prod['brand'] = brand

        span_out_of_stock = response.xpath(
            '//span[@class="outOfStock"]'
        ).extract()
        if span_out_of_stock:
            cond_set_value(prod, 'is_out_of_stock', True)
        else:
            cond_set_value(prod, 'is_out_of_stock', False)

        if self.fetch_related_products:
            # continue requests to get related products
            return self._request_related_products(response)
        else:
            return prod

    def _request_related_products(self, response):
        url = self._get_recommendations_url(response)
        yield Request(url, self._get_related_products, meta=response.meta)

    def _get_recommendations_url(self, response):
        url = response.meta['product']['url']
        prod_id = re.findall(r"productId=(\d+)", url)
        root_url = "https://www.res-x.com/ws/r2/Resonance.aspx?appid"\
                   "=peapod01&tk=281487701926380&ss=152382991509512&sg"\
                   "=1&vr=5.3x&bx=true&sc=product1_rr&ev=product&ei={prod_id}"\
                   "&cu=1011100700&no=3&ex={prod_id}&storeid=38&storeprice="\
                   "38_38&pricezone=38&ccb=recService.processRec&"\
                   "cv12=38&plk=&rf="
        if prod_id:
            request_url = root_url.format(prod_id=prod_id[0])
            return request_url

    def _get_related_products(self, response):
        ids = re.findall(r'"id":"(\d+)"', response.body_as_unicode())
        root_url = "https://www.peapod.com/frags/recommendations/"\
                   "frag_rec.jhtml?recsContainerClass=itemDetail&rrelem"\
                   "=product1_rr&zipCityId=96019&storeId=38&pids="
        url = root_url + ','.join(ids)
        return Request(url, callback=self._parse_related_products,
                       meta=response.meta, dont_filter=True)

    def _parse_related_products(self, response):
        prod = response.meta['product']
        rp = []
        recs_info = response.xpath(
            '//div[@class="recs_info"]'
        )
        if recs_info:
            for info in recs_info:
                url = info.xpath('.//dt/a/@href').extract()
                if url:
                    url = 'http://www.peapod.com/' + url[0]
                title = info.xpath('.//dt/a/text()').extract()
                if url and title:
                    rp.append(RelatedProduct(title[0], url))
        prod['related_products'] = {'recommended': rp}
        return prod

    def _scrape_total_matches(self, response):
        total_matches = response.xpath(
            '//div[@id="SRResultCount"]/text()'
        ).extract()
        if total_matches:
            total_matches = re.findall("\d+", total_matches[0])
            if total_matches:
                return int(total_matches[0])
            return 0

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

    def _parse_single_product(self, response):
        return self.parse_product(response)

