#
# Discount coupons for pages like http://www.jcpenney.com/jsp/browse/marketing/promotion.jsp?pageId=pg40027800029#
#

import re
import urlparse

import scrapy
from scrapy.http import Request
from dateutil.parser import parse as parse_date

from product_ranking.items import DiscountCoupon

is_empty = lambda x: x[0] if x else None


class JCPenneyCouponsSpider(scrapy.Spider):
    name = 'jcpenney_coupons_products'
    allowed_domains = ['jcpenney.com', 'www.jcpenney.com']
    DEFAULT_URL = 'http://www.jcpenney.com/jsp/browse/marketing/promotion.jsp?pageId=pg40027800029#'

    def __init__(self, *args, **kwargs):
        super(JCPenneyCouponsSpider, self).__init__(**kwargs)
        self.product_url = kwargs.get('product_url', self.DEFAULT_URL)
        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
                          " AppleWebKit/537.36 (KHTML, like Gecko)" \
                          " Chrome/37.0.2062.120 Safari/537.36"
        self.start_urls = [self._valid_url(self.product_url)]

    def _valid_url(self, url):
        if not re.match("https?://", url):
            url = '%s%s' % ("http://", url)
        return url

    def _parse_coupons(self, response):
        return response.css('.coupon > .offer')

    def _parse_description(self, coupon):
        return is_empty(coupon.css('::text').extract())

    def _parse_category(self, coupon):
        return is_empty(
            coupon.xpath('preceding-sibling::div[contains(@class,"grey12")]'
                         '/strong/text()').extract()
        )

    def _parse_end_date(self, coupon):
        e = coupon.xpath('following-sibling::div[contains(@class,"grey12")]'
                         '/text()').extract()
        if e:
            e = re.search('valid through (.+)', e[0], re.IGNORECASE)
            if e:
                return parse_date(e.group(1))

    def _parse_discount(self, coupon):
        return coupon.css('::text').re('\d+\%')

    def _parse_conditions(self, coupon):
        return is_empty(
            coupon.xpath('following-sibling::div[contains(@class,"grey14")]'
                         '/text()').extract()
        )

    def parse(self, response):
        for coupon in self._parse_coupons(response):
            item = DiscountCoupon()
            item['category'] = self._parse_category(coupon)
            item['description'] = self._parse_description(coupon)
            item['end_date'] = self._parse_end_date(coupon)
            item['discount'] = self._parse_discount(coupon)
            item['conditions'] = self._parse_conditions(coupon)
            yield item
