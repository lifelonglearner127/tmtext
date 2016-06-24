import re
import urlparse
from product_ranking.items import SiteProductItem
from .drugstore import DrugstoreProductsSpider
from scrapy import Request


class DrugstoreShelfPagesSpider(DrugstoreProductsSpider):
    name = 'drugstore_shelf_urls_products'
    allowed_domains = ["drugstore.com",
                       "recs.richrelevance.com"]

    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = 99999
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.zip_code = '12345'
        self.current_page = 1

    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': 99999, 'search_term': ''}.copy()

    def __init__(self, *args, **kwargs):
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
        if not re.findall(r"http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility())  # meta is for SC baseclass compatibility

    def _scrape_product_links(self, response):
        urls = response.xpath('//div[@itemtype="http://schema.org/Product"]/'
                              'div[@class="info"]/'
                              'span/a[@class="oesLink"]/'
                              '@href').extract()
        urls = [urlparse.urljoin(response.url, x) if x.startswith('/') else x
                for x in urls]

        # parse shelf category
        shelf_categories = response.xpath('//td[@itemprop="breadcrumb"]/'
                                          'a[@class="srchLink"]/'
                                          'text()').extract()
        shelf_category = response.xpath('//td[@itemprop="breadcrumb"]//'
                                        'h1[@class="breadCrumbH1"]/'
                                        'text()').extract()
        shelf_categories += shelf_category
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
        return super(DrugstoreShelfPagesSpider,
                     self)._scrape_next_results_page_link(response)

    def parse_product(self, response):
        return super(DrugstoreShelfPagesSpider, self).parse_product(response)
