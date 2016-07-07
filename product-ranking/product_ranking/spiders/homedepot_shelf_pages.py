import re
import urlparse
from product_ranking.items import SiteProductItem
from .homedepot import HomedepotProductsSpider
from scrapy import Request
from scrapy.conf import settings
from scrapy.log import DEBUG


class HomedepotShelfPagesSpider(HomedepotProductsSpider):
    name = 'homedepot_shelf_pages_products'
    allowed_domains = ["homedepot.com", "www.res-x.com"]

    def __init__(self, *args, **kwargs):
        super(HomedepotShelfPagesSpider, self).__init__(*args, **kwargs)
        self.product_url = kwargs['product_url']

        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1
        self.current_page = 1
        settings.overrides['CRAWLERA_ENABLED'] = True

    @staticmethod
    def valid_url(url):
        if not re.findall(r"http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta={'remaining': self.quantity,
                            'search_term': ''})

    def _scrape_product_links(self, response):
        urls = response.xpath(
            "//div[contains(@class,'product') "
            "and contains(@class,'plp-grid')]"
            "//descendant::a[contains(@class, 'item_description')]/@href").extract()

        if not urls:
            self.log("Found no product links.", DEBUG)

        for link in links:
            if link in self.product_filter:
                continue
            self.product_filter.append(link)
        # parse shelf category
        shelf_categories =  response.xpath('//ul[@id="headerCrumb"]/li/a/text()'
                                           ).extract()
        for url in urls:
            item = SiteProductItem()
            if shelf_categories:
                if shelf_categories:
                    item['shelf_name'] = shelf_categories[-1]
                    item['shelf_path'] = shelf_categories[1:]
            yield url, item

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        return super(HomedepotShelfPagesSpider,
                     self)._scrape_next_results_page_link(response)

    def parse_product(self, response):
        return super(HomedepotShelfPagesSpider, self).parse_product(response)
