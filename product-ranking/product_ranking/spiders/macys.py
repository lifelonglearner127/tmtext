import urllib
import string
import urlparse

from scrapy.log import INFO
from scrapy import Request

from product_ranking.items import SiteProductItem
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value, FormatterWithDefaults
from product_ranking.spiders.products_test_suit import init_testsuit


@init_testsuit
class MacysProductsSpider(BaseProductsSpider):
    name = 'macys_products'
    allowed_domains = ['macys.com']
    SEARCH_URL = "http://www1.macys.com/shop/search?keyword={search_term}&x=0&y=0&sortBy={sort_mode}&pageIndex={page}"

    SORT_MODES = {
        'default': 'PRICE_LOW_TO_HIGH',
        'featured': 'ORIGINAL',
        'price_asc': 'PRICE_LOW_TO_HIGH',
        'price_desc': 'PRICE_HIGH_TO_LOW',
        'rating': 'TOP_RATED',
        'best_sellers': 'BEST_SELLERS',
        'new': 'NEW_ITEMS'
    }

    def __init__(self, sort_mode='default', *args, **kwargs):
        self.sort_mode = self.SORT_MODES.get(sort_mode, 'PRICE_LOW_TO_HIGH')
        formatter = FormatterWithDefaults(sort_mode=sort_mode, page=1)
        super(MacysProductsSpider, self).__init__(formatter, *args, **kwargs)


    def start_requests(self):  # Stolen from walmart
        for request in super(MacysProductsSpider, self).start_requests():
            request.meta['dont_redirect'] = True
            request.meta['handle_httpstatus_list'] = [302]
            request.meta['page'] = 1
            yield request

    def parse(self, response):  # Stolen again
        if response.status == 302:
            yield self._create_from_redirect(response)
        else:
            for request in super(MacysProductsSpider, self).parse(response):
                request.meta['dont_redirect'] = True
                request.meta['handle_httpstatus_list'] = [302]
                yield request

    def _create_from_redirect(self, response):  # Thanks walmart
        # Create comparable URL tuples.
        redirect_url = response.url
        redirect_url_split = urlparse.urlsplit(redirect_url)
        redirect_url_split = redirect_url_split._replace(
            query=urlparse.parse_qs(redirect_url_split.query))
        original_url_split = urlparse.urlsplit(response.request.url)
        original_url_split = original_url_split._replace(
            query=urlparse.parse_qs(original_url_split.query))

        if redirect_url_split == original_url_split:
            self.log("Found identical redirect!", INFO)
            request = response.request.replace(dont_filter=True)
        else:
            self.log("Found legit redirect!", INFO)
            request = response.request.replace(url=redirect_url)
        request.meta['dont_redirect'] = True
        request.meta['handle_httpstatus_list'] = [302]
        return request

    def _scrape_total_matches(self, response):
        try:
            return int(response.css('#productCount::text').extract()[0].strip())
        except (ValueError, IndexError):
            return 0

    def _scrape_product_links(self, response):
        for box in response.css('.productThumbnail'):
            product = SiteProductItem()
            url = box.css('.shortDescription a::attr(href)').extract()[0]
            cond_set(product, 'title', box.css('.shortDescription a::text').extract(), string.strip)
            cond_set(product, 'price', box.css('.prices span::text').extract())
            cond_set(product, 'image_url',
                     response.css('[id^=main_images_holder_] img[id^=image]::attr(src)').extract())
            yield url, product

    def _scrape_next_results_page_link(self, response):
        anchors = response.css('#paginateTop a::text').extract()
        anchors = filter(lambda s: s.isdigit(), anchors)
        if len(anchors) > 1:
            last_page = int(anchors[-1])
            if last_page <= response.meta['page']:
                return None
            page = response.meta['page'] + 1
            url = self.url_formatter.format(self.SEARCH_URL,
                                            search_term=urllib.quote_plus(response.meta['search_term']),
                                            page=page, sort_mode=self.sort_mode)
            meta = response.meta.copy()
            meta['page'] = page
            return Request(url, meta=meta)
        else:
            return None


    def parse_product(self, response):
        """
        @returns items 1 1
        @scrapes title description locale
        """
        product = response.meta.get('product', SiteProductItem())
        cond_set(product, 'title', response.css('#productTitle::text').extract())
        cond_set_value(product, 'description',
                       response.xpath('//*[@id="memberProductDetails"]/node()[normalize-space()]').extract(), ''.join)
        cond_set(product, 'locale', response.css('#headerCountryFlag::attr(title)').extract())
        cond_set(product, 'brand', response.css('#brandLogo img::attr(alt)').extract())
        return product
        

