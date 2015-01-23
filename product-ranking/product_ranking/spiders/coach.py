from __future__ import division, absolute_import, unicode_literals
from future_builtins import *
import urlparse
import urllib
import re

from scrapy.log import WARNING, INFO
from scrapy.http import Request

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults
from product_ranking.spiders import cond_set, cond_set_value,\
    cond_replace_value, _extract_open_graph_metadata, populate_from_open_graph


# to run - add additional argument -a search_sort="low-to-high"/"high-to-low"
# default "low-to-high"
class CoachSpider(BaseProductsSpider):
    handle_httpstatus_list = [404]
    name = 'coach_products'
    allowed_domains = ["coach.com"]
    start_urls = []

    NEW_SEARCH_URL = "http://www.coach.com/search?&q={search_term}"\
                     "&srule=price-{search_sort}&format=ajax"

    SEARCH_URL = "http://www.coach.com/online/handbags/SearchResultsView?"\
                 "storeId=10551&catalogId=10051&searchKeyword={search_term}"\
                 "&srule=price-{search_sort}"

    def __init__(self, search_sort='low-to-high', *args, **kwargs):
        self.search_sort = search_sort
        self.new_stile = False
        super(CoachSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                search_sort=search_sort,
            ), *args, **kwargs
        )

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
            return super(CoachSpider, self).start_requests()

    def parse_product(self, response):
        if self.new_stile:
            return self.parse_product_new(response)
        else:
            return self.parse_product_old(response)

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
        return prod

    def parse_product_old(self, response):
        prod = response.meta['product']
        # populate_from_open_graph not awailable cause no type=product
        metadata = _extract_open_graph_metadata(response)
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
            '//span[@id="pdTabProductSalePrice"]/text()'
        ).re(re_pattern)
        # in case item use usual price, not sale
        if not price:
            price = response.xpath(
                '//span[@id="pdTabProductPriceSpan"]/text()'
            ).re(re_pattern)
        prod['price'] = Price(
            priceCurrency='USD',
            price=price[0]
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
        matches = response.xpath(
            '//div[@class="container-shopGrid"]/h2/text()'
        ).extract()
        if matches:
            matches_stripped = re.findall(r'(\d+)', matches[0])
            matches_result = int(matches_stripped[0])
            if matches_result == 0:
                st = response.meta.get('search_term')
                self.log("No products found with search_term '%s'" % st,
                         WARNING)
            return matches_result

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
        links = self.scrape_links_at_the_new_site(response)
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
        uniqe_links = []
        for link in stripped_links:
            if link not in uniqe_links:
                uniqe_links.append(link)
        return uniqe_links
