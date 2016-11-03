from urllib import quote, urlencode

#http://www.staplesadvantage.com/webapp/wcs/stores/servlet/StplCategoryDisplay?catalogId=4&langId=-1&storeId=10101&act=8&currentSearchURL=http%3A%2F%2Fmdex-sa-us-prod-n.staples.com%2Fassembler%2Fgallery%3Fformat%3Djson%26billtoValue%3D1000203%26shiptoValue%3DGUESTSHIP%26divValue%3DHOU%26maValue%3D0001818309001HOU%26uid%3D-1002%26contractValue%3DHOU0000000410%26blockType%3DX%26isWholeSalerAllowed%3DY%26%26Ntt%3Dapple%2Bblack%2Biphone%26isSmartDeadEnds%3DN%26referrer%3Dsagallery%26Nrpp%3D25%26No%3D0&filetersrch=N&filterSearchNoResults=false&forceGallery=true&ggpCatId=&gpCatId=&histSortId=Rel|descending&histSrchURL=&initialOnContractCount=&initialPrevOrderCount=0&interimURL=&isInterim=&isMSIE=false&isSimilarProd=&isSmartDeadEnds=&itemsPerPage=25&l4Count=&level=&model=&origAct=4&pCatId=&pg=1&pgs=25&prevTxy=&selSortOption=Top%20Rated&selectedNavForm=gallerynav&sortId=top_rated|descending&src=SRCH&srchurl=O8MpYrswxCADTA3Daf7YMC3KiUrlF5xOIis2DiO%2FW6kNijD5LxJO39lbtAMCvx9z5kEc9tBH8LFyLkuKq8E8ZoGSZkoNerFQSD0ZIkp79vppQuIK3LB2oZpqelDHkrAQrTL7INv1ZTk%3D&term=apple%20black%20iphone&term=apple%20black%20iphone&tpvBrowse=false&txy=
#http://www.staplesadvantage.com/webapp/wcs/stores/servlet/StplCategoryDisplay?catalogId=4&langId=-1&storeId=10101&act=8&filetersrch=N&filterSearchNoResults=false&forceGallery=true&ggpCatId=&gpCatId=&histSortId=Rel|descending&histSrchURL=&initialOnContractCount=&initialPrevOrderCount=0&interimURL=&isInterim=&isMSIE=false&isSimilarProd=&isSmartDeadEnds=&itemsPerPage=25&l4Count=&level=&model=&origAct=4&pCatId=&pg=1&pgs=25&prevTxy=&selSortOption=Top%20Rated&selectedNavForm=gallerynav&sortId=top_rated|descending&src=SRCH&srchurl=O8MpYrswxCADTA3Daf7YMC3KiUrlF5xOIis2DiO%2FW6kNijD5LxJO39lbtAMCvx9z5kEc9tBH8LFyLkuKq8E8ZoGSZkoNerFQSD0ZIkp79vppQuIK3LB2oZpqelDHkrAQrTL7INv1ZTk%3D&term=apple%20black%20iphone&term=apple%20black%20iphone&tpvBrowse=false&txy=
#http://www.staplesadvantage.com/webapp/wcs/stores/servlet/StplCategoryDisplay?catalogId=4&langId=-1&storeId=10101&act=8&filetersrch=N&filterSearchNoResults=false&forceGallery=true&ggpCatId=&gpCatId=&histSortId=Rel|descending&interimURL=&isInterim=&isMSIE=false&isSimilarProd=&isSmartDeadEnds=&itemsPerPage=25&l4Count=&level=&model=&origAct=4&pCatId=&pg=1&pgs=25&prevTxy=&selSortOption=Top%20Rated&selectedNavForm=gallerynav&sortId=top_rated|descending&src=SRCH&srchurl=O8MpYrswxCADTA3Daf7YMC3KiUrlF5xOIis2DiO%2FW6kNijD5LxJO39lbtAMCvx9z5kEc9tBH8LFyLkuKq8E8ZoGSZkoNerFQSD0ZIkp79vppQuIK3LB2oZpqelDHkrAQrTL7INv1ZTk%3D&term=apple%20black%20iphone&term=apple%20black%20iphone&tpvBrowse=false&txy=
#http://www.staplesadvantage.com/webapp/wcs/stores/servlet/StplCategoryDisplay?catalogId=4&langId=-1&storeId=10101&act=8&filetersrch=N&filterSearchNoResults=false&forceGallery=true&ggpCatId=&gpCatId=&histSortId=Rel|descending&interimURL=&isInterim=&isMSIE=false&isSimilarProd=&isSmartDeadEnds=&itemsPerPage=25&l4Count=&level=&model=&origAct=4&pCatId=&pg=1&pgs=25&prevTxy=&selSortOption=Top%20Rated&selectedNavForm=gallerynav&sortId=top_rated|descending&src=SRCH&term=apple%20black%20iphone&srchurl=O8MpYrswxCADTA3Daf7YMC3KiUrlF5xOIis2DiO/W6kNijD5LxJO39lbtAMCvx9z5kEc9tBH8LFyLkuKq8E8ZoGSZkoNerFQSD0ZIkp79vppQuIK3LB2oZpqelDHkrAQrTL7INv1ZTk=


import json
import re
from urlparse import urljoin

from scrapy import Request
from scrapy.log import WARNING

from .contrib.product_spider import ProductsSpider
from product_ranking.items import RelatedProduct, BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import cond_set, cond_set_value


class StaplesadvantageProductsSpider(ProductsSpider):
    """" staplesadvantage.com product ranking spider

    Takes `order` argument with following possible values:

    * `relevance` (default)
    * `rating` - user rating from low to high
    * `best` - best sellers

    Following fields are not scraped:

    * `price`, `is_out_of_stock`, `is_in_store_only`, `upc`
    """
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) "\
                 "Gecko/20100101 Firefox/10.0"

    name = "staplesadvantage_products"

    allowed_domains = ['staplesadvantage.com']
    SEARCH_URL = "https://www.staplesadvantage.com/webapp/wcs/stores/servlet" \
                 "/StplCategoryDisplay?term={search_term}" \
                 "&act=4&src=SRCH&reset=true&storeId=10101&pg={page}"

    START_URL = 'https://www.staplesadvantage.com/learn?storeId=10101'

    BASE_URL = "https://www.staplesadvantage.com/webapp/wcs/stores/servlet" \
               "/StplCategoryDisplay?catalogId=4&langId=-1&storeId=10101"

    SORT_MODES = {
        'default': '',
        'relevance': '',
        'rating': (quote('Top Rated'), 'top_rated|descending'),
        'best': (quote('Best Sellers'), 'best_selling|descending')
    }

    OPTIONAL_REQUESTS = {
        'buyer_reviews': True
    }

    HARDCODED_FIELDS = {
        'locale': 'en_US'
    }

    def __init__(self, *args, **kwargs):
        super(StaplesadvantageProductsSpider, self).__init__(*args, **kwargs)
        self.url_formatter.defaults['page'] = 1

    def start_requests(self):
        requests = super(StaplesadvantageProductsSpider, self).start_requests()
        return [Request(self.START_URL, self._begin_search,
                        meta={'requests': requests})]

    def _begin_search(self, response):
        if not self.sort_mode:
            for request in response.meta['requests']:
                yield request
        for request in response.meta['requests']:
            request.callback = self._parse_unsorted_first
            yield request

    def _parse_unsorted_first(self, response):
        """This method will create first url for sorted results.
        But response will be sorted in another orded.
        """
        css = '[id="%s"]::attr(value)' % self.sort_mode[1]
        magic = response.css(css)
        if not magic:
            self.log('Could not apply ordering', WARNING)
            return
        magic = magic[0].extract()
        term = response.meta['search_term']
        fields = self._extract_fields(response)
        fields.update({'sortId': self.sort_mode[1],
                       'selSortOption': self.sort_mode[0],
                       'srchurl': magic})
        url = '%s&%s' % (self.BASE_URL, urlencode(fields))
        yield Request(url, meta=response.meta,
                      callback=self._parse_unsorted_again)

    def generate_url_from_inputs(self, response, gallery_name):
        """This method will create search url based on hidden
        inputs on page. All data can be captured from inputs,
        but not 'srchurl' because it dynamically added by javascript.
        We should find it in another place.
        """
        inputs = response.xpath(
            '//div[@class="secondary-search-filter text-upp clearfix"]'
            '/form["%s"]/input' % gallery_name
        )
        additional_part = ''
        for inp in inputs:
            try:
                name = inp.xpath('@name').extract()[0]
            except:
                name = inp.xpath('@id').extract()[0]
            value = inp.xpath('@value').extract()[0]
            if name != 'srchurl':
                part = '&%s=%s' % (name, value)
                additional_part += part
        search_urls = response.xpath(
            '//input[@name="srchurl"]/@value'
        ).extract()
        if gallery_name == 'galleryfullnav':
            search_urls = [url for url in search_urls if url]
        if gallery_name == 'gallerynav':
            search_urls = re.findall(
                r'f\.srchurl\.value\s=\s"(.*)";\sf.pgs',
                response.body
            )
        search_url = quote(search_urls[0])
        additional_part += '&srchurl=' + search_url
        url = self.BASE_URL + additional_part
        return url

    def _parse_unsorted_again(self, response):
        """Generate final sorted url based on data from page."""
        url = self.generate_url_from_inputs(response, 'galleryfullnav')
        return Request(url, meta=response.meta)

    def _total_matches_from_html(self, response):
        total = response.css('.didYouMeanNoOfItems').extract()
        if not total:
            total = response.xpath(
                '//span[@class="search-mean-count"]/text()'
            ).extract()
        if not total: return 0
        total = re.search('[\d,]+', total[0])
        return int(total.group().replace(',', '')) if total else 0

    def _extract_fields(self, response):
        fields = {fld.css('::attr(name)')[0].extract():
                      fld.css('::attr(value)')[0].extract()
                  for fld in response.css('#gallerynav input[name][value]')}
        return fields

    def _scrape_next_results_page_link(self, response):
        if not self.sort_mode:
            if not self._fetch_product_boxes(response):
                return None
            fields = self._extract_fields(response)
            fields['pg'] = str(int(fields['pg']) + 1)
            url = '%s&%s' % (self.BASE_URL, urlencode(fields))
            return url
        else:
            url = self.generate_url_from_inputs(response, 'gallerynav')
            page_number = re.findall(r'pg=(\d+)', url)[0]
            next_page_number = int(page_number) + 1
            next_page = 'pg=%s' % next_page_number
            url = re.sub(r'(pg=\d+)', next_page, url)
            return url

    def _fetch_product_boxes(self, response):
        return response.xpath('//div[@class="search-prod-info"]')

    def _link_from_box(self, box):
        return box.xpath(
            './/a[contains(@class, "search-prod-desc")]/@href'
        ).extract()[0]

    def _populate_from_box(self, response, box, product):
        title = box.css('.plainlink::text').extract()
        if not title:
            title = box.xpath(
            './/a[contains(@class, "search-prod-desc")]/text()'
        ).extract()
        cond_set(product, 'title', title,
                 unicode.strip)

    def _populate_from_html(self, response, product):
        title = response.xpath('//h1[contains(@class, "search-prod-desc")]/text()'
            #'/@title'
            ).extract()
        cond_set(product, 'title', title)
        xpath = '//div[@id="dotcombrand"]/../preceding-sibling::li[1]/text()'
        brand = response.xpath(xpath).extract()
        if not brand:
            brand = response.xpath(
                '//p[@class="brand-name"]/text()'
            ).extract()
            if brand:
                brand = brand[0].split(':')
                if len(brand) == 1:
                    brand = [brand[0]]
                else:
                    brand = [brand[1]]
        cond_set(product, 'brand', brand)
        xpath = '//h3[text()="Description"]' \
                '/following-sibling::p[normalize-space()] |' \
                '//div[contains(@class, "product-details-desc")]'
        desc = response.xpath(xpath).extract()
        cond_set(product, 'description', desc)
        image_url = re.findall("enlargedImageURL = '([^']*)'", response.body)
        cond_set(product, 'image_url', image_url)
        model = re.findall('"model" : "([^"]*)"', response.body)
        cond_set(product, 'model', model)
        self._populate_related_products(response, product)

    def _populate_related_products(self, response, product):
        products = []
        for item in response.xpath('//div[@class="related-products-container"]'
            '//li[@class="deals-Blk"]//a[contains'
            '(@class, "recent-purchase-product-desc")]'
            ):
            url = item.xpath('@href')
            text = item.xpath('text()')
            if url and text:
                products.append(
                    RelatedProduct(url=url[0].extract(),
                                   title=text[0].extract().strip()))
        cond_set_value(product, 'related_products',
                       {'More product options': products})

    def _request_buyer_reviews(self, response):
        prod_id = re.search('var pr_page_id="(\d+)"', response.body)
        if not prod_id:
            return
        prod_id = prod_id.group(1)
        CH = sum((ord(c) * abs(255 - ord(c)) for c in str(prod_id)))
        CH = str(CH % 1023).rjust(4, '0')
        CH = '%s/%s' % (CH[:2], CH[2:])
        url = "http://www.staplesadvantage.com/pwr/content/%s/contents.js" % CH
        meta = response.meta.copy()
        meta['prod_id'] = prod_id
        meta['field'] = 'buyer_reviews'
        return Request(url, callback=self._parse_buyer_reviews, meta=meta,
                       errback=self._handle_option_error, dont_filter=True)

    def _parse_buyer_reviews(self, response):
        product = response.meta['product']
        json_str = re.search("POWERREVIEWS\.common\.gResult"
                             "\['content/\d+/\d+/contents.js'\] = (.+);",
                             response.body)
        if not json_str:
            cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
            return
        data = json.loads(json_str.group(1))
        try:
            data = data['locales']['en_US'][
                'p' + str(response.meta['prod_id'])]
            data = data['reviews']
        except KeyError:
            cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
            return
        ratings = {i + 1: val for i, val in enumerate(data['review_ratings'])}
        avg = float(data['avg'])
        total = data['review_count']
        cond_set_value(response.meta['product'], 'buyer_reviews',
                       BuyerReviews(total, avg,
                                    ratings) if total else ZERO_REVIEWS_VALUE)

    def _parse_single_product(self, response):
        return self.parse_product(response)
