# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
import re
import json

from scrapy.http import Request
from scrapy.log import ERROR
from scrapy.selector import Selector

from product_ranking.items import SiteProductItem, Price, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, cond_set, \
    cond_set_value

# scrapy crawl amazoncouk_products -a searchterms_str="iPhone"


class AmazonCoUkProductsSpider(BaseProductsSpider):
    name = "amazoncouk_products"
    allowed_domains = ["www.amazon.co.uk"]
    start_urls = []
    
    SEARCH_URL = ("http://www.amazon.co.uk/s/ref=nb_sb_noss?"
                  "url=search-alias=aps&field-keywords={search_term}&rh=i:aps,"
                  "k:{search_term}&ajr=0")

    def _get_products(self, response):
        result = super(AmazonCoUkProductsSpider, self)._get_products(response)
        for r in result:
            if isinstance(r, Request):
                r = r.replace(dont_filter=True)
                yield r
            else:
                yield r

    def parse_product(self, response):
        prod = response.meta['product']

        title = response.xpath(
            '//span[@id="productTitle"]/text()[normalize-space()] |'
            '//div[@class="buying"]/h1/span[@id="btAsinTitle"]'
            '/text()[normalize-space()] |'
            '//div[@id="title_feature_div"]/h1/text()[normalize-space()] |'
            '//div[@id="title_row"]/span/h1/text()[normalize-space()] |'
            '//h1[@id="aiv-content-title"]/text()[normalize-space()] |'
            '//div[@id="item_name"]/text()[normalize-space()] |'
            '//h1[@class="parseasinTitle"]/span[@id="btAsinTitle"]'
            '/span/text()[normalize-space()]'
        ).extract()
        cond_set(prod, 'title', title)

        brand = response.xpath('//a[@id="brand"]/text()').extract()
        cond_set(prod, 'brand', brand)

        cond_set(
            prod,
            'price',
            response.css(
                '#priceblock_ourprice ::text'
                ', #unqualifiedBuyBox .a-color-price ::text'
                ', #priceblock_saleprice ::text'
                ', #buyNewSection .offer-price ::text'
            ).extract(),
        )
        if not prod.get('price', None):
            cond_set(
                prod,
                'price',
                response.xpath(
                    '//td/b[@class="priceLarge"]/text() |'
                    '//span[@class="olp-padding-right"]'
                    '/span[@class="a-color-price"]/text() |'
                    '//div[contains(@data-reftag,"atv_dp_bb_est_hd_movie")]'
                    '/button/text() |'
                    '//span[@id="priceblock_saleprice"]/text() |'
                    '//li[@class="swatchElement selected"]'
                    '//span[@class="a-color-price"]/text() |'
                    '//div[contains(@data-reftag,"atv_dp_bb_est_sd_movie")]'
                    '/button/text() |'
                    '//div[@id="mocaBBRegularPrice"]'
                    '/div/text()[normalize-space()] |'
                    '//span[@id="actualPriceValue"]/b/text()'
                    '[normalize-space()] |'
                    '//span[@id="actualPriceValue"]/text()[normalize-space()]'
                ).extract()
            )

        if prod.get('price', None):
            if not u'£' in prod.get('price', ''):
                self.log('Invalid price at: %s' % response.url, level=ERROR)
            else:
                price = re.findall('[\d ,.]+\d', prod['price'])
                price = re.sub('[, ]', '', price[0])
                prod['price'] = Price(
                    price=price.replace(u'£', '').replace(
                        ' ', '').replace(',', '').strip(),
                    priceCurrency='GBP'
                )

        description = response.css('.productDescriptionWrapper').extract()
        if not description:
            description = response.xpath(
                '//div[@id="descriptionAndDetails"] |'
                '//div[@id="feature-bullets"] |'
                '//div[@id="ps-content"] |'
                '//div[@id="productDescription_feature_div"] |'
                '//div[contains(@class, "dv-simple-synopsis")] |'
                '//div[@class="bucket"]/div[@class="content"]'
            ).extract()

        cond_set(prod, 'description', description)

        image = []
        j = re.findall(r"'colorImages': { 'initial': (.*)},",
                       response.body)
        if not j:
            j = re.findall(r'colorImages = {"initial":(.*)}',
                           response.body)
        if j:
            try:
                res = json.loads(j[0])
                try:
                    image = res[0]['large']
                except:
                    image = res[1]['large']
                image = [image]
            except:
                pass
        if not image:
            image = response.xpath(
                '//div[@class="main-image-inner-wrapper"]/img/@src |'
                '//div[@id="coverArt_feature_div"]//img/@src |'
                '//div[@id="img-canvas"]/img/@src |'
                '//div[@class="dp-meta-icon-container"]/img/@src |'
                '//input[@id="mocaGlamorImageUrl"]/@value |'
                '//div[@class="egcProdImageContainer"]'
                '/img[@class="egcDesignPreviewBG"]/@src |'
                '//img[@id="main-image"]/@src |'
                '//div[@id="imgTagWrapperId"]/img/@src |'
                '//div[@id="kib-container"]/div[@id="kib-ma-container-0"]'
                '/img/@src'
            ).extract()

        cond_set(prod, 'image_url', image)

        cond_set(prod, 'locale', ['en-US'])

        prod['url'] = response.url
        self._buyer_reviews_from_html(response, prod)
        return prod

    def _search_page_error(self, response):
        sel = Selector(response)

        try:
            found1 = sel.xpath('//div[@class="warning"]/p/text()').extract()[0]
            found2 = sel.xpath(
                '//div[@class="warning"]/p/strong/text()'
            ).extract()[0]
            found = found1 + " " + found2
            if 'did not match any products' in found:
                self.log(found, ERROR)
                return True
            return False
        except IndexError:
            return False

    def _scrape_total_matches(self, response):
        if 'did not match any products.' in response.body_as_unicode():
            total_matches = 0
        else:
            count_matches = response.xpath(
                '//h2[@id="s-result-count"]/text()').re('of ([\d,]+)')
            if count_matches and count_matches[-1]:
                total_matches = int(count_matches[-1].replace(',', ''))
            else:
                total_matches = None
        return total_matches

    def _scrape_product_links(self, response):
        links = response.xpath(
            '//div[contains(@class, "s-item-container")]'
            '//a[contains(@class, "s-access-detail-page")]/@href'
        ).extract()
        for link in links:
            yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        links = response.xpath(
            '//a[@id="pagnNextLink"]/@href'
        )
        if links:
            return links.extract()[0].strip()
        return None

    def _buyer_reviews_from_html(self, response, product):
        stars_regexp = r'% .+ (\d[\d, ]*) '
        total = ''.join(response.css('#summaryStars a::text').extract())
        total = re.search('\d[\d, ]*', total)
        total = total.group() if total else None
        total = int(re.sub('[ ,]+', '', total)) if total else None
        average = response.css('#avgRating span::text').extract()
        average = re.search('\d[\d ,.]*', average[0] if average else '')
        average = float(re.sub('[ ,]+', '',
                               average.group())) if average else None
        ratings = {}
        for row in response.css('.a-histogram-row .a-span10 ~ td a'):
            title = row.css('::attr(title)').extract()
            text = row.css('::text').extract()
            stars = re.search(stars_regexp, title[0]) \
                if text and text[0].isdigit() and title else None
            if stars:
                stars = int(re.sub('[ ,]+', '', stars.group(1)))
                ratings[stars] = int(text[0])
        if not total:
            total = sum(ratings.itervalues()) if ratings else 0
        if not average:
            average = sum(k * v for k, v in
                          ratings.iteritems()) / total if ratings else 0
        buyer_reviews = BuyerReviews(num_of_reviews=total,
                                     average_rating=average,
                                     rating_by_star=ratings)
        cond_set_value(product, 'buyer_reviews', buyer_reviews)