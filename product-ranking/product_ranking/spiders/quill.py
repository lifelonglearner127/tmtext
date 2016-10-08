import re
import json
from urlparse import urljoin
import urllib
import string

from scrapy.http import Request

from product_ranking.items import RelatedProduct, Price, BuyerReviews
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.spiders import cond_set, cond_set_value, \
    cond_replace_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider


def _itemprop(data, name, attr=None):
    attr = 'text' if attr is None else 'attr(%s)' % attr
    return data.css('[itemprop=%s]::%s' % (name, attr)).extract()


def _strip_non_ascii(s):
    return filter(lambda x: x in string.printable, s)


class QuillProductsSpider(ProductsSpider):
    """ quill.com product ranking spider.

    Takes `order` argument with following possible values:

    * `relevance` (default)
    * `price_asc`, `price_desc`
    * `rating_asc`, `rating_desc`
    * `sale`
    * `new`

    Following fields are not scraped:
    * `is_out_of_stock`, `is_in_store_only`, `upc`
    """

    name = 'quill_products'

    allowed_domains = [
        'quill.com'
    ]

    SEARCH_URL = "http://www.quill.com/search?dsNav=Ns:{sort_mode}" \
                 ",Up:Page_Search_Leap&keywords={search_term}&act=Sort"

    SORT_MODES = {
        'default': '',
        'relevance': '',
        'price_desc': 'p.price|101|-1|:',
        'price_asc': 'p.price|101|1|:',
        'sale': 'p.sale_flag|101|-1|:',
        'new': 'p.new_flag|101|-1|:',
        'rating_desc': 'p.avg_rating|101|-1|:',
        'rating_asc': 'p.avg_rating|101|1|:'
    }

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse(self, response):
        redirected_url = response.request.meta.get('redirect_urls')
        if redirected_url:
            root_url = response.url
            additional_url = "?dsNav=Ns:{sort_mode},Up:Page_Browse_Leap,"\
                             "Nea:True,N:17361&act=Sort"
            url = urljoin(root_url, additional_url)
            for st in self.searchterms:
                return Request(
                    self.url_formatter.format(
                        url,
                        search_term=urllib.quote_plus(st.encode('utf-8')),
                    ),
                    meta={'search_term': st, 'remaining': self.quantity},
                )
        else:
            return super(QuillProductsSpider, self).parse(response)


    def _total_matches_from_html(self, response):
        # for exact results
        total = response.css('.noItemsFound').extract()
        # for broad results(ex: table)
        if not total:
            total = response.xpath(
                '//span[contains(@class, "results")]/span[@class="L"]/text()'
            ).extract()
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
        link = box.xpath('.//h3/a/@href').extract()
        possible_link = box.xpath('.//h3/span/@data-url').extract()
        link.extend(possible_link)
        return link[0]

    def _populate_from_box(self, response, box, product):
        red_span = box.xpath('..//span[@class="red"]/text()').extract()
        if red_span:
            s = 'Currently out of stock'
            if s in red_span[0]:
                cond_set_value(product, 'is_out_of_stock', True)
        else:
            cond_set_value(product, 'is_out_of_stock', False)
        cond_set(
            product, 'title', _itemprop(box, 'name'),
            unicode.strip
        )
        product['title'] = _strip_non_ascii(product.get('title', ''))
        cond_set(product, 'price', _itemprop(box, 'price'))

    def _populate_from_html(self, response, product):
        cond_set(
            product, 'title',
            _itemprop(response, 'name'),
            unicode.strip
        )
        product['title'] = _strip_non_ascii(product.get('title', ''))
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

        if not product.get("description"):
            desc = response.xpath("//div[@id='SkuTabDescription']").extract()
            if desc:
                product["description"] = desc[0]
        cond_set(
            product, 'brand',
            filter(product.get('title', '').startswith,
                   response.meta.get('brands', []))
        )
        if product.get('description', '') == '':
            xpath = '//div[@id="divDescription"]/node()[normalize-space()]'
            product['description'] = ''.join(response.xpath(xpath).extract())
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
        self._buyer_reviews_from_html(response, product)
        cond_replace_value(product, 'url', response.url.split('?', 1)[0])

        regex = "\/(\d+)\."
        reseller_id = re.findall(regex, response.url)
        reseller_id = reseller_id[0] if reseller_id else None
        cond_set_value(product, "reseller_id", reseller_id)

        data = r'quillMData\s=\s(.*)</script>'
        data_script = re.findall(data, response.body_as_unicode())
        j = json.loads(data_script[0])
        brand = j.get('brandName')
        if brand:
            cond_set_value(product, 'brand', brand[0])

        locale = j['culturecode']
        cond_set_value(product, 'locale', locale)

        if not product.get("is_out_of_stock"):
            red_span = response.xpath('//span[@class="red"]/text()').extract()
            if red_span:
                s = 'Currently out of stock'
                if s in red_span[0]:
                    cond_set_value(product, 'is_out_of_stock', True)
            else:
                cond_set_value(product, 'is_out_of_stock', False)

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
                                   title=_strip_non_ascii(title[0].extract())))
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
                    title=_strip_non_ascii(title[0].extract()))

    def _buyer_reviews_from_html(self, response, product):
        rarea = response.xpath(
            "//div[@id='ReviewContent']")
        if rarea:
            rarea = rarea[0]
        else:
            return
        total = rarea.xpath("//span[@class='count']/text()").extract()
        if total:
            try:
                total = int(total[0])
            except ValueError:
                total = 0
        if not total:
            cond_set_value(product, 'buyer_reviews', ZERO_REVIEWS_VALUE)
            return
        avrg = rarea.xpath(
            "//span[contains(@class,'average')]/text()").extract()
        if avrg:
            try:
                avrg = float(avrg[0])
            except ValueError:
                avrg = 0.0
        else:
            return
        ratings = {}
        rat = rarea.xpath("//ul[@class='pr-ratings-histogram-content']/li")
        for irat in rat:
            label = irat.xpath(
                "p[@class='pr-histogram-label']/span/text()").re("(\d) Stars")
            if label:
                label = label[0]
            val = irat.xpath(
                "p[@class='pr-histogram-count']/span/text()").re("\((\d+)\)")
            try:
                val = int(val[0])
            except ValueError:
                val = 0
            ratings[label] = val
        reviews = BuyerReviews(num_of_reviews=total,
                               average_rating=avrg,
                               rating_by_star=ratings)
        cond_set_value(product, 'buyer_reviews', reviews)
