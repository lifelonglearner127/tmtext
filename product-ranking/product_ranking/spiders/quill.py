import re
from urlparse import urljoin

from product_ranking.items import RelatedProduct, Price
from product_ranking.spiders import cond_set, cond_set_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider


def _itemprop(data, name, attr=None):
    attr = 'text' if attr is None else 'attr(%s)' % attr
    return data.css('[itemprop=%s]::%s' % (name, attr)).extract()


class QuillProductsSpider(ProductsSpider):
    name = 'quill_products'

    allowed_domains = [
        'quill.com'
    ]

    SEARCH_URL = "http://www.quill.com/search?dsNav={sort_mode}:" \
                 ",Up:Page_Search_Leap&keywords={search_term}&act=Sort"

    SORT_MODES = {
        'default': '',
        'relevance': '',
        'price_desc': 'Ns:p.price|101|-1|',
        'price_asc': 'Ns:p.price|101|1|',
        'sale': 'Ns:p.sale_flag|101|-1|',
        'new': 'Ns:p.new_flag|101|-1|',
        'rating_desc': 'p.avg_rating|101|-1|',
        'rating_asc': 'p.avg_rating|101|1|'
    }

    def _total_matches_from_html(self, response):
        total = response.css('.noItemsFound').extract()
        if not total:
            return 0
        total = re.search('\d+', total[0])
        return int(total.group()) if total else 0

    def _scrape_next_results_page_link(self, response):
        link = response.css('#ShowMoreResults::attr(href)')
        return urljoin(response.url, link[0].extract()) if link else None

    def _fetch_product_boxes(self, response):
        return response.css('.BrowseItem .itemDetails')

    def _link_from_box(self, box):
        return _itemprop(box, 'name', 'href')[0]

    def _populate_from_box(self, response, box, product):
        cond_set(product, 'title', _itemprop(box, 'name'), unicode.strip)
        cond_set(product, 'price', _itemprop(box, 'price'))

    def _populate_from_html(self, response, product):
        cond_set(product, 'title', _itemprop(response, 'name'), unicode.strip)
        cond_set(product, 'model', _itemprop(response, 'model'),
                 lambda s: s.replace(u'\xa0 Model # ', ''))
        cond_set(product, 'price', _itemprop(response, 'price'))
        cond_set(product, 'image_url',
                 response.css('.skuImageSTD::attr(src)').extract(),
                 lambda url: urljoin(response.url, url))
        xpath = '//div[@id="divDescription"]/div[@class="qOverflow"]' \
                '/node()[normalize-space()]'
        cond_set_value(product, 'description',
                       response.xpath(xpath).extract(), ''.join)
        self._populate_related_products(response, product)
        price = product.get('price')
        if price:
            if price.startswith('$'):
                price = re.sub('[$ ,]+', '', price)
                product['price'] = Price(priceCurrency='USD', price=price)
            else:
                self.log('Incorrect price format %s at %s' %
                         (price, response.url))
                product['price'] = None

    def _populate_related_products(self, response, product):
        related_products = {}
        cond_set_value(related_products, 'Customers also viewed',
                       list(self._carousel_getitems(
                           response.css('.skuRightColInner .carouselInner')
                       )) or None)
        cond_set_value(related_products, 'Customers also bought', list(
            self._carousel_getitems(
                response.xpath('//h3[text()="Customers also bought"]/..'))
        ) or None)
        fbt = []
        for item in response.css('.bTogether .formRow'):
            title = item.css('.desc::text')
            url = item.css('.formLabel.SL_m::attr(href)')
            if url and title:
                fbt.append(
                    RelatedProduct(url=urljoin(response.url, url[0].extract()),
                                   title=title[0].extract()))
        cond_set_value(related_products, 'Frequently Bought Together,',
                       fbt or None)
        cond_set_value(product, 'related_products', related_products)


    def _carousel_getitems(self, carousel):
        if not carousel:
            return
        for item in carousel[0].css('.item_ph'):
            link = item.css('.desc2')
            url = link.css('::attr(href)')
            title = link.css('::text')
            if url and title:
                yield RelatedProduct(
                    url=urljoin('http://quill.com', url[0].extract()),
                    title=title[0].extract())
