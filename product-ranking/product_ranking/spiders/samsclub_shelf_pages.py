from __future__ import division, absolute_import, unicode_literals
from .samsclub import SamsclubProductsSpider
import re
from scrapy.http import Request, FormRequest
from product_ranking.items import SiteProductItem
from scrapy.log import DEBUG, WARNING
import urlparse
import json
from math import ceil

is_empty = lambda x: x[0] if x else None

class SamsclubShelfPagesSpider(SamsclubProductsSpider):
    name = 'samsclub_shelf_urls_products'
    allowed_domains = ["samsclub.com", "api.bazaarvoice.com"]

    _NEXT_SHELF_URL = "http://www.samsclub.com/sams/shop/common/ajaxSearchPageLazyLoad.jsp?sortKey=p_sales_rank" \
                      "&searchCategoryId={category_id}&searchTerm=null&noOfRecordsPerPage={prods_per_page}" \
                      "&sortOrder=0&offset={offset}" \
                      "&rootDimension=0&tireSearch=&selectedFilter=null&pageView=list&servDesc=null&_=1407437029456"

    def __init__(self, *args, **kwargs):
        super(SamsclubShelfPagesSpider, self).__init__(clubno='4704', zip_code='94117', *args, **kwargs)
        self.current_page = 0
        self.prods_per_page = 18
        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0
        self.quantity = self.num_pages * self.prods_per_page
        if "quantity" in kwargs:
            self.quantity = int(kwargs['quantity'])

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
            return Request(self.product_url, callback=self._get_shelf_path_from_firstpage ,meta={
                'search_term': '',
                'remaining': self.quantity,
                'club': 4})

        elif club == 4:
            return super(SamsclubProductsSpider, self).parse(response)

    def _get_shelf_path_from_firstpage(self, response):
        shelf_categories = [c.strip() for c in response.xpath('.//ol[@id="breadCrumbs"]/li//a/text()').extract()
                            if len(c.strip()) > 1]

        shelf_category = shelf_categories[-1] if shelf_categories else None
        total_matches = self._scrape_total_matches(response)
        if total_matches:
            try:
                # determining final amount of pages to scrape
                self.num_pages = min(ceil(int(total_matches)/float(self.prods_per_page)),self.num_pages)
            except BaseException:
                pass
        return Request(self._NEXT_SHELF_URL.format(
            category_id=self._get_category_id(response),
            offset=0,
            prods_per_page=self.prods_per_page), meta={
            'shelf_path': shelf_categories,
            'shelf_name': shelf_category,
            'total_matches':total_matches,
            'search_term': '',
            'remaining': self.quantity,
            'club': 4},
            dont_filter=True)

    def _scrape_product_links(self, response):
        if response.url.find('ajaxSearch') > 0:
            shelf_category = response.meta.get('shelf_name')
            shelf_categories = response.meta.get('shelf_path')
            total_matches = response.meta.get('total_matches', 0)
            urls = response.xpath("//body/ul/li/a/@href").extract()
            if not urls:
                urls = response.xpath('//*[contains(@href, ".ip") and contains(@href, "/sams/")]/@href').extract()
            if urls:
                urls = [urlparse.urljoin(response.url, x) for x in urls if x.strip()]
            for url in urls:
                item = response.meta.get('product', SiteProductItem())
                item['total_matches'] = total_matches
                if shelf_category:
                    item['shelf_name'] = shelf_category
                if shelf_categories:
                    item['shelf_path'] = shelf_categories
                yield url, item
        else:
            self.log("This method should not be called with such url {}".format(
                response.url), WARNING)

    def _scrape_next_results_page_link(self, response, remaining):
        prods_per_page = self._get_items_per_page(response)
        if prods_per_page:
            self.prods_per_page = prods_per_page
        if self.current_page >= int(self.num_pages):
            return None
        else:
            self.current_page += 1
            return self._NEXT_SHELF_URL.format(
                category_id=self._get_category_id(response),
                offset=self.current_page * self.prods_per_page,
                prods_per_page=self.prods_per_page)

    @staticmethod
    def _get_category_id(response):
        cat_id = None
        if response.url.find('ajaxSearch') > 0:
            js_text = response.xpath('//script[@id="tb-djs-hubbleParams"]/text()').extract()
            js_text = js_text[0] if js_text else None
            if js_text:
                jsn = json.loads(js_text)
                cat_id = jsn.get('constraint', None)
            if not cat_id:
                rgx = r'searchCategoryId=(\d+)'
                match_list = re.findall(rgx, response.url)
                cat_id = match_list[0] if match_list else None
        else:
            js_text = response.xpath('//script[contains(text(), "searchInfo")]/text()').extract()
            js_text = js_text[0] if js_text else None
            try:
                js_text = js_text.split(';')[0].split('=')[1].strip().replace("'", '"')
                jsn = json.loads(js_text)
                cat_id = jsn.get('searchCategoryId', None)
            except BaseException:
                cat_id = None
            if not cat_id:
                rgx = r'\/(\d+).cp'
                match_list = re.findall(rgx, response.url)
                cat_id =  match_list[0] if match_list else None
        return cat_id

    @staticmethod
    def _get_items_per_page(response):
        js_text = response.xpath('//script[contains(text(), "searchInfo")]/text()').extract()
        js_text = js_text[0] if js_text else None
        try:
            js_text = js_text.split(';')[0].split('=')[1].strip().replace("'", '"')
            jsn = json.loads(js_text)
            itm_per_page = jsn.get('numberOfRecordsRequested', None)
            itm_per_page = int(itm_per_page) if itm_per_page else None
        except BaseException:
            itm_per_page = None
        return itm_per_page

    def _scrape_total_matches(self, response):
        if response.url.find('ajaxSearch') > 0:
            items = response.xpath("//body/li[contains(@class,'item')]")
            return len(items)
        totals = response.xpath(
            "//div[contains(@class,'shelfSearchRelMsg2')]"
            "/span/span[@class='gray3']/text()"
        ).extract()
        if not totals:
            totals = response.xpath('//*[@class="resultsfound"]/span[@ng-show="!clientAjaxCall"]/text()').extract()
        if totals:
            total = int(totals[0])
        else:
            js_text = response.xpath('//script[contains(text(), "searchInfo")]/text()').extract()
            js_text = js_text[0] if js_text else None
            try:
                js_text = js_text.split(';')[0].split('=')[1].strip().replace("'", '"')
                jsn = json.loads(js_text)
                total = jsn.get('totalRecords', None)
                total = int(total) if total else None
            except BaseException:
                rgx = r'totalRecords[\'\:]+(\d+)'
                try:
                    match_list = re.findall(rgx, js_text)
                    total = int(match_list[0]) if match_list else None
                except TypeError:
                    total = None
            if not total:
                js_text = response.xpath('//script[@id="tb-djs-hubbleParams"]/text()').extract()
                js_text = js_text[0] if js_text else None
                if js_text:
                    jsn = json.loads(js_text)
                    total = jsn.get('total_results', None)
                    total = int(total) if total else None
        return total