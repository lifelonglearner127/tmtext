from .samsclub import SamsclubProductsSpider
import re
from scrapy.http import Request
import urlparse
from product_ranking.items import SiteProductItem

is_empty = lambda x: x[0] if x else None

class SamsclubShelfPagesSpider(SamsclubProductsSpider):
    name = 'samsclub_shelf_urls_products'
    allowed_domains = ["samsclub.com"]

    _NEXT_SHELF_URL = "http://www.samsclub.com/sams/shop/common/ajaxSearchPageLazyLoad.jsp?sortKey=p_sales_rank" \
                      "&searchCategoryId={category_id}&searchTerm=null&noOfRecordsPerPage={prods_per_page}" \
                      "&sortOrder=0&offset={offset}" \
                      "&rootDimension=0&tireSearch=&selectedFilter=null&pageView=list&servDesc=null&_=1407437029456"

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
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0

        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
                          " AppleWebKit/537.36 (KHTML, like Gecko)" \
                          " Chrome/37.0.2062.120 Safari/537.36"

    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url),
                      meta=self._setup_meta_compatibility())  # meta is for SC baseclass compatibility

    def _scrape_product_links(self, response):
        item = response.meta.get('product', SiteProductItem())
        meta = response.meta
        if response.url.find('ajaxSearch') > 0:
            urls = response.xpath("//body/ul/li/a/@href").extract()
        else:
            urls = response.xpath('.//a[@class="cardProdLink ng-scope" or @class="cardProdLink"]/@href').extract()
        if not urls:
            urls = response.xpath('//*[contains(@href, ".ip") and contains(@href, "/sams/")]/@href').extract()
        if urls:
            urls = [urlparse.urljoin(response.url, x) for x in urls if x.strip()]

        shelf_categories = [c.strip() for c in response.xpath('.//ol[@id="breadCrumbs"]/li//a/text()').extract()
                            if len(c.strip()) > 1]
        shelf_category = shelf_categories[-1] if shelf_categories else None

        for url in urls:
            item = SiteProductItem()
            if shelf_category:
                item['shelf_name'] = shelf_category
            if shelf_categories:
                item['shelf_path'] = shelf_categories
            yield url, item