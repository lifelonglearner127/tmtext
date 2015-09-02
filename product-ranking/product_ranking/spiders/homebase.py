# todo:
#  reviews
#  related products
#  upc [none]
#  marketplace [none]


from scrapy import Request, FormRequest
from scrapy.log import ERROR, WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.guess_brand import guess_brand_from_first_words


class HomebaseProductSpider(BaseProductsSpider):
    name = 'homebase_products'
    allowed_domains = ['homebase.co.uk', 'recs.richrelevance.com',
                       'homebase.ugc.bazaarvoice.com']
    start_urls = []

    # url is the same for any request, all parameters passed via form data
    SEARCH_URL = ('http://www.homebase.co.uk/CategoryNavigationResultsView?'
                  'searchTermScope=&searchType=&filterTerm=&langId=110&'
                  'advancedSearch=&sType=SimpleSearch&metaData=&pageSize=12&'
                  'manufacturer=&filterType=&resultCatEntryType=&'
                  'catalogId=10011&searchForContent=false&categoryId=&'
                  'storeId=10201&filterFacet=')
    RESULTS_PER_PAGE = 43
    SORT_MODES = {
        'default': '1',
        'relevance': '1',  # default
        'price_asc': '3',  # price low to high
        'price_desc': '4',  # price high to low
        'rating': '5'  # customers rating, high to low
    }
    FORM_DATA = {
        'contentBeginIndex': 0,  # always 0
        'beginIndex': 0,  # set items offset
        'isHistory': False,
        'pageView': '',
        'resultType': 'products',
        'orderByContent': '',
        'searchTerm': 'phones',
        'storeId': 10201,
        'catalogId': 10011,
        'langId': 110,
        'pageFromName': 'SearchPage',
        'pagename': 'Search successful',
        'objectId': '',
        'requesttype': 'ajax',
        'productBeginIndex': 0,  # set items offset
        'orderBy': ''  # set order type
    }
    REVIEWS_URL = ('http://homebase.ugc.bazaarvoice.com/1494redes-en_gb/'
                   '{product_id}/reviews.djs?format=embeddedhtml')

    def __init__(self, sort_mode=None, *args, **kwargs):
        if sort_mode not in self.SORT_MODES:
            sort_mode = 'default'
        self.SORT = self.SORT_MODES[sort_mode]
        self.pages = dict()
        super(HomebaseProductSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for st in self.search_terms:
            form_data = self.FORM_DATA.copy()
            form_data['orderBy'] = self.SORT
            self.pages[st] = 1
            yield FormRequest(url=self.SEARCH_URL, form_data=form_data,
                              meta={'form_data': form_data})
        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            prod['search_term'] = ''
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod})

        if self.products_url:
            urls = self.products_url.split('||||')
            for url in urls:
                prod = SiteProductItem()
                prod['url'] = url
                prod['search_term'] = ''
                yield Request(url,
                              self._parse_single_product,
                              meta={'product': prod})

    def _scrape_product_links(self, response):
        items = response.css('.product_lister-product > '
                             '.product_lister-product-summary > '
                             'h4 > a::attr(href)').extract()
        for item in items:
            yield item

    def _scrape_total_matches(self, response):
        items = response.css('#totalProcCount::attr(value)').extract()
        try:
            return int(items[0])
        except (IndexError, ValueError) as e:
            self.log(str(e), ERROR)
            return 0

    def _scrape_results_per_page(self, response):
        items = response.css(
            '.product_lister-product > .product_lister-product-summary')
        per_page = int(len(items))
        if per_page != self.RESULTS_PER_PAGE:
            self.log('Got different results per page number', WARNING)
            self.RESULTS_PER_PAGE = per_page
        return per_page

    def _scrape_next_results_page_link(self, response):
        meta = response.meta.copy()
        st = meta['search_term']
        offset = self.pages[st] * self.RESULTS_PER_PAGE
        form_data = meta['form_data']
        form_data['beginIndex'] = offset
        form_data['productBeginIndex'] = offset
        self.pages[st] += 1
        return FormRequest(url=self.SEARCH_URL, formdata=form_data, meta=meta)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _populate_from_html(self, response, prod):
        cond_set(prod, 'title', response.xpath('/html/head/title/text()'))

        # price
        currency = response.css(
            'span[itemprop=priceCurrency]::text()').extract()
        price = response.css('#prodOfferPrice::attr(value)').extract()
        if currency and price:
            cond_set_value(prod, 'price', Price(price=price[0],
                                                priceCurrency=currency[0]))
        # image
        img = response.xpath(
            '/html/head/meta[@property="og:image"]/@content').extract()
        if img:
            cond_set_value(prod, 'image_url', 'http:%s' % img[0])
        # description
        cond_set(prod, 'description',
                 response.css('.product_detail-left-summary > div').extract())
        # brand
        brand = response.css('#supplier_shop img::attr(alt)').extract()
        if brand:
            brand = brand[0]
        else:
            brand = guess_brand_from_first_words(prod['title'])
        cond_set_value(prod, 'brand', brand)
        # model
        cond_set(prod, 'model', response.css('span[itemprop=sku]::text'),
                 unicode.strip)
        # out of stock
        cond_set_value(prod, 'is_out_of_stock',
                       response.css('.currently-out-of-stock'), bool)

    def parse_product(self, response):
        prod = response.meta['product']
        cond_set_value(
            prod, 'locale', response.headers.get('Content-Language', 'en-GB'))
        prod['url'] = response.url
        self._populate_from_html(response, prod)

        # todo: get urls for reviews and related
        return prod