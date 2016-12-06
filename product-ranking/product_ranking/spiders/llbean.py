# coding=utf-8
from __future__ import division, absolute_import, unicode_literals

import re
import json
import urllib
from urlparse import urljoin

from scrapy import Request

from product_ranking.items import SiteProductItem, Price, RelatedProduct, \
    BuyerReviews
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set_value


class LLBeanProductsSpider(BaseProductsSpider):
    name = 'llbean_products'
    allowed_domains = ["llbean.com"]
    start_urls = []

    SEARCH_URL = "http://www.llbean.com/llb/gnajax/2?storeId=1&catalogId=1" \
                 "&langId=-1&position={pagenum}&sort_field={search_sort}&freeText={search_term}"

    URL = "http://www.llbean.com"

    SEARCH_SORT = {
        'best_match': 'Relevance',
        'high_price': 'Price (Descending)',
        'low_price': 'Price (Ascending)',
        'best_sellers': 'Num_Of_Orders',
        'avg_review': 'Grade (Descending)',
        'product_az': 'Name (Ascending)',
    }

    RR_URL = "http://recs.richrelevance.com/rrserver/p13n_generated.js" \
             "?a=45a98cdf34a56c26&p={product_id}" \
             "&n={short_title}" \
             "&pt=|item_page.rrtop|item_page.rrright" \
             "&cts=http%3A%2F%2Fwww.llbean.com&st=&flv=0.0.0&l=1"

    RR_RELATIONS = {'Customers Also Purchased': lambda lst: lst[-4:],
                    'Customers Also Viewed': lambda lst: lst[:5], }

    BUNDLE_URL = "http://www.llbean.com/webapp/wcs/stores/servlet" \
                 "/ShowBundleJSON?storeId=1&catalogId=1&langId=-1&subrnd=0" \
                 "&categoryId={product_id}"

    image_url = "http://cdni.llbean.com/is/image/wim/"

    def __init__(self, search_sort='best_match', *args, **kwargs):
        super(LLBeanProductsSpider, self).__init__(
            url_formatter=FormatterWithDefaults(pagenum=1,
                                                search_sort=self.SEARCH_SORT[
                                                    search_sort]
            ),
            *args,
            **kwargs)

    def parse_product(self, response):
        product = response.meta['product']

        reseller_id = response.xpath('.//*[@itemprop="productID"]/text()').extract()
        reseller_id = reseller_id[0] if reseller_id else None
        cond_set_value(product, 'reseller_id', reseller_id)

        elts = response.xpath('//div[@id="ppDetails"]/node()')
        elts = [elt.extract()
                for elt in elts if not elt.css('#ppPremiseStatement')]
        cond_set_value(product, 'description', elts, ''.join)
        regexp = '\$([\d ,.]+)'
        price = response.css('.toOrderItemSalePrice::text').re(regexp) or []
        price += response.css('.toOrderItemPrice::text').re(regexp)
        price = min([re.sub('[, ]', '', p) for p in price] or (0, 0),
                    key=float)
        if price:
            product['price'] = Price(priceCurrency='USD', price=price)
        self._populate_buyer_reviews(response)
        return self._request_related_products(response)

    def _scrape_total_matches(self, response):
        data = json.loads(response.body_as_unicode())
        response.meta['position'] = {}
        response.meta['position'] = data[0]['productsPerPage']
        return data[0]['pageFoundSize']

    def _scrape_product_links(self, response):
        data = json.loads(response.body_as_unicode())
        for item in data[0]['products']:
            prod = SiteProductItem()
            prod['title'] = item['name']
            cond_set_value(prod, 'brand',
                           item['brand'] if item['brand'] != '0' else None)

            prod['upc'] = item['item'][0]['prodId']
            prod['image_url'] = self.image_url + item['img']
            cond_set_value(prod, 'is_out_of_stock',
                           item['item'][0]['stock'] != "IN")
            prod['locale'] = "en-US"
            url = urljoin(response.url, item['displayUrl'])
            yield url, prod

    def _scrape_next_results_page_link(self, response):
        data = json.loads(response.body_as_unicode())
        if response.meta['position'] == 48:
            pos = 49
            response.meta['position'] = pos
        else:
            pos = response.meta['position'] + data[0]['productsPerPage']
            response.meta['position'] = pos
        max_pages = data[0]['pageFoundSize']
        cur_page = pos
        if cur_page >= max_pages:
            return None

        st = urllib.quote(data[0]['originalSearchTerm'])
        return self.url_formatter.format(self.SEARCH_URL,
                                         search_term=st,
                                         pagenum=cur_page)

    def _request_related_products(self, response):
        title = response.css('#ppName [itemprop=name]::text').extract()
        prod_id = re.findall('pzCategoryId = "([^"]+)"', response.body)
        if not (title and prod_id):
            self.log("Could not request related products")
            return response.meta['product']
        url = self.RR_URL.format(short_title=title[0], product_id=prod_id[0])
        response.meta['product_id'] = prod_id[0]
        return Request(url, self._parse_related_products, dont_filter=True,
                       meta=response.meta)

    def _parse_related_products(self, response):
        results = {}
        text = response.body
        bodies = re.findall("',html:'(.+)'}]},", response.body)
        for relation, limit_func in self.RR_RELATIONS.iteritems():
            products = []
            body = next((b for b in bodies if relation in b), None)
            if not body:
                continue
            prods = re.findall('id="link\d+" href="([^"]+)".+?title="([^"]+)',
                               body)
            for link, title in prods:
                prod_id = re.findall('&p=([^&]+)', link)
                if not prod_id:
                    continue
                url = 'http://www.llbean.com/llb/shop/%s' % prod_id[0]
                products.append(RelatedProduct(url=url, title=title))
            results[relation] = limit_func(products)
        cond_set_value(response.meta['product'], 'related_products', results)
        return self._request_bundle(response)

    def _request_bundle(self, response):
        product_id = response.meta['product_id']
        url = self.BUNDLE_URL.format(product_id=product_id)
        return Request(url, self._parse_bundle, meta=response.meta)

    def _parse_bundle(self, response):
        product = response.meta['product']
        related_products = product.get('related_products', {})
        data = json.loads(response.body_as_unicode())
        error = data.get('errorOccurred', 'true') == 'true'
        no_bundle = data.get('hasBundle', 'false') == 'false'
        if error or no_bundle:
            return product
        relation = data.get('headerTopMainTxt',
                            'Frequently Purchased Together')
        url = urljoin(response.url, data['rcmdLinkURL'].split('?')[0])
        title = data['rcmdName']
        related_products[relation] = [RelatedProduct(url=url, title=title)]
        product['related_products'] = related_products
        return product

    def _populate_buyer_reviews(self, response):
        product = response.meta['product']
        total = int((response.css('.PPNumber::text').extract() or ['0'])[0])
        if not total:
            return
        avg = response.css('[itemprop=ratingValue]::attr(content)').extract()
        avg = float(avg[0])
        by_star = {int(div.css('.PPHistStarLabelText::text').re('\d+')[0]):
                       int(div.css('.PPHistAbsLabel::text').re('\d+')[0])
                   for div in response.css('.PPHistogramBarRow')}
        cond_set_value(product, 'buyer_reviews',
                       BuyerReviews(num_of_reviews=total,
                                    average_rating=avg,
                                    rating_by_star=by_star))


