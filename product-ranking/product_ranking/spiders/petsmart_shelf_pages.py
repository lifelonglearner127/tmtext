import re
import string
import urllib

from scrapy import Request

from product_ranking.items import SiteProductItem
from petsmart import PetsmartProductsSpider



class PetsmartShelfPagesSpider(PetsmartProductsSpider):
    name = 'petsmart_shelf_urls_products'
    allowed_domains = ['petsmart.com']


    def _setup_class_compatibility(self):
        """ Needed to maintain compatibility with the SC spiders baseclass """
        self.quantity = 99999
        self.site_name = self.allowed_domains[0]
        self.user_agent_key = None
        self.current_page = 1


    def _setup_meta_compatibility(self):
        """ Needed to prepare first request.meta vars to use """
        return {'remaining': 99999, 'search_term': ''}.copy()


    def __init__(self, *args, **kwargs):
        super(PetsmartShelfPagesSpider, self).__init__(*args, **kwargs)
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
        if not re.match(r'http(s)?:\/\/', url):
            url = 'http://' + url
        return url


    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility())


    def _scrape_product_links(self, response):
        categories = response.xpath(
            '//li[contains(@class,"ws-breadcrumbs-list-item")]'
        ).xpath('string()').extract()
        shelf_categories = map(string.strip, categories[1:]) if categories else None
        shelf_category = categories[-1] if categories else None

        for link in response.xpath(self.XPATH['search']['prod_links']).extract():
            url = link.split('?')[0].split(';')[0]
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
        return super(
            PetsmartShelfPagesSpider, self
        )._scrape_next_results_page_link(response)


    def _total_matches_from_html(self, response):
        total_matches = response.xpath(
            '//a[contains(@class, "ws-product-listing-view-all-items")]/text()'
        ).extract()
        total_matches = map(
            lambda _: re.search(r'(\d+)\s+item', _, re.I),
            total_matches
        )
        if total_matches:
            return int(total_matches[0].group(1))
        else:
            return 0


