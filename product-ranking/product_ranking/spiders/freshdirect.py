from __future__ import division, absolute_import, unicode_literals
import re
import urlparse
import json

from scrapy.log import WARNING

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider, cond_set_value, \
    cond_replace_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider


class FreshDirectProductsSpider(ProductsSpider):
    name = "freshdirect_products"
    allowed_domains = ["freshdirect.com"]
    SEARCH_URL = "https://www.freshdirect.com/srch.jsp?pageType=search" \
                 "&searchParams={search_term}" \
                 "&sortBy={sort_mode}&orderAsc=true" \
                 "&activePage={page}"

    SORT_MODES = {
        'default': 'Sort_Relevancy',
        'relevance': 'Sort_Relevancy',
        'name_asc': 'Sort_Name',
        'price_asc': 'Sort_PriceUp',
        'best': 'Sort_PopularityUp',
        'sale': 'Sort_SaleUp'
    }

    def __init__(self, sort_direction='asc', *args, **kwargs):
        super(FreshDirectProductsSpider, self).__init__(*args, **kwargs)
        self.url_formatter.defaults['page'] = 1

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _total_matches_from_html(self, response):
        matches = response.css('.pagination-text::text')
        if not matches:
            return 0
        matches = matches[0].extract()
        matches = re.search('\d+-\d+ of (\d+)', matches)
        return int(matches.group(1)) if matches else 0

    def _get_pages(self, response):
        buttons = response.css('.pagination-pager-button::text')
        if not buttons:
            return 0
        return int(buttons[-1].extract())

    def _get_page_url(self, response, page):
        search_term = response.meta['search_term']
        return self.url_formatter.format(self.SEARCH_URL,
                                         search_term=search_term, page=page)

    def _get_current_page(self, response):
        css = '.pagination-pager-button.selected::text'
        try:
            return int(response.css(css).extract()[0])
        except IndexError:
            return 1

    def _scrape_next_results_page_link(self, response):
        current = self._get_current_page(response)
        last = self._get_pages(response)
        if last > current:
            return self._get_page_url(response, current + 1)

    def _fetch_product_boxes(self, response):
        return response.css('.transactional .products li')

    def _link_from_box(self, box):
        return box.css('.portrait-item-header-name::attr(href)')[0].extract()

    def _populate_from_html(self, response, prod):
        self._populate_from_js(response, prod)
        des = response.xpath(
            '//div[contains(@class,"pdp-accordion-description-description")]'
            '//text()'
        ).extract()
        des = ''.join(i.strip() for i in des)
        cond_set_value(prod, 'description', des)

        reseller_id_regex = "[Pp]roduct[Ii][dD]=([^\&]+)"
        reseller_id = re.findall(reseller_id_regex, response.url)
        reseller_id = reseller_id[0] if reseller_id else None
        cond_set_value(prod, 'reseller_id', reseller_id)

        related_products = []
        for li in response.xpath(
                '//div[@class="pdp-likethat"]'
                '//li[contains(@class,"portrait-item")]'
        ):
            url = None
            urls = li.xpath(
                './/div[@class="portrait-item-header"]/a/@href').extract()
            if urls:
                url = urlparse.urljoin(response.url, urls[0])

            title = ' '.join(s.strip() for s in li.xpath(
                './/div[@class="portrait-item-header"]//text()').extract())

            if url and title:
                related_products.append(RelatedProduct(title, url))
        cond_set_value(
            prod.setdefault('related_products', {}),
            'recommended',
            related_products,
        )
        self._unify_price(prod)

    def _populate_from_js(self, response, product):
        data_jsons = response.xpath('//script/text()').re(
            "productData=(\{.+\})")
        if not data_jsons:
            self.log("Could not get JSON match in %s" % response.url, WARNING)
        else:
            data = json.loads(data_jsons[0])

            brand = data.get('brandName')
            if brand:
                product['brand'] = brand

            price = data.get('price')
            if price:
                product['price'] = price

            img_url = data.get('productZoomImage')
            if img_url:
                product['image_url'] = urlparse.urljoin(response.url, img_url)

            title = data.get('productName')
            if title:
                product['title'] = title

            model = data.get('skuCode')
            if model:
                product['model'] = model

    def _unify_price(self, product):
        price = product.get('price')
        if not price:
            return
        cond_replace_value(product, 'price', Price('USD', price))


class FreshDirectProductsSpider_(BaseProductsSpider):
    name = "freshdirect_products_"
    allowed_domains = ["freshdirect.com"]
    start_urls = []

    SEARCH_URL = "https://www.freshdirect.com/srch.jsp&pageType=search&" \
                 "searchParams={search_term}&view=grid&refinement=1"

    def parse_product(self, response):
        prod = response.meta['product']

        prod['url'] = response.url

        self._populate_from_js(response, prod)

        self._populate_from_html(response, prod)

        cond_set_value(prod, 'locale', 'en-US')

        return prod

    def _populate_from_html(self, response, prod):
        des = response.xpath(
            '//div[contains(@class,"pdp-accordion-description-description")]'
            '//text()'
        ).extract()
        des = ''.join(i.strip() for i in des)
        cond_set_value(prod, 'description', des)

        related_products = []
        for li in response.xpath(
                '//div[@class="pdp-likethat"]'
                '//li[contains(@class,"portrait-item")]'
        ):
            url = None
            urls = li.xpath(
                './/div[@class="portrait-item-header"]/a/@href').extract()
            if urls:
                url = urlparse.urljoin(response.url, urls[0])

            title = ' '.join(s.strip() for s in li.xpath(
                './/div[@class="portrait-item-header"]//text()').extract())

            if url and title:
                related_products.append(RelatedProduct(title, url))
        cond_set_value(
            prod.setdefault('related_products', {}),
            'recommended',
            related_products,
        )

    def _populate_from_js(self, response, product):
        data_jsons = response.xpath('//script/text()').re(
            "productData=(\{.+\})")
        if not data_jsons:
            self.log("Could not get JSON match in %s" % response.url, WARNING)
        else:
            data = json.loads(data_jsons[0])

            brand = data.get('brandName')
            if brand:
                product['brand'] = brand

            price = data.get('price')
            if price:
                product['price'] = price

            img_url = data.get('productZoomImage')
            if img_url:
                product['image_url'] = urlparse.urljoin(response.url, img_url)

            title = data.get('productName')
            if title:
                product['title'] = title

            model = data.get('skuCode')
            if model:
                product['model'] = model

    def _scrape_total_matches(self, response):
        try:
            count = response.xpath(
                '//span[@class="itemcount"]/text()').extract()[0]
            return int(count)
        except IndexError:
            return 0

    def _scrape_product_links(self, response):
        for link in response.xpath(
                '//div[@class="items"]//div[@class="grid-item-name"]/a/@href'
        ).extract():
            link = urlparse.urljoin(response.url, link)
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath('//span[@class="pager-next"]/a/@href').extract()

        if links:
            link = urlparse.urljoin(response.url, links[0])
        else:
            link = None

        return link
