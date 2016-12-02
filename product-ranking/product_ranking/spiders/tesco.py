from __future__ import division, absolute_import, unicode_literals
from future_builtins import zip

import json
import re
import urlparse

from scrapy.log import ERROR

from product_ranking.items import SiteProductItem, Price
from product_ranking.spiders import BaseProductsSpider, \
    cond_set, cond_set_value, FLOATING_POINT_RGEX

is_empty = lambda x,y=None: x[0] if x else y

def brand_at_start(brand):
    return (
        lambda t: t.lower().startswith(brand.lower()),
        lambda _: brand,
        lambda t: t,
    )


class TescoProductsSpider(BaseProductsSpider):
    """ tesco.com product ranking spider

    There are following caveats:

    - always add -a user_agent='android_pad',
      sample reverse calling
        scrapy crawl tesco_products -a product_url='http://www.tesco.com/groceries/product/details/?id=286394325' \
            -a user_agent='android_pad'
    """

    name = 'tesco_products'
    allowed_domains = ["tesco.com"]

    # TODO: change the currency if you're going to support different countries
    #  (only UK and GBP are supported now)
    SEARCH_URL = "http://www.tesco.com/groceries/product/search/default.aspx" \
        "?searchBox={search_term}&newSort=true"

    KNOWN_BRANDS = (
        brand_at_start('Dri Pak'),
        brand_at_start('Girlz Only'),
        brand_at_start('Alberto Balsam'),
        brand_at_start('Mum & Me'),
        brand_at_start('Head & Shoulder'),  # Also matcher Head & Shoulders.
        brand_at_start('Ayuuri Natural'),
        (lambda t: ' method ' in t.lower(),
         lambda _: 'Method',
         lambda t: t
         ),
        (lambda t: t.lower().startswith('dr ') or t.lower().startswith('dr. '),
         lambda t: ' '.join(t.split()[:2]),
         lambda t: t,
         ),
    )

    @staticmethod
    def brand_from_title(title):
        for recognize, parse_brand, clean_title \
                in TescoProductsSpider.KNOWN_BRANDS:
            if recognize(title):
                brand = parse_brand(title)
                new_title = clean_title(title)
                break
        else:
            brand = title.split()[0]
            new_title = title
        return brand, new_title

    def parse_product(self, response):
        if self.user_agent_key not in ["desktop", "default"]:
            return self.parse_product_mobile(response)
        else:
            raise AssertionError("This method should never be called.")

    def _scrape_total_matches(self, response):
        if self.user_agent_key not in ["desktop", "default"]:
            return self._scrape_total_matches_mobile(response)
        else:
            return int(response.css("span.pageTotalItemCount ::text").extract()[0])

    def _scrape_total_matches_mobile(self, response):
        total = response.xpath(
            '//h1[@class="heading_button"]'
            '/span[@class="title"]/text()').re('(\d+) result')
        if total:
            return int(total[0])
        return None

    def _scrape_product_links(self, response):
        # To populate the description, fetching the product page is necessary.

        if self.user_agent_key not in ["desktop", "default"]:
            links = response.xpath(
                '//section[contains(@class,"product_listed")]'
                '//div[contains(@class,"product_info")]//a/@href').extract()

            if not links:
                self.log("[Mobile] Found no product data on: %s" % response.url, ERROR)

            for link in links:
                yield urlparse.urljoin(response.url, link), SiteProductItem()
        else:
            url = response.url

            # This will contain everything except for the URL and description.
            product_jsons = response.xpath('//meta[@name="productdata"]/@content').extract()

            if not product_jsons:
                self.log("Found no product data on: %s" % url, ERROR)

            product_links = response.css(
                ".product > .desc > h2 > a ::attr('href')").extract()
            if not product_links:
                self.log("Found no product links on: %s" % url, ERROR)

            for product_json, product_link in zip(product_jsons[0].split('|'), product_links):
                prod = SiteProductItem()
                cond_set_value(prod, 'url', urlparse.urljoin(url, product_link))

                product_data = json.loads(product_json)

                cond_set_value(prod, 'price', product_data.get('price'))
                cond_set_value(prod, 'image_url', product_data.get('mediumImage'))

                #prod['upc'] = product_data.get('productId')
                if prod.get('price', None):
                    prod['price'] = Price(
                        price=str(prod['price']).replace(',', '').strip(),
                        priceCurrency='GBP'
                    )

                try:
                    brand, title = self.brand_from_title(product_data['name'])
                    cond_set_value(prod, 'brand', brand)
                    cond_set_value(prod, 'title', title)
                except KeyError:
                    raise AssertionError(
                        "Did not find title or brand from JS for product: %s"
                        % product_link
                    )

                yield None, prod

    def _scrape_next_results_page_link(self, response):
        if self.user_agent_key not in ["desktop", "default"]:
            return self._scrape_next_results_page_link_mobile(response)
        else:
            next_pages = response.css('p.next > a ::attr(href)').extract()
            next_page = None
            if len(next_pages) == 2:
                next_page = next_pages[0]
            elif len(next_pages) > 2:
                self.log(
                    "Found more than two 'next page' link: %s" % response.url,
                    ERROR
                )
            return next_page

    def _scrape_next_results_page_link_mobile(self, response):
        url = response.url
        total = self._scrape_total_matches(response)
        current_page = re.findall("plpPage=(\d+)", url)

        if not current_page:
            return url + "&plpPage=2"
        else:
            curr = int(current_page[0])
            if curr < total/20:
                curr += 1
                return re.sub("plpPage=(\d+)", "plpPage=%s" %curr, url)
            return None

    def _scrape_product_links_mobile(self, response):
        links = response.xpath(
            '//section[contains(@class,"product_listed")]'
            '//div[contains(@class,"product_info")]//a/@href').extract()

        if not links:
            self.log("Found no product data on: %s" % response.url, ERROR)

        for link in links:
            yield urlparse.urljoin(response.url, link), SiteProductItem()

    def parse_product_mobile(self, response):
        prod = response.meta['product']

        prod['url'] = response.url

        cond_set(prod, 'locale', ['en-GB'])

        title = response.xpath(
            '//div[contains(@class,"descriptionDetails")]//h1//span[@data-title="true"]//text()'
        ).extract()
        cond_set(prod, 'title', title)

        try:
            brand, title = self.brand_from_title(prod['title'])
            cond_set_value(prod, 'brand', brand)
        except KeyError:
            raise AssertionError(
                "Did not find title or brand from JS for product: %s"
                % response.url
            )

        img = response.xpath('//*[@id="pdp_image"]/img/@src').extract()
        cond_set(prod, 'image_url', img)

        price = response.xpath(
            '//div[contains(@class,"main_price")]'
            '/text()').re(FLOATING_POINT_RGEX)
        if price:
            prod['price'] = Price(price=price[0],
                                  priceCurrency='GBP')

        desc = response.xpath('string(//p[@class="descriptionText"])').extract()
        cond_set(prod, "description", desc)
        return prod

    def _parse_single_product(self, response):
        productdata = "[" + is_empty(response.xpath(
            '//meta[@name="productdata"]/@content'
        ).extract(), "")[:-1].replace("|", ",") + "]"
        productdata = is_empty(json.loads(productdata))
        product = SiteProductItem()
        if productdata:
            product["title"] = productdata["name"]
            product["is_out_of_stock"] = not productdata["available"]
            product["url"] = "http://www.tesco.com/groceries/product/details/"\
                "?id=" + str(productdata["productId"])
            try:
                product["price"] = Price(
                    price=productdata["price"],
                    priceCurrency="GBP"
                )
            except:
                pass
            product["image_url"] = productdata["mediumImage"]
            product["search_term"] = ""
            product["brand"] = is_empty(self.brand_from_title(product["title"]))
            product["site"] = is_empty(self.allowed_domains)

        return product
