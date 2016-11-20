import re
import urlparse
import copy
import json

from scrapy.http import FormRequest

from product_ranking.items import SiteProductItem

is_empty = lambda x: x[0] if x else None

from .walgreens import WalGreensProductsSpider


class WalgreensShelfPagesSpider(WalGreensProductsSpider):
    name = 'walgreens_shelf_urls_products'
    allowed_domains = ["walgreens.com", "api.bazaarvoice.com"]  # without this find_spiders() fails

    AJAX_PRODUCT_LINKS_URL = "http://www.walgreens.com/svc/products/search"

    JSON_SEARCH_STRUCT = {"p": "1", "s": "20", "sort": "Top Sellers", "view": "allView",
                          "geoTargetEnabled": 'false', "id": "[{page_id}]", "requestType": "tier3",
                          "deviceType": "desktop",}# "closeMatch": 'false'}

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

        """
        # variants are switched off by default, see Bugzilla 3982#c11
        self.scrape_variants_with_extra_requests = False
        if 'scrape_variants_with_extra_requests' in kwargs:
            scrape_variants_with_extra_requests = kwargs['scrape_variants_with_extra_requests']
            if scrape_variants_with_extra_requests in (1, '1', 'true', 'True', True):
                self.scrape_variants_with_extra_requests = True
        """

    """
    @staticmethod
    def valid_url(url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url
    """

    @staticmethod
    def _get_page_id(url):
        _id = re.search('N=([\d\-]+)', url)
        if not _id:
            _id = re.search('ID=([\d\-]+)', url)
        if _id:
            return _id.group(1).replace('-', ',')

    def start_requests(self):
        self.page_id = self._get_page_id(self.product_url)

        json_struct = copy.deepcopy(self.JSON_SEARCH_STRUCT)
        json_struct['id'] = json_struct['id'].format(page_id=self.page_id)

        yield FormRequest(self.AJAX_PRODUCT_LINKS_URL,
                          meta=self._setup_meta_compatibility(),
                          formdata=json_struct)

    def _scrape_product_links(self, response):
        for j_product in json.loads(response.body).get('products', []):
            j_url = j_product.get('productInfo', {}).get('productURL', '')
            if j_url.startswith('/'):
                j_url = urlparse.urljoin(response.url, j_url)
            yield j_url, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        if self.current_page >= self.num_pages:
            return
        self.current_page += 1

        json_struct = copy.deepcopy(self.JSON_SEARCH_STRUCT)
        json_struct['id'] = json_struct['id'].format(page_id=self.page_id)
        json_struct['p'] = str(self.current_page)

        return FormRequest(self.AJAX_PRODUCT_LINKS_URL,
                          meta=self._setup_meta_compatibility(),
                          formdata=json_struct)

    """
    def parse_product(self, response):
        product = response.meta['product']
        # scrape Shelf Name, e.g. Diapers, and Shelf Path, e.g. Baby/Diapering/Diapers
        wcp = WalmartCategoryParser()
        wcp.setupSC(response)
        try:
            product['categories'] = wcp._categories_hierarchy()
        except Exception as e:
            self.log('Category not parsed: '+str(e), WARNING)
        try:
            product['category'] = wcp._category()
        except Exception as e:
            self.log('No department to parse: '+str(e), WARNING)
        response.meta['product'] = product
        return super(WalmartShelfPagesSpider, self).parse_product(response)
    """
