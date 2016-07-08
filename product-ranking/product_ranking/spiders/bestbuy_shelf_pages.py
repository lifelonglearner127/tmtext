from __future__ import division, absolute_import, unicode_literals

import re

from scrapy.http import Request
from product_ranking.items import Price, BuyerReviews
from product_ranking.spiders import cond_set, cond_set_value, cond_replace_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider
from product_ranking.spiders.bestbuy import BestBuyProductSpider
from product_ranking.items import SiteProductItem

class BestBuyShelfPagesSpider(BestBuyProductSpider):
    name = 'bestbuy_shelf_urls_products'
    allowed_domains = ["bestbuy.com"]

    def __init__(self, *args, **kwargs):
        super(BestBuyShelfPagesSpider, self).__init__(*args, **kwargs)
        self.current_page = 1
        if "num_pages" in kwargs:
            self.num_pages = int(kwargs['num_pages'])
        else:
            self.num_pages = 1  # See https://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=3313#c0
        if "quantity" in kwargs:
            self.quantity = int(kwargs['quantity'])


    def start_requests(self):
        if self.product_url:
            yield Request(self.product_url,
                meta={'search_term': '', 'remaining': self.quantity},)

    def _scrape_product_links(self, response):
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        item_urls = response.xpath(
            './/*[@class="list-item-postcard"]//a[@data-rank="pdp"]/@href').extract()
        shelf_categories = [c.strip() for c in response.xpath('.//*[@class="breadcrumb"]//li//a/text()').extract()
                            if len(c.strip()) > 1 and not c.strip()=="Best Buy"]
        shelf_category = shelf_categories[-1] if shelf_categories else None
        for item_url in item_urls:
            item = SiteProductItem()
            if shelf_category:
                # cond_set(item, 'shelf_name', shelf_category)
                item['shelf_name'] = shelf_category
            if shelf_categories:
                # cond_set(item, 'shelf_path', shelf_categories)
                item['shelf_path'] = shelf_categories
            yield item_url, item

    def _scrape_total_matches(self, response):
        matches = response.xpath('.//*[@class="number-of-items"]/strong/text()')
        if not matches:
            return 0
        matches = matches.extract()[0]
        matches = re.search('(\d+)', matches)
        if not matches:
            return
        return int(matches.group(1))

    def _scrape_next_results_page_link(self, response):
        next_link = response.xpath('.//*[@class="pager-next"]/a/@href').extract()
        print next_link
        print self.current_page
        print self.num_pages
        print self.quantity
        next_link = next_link[0] if next_link else None
        if not next_link or self.current_page >= int(self.num_pages):
            return None
        else:
            self.current_page += 1
            return next_link

