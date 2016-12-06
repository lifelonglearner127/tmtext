from __future__ import division, absolute_import, unicode_literals
import urlparse
import urllib
import re

from scrapy.log import WARNING, INFO
from scrapy.http import Request

from product_ranking.items import SiteProductItem, Price, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults
from product_ranking.spiders import cond_set, cond_set_value,\
    cond_replace_value, _extract_open_graph_metadata, populate_from_open_graph


# You may add additional argument -a search_sort="price-desc"/"price-asc"
class CoachSpider(BaseProductsSpider):
    handle_httpstatus_list = [404]
    name = 'coach_products'
    allowed_domains = ["coach.com"]
    start_urls = []

    NEW_SEARCH_URL = "http://www.coach.com/search?&q={search_term}"\
                     "&srule={search_sort}&format=ajax"

    SEARCH_URL = "http://www.coach.com/online/handbags/SearchResultsView?"\
                 "storeId=10551&catalogId=10051&searchKeyword={search_term}"\
                 "&srule={search_sort}"

    SEARCH_SORT = {
        'default': "",
        'price-asc': "price-low-to-high",
        'price-desc': "price-high-to-low",
    }

    def __init__(self, search_sort='default', *args, **kwargs):
        self.search_sort = self.SEARCH_SORT[search_sort]
        self.new_stile = False
        # used to store unique links
        self.links = []
        # used to store all response from new_stile site version
        # to prevent make additional requests
        self.initial_responses = []
        super(CoachSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=self.search_sort,
            ), *args, **kwargs
        )

    def start_requests(self):
        """If new_stile site version, we need first crawl
        all pagination and count all unique links and
        generate total_matches"""
        if self.new_stile:
            for st in self.searchterms:
                url = self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8')),
                )
            return Request(url, callback=self.count_products,
                           meta={'search_term': st,
                                 'remaining': self.quantity})
        else:
            return super(CoachSpider, self).start_requests()

    def parse(self, response):
        """Check is old-stile site still alive.
        If yes - check is it redirecting to another url by AJAX.
        If no response - use NEW_SEARCH_URL to make new request.
        """
        if response.status != 404:
            if not self.new_stile:
                # check is there AJAX redirect (at the old-stile site)
                term = r"document.location.href\s=\s'(.*)';"
                # try to find AJAX redirecting script
                script = re.findall(term, response.body_as_unicode())
                if script:
                    domain = "http://www.coach.com/"
                    link = urlparse.urljoin(domain, script[0])
                    self.log('Follow the redirecting link %s' % link, WARNING)
                    new_meta = dict(response.meta)
                    return Request(link, callback=self.parse, meta=new_meta)
            return super(CoachSpider, self).parse(response)
        # if first request to old-stile site failed
        else:
            self.log("Follow to the new stile site. Old stile response 404",
                     INFO)
            # populate request to new url
            self.new_stile = True
            self.SEARCH_URL = self.NEW_SEARCH_URL
            return self.start_requests()

    def parse_product(self, response):
        if self.new_stile:
            return self.parse_product_new(response)
        else:
            return self.parse_product_old(response)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse_product_new(self, response):
        prod = response.meta['product']
        populate_from_open_graph(response, prod)

        prod['locale'] = 'en_US'

        title = response.xpath(
            '//meta[@property="og:title"]/@content'
            ).extract()
        if title:
            cond_set_value(prod, 'title', title[0].capitalize())

        price = response.xpath(
            '//div[@class="sales-price-container"]'
            '/span[contains(@class, "salesprice")]/text()'
        ).extract()
        # if no sale price was found
        if not price:
            price = response.xpath(
                '//div[@class="product-price"]/span/text()'
            ).extract()
        if price and '$' in price[0]:
            n_price = price[0].strip().replace('$', '').\
                replace(',', '').strip()
            prod['price'] = Price(priceCurrency='USD', price=n_price)

        brand = response.xpath(
            '//meta[@itemprop="brand"]/@content'
        ).extract()
        cond_set(prod, 'brand', brand)

        # we need repopulate description cause at meta data it may be false
        description = response.xpath(
            '//p[@itemprop="description"]/text()'
        ).extract()
        if description:
            cond_replace_value(prod, 'description', description[0].strip())

        only_in_online_stock = response.xpath(
            '//li[@class="product-message"]'
        ).extract()
        if only_in_online_stock:
            prod['is_in_store_only'] = True
        else:
            prod['is_in_store_only'] = False

        recommendations = []
        unique_checker = []
        related_div = response.xpath(
            '//div[@id="relatedProducts"]/div[contains(@class, '
            '"recommendations")]//div[@itemprop="isRelatedTo"]'
        )
        for div in related_div:
            link = div.xpath('.//a[@itemprop="url"]/@href').extract()
            name = div.xpath('.//meta[@itemprop="name"]/@content').extract()
            if name and link:
                # because site can recommend the same items
                if name not in unique_checker:
                    unique_checker.append(name)
                    item = RelatedProduct(title=name[0].strip().capitalize(),
                                          url=link[0].strip())
                    recommendations.append(item)
        prod['related_products'] = {'recommended': recommendations}
        return prod

    def parse_product_old(self, response):
        prod = response.meta['product']
        # populate_from_open_graph not awailable cause no type=product
        metadata = _extract_open_graph_metadata(response)
        description = response.xpath('//p[@itemprop="description"]//text()').extract()
        if description:
            cond_set_value(prod, 'description', description[0])
        else:
            cond_set_value(prod, 'description', metadata.get('description'))
        cond_set_value(prod, 'title', metadata.get('title'))
        cond_replace_value(prod, 'url', metadata.get('url'))

        img_url = metadata.get('image').rstrip('?$browse_thumbnail$')
        cond_set_value(prod, 'image_url', img_url)
        locale = response.xpath(
            '//meta[@name="gwt:property"]/@content'
        ).re(r'locale=\s*(.*)')
        if locale:
            cond_set_value(prod, 'locale', locale[0])

        re_pattern = r'(\d+,\d+|\d+)'
        price = response.xpath(
            '//span[@itemprop="price"]//span[contains(@class,"price-sales")]//text()'
        ).extract()
        if len(price) > 0:
            price = re.findall(r'[\d\.]+', price[0])
            if len(price) > 0:
                price = price[0].replace(",", "")
        else:
            price = None
        # in case item use usual price, not sale
        if price:
            prod['price'] = Price(
                priceCurrency='USD',
                price=price
            )

        brand = response.xpath(
            '//meta[@itemprop="brand"]/@content'
        ).extract()
        cond_set(prod, 'brand', brand)
        return prod

    def _scrape_total_matches(self, response):
        if self.new_stile:
            return self._scrape_total_matches_new(response)
        else:
            return self._scrape_total_matches_old(response)

    def _scrape_total_matches_new(self, response):
        total = len(self.links)
        if total == 0:
            st = response.meta.get('search_term')
            self.log("No products found with search_term %s" % st,
                     WARNING)
        return total

    def _scrape_total_matches_old(self, response):
        divs_with_items = response.xpath('//div[contains(@id, "seq")]')
        if not divs_with_items:
            allert = response.xpath('//p[@class="searchAlert"]')
            if allert:
                st = response.meta.get('search_term')
                self.log("No products found with search_term %s" % st,
                         WARNING)
                return 0
        return len(divs_with_items)

    def _scrape_product_links(self, response):
        if self.new_stile:
            return self._scrape_product_links_new(response)
        else:
            return self._scrape_product_links_old(response)

    def _scrape_product_links_new(self, response):
        links = self.links
        if not links:
            st = response.meta.get('search_term')
            self.log("Found no product links at page %s with "
                     "search term '%s'" % (response.url, st),
                     WARNING)
        for link in links:
            yield link, SiteProductItem()

    def _scrape_product_links_old(self, response):
        divs_with_items = response.xpath('//div[contains(@id, "seq")]')
        links = divs_with_items.xpath('.//a/@href').extract()
        if not links:
            st = response.meta.get('search_term')
            self.log("Found no product links at page %s with "
                     "search term '%s'" % (response.url, st),
                     WARNING)
        for link in links:
            img_link = divs_with_items.xpath('.//img/@src').extract()[0]
            product_link = urlparse.urljoin(self.PRODUCT_BASE_URL, link)
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        """All links was scrapped before. Not implemented
        for BaseProductsSpider in this case"""
        return None

    def scrape_next_results_page(self, response):
        links = response.xpath(
            '//div[@class="pagination"]/ul/li[@class="current-page"]'
            '/following-sibling::li/a/@href'
        ).extract()
        if links and links[0]:
            return links[0]
        return None

    def scrape_links_at_the_new_site(self, response):
        """Scrape only uniqe links with color stripped"""
        links = response.xpath(
            '//div[@itemid="#product"]/div[@class="product-info"]//h2/a/@href'
        ).extract()
        color_ext = r"\?dwvar_color=.*"
        stripped_links = [re.sub(color_ext, '', link) for link in links]
        for link in stripped_links:
            if link not in self.links:
                self.links.append(link)

    def count_products(self, response):
        self.initial_responses.append(response)
        self.scrape_links_at_the_new_site(response)
        next_link = self.scrape_next_results_page(response)
        if next_link:
            return Request(next_link, callback=self.count_products)
        else:
            for resp in self.initial_responses:
                return self.parse(resp)
