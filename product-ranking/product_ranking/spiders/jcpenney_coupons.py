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

    def __init__(self, *args, **kwargs):
        self.product_url = kwargs['product_url']

        self.user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64))" \
            " AppleWebKit/537.36 (KHTML, like Gecko)" \
            " Chrome/37.0.2062.120 Safari/537.36"

    def start_requests(self):
        yield Request(url=self.valid_url(self.product_url))

    def _parse_end_date(self, coupon):
        element = coupon.xpath('.//*[contains(text(), "Valid THROUGH")]/text()').extract()
        if element:
            element = element[0].lower().replace('valid through', '').strip()
            return parse_date(element)

    def _parse_discount(self, description):
        if description:
            description = description.lower()
            _match = re.search(r' (\d+)%.*off', description)
            if _match:
                return _match.group(1) + '%'

    def _parse_conditions(self, coupon):
        return is_empty(
            coupon.xpath('.//*[contains(@class, "txt_caps")]/following-sibling'
                         '::div[contains(@class, "grey14")]/text()').extract()
        )

    def parse(self, response):
        for coupon in response.xpath('//li[contains(@class, "flt_lft")]'):
            item = DiscountCoupon()
            item['category'] = is_empty(
                coupon.xpath('../div[contains(@class, "section-bar")]'
                             '/p/text()').extract()
            )
            item['description'] = is_empty(coupon.css('.offer ::text').extract())
            item['end_date'] = self._parse_end_date(coupon)
            item['discount'] = self._parse_discount(item.get('description', None))
            item['conditions'] = self._parse_conditions(coupon)
            yield item

    def valid_url(self, url):
        if not re.findall("http(s){0,1}\:\/\/", url):
            url = "http://" + url
        return url