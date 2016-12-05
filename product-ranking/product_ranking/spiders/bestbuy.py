from __future__ import division, absolute_import, unicode_literals

import re

from product_ranking.items import Price, BuyerReviews
from product_ranking.spiders import cond_set, cond_set_value, cond_replace_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider


class BestBuyProductSpider(ProductsSpider):
    name = 'bestbuy_products'
    allowed_domains = ["bestbuy.com"]

    SEARCH_URL = "http://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-" \
                 "8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp={page}" \
                 "&nrp=15&sp=&qp=" \
                 "&list=n&iht=y&usc=All+Categories&ks=960&st={search_term}"

    def __init__(self, *args, **kwargs):
        super(BestBuyProductSpider, self).__init__(*args, **kwargs)
        self.url_formatter.defaults['page'] = 1

    def parse_product(self, response):
        product = response.meta['product']
        rows = ''.join(response.xpath("//div[contains(@class,'cart-button')]/@data-add-to-cart-message").extract())
        if "Sold Out Online" in rows:
            product['is_out_of_stock'] = True
        else:
            product['is_out_of_stock'] = False
        if 'this item is no longer available' in response.body_as_unicode().lower():
            product['not_found'] = True
            return product
        return super(BestBuyProductSpider, self).parse_product(response)

    def _scrape_total_matches(self, response):
        matches = response.css('.ui-state-active [data-facet-value=All]::text')
        if not matches:
            return 0
        matches = matches.extract()[0]
        matches = re.search('\((\d+)\)', matches)
        if not matches:
            return
        return int(matches.group(1))

    def _scrape_next_results_page_link(self, response):
        next_link = response.css('.pager-next::attr(data-page-no)')
        if not next_link:
            return None
        next_link = int(next_link.extract()[0])
        search_term = response.meta['search_term']
        return self.url_formatter.format(self.SEARCH_URL,
                                         search_term=search_term,
                                         page=next_link)

    def _fetch_product_boxes(self, response):
        return response.css('.list-items .list-item')

    def _link_from_box(self, box):
        return box.css('::attr(data-url)').extract()[0]

    def _populate_from_box(self, response, box, product):
        return

    def _populate_from_schemaorg(self, response, product):
        product_tree = response.xpath("//*[@itemtype='http://schema.org/Product']")

        cond_set(product, 'reseller_id', product_tree.xpath(
            "//*[@itemtype='http://schema.org/Product']//*[@id='pdp-model-data']/@data-sku-id"
        ).extract())

        cond_set(product, 'title', product_tree.xpath(
            "descendant::*[not (@itemtype)]/meta[@itemprop='name']/@content"
        ).extract())
        cond_set(product, 'image_url', product_tree.xpath(
            "descendant::*[not (@itemtype)]/img[@itemprop='image']/@src"
        ).extract())
        if not product.get('image_url', None):
            image = response.xpath('//meta[contains(@property, "og:image")]/@content').extract()
            if image:
                product['image_url'] = image[0]
        if product.get('image_url', None):
            image = product.get('image_url')
            if 'maxHeight' in image:
                image = image.split(';maxHeight', 1)[0]
                product['image_url'] = image
        cond_set(product, 'model', product_tree.xpath(
            "descendant::*[not (@itemtype)]/*[@itemprop='model']/text()"
        ).extract())
        cond_set(product, 'upc', product_tree.xpath(
            "descendant::*[not (@itemtype)]/*[@itemprop='productID']/text()"
        ).extract())
        cond_set(product, 'url', product_tree.xpath(
            "descendant::*[not (@itemtype)]/*[@itemprop='url']/@content"
        ).extract())
        cond_set(
            product,
            'description',
            product_tree.xpath(
                "descendant::*[not (@itemtype)]/"
                "*[@itemprop='description']/node()"
            ).extract(),
            conv=lambda desc_parts: ''.join(desc_parts).strip(),
        )

        offer_tree = product_tree.xpath(
            ".//*[@itemtype='http://schema.org/Offer']"
        )
        cond_set(product, 'price', offer_tree.xpath(
            "descendant::*[not (@itemtype) and @itemprop='price']/@content"
        ).extract())

        brand_tree = product_tree.xpath(
            ".//*[@itemtype='http://schema.org/Brand']"
        )
        cond_set(product, 'brand', brand_tree.xpath(
            "descendant::*[not (@itemtype) and @itemprop='name']/@content"
        ).extract())

    def _get_buyer_reviews(self, response):
        average = response.xpath('//*[contains(@class, "average-score")]'
                                 '[contains(@itemprop, "ratingValue")]//text()').extract()
        if not average:
            return
        try:
            average = float(average[0])
        except:
            self.log('Invalid buyer reviews at %s' % response.url)
            return
        num = response.xpath('//meta[contains(@itemprop, "reviewCount")]/@content').extract()
        num = int(num[0].replace(',', ''))
        # scrape rating by star
        rating_by_star = {}
        for star_num, star_breakdown in enumerate(response.xpath(
                '//*[contains(@id, "ratings-tooltip")]'
                '//*[contains(@class, "star-breakdowns")]'
                '//*[contains(@class, "star-breakdown")]')):
            current_mark = 5 - star_num
            if star_num >= 5:
                break
            star_count = star_breakdown.css('.star-count ::text').extract()[0].replace(',', '')
            rating_by_star[str(current_mark)] = int(re.search('(\d+)', star_count).group(1))
        return BuyerReviews(num_of_reviews=num, average_rating=average, rating_by_star=rating_by_star)

    def _populate_from_html(self, response, product):
        self._populate_from_schemaorg(response, product)
        title = response.css("#sku-title ::text").extract()[0]
        if len(re.split(r'\s+-\s+ | -', title, 1)) > 1:
            brand, _ = re.split(r'\s+-\s+', title, 1)
            cond_set(product, 'brand', [brand])

        cond_set(product, 'title', [title])
        cond_set_value(product, 'buyer_reviews', self._get_buyer_reviews(response))
        cond_set(product, 'upc', response.css("#sku-value ::text").extract())
        cond_set(product, 'model',
                 response.css("#model-value ::text").extract())
        self._unify_price(product)

    def _unify_price(self, product):
        price = product.get('price')
        if not price:
            return
        price_match = re.search('\$ *([, 0-9]+(?:\.[, 0-9]+)?)', price)
        if price_match:
            price = price_match.group(1)
            price = ''.join(re.split('[ ,]+', price))
        cond_replace_value(product, 'price', Price('USD', price))

    def _parse_single_product(self, response):
        return self.parse_product(response)