#http://www.staplesadvantage.com/webapp/wcs/stores/servlet/StplCategoryDisplay?catalogId=4&langId=-1&storeId=10101&act=8&backButtonClick=Y&brand=&catGroupName=&catId=-999999&clearurl=&currentSearchURL=&filetersrch=N&filterSearchNoResults=false&forceGallery=true&ggpCatId=&gpCatId=&histSortId=best_selling|descending&histSrchURL=&initialOnContractCount=&initialPrevOrderCount=0&interimURL=&isInterim=&isMSIE=false&isSimilarProd=&isSmartDeadEnds=&itemsPerPage=25&l4Count=&level=&model=&origAct=4&pCatId=&pg=1&pgs=25&prevTxy=&selSortOption=Top%20Rated&selectedNavForm=gallerynav&sortId=top_rated|descending&src=SRCH&term=apple&term=apple&tpvBrowse=false&txy=
#http://www.staplesadvantage.com/webapp/wcs/stores/servlet/StplCategoryDisplay?langId=-1&storeId=10101&act=8&catId=-999999&&filetersrch=N&filterSearchNoResults=false&selSortOption=Top%20Rated&sortId=top_rated|descending&src=SRCH&term=apple&tpvBrowse=false
#http://www.staplesadvantage.com/webapp/wcs/stores/servlet/StplCategoryDisplay?act=8&filetersrch=N&filterSearchNoResults=false&selSortOption=Top%20Rated&sortId=best_match|descending&src=SRCH&term=apple&tpvBrowse=false
import re

from scrapy import Request

from .contrib.product_spider import ProductsSpider


class StaplesadvantageProductsSpider(ProductsSpider):
    name = "staplesadvantage_products"

    allowed_domains = ['staplesadvantage.com']

    SEARCH_URL = "http://www.staplesadvantage.com/webapp/wcs/stores/servlet" \
                 "/StplCategoryDisplay" \
                 "?act=8&filetersrch=N&filterSearchNoResults=false" \
                 "&selSortOption=Top%20Rated" \
                 "&sortId={sort_mode}&src=SRCH&term={search_term}" \
                 "&tpvBrowse=false&pg={page}"

    START_URL = 'http://www.staplesadvantage.com/learn?storeId=10101'

    SORT_MODES = {
        'default': 'Rel|descending',
        'relevance': 'Rel|descending',
        'rating': 'top_rated|descending',
        'best': 'best_selling|descending'
    }

    def __init__(self, *args, **kwargs):
        super(StaplesadvantageProductsSpider, self).__init__(*args, **kwargs)
        self.url_formatter.defaults['page'] = 1

    def start_requests(self):
        requests = super(StaplesadvantageProductsSpider, self).start_requests()
        return [Request(self.START_URL, self._begin_search,
                        meta={'requests': requests})]

    def _begin_search(self, response):
        return response.meta['requests']

    def _total_matches_from_html(self, response):
        total = response.css('.didYouMeanNoOfItems').extract()
        if not total: return 0
        total = re.search('[\d,]+', total[0])
        return int(total.group().replace(',', '')) if total else 0

    def _scrape_next_results_page_link(self, response):
        if not self._fetch_product_boxes(response):
            return None
        page = response.meta.get('page', 1)
        search_term = response.meta['search_term']
        response.meta['page'] = page + 1
        return self.url_formatter.format(self.SEARCH_URL,
                                         search_term=search_term,
                                         page=page + 1)

    def _fetch_product_boxes(self, response):
        return response.css('.productdescription')

