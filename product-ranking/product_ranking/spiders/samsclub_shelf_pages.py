from __future__ import division, absolute_import, unicode_literals
from .samsclub import SamsclubProductsSpider
from scrapy.http import Request, FormRequest
from product_ranking.items import SiteProductItem
from scrapy.log import DEBUG, WARNING, ERROR
import urlparse
import socket
import math


class SamsclubShelfPagesSpider(SamsclubProductsSpider):
    name = 'samsclub_shelf_urls_products'
    allowed_domains = ["samsclub.com", "api.bazaarvoice.com"]

    _NEXT_SHELF_URL = "http://www.samsclub.com/sams/shop/common/ajaxSearchPageLazyLoad.jsp?sortKey=p_sales_rank" \
                      "&searchCategoryId={category_id}&searchTerm=null&noOfRecordsPerPage={prods_per_page}" \
                      "&sortOrder=0&offset={offset}" \
                      "&rootDimension=0&tireSearch=&selectedFilter=null&pageView=list&servDesc=null&_=1407437029456"

    def __init__(self, *args, **kwargs):
        super(SamsclubShelfPagesSpider, self).__init__(clubno='4704', zip_code='94117', *args, **kwargs)
        self.prods_per_page = 48
        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0
        self.current_page = 1

    def start_requests(self):
        yield Request(
            url="http://www.samsclub.com/",
            meta={'club': 1})

    @staticmethod
    def _parse_shelf_path(response):
        breadcrumbs = response.xpath('//*[@id="breadCrumbs"]//span/a/text()').extract()
        """<h1 class="catLeftTitle plp-catLeftTitle">TVs &amp; Displays</h1>"""
        shelf_name = response.xpath('//h1[contains(@class, "catLeftTitle")]/text()').extract()
        return breadcrumbs + shelf_name

    def _scrape_product_links(self, response):
        links = response.xpath('//a[contains(@class, "cardProdLink")]/@href').extract()
        for link in links:
            item = SiteProductItem()
            item['shelf_path'] = self._parse_shelf_path(response)
            item['shelf_name'] = item['shelf_path'][-1]
            yield link, item

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
            return Request(
                self.product_url,
                meta={'search_term': '',
                      'remaining': self.quantity,
                      'club': 4})

        elif club == 4:
            return super(SamsclubProductsSpider, self).parse(response)

    def _scrape_total_matches(self, response):
        return int(response.xpath('//script[contains(text(), "totalRecords")]/text()').re("'totalRecords':'(\d+)'")[0])

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        pages = math.ceil(self._scrape_total_matches(response) / float(self.prods_per_page))
        if self.current_page <= pages:
            return self._set_next_results_page_url()

    def _get_next_products_page(self, response, prods_found):
        return super(SamsclubProductsSpider, self)._get_next_products_page(response, prods_found)

    def _set_next_results_page_url(self):
        scheme, netloc, path, query_string, fragment = urlparse.urlsplit(self.product_url)
        query_string = 'offset={}&navigate={}'.format(
            self.prods_per_page * (self.current_page - 1),
            self.current_page)
        return urlparse.urlunsplit((scheme, netloc, path, query_string, fragment))
