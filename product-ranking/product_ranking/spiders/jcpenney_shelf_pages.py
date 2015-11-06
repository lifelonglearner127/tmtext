import re
import urlparse

from scrapy.http import Request

from product_ranking.items import SiteProductItem
from .jcpenney import JcpenneyProductsSpider

is_empty = lambda x: x[0] if x else None


class JCPenneyShelfPagesSpider(JcpenneyProductsSpider):
    name = 'jcpenney_shelf_urls_products'
    allowed_domains = ['jcpenney.com', 'www.jcpenney.com']

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = 99999
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.zipcode = '12345'
        self.current_page = 1

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': 99999, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
        super(JCPenneyShelfPagesSpider, self).__init__(*args, **kwargs)
        self._setup_class_compatibility()
        self.product_url = kwargs['product_url']
        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1
        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
                          " AppleWebKit/537.36 (KHTML, like Gecko)" \
                          " Chrome/37.0.2062.120 Safari/537.36"

        # variants are switched off by default, see Bugzilla 3982#c11
        self.scrape_variants_with_extra_requests = False
        if 'scrape_variants_with_extra_requests' in kwargs:
            scrape_variants_with_extra_requests = kwargs['scrape_variants_with_extra_requests']
            if scrape_variants_with_extra_requests in (1, '1', 'true', 'True', True):
                self.scrape_variants_with_extra_requests = True

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility())

    def _scrape_product_links(self, response):
        urls = response.xpath(
            '//div[contains(@class, "product_description")]'
            '//img[contains(@id, "ThumbnailImage")]/../../../a/@href'
        ).extract()
        urls = [urlparse.urljoin(response.url, x) if x.startswith('/') else x
                for x in urls]

        sample = response.xpath('//div[@id="breadcrumb"]/'
                                'ul/li//text()').extract()
        shelf_categories = [i.strip() for i in sample if i.strip() and i != '>']
        shelf_category = shelf_categories[-1] if shelf_categories else None

        urls = ["".join(i.replace('http://www.jcpenney.com', '')) for i in urls]

        for url in urls:
            item = SiteProductItem()
            if shelf_categories:
                item['shelf_name'] = shelf_categories
            if shelf_category:
                item['shelf_path'] = shelf_category
            yield url, item

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1
        return super(JCPenneyShelfPagesSpider,
                     self)._scrape_next_results_page_link(response)

    def parse_product(self, response):
        return super(JCPenneyShelfPagesSpider, self).parse_product(response)
