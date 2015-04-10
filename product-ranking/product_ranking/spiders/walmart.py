from __future__ import division, absolute_import, unicode_literals

import json
import pprint
import re
import urlparse
import uuid
import string
from datetime import datetime

from scrapy import Selector
from scrapy.http import Request, FormRequest
from scrapy.log import ERROR, INFO

from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.items import (SiteProductItem, RelatedProduct,
                                   BuyerReviews, Price)
from product_ranking.spiders import BaseProductsSpider, FormatterWithDefaults, \
    cond_set, cond_set_value


is_empty = lambda x: x[0] if x else ""


def get_string_from_html(xp, link):
    loc = is_empty(link.xpath(xp).extract())
    return Selector(text=loc).xpath('string()').extract()


class WalmartProductsSpider(BaseProductsSpider):
    """Implements a spider for Walmart.com.

    This spider has 2 very peculiar things.
    First, it receives 2 types of pages so it need 2 rules for every action.
    Second, the site sometimes redirects a request to the same URL so, by
    default, Scrapy would discard it. Thus we override everything to handle
    redirects.

    FIXME: Currently we redirect infinitely, which could be a problem.
    """
    name = 'walmart_products'
    allowed_domains = ["walmart.com", "msn.com"]

    SEARCH_URL = "http://www.walmart.com/search/search-ng.do?Find=Find" \
        "&_refineresult=true&ic=16_0&search_constraint=0" \
        "&search_query={search_term}&sort={search_sort}"

    LOCATION_URL = "http://www.walmart.com/location"

    QA_URL = "http://www.walmart.com/reviews/api/questions" \
             "/{product_id}?sort=mostRecentQuestions&pageNumber={page}"

    QA_LIMIT = 0xffffffff

    _SEARCH_SORT = {
        'best_match': 0,
        'high_price': 'price_high',
        'low_price': 'price_low',
        'best_sellers': 'best_seller',
        'newest': 'new',
        'rating': 'rating_high',
    }

    sponsored_links = []

    _JS_DATA_RE = re.compile(
        r'define\(\s*"product/data\"\s*,\s*(\{.+?\})\s*\)\s*;', re.DOTALL)

    user_agent = 'default'


    def __init__(self, search_sort='best_match', zipcode='94117',
                 *args, **kwargs):
        if zipcode:
            self.zipcode = zipcode
        if search_sort == 'best_sellers':
            self.SEARCH_URL += '&soft_sort=false&cat_id=0'
        super(WalmartProductsSpider, self).__init__(
            site_name=self.allowed_domains[0],
            url_formatter=FormatterWithDefaults(
                search_sort=self._SEARCH_SORT[search_sort]
            ),
            *args, **kwargs)

    def start_requests(self):
        for st in self.searchterms:
            url = "http://www.walmart.com/midas/srv/ypn?" \
                "query=%s&context=Home" \
                "&clientId=walmart_us_desktop_backfill_search" \
                "&channel=ch_8,backfill" % (st,)
            yield Request(url=url, callback=self.get_sponsored_links)

        if self.product_url:
            prod = SiteProductItem()
            prod['is_single_result'] = True
            yield Request(self.product_url,
                          self._parse_single_product,
                          meta={'product': prod})

    def get_sponsored_links(self, response):
        self.reql = []
        self.sponsored_links = []
        for link in response.xpath(
            '//div[contains(@class, "yahoo_sponsored_link")]'
                '/div[contains(@class, "yahoo_sponsored_link")]'):
            ad_title = is_empty(
                get_string_from_html('div/span[@class="title"]/a', link))
            ad_text = is_empty(
                get_string_from_html('div/span[@class="desc"]/a', link))
            visible_url = is_empty(
                get_string_from_html('div/span/span[@class="host"]/a', link))
            actual_url = is_empty(
                link.xpath('div/span[@class="title"]/a/@href').extract())
            sld = {"ad_title": ad_title,
                   "ad_text": ad_text,
                   "visible_url": visible_url,
                   "actual_url": actual_url,
                   }
            new_meta = response.meta.copy()
            new_meta["sld"] = sld
            new_meta['handle_httpstatus_list'] = [400, 403, 404, 405]
            self.reql.append(Request(
                actual_url,
                callback=self.parse_sponsored_links,
                errback=self.parse_sponsored_links,
                meta=new_meta,
                dont_filter=True))
        if self.reql:
            req1 = self.reql.pop(0)
            new_meta = req1.meta
            new_meta['reql'] = self.reql
            self.sld = new_meta["sld"]
            return req1.replace(meta=new_meta)
        return super(WalmartProductsSpider, self).start_requests()

    def parse_sponsored_links(self, response):
        if hasattr(response, "meta"):
            if response.status == 200:
                self.sld['actual_url'] = response.url
                self.sponsored_links.append(self.sld)

            if self.reql:
                req1 = self.reql.pop(0)
                new_meta = req1.meta
                new_meta['reql'] = self.reql
                self.temp_spons_link = req1.url
                self.sld = new_meta["sld"]
                return req1.replace(meta=new_meta)
        else:
            self.sld['actual_url'] = self.temp_spons_link
            self.sponsored_links.append(self.sld)

            req1 = self.reql.pop(0)
            new_meta = req1.meta
            new_meta['reql'] = self.reql
            self.temp_spons_link = req1.url
            self.sld = new_meta["sld"]
            return req1.replace(meta=new_meta)
        del self.temp_spons_link, self.sld, self.reql
        return super(WalmartProductsSpider, self).start_requests()

    def parse_product(self, response):
        if self._search_page_error(response):
            self.log(
                "Got 404 when coming from %r." % response.request.url, ERROR)
            return

        product = response.meta['product']

        if self.sponsored_links:
            product["sponsored_links"] = self.sponsored_links

        self._populate_from_js(response, product)
        self._populate_from_html(response, product)
        product['buyer_reviews'] = self._build_buyer_reviews(response)
        cond_set_value(product, 'locale', 'en-US')  # Default locale.
        if 'brand' not in product:
            cond_set_value(product, 'brand', u'NO BRAND')
        self._gen_related_req(response)

        id = re.findall('\/(\d+)', response.url)
        response.meta['product_id'] = id[0] if id else None
        # if id:
        #    url = 'http://www.walmart.com/reviews/api/questions/{0}?' \
        #          'sort=mostRecentQuestions&pageNumber=1'.format(id[0])
        #    meta = {
        #        "product": product,
        #        "relreql": response.meta["relreql"],
        #        "response": response
        #    }

        #    return Request(url=url, meta=meta, callback=self.get_questions)

        if not product.get('price'):
            return self._gen_location_request(response)
        return self._start_related(response)

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def _search_page_error(self, response):
        path = urlparse.urlsplit(response.url)[2]
        return path == '/FileNotFound.aspx'

    def _build_related_products(self, url, related_product_nodes):
        also_considered = []
        for node in related_product_nodes:
            link = urlparse.urljoin(url, node.xpath('../@href').extract()[0])
            title = node.xpath('text()').extract()[0]
            also_considered.append(RelatedProduct(title, link))
        return also_considered

    def _build_buyer_reviews(self, response):
        overall_block = response.xpath(
            '//*[contains(@class, "review-summary")]'
            '//p[contains(@class, "heading")][contains(text(), "|")]//text()'
        ).extract()
        overall_text = ' '.join(overall_block)
        if not overall_text.strip():
            return
        buyer_reviews = {}
        buyer_reviews['num_of_reviews'] = int(
            overall_text.split('review')[0].strip())
        buyer_reviews['average_rating'] = float(
            overall_text.split('|')[1].split('out')[0].strip())
        buyer_reviews['rating_by_star'] = {}
        for _revs in response.css('.review-histogram .rating-filter'):
            _star = _revs.css('.meter-inline ::text').extract()[0].strip()
            _reviews = _revs.css('.rating-val ::text').extract()[0].strip()
            _star = (_star.lower().replace('stars', '').replace('star', '')
                     .strip())
            buyer_reviews['rating_by_star'][int(_star)] = int(_reviews)
        return BuyerReviews(**buyer_reviews)

    def _populate_from_html(self, response, product):
        cond_set(
            product,
            'description',
            response.css('.about-product-section').extract(),
            conv=''.join
        )
        cond_set(
            product,
            'title',
            response.xpath(
                "//h1[contains(@class,'product-name')]/text()").extract(),
            conv=string.strip)
        cond_set(
            product,
            'brand',
            response.xpath(
                "//div[@class='product-subhead-section']"
                "/a[@id='WMItemBrandLnk']/text()").extract())     
        if not product.get("brand"):
            brand = is_empty(response.xpath(
                "//h1[contains(@class, 'product-name product-heading')]/text()"
            ).extract())
            cond_set(
                product,
                'brand',
                (guess_brand_from_first_words(brand.strip()),)
            )
        also_considered = self._build_related_products(
            response.url,
            response.css('.top-product-recommendations .tile-heading'),
        )
        if also_considered:
            product.setdefault(
                'related_products', {})["buyers_also_bought"] = also_considered

        recommended = self._build_related_products(
            response.url,
            response.xpath(
                "//p[contains(text(), 'Check out these related products')]/.."
                "//*[contains(@class, 'tile-heading')]"
            ),
        )
        if recommended:
            product.setdefault(
                'related_products', {})['recommended'] = recommended
        if not product.get('price'):
            currency = response.css('[itemprop=priceCurrency]::attr(content)')
            price = response.css('[itemprop=price]::attr(content)')
            if price and currency:
                currency = currency.extract()[0]
                price = re.search('[,. 0-9]+', price.extract()[0])
                if price:
                    price = price.group()
                    price = price.replace(',', '').replace(' ', '')
                    cond_set_value(product, 'price',
                                   Price(priceCurrency=currency, price=price))

    def _gen_location_request(self, response):
        data = {"postalCode": ""}
        new_meta = response.meta.copy()
        new_meta['handle_httpstatus_list'] = [404, 405]
        # Need Conetnt-Type= app/json
        req = FormRequest.from_response(
            response=response,
            url=self.LOCATION_URL,
            method='POST',
            formdata=data,
            callback=self._after_location,
            meta=new_meta,
            headers={'x-requested-with': 'XMLHttpRequest',
                     'Content-Type': 'application/json'},
            dont_filter=True)
        req = req.replace(body='{"postalCode":"' + self.zipcode + '"}')
        return req

    def _gen_related_req(self, response):
        prodid = response.meta.get('productid')
        if not prodid:
            prodid = response.xpath(
                "//div[@id='recently-review']/@data-product-id").extract()
            if prodid:
                prodid = prodid[0]
        if not prodid:
            self.log("No PRODID in %r." % response.url, ERROR)
            return
        cid = uuid.uuid4()
        reql = []
        url1 = (
            "http://www.walmart.com/irs?parentItemId%5B%5D={prodid}"
            "&module=ProductAjax&clientGuid={cid}").format(
                prodid=prodid,
                cid=cid)
        reql.append((url1, self._proc_mod_related))
        response.meta['relreql'] = reql
        return reql

    def _start_related(self, response):
        product = response.meta['product']
        reql = response.meta.get('relreql')
        if not reql:
            return self._request_questions_info(response)
            #return product
        (url, proc) = reql.pop(0)
        response.meta['relreql'] = reql
        return Request(
            url,
            meta=response.meta.copy(),
            callback=proc,
            dont_filter=True)

    def _proc_mod_related(self, response):
        product = response.meta['product']
        text = response.body_as_unicode().encode('utf-8')
        try:
            jdata = json.loads(text)
            modules = jdata['moduleList']
            for m in modules:
                html = m['html']
                sel = Selector(text=html)
                title, rel = self._parse_related(sel, response)
                if 'related_products' not in product:
                    product['related_products'] = {}
                if rel:
                    product['related_products'][title] = rel[:]
        except ValueError:
            self.log(
                "Unable to parse JSON from %r." % response.request.url, ERROR)
        return self._start_related(response)

    def _parse_related(self, sel, response):
        def full_url(url):
            return urlparse.urljoin(response.url, url)
        related = []
        title = sel.xpath("//div[@class='parent-heading']/h4/text()").extract()
        if not title:
            title = sel.xpath("//p[@class='heading-a']/text()").extract()
        if not title:
            title = sel.xpath("//div/h1/text()").extract()
        if title:
            title = title[0]
        els = sel.xpath("//ol/li//a[@class='tile-section']/p/..")
        for el in els:
            name = el.xpath("p/text()").extract()
            if name:
                name = name[0]
            href = el.xpath("@href").extract()
            if href:
                href = href[0]
                if 'dest=' in href:
                    url_split = urlparse.urlsplit(href)
                    query = urlparse.parse_qs(url_split.query)
                    original_url = query.get('dest')
                    if original_url:
                        original_url = original_url[0]
                else:
                    original_url = href
                related.append(RelatedProduct(name, full_url(original_url)))
        return (title, related)

    def _after_location(self, response):
        if response.status == 200:
            url = response.meta['product']['url']
            return Request(
                url,
                meta=response.meta.copy(),
                callback=self._reload_page,
                dont_filter=True)
        return self._start_related(response)

    def _reload_page(self, response):
        product = response.meta['product']
        self._populate_from_js(response, product)
        self._populate_from_html(response, product)
        return self._start_related(response)

    def _populate_from_js(self, response, product):
        data = {}
        m = re.search(
            self._JS_DATA_RE, response.body_as_unicode().encode('utf-8'))
        if m:
            text = m.group(1)
            try:
                data = json.loads(text)
            except ValueError:
                pass
        if not data:
            self.log("No JS matched in %r." % response.url, ERROR)
            return
        try:
            response.meta['productid'] = str(data['buyingOptions']['usItemId'])
            cond_set_value(product, 'title', data['productName'])
            available = data['buyingOptions']['available']
            cond_set_value(
                product,
                'is_out_of_stock',
                not available,
            )
            cond_set_value(
                product,
                'is_in_store_only',
                data['buyingOptions']['storeOnlyItem'],
            )
            if available:
                price_block = None
                try:
                    price_block = data['buyingOptions']['price']
                except KeyError:
                    # Packs of products have different buyingOptions.
                    try:
                        price_block =\
                            data['buyingOptions']['minPrice']
                        #     data['buyingOptions']['maxPrice']
                    except KeyError:
                        self.log((
                            "Product with unknown buyingOptions "
                            "structure: %s\n%s") % (
                                response.url, pprint.pformat(data)),
                            ERROR
                        )
                if price_block:
                    try:
                        _price = Price(
                            priceCurrency=price_block['currencyUnit'],
                            price=price_block['currencyAmount']
                        )
                        cond_set_value(product, 'price', _price)
                    except KeyError:
                        try:
                            if price_block["currencyUnitSymbol"] == "$":
                                _price = Price(
                                    priceCurrency="USD",
                                    price=price_block['currencyAmount']
                                )
                            cond_set_value(product, 'price', _price)
                        except KeyError:
                            self.log(
                                ("Product with unknown buyingOptions "
                                    "structure: %s\n%s") % (
                                        response.url, pprint.pformat(data)),
                                ERROR
                            )
        except KeyError:
            pass
        try:
            cond_set_value(
                product, 'upc', data['analyticsData']['upc'], conv=unicode)
        except (ValueError, KeyError):
            pass  # Not really a UPC.
        try:
            cond_set_value(
                product,
                'image_url',
                data['primaryImageUrl'],
                conv=unicode)
        except KeyError:
            pass

        try:
            cond_set_value(
                product,
                'brand',
                data['analyticsData']['brand'],
                conv=unicode)
        except KeyError:
            pass

    def _scrape_total_matches(self, response):
        if response.css('.no-results'):
            return 0

        matches = response.css('.result-summary-container ::text').re(
            'Showing \d+ of (.+) results')
        if matches:
            num_results = matches[0].replace(',', '')
            num_results = int(num_results)
        else:
            num_results = None
            self.log(
                "Failed to extract total matches from %r." % response.url,
                ERROR
            )
        return num_results

    def _scrape_results_per_page(self, response):
        num = response.css('.result-summary-container ::text').re(
            'Showing (\d+) of')
        if num:
            return int(num[0])
        return None

    def _scrape_product_links(self, response):
        items = response.xpath('//div[@class="js-tile tile-landscape"]')
        if not items:
            self.log("Found no product links in %r." % response.url, INFO)

        for item in items:
            link = item.css('a.js-product-title ::attr(href)')[0].extract()

            if item.css('div.pick-up-only').xpath('text()').extract():
                is_pickup_only = True
            else:
                is_pickup_only = False

            if item.xpath(
                './/div[@class="tile-row"]'
                '/span[@class="in-store-only"]/text()'
            ).extract():
                is_in_store_only = True
            else:
                is_in_store_only = False

            res_item = SiteProductItem()
            res_item['is_pickup_only'] = is_pickup_only
            res_item['is_in_store_only'] = is_in_store_only

            yield link, res_item

    def _scrape_next_results_page_link(self, response):
        next_page = None

        next_page_links = response.css(".paginator-btn-next ::attr(href)")
        if len(next_page_links) == 1:
            next_page = next_page_links.extract()[0]
        elif len(next_page_links) > 1:
            self.log(
                "Found more than one 'next page' link in %r." % response.url,
                ERROR
            )
        else:
            self.log(
                "Found no 'next page' link in %r (which could be OK)."
                % response.url,
                INFO
            )

        return next_page

    def _request_questions_info(self, response):
        product_id = response.meta['product_id']
        if product_id is None:
            return response.meta['product']
        response.meta['product']['recent_questions'] = []
        url = self.QA_URL.format(product_id=product_id, page=1)
        return Request(url, self._parse_questions,
                       meta=response.meta, dont_filter=True)

    def _parse_questions(self, response):
        data = json.loads(response.body_as_unicode())
        product = response.meta['product']
        last_date = product.get('date_of_last_question')
        questions = product['recent_questions']
        dateconv = lambda date: datetime.strptime(date, '%m/%d/%Y').date()
        for question_data in data.get('questionDetails', []):
            date = dateconv(question_data['submissionDate'])
            if last_date is None:
                product['date_of_last_question'] = last_date = date
            if date == last_date:
                questions.append(question_data)
            else:
                break
        else:
            total_pages = min(self.QA_LIMIT,
                              data['pagination']['pages'][-1]['num'])
            current_page = response.meta.get('current_qa_page', 1)
            if current_page < total_pages:
                url = self.QA_URL.format(
                    product_id=response.meta['product_id'],
                    page=current_page + 1)
                response.meta['current_qa_page'] = current_page + 1
                return Request(url, self._parse_questions, meta=response.meta,
                               dont_filter=True)
        if not questions:
            del product['recent_questions']
        else:
            product['date_of_last_question'] = str(last_date)
        return product