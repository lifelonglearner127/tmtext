import re
import urllib
import json
import urlparse
from product_ranking.items import SiteProductItem
from .zulily import ZulilyProductsSpider
from scrapy import Request
from scrapy.log import DEBUG


class ZulilyShelfPagesSpider(ZulilyProductsSpider):
    name = 'zulily_shelf_pages_products'
    allowed_domains = ["zulily.com", "www.res-x.com"]
    LOG_IN_URL = "https://www.zulily.com/auth"
    BASE_URL = "http://www.zulily.com/"

    def __init__(self, *args, **kwargs):
        super(ZulilyShelfPagesSpider, self).__init__(*args, **kwargs)
        self.product_url = kwargs['product_url']

        if "page" in kwargs:
            self.num_pages = int(kwargs['page'])
        else:
            self.num_pages = 1
        self.current_page = 1
        #settings.overrides['CRAWLERA_ENABLED'] = True

    def start_requests(self):
        #Category
        event_id = re.findall(r"/e/.*-((\d)+)\.html", self.product_url)
        if event_id:
            url = self.BASE_URL + "event/" + event_id[0][0]
            yield Request(
                self.product_url,
                meta={'remaining':self.quantity, "search_term":''},
                headers=self._get_antiban_headers()
            )

        #Search
        parsed = urlparse.urlparse(self.product_url)

        if urlparse.parse_qs(parsed.query)['fromSearch']:
            search_term = urlparse.parse_qs(parsed.query)['searchTerm']
            url = self.BASE_URL + "mainpanel/search_carousel/?q=" + search_term
        yield Request(
            url,
            meta={'remaining': self.quantity, "search_term": ''},
            headers=self._get_antiban_headers()
        )

    @staticmethod
    def _get_antiban_headers():
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0',
            'Connection': 'keep-alive',
            'Accept-Language': 'en-US,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'X-Requested-With' : 'XMLHttpRequest',
            'Accept-Encoding': 'gzip, deflate, sdch'
        }
    @staticmethod
    def valid_url(url):
        if not re.findall(r"http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def _scrape_product_links(self, response):
        urls = response.xpath(
            "//ul[contains(@class,'products-grid')]/li//a[contains(@class, 'product-image')]/@href").extract()
        urls = [urlparse.urljoin(response.url, x) if x.startswith('/') else x
                for x in urls]

        if not urls:
            self.log("Found no product links.", DEBUG)

        # parse shelf category
        shelf_categories = response.xpath(
            '//ul[@id="headerCrumb"]/li//text()').extract()
        shelf_categories = [category.strip() for category in shelf_categories]
        shelf_categories = filter(None, shelf_categories)
        try:
            shelf_name = response.xpath('//meta[@name="og:title"]/@content').extract()[0].strip()
        except IndexError:
            pass
        for url in urls:
            if url in self.product_filter:
                continue
            self.product_filter.append(url)
            item = SiteProductItem()
            if shelf_categories:
                if shelf_categories:
                    item['shelf_name'] = shelf_name
                    item['shelf_path'] = shelf_categories[1:]
            yield url, item

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        return super(ZulilyShelfPagesSpider,
                     self)._scrape_next_results_page_link(response)

    def parse_product(self, response):
        return super(ZulilyShelfPagesSpider, self).parse_product(response)
