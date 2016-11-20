from __future__ import division, absolute_import, unicode_literals
from .samsclub_shelf_pages import SamsclubShelfPagesSpider
from scrapy.http import Request
from product_ranking.items import SiteProductItem
from scrapy.log import ERROR
import urlparse
import time
from product_ranking.spiders import cond_set, cond_set_value
from product_ranking.items import SiteProductItem
import lxml.html

is_empty = lambda x: x[0] if x else None

class SamsclubCpPagesSpider(SamsclubShelfPagesSpider):
    name = 'samsclub_cp_urls_products'

    def __init__(self, *args, **kwargs):
        return super(SamsclubCpPagesSpider, self).__init__(*args, **kwargs)

    def _get_shelf_path_from_firstpage(self, page_source):
        lxml_doc = lxml.html.fromstring(page_source)
        shelf_categories = [
            c.strip() for c in lxml_doc.xpath('.//ol[@id="breadCrumbs"]/li//a/text()')
            if len(c.strip()) > 1]
        shelf_category = lxml_doc.xpath('//h1[contains(@class, "catLeftTitle")]/text()')
        return shelf_categories, shelf_category

    def parse(self, response):
        collected_links = []

        # get phantomjs page
        driver = self._init_phantomjs()
        driver.get(self.product_url)
        time.sleep(15)

        num_exceptions = 0
        while 1:
            self.log('Selenium: collected %s links' % len(collected_links))

            if num_exceptions > 10:
                break

            try:
                for link in self._get_links_from_selenium_page(driver):
                    if link not in collected_links:
                        collected_links.append(link)
                next_link_btn = driver.find_element_by_id('plp-seemore')
                if next_link_btn:
                    self.current_page += 1
                    if self.current_page >= self.num_pages:
                        break
                    # TODO: check num_pages
                    next_link_btn.click()
                    time.sleep(15)
                    continue

            except Exception as e:
                self.log('Error: %s' % str(e), ERROR)
                num_exceptions += 1

        try:
            self.driver.quit()
        except:
            pass

        collected_links = [l for l in collected_links if l]

        for i, link in enumerate(collected_links):
            item = SiteProductItem()
            item['ranking'] = i+1
            item['url'] = link
            shelf_categories, shelf_category \
                = self._get_shelf_path_from_firstpage(driver.page_source)
            if shelf_category:
                item['shelf_name'] = shelf_category[0]
            for category_index, category_value in enumerate(shelf_categories[:10]):
                item['level{}'.format(category_index+1)] = category_value
            item['total_matches'] = self._scrape_total_matches(driver.page_source)
            if not link.startswith('http'):
                link = urlparse.urljoin('http://samsclub.com', link)
            yield Request(
                link, callback=self.parse_product, meta={'product': item})

    def parse_product(self, response):
        if response.url != self.product_url:
            product = response.meta['product']

            cond_set(
                product,
                'title',
                response.xpath(
                    "//div[contains(@class,'prodTitle')]/h1/span[@itemprop='name']"
                    "/text()"
                ).extract())

            # Title key must be present even if it is blank
            cond_set_value(product, 'title', "")
            return product
