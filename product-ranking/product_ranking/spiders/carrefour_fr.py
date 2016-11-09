# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals

import string

from scrapy.log import ERROR, DEBUG

from product_ranking.items import SiteProductItem, RelatedProduct, Price
from product_ranking.spiders import BaseProductsSpider, cond_set, cond_set_value


class CarrefourProductsSpider(BaseProductsSpider):
    name = 'carrefour_fr_products'
    allowed_domains = ["carrefour.fr"]
    start_urls = []

    SEARCH_URL = 'http://www.carrefour.fr/search/site/--{search_term}/100'

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _scrape_product_links(self, response):
        products = response.xpath('//ol[contains(@class, "search-results")]'
                                  '//div[contains(@class, "sc_result_list")]')
        if not products:
            self.log("Found no product links.", ERROR)

        for product in products:
            prod_links = product.xpath(
                './/div[contains(@class, "sc_result_title")]//a/@href'
            ).extract()
            if not prod_links:
                self.log(
                    "Failed to extract product link for item: %r"
                    % (product.extract(),),
                    ERROR
                )
                continue
            prod_link = prod_links[0]

            item = SiteProductItem()

            cond_set(
                item,
                'title',
                product.css('div.sc_result_title a::text').extract(),
                conv=string.strip,
            )

            cond_set(
                item,
                'price',
                product.css('div.sc_result_price::text').re('(\d.+)'),
            )
            if item.get('price', None):
                if not '€' in item['price']:
                    self.log('Unknown currency at' % response.url)
                else:
                    item['price'] = Price(
                        price=item['price'].replace(',', '').replace(
                            '€', '').strip(),
                        priceCurrency='EUR'
                    )

            cond_set(
                item,
                'locale',
                response.xpath('//html/@lang').extract(),
                conv=string.strip,
            )
            cond_set_value(item, 'locale', 'fr-FR')  # Default.

            yield prod_link, item

    def _scrape_next_results_page_link(self, response):
        link = response.xpath(
            '//ul[@class="pager"]'
            '//li[@class="pager-current"]/following-sibling::li[1]//a/@href'
        ).extract()
        if not link:
            self.log("Next page link not found.", DEBUG)
            return
        return link[0]

    def _scrape_total_matches(self, response):
        totals = response.css('h2.search-results-message::text').re('(\d+)')
        if totals:
            total = int(totals[0])
        else:
            self.log(
                "'total matches' string not found at %s" % response.url,
                ERROR
            )
            return
        return total

    def parse_product(self, response):
        product = response.meta['product']

        _big_img = response.xpath('//*[contains(@class, "superbox-gallery")]'
                                  '//a[contains(@class, "cloud-zoom")]/@href')
        _big_img = _big_img.extract()
        if _big_img:
            product['image_url'] = _big_img[0].strip()

        cond_set(product, 'brand',
                 response.xpath('//*[@itemprop="brand"]/text()').extract())

        cond_set_value(
            product,
            'is_out_of_stock',
            not response.css('.prd-available'),
        )

        related = response.xpath(
            u'//h2[contains(text(), "également consulté ces articles")]/..'
            u'//p/a[contains(@href, "carrefour.fr")]'
            u'[contains(@onclick, "Proposition_accessoire")]'
        )
        recommended_prods = []
        for rel in related:
            try:
                title = rel.xpath('text()').extract()[0].strip()
                href = rel.xpath('@href').extract()[0].strip()
                recommended_prods.append(RelatedProduct(title, href))
            except IndexError:
                pass
        if recommended_prods:
            product['related_products'] = {"recommended": recommended_prods}

        cond_set(
            product, 'description', response.css('.box-prd-desc').extract())
        if product.get('description'):
            product['description'] = product['description'].replace(
                u'<a class="action-link see-tech-specs" href="#box-tech-specs">'
                u'Voir la fiche technique complète du produit</a>', ''
            )

        if not product.get("title"):
            cond_set(
                product,
                'title',
                response.css('h1.page-title span::text').extract(),
                conv=string.strip,
            )

        if not product.get("locale"):
            cond_set(
                product,
                'locale',
                response.xpath('//html/@lang').extract(),
                conv=string.strip,
            )

        if not product.get("price"):
            cond_set(
                product,
                'price',
                response.css('div p strong::text').re('(\d.+)'),
            )
            if product.get('price', None):
                if not '€' in product['price']:
                    self.log('Unknown currency at' % response.url)
                else:
                    product['price'] = Price(
                        price=str(product['price'].replace(
                            "\xa0", "").replace(
                            ',', '.').replace(
                            '€', '').strip()),
                        priceCurrency='EUR'
                    )

        return product
