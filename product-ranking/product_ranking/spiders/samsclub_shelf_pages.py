from __future__ import division, absolute_import, unicode_literals
from .samsclub import SamsclubProductsSpider
import re
import time
from scrapy.http import Request, FormRequest
from product_ranking.items import SiteProductItem
from scrapy.log import DEBUG, WARNING, ERROR
from scrapy.conf import settings
import urlparse
import socket
import json
from math import ceil

import lxml.html

is_empty = lambda x: x[0] if x else None


socket.setdefaulttimeout(30)


class SamsclubShelfPagesSpider(SamsclubProductsSpider):
    name = 'samsclub_shelf_urls_products'
    allowed_domains = ["samsclub.com", "api.bazaarvoice.com"]

    _NEXT_SHELF_URL = "http://www.samsclub.com/sams/shop/common/ajaxSearchPageLazyLoad.jsp?sortKey=p_sales_rank" \
                      "&searchCategoryId={category_id}&searchTerm=null&noOfRecordsPerPage={prods_per_page}" \
                      "&sortOrder=0&offset={offset}" \
                      "&rootDimension=0&tireSearch=&selectedFilter=null&pageView=list&servDesc=null&_=1407437029456"

    def __init__(self, *args, **kwargs):
        super(SamsclubShelfPagesSpider, self).__init__(clubno='4704', zip_code='94117', *args, **kwargs)
        self.current_page = 0
        self.prods_per_page = 18
        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0
        self.quantity = self.num_pages * self.prods_per_page
        if "quantity" in kwargs:
            self.quantity = int(kwargs['quantity'])
        #settings.overrides['CRAWLERA_ENABLED'] = True
        self.proxy = None

    def _init_phantomjs(self):
        from selenium import webdriver
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        self.log('No product links found at first attempt'
                 ' - trying PhantomJS with UA %s' % self.user_agent)
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = self.user_agent
        service_args = []
        if self.proxy:
            service_args.append('--proxy="%s"' % self.proxy)
            service_args.append('--proxy-type=' + self.proxy_type)
            proxy_auth = getattr(self, '_proxy_auth', None)
            if proxy_auth:
                service_args.append("--proxy-auth=\"%s\":" % proxy_auth)

        #assert False, service_args
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=service_args)
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)
        return driver

    def _get_links_from_selenium_page(self, driver):
        return [l.get_attribute('href') for l in driver.find_elements_by_xpath(
            '//*[@id="productRow"]//a')]

    def parse(self, response):
        collected_links = []

        # get phantomjs page
        driver = self._init_phantomjs()
        driver.get(self.product_url)
        time.sleep(15)

        results_per_page = None
        try:
            results_per_page = int(re.search('Showing.+?>(\d+)?<', driver.page_source).group(1))
        except Exception as e:
            self.log('Error getting results_per_page: %s' % e, ERROR)
            pass

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
            item['shelf_path'], item['shelf_name'] \
                = self._get_shelf_path_from_firstpage(driver.page_source)
            item['total_matches'] = self._scrape_total_matches(driver.page_source)
            if results_per_page:
                item['results_per_page'] = results_per_page
            item['scraped_results_per_page'] = len(collected_links)
            if not link.startswith('http'):
                link = urlparse.urljoin('http://samsclub.com', link)
            yield Request(
                link, callback=self.parse_product, meta={'product': item})

    def parse_product(self, response):
        if response.url != self.product_url:
            return super(SamsclubShelfPagesSpider, self).parse_product(response)

    def _get_shelf_path_from_firstpage(self, page_source):
        lxml_doc = lxml.html.fromstring(page_source)
        shelf_categories = [
            c.strip() for c in lxml_doc.xpath('.//ol[@id="breadCrumbs"]/li//a/text()')
            if len(c.strip()) > 1]
        shelf_category = shelf_categories[-1] if shelf_categories else None
        return shelf_categories, shelf_category

    def _scrape_total_matches(self, page_source):
        total_matches = re.search('plpCtrl.totalCount.+?>(.+)?<', page_source)
        if total_matches:
            total_matches = total_matches.group(1)
            return int(total_matches)
