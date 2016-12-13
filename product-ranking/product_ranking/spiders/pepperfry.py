import urllib
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set, cond_set_value
from product_ranking.items import SiteProductItem, RelatedProduct, Price
from spiders_shared_code.pepperfry_variants import PepperfryVariants
from scrapy import Request
from scrapy.log import ERROR


class PepperfryProductsSpider(BaseProductsSpider):
    """ pepperfry.com product ranking spider

    Missing fields:
    * `reviews`
    * `upc`

    Takes `order` argument with the following values:
    * `new` (default)
    * `fastest`
    * `price_asc`, `price_desc`
    """
    name = 'pepperfry_products'
    allowed_domains = ['pepperfry.com']
    SEARCH_URL = ('http://www.pepperfry.com/site_product/search?'
                  'q={search_term}&'
                  'src={search_term}&'
                  'order={sort_mode}&'
                  'dir={dir}&p={page}')

    SORT_MODES = {
        'default': ' ',
        'new': 'updated_at desc',
        'price_asc': 'price asc',  # from low to high price
        'price_desc': 'price desc',  # from high to low price
        'fastest': 'ttw asc'  # fastest shipping
    }

    def __init__(self, sort_mode=None, *args, **kwargs):
        self.SORT = self._parse_sort(sort_mode)
        self.pages = dict()
        super(PepperfryProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(
                sort_mode=self.SORT[0], dir=self.SORT[1]),
            site_name=self.allowed_domains[0],
            *args, **kwargs)

    def _parse_sort(self, sort_mode):
        if not sort_mode or sort_mode.lower() not in self.SORT_MODES:
            key = 'default'
        else:
            key = sort_mode.lower()
        return self.SORT_MODES[key].split(' ')  # ex: ['price', 'asc']

    def start_requests(self):
        for st in self.searchterms:
            url = self.url_formatter.format(
                self.SEARCH_URL,
                search_term=urllib.quote_plus(st.encode('utf-8')),
                page=''  # don't set for first request, or results will differ
            )
            self.pages[st] = 2
            yield Request(url,
                          meta=dict(search_term=st, remaining=self.quantity))

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            prod['url'] = self.product_url
            prod['search_term'] = ''
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod})

        if self.products_url:
            urls = self.products_url.split('||||')
            for url in urls:
                prod = SiteProductItem()
                prod['url'] = url
                prod['search_term'] = ''
                yield Request(url,
                              self._parse_single_product,
                              meta={'product': prod})

    def _search_page_error(self, response):
        return not self.is_nothing_found(response)

    def is_nothing_found(self, response):
        items = response.css('#clip_grid > div[id]')
        return bool(len(items))

    def _scrape_product_links(self, response):
        items = response.css('#clip_grid > div[id] > .title_1 > '
                             'a::attr(href)').extract()
        for item in items:
            yield item, SiteProductItem()

    def _scrape_total_matches(self, response):
        items = response.css('#total_product_count::text').extract()
        try:
            return int(items[0])
        except (ValueError, IndexError) as e:
            self.log(str(e), ERROR)
            return 0

    def _scrape_results_per_page(self, response):
        items = response.css('#clip_grid > div[id]')
        return int(len(items))

    def _scrape_next_results_page_link(self, response):
        search_term = response.meta['search_term']
        link = self.url_formatter.format(
            self.SEARCH_URL,
            search_term=search_term, page=self.pages[search_term])
        self.pages[search_term] += 1
        return link

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _populate_from_html(self, response, prod):
        # title
        title = response.css('h2[itemprop=name]::text')
        cond_set(prod, 'title', title.extract())

        # price
        price_div = response.css('[itemprop=offers] > [itemprop=price]')
        price_div = price_div[0]
        currency = price_div.css('[itemprop=priceCurrency]::attr(content)')
        price = price_div.css('[itemprop=price]::attr(content)')
        if currency and price:
            prod['price'] = Price(currency[0].extract(), price[0].extract())

        # out of stock
        cond_set_value(
            prod, 'is_out_of_stock', response.css('.out_of_stock_box'), bool)

        # image
        img = response.css('.vip_gallery [itemprop=image] ::attr(src)')
        cond_set(prod, 'image_url', img.extract())

        # description, merged with details
        desc = response.xpath('//div[@itemprop="description"]/p | '
                              '//ul[@class="linear_list"]')
        cond_set_value(prod, 'description', ''.join(desc.extract()))

        # brand
        brand = response.css('input[name=brand_name] ::attr(value)')
        cond_set(prod, 'brand', brand.extract())

        # reseller_id
        regex = "-(\d+)\."
        reseller_id = re.findall(regex, response.url)
        reseller_id = reseller_id[0] if reseller_id else None
        cond_set_value(prod, "reseller_id", reseller_id)

        # related products
        related = []
        rel_key = ' '.join(response.xpath('//div[@class="moreby_brand"]'
                                          '/a/h2//text()').extract())
        rel_items = response.css('#morefrom_slider > ul > li')
        for rel_item in rel_items:
            r_hr = rel_item.css('a::attr(href)')
            r_t = rel_item.css('a > span::text')
            if not r_hr or not r_t:
                continue
            r = RelatedProduct(r_t[0].extract(), r_hr[0].extract())
            related.append(r)
        related_products = {rel_key: related}
        if related_products and related_products.values()[0]:
            cond_set_value(prod, 'related_products', related_products)

    def parse_product(self, response):
        prod = response.meta['product']
        cond_set_value(prod, 'url', response.url)
        cond_set_value(prod, 'locale', 'en-IN')
        self._populate_from_html(response, prod)
        pv = PepperfryVariants()
        pv.setupSC(response)
        variants = pv._variants()
        cond_set_value(prod, 'variants', variants)
        return prod
