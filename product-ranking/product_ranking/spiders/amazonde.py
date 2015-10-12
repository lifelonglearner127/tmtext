# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import json
import re
import string
import urlparse
from datetime import datetime

from scrapy.http import Request
from scrapy.http.request.form import FormRequest
from scrapy.log import msg, ERROR, WARNING, INFO, DEBUG

from product_ranking.items import SiteProductItem, Price, BuyerReviews, RelatedProduct
from product_ranking.spiders import BaseProductsSpider, cond_set,\
    cond_set_value, FLOATING_POINT_RGEX
from product_ranking.validation import BaseValidator
from product_ranking.amazon_bestsellers import amazon_parse_department
from product_ranking.settings import ZERO_REVIEWS_VALUE
from product_ranking.marketplace import Amazon_marketplace


try:
    from captcha_solver import CaptchaBreakerWrapper
except ImportError as e:
    import sys
    print(
        "### Failed to import CaptchaBreaker.",
        "Will continue without solving captchas:",
        e,
        file=sys.stderr,
    )

    class FakeCaptchaBreaker(object):
        @staticmethod
        def solve_captcha(url):
            msg("No CaptchaBreaker to solve: %s" % url, level=WARNING)
            return None
    CaptchaBreakerWrapper = FakeCaptchaBreaker


is_empty = lambda x, y=None: x[0] if x else y


class AmazonDeValidatorSettings(object):  # do NOT set BaseValidatorSettings as parent
    optional_fields = ['model', 'brand', 'price', 'buyer_reviews', 'image_url']
    ignore_fields = [
        'is_in_store_only', 'is_out_of_stock', 'related_products', 'upc',
        'google_source_site', 'description', 'special_pricing', 'bestseller_rank'
    ]
    ignore_log_errors = False  # don't check logs for errors?
    ignore_log_duplications = False  # ... duplicated requests?
    ignore_log_filtered = False  # ... filtered requests?
    test_requests = {
        'abrakadabrasdafsdfsdf': 0,  # should return 'no products' or just 0 products
        'nothing_found_1234654654': 0,
        'iphone red edition': [50, 300],
        'xperia screen replacement': [5, 150],
        'ceiling fan industrial': [15, 90],
        'kaspersky total': [5, 250],
        'car navigator garmin': [5, 100],
        'yamaha drums midi': [2, 50],
        'black men shoes size 8 red': [5, 70],
        'car audio equalizer pioneer': [5, 120]
    }


class AmazonProductsSpider(BaseValidator, BaseProductsSpider):

    name = 'amazonde_products'
    allowed_domains = ["amazon.de"]

    SEARCH_URL = "http://www.amazon.de/s/?field-keywords={search_term}"

    REVIEW_DATE_URL = "http://www.amazon.de/product-reviews/" \
                      "{product_id}/ref=cm_cr_dp_see_all_btm?ie=UTF8&" \
                      "showViewpoints=1&sortBy=bySubmissionDateDescending"

    settings = AmazonDeValidatorSettings

    use_proxies = False

    handle_httpstatus_list = [502, 503, 504]

    def __init__(self, captcha_retries='20', *args, **kwargs):
        super(AmazonProductsSpider, self).__init__(*args, **kwargs)

        self.captcha_retries = int(captcha_retries)

        self.mtp_class = Amazon_marketplace(self)

        self._cbw = CaptchaBreakerWrapper()

    def _parse_single_product(self, response):
        return self.parse_product(response)

    def parse(self, response):
        if self._has_captcha(response):
            result = self._handle_captcha(response, self.parse)
        else:
            result = super(AmazonProductsSpider, self).parse(response)
        return result

    def _get_products(self, response):
        result = super(AmazonProductsSpider, self)._get_products(response)
        for r in result:
            if isinstance(r, Request):
                r = r.replace(dont_filter=True)
                yield r
            else:
                yield r

    @staticmethod
    def _parse_product_id(url):
        prod_id = re.findall(r'/dp?/(\w+)|product/(\w+)/', url)
        if not prod_id:
            prod_id = re.findall(r'/dp?/(\w+)|product/(\w+)', url)
        if not prod_id:
            prod_id = re.findall(r'([A-Z0-9]{4,20})', url)
        if isinstance(prod_id, (list, tuple)):
            prod_id = [s for s in prod_id if s][0]
        if isinstance(prod_id, (list, tuple)):
            prod_id = [s for s in prod_id if s][0]
        return prod_id

    def parse_product(self, response):
        prod = response.meta['product']

        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self.parse_product
            )

        if not self._has_captcha(response):
            meta = response.meta.copy()
            response.meta['product'] = prod
            prod_id = self._parse_product_id(response.url)
            response.meta['product_id'] = prod_id

            self._populate_from_js(response, prod)

            self._populate_from_html(response, prod)

            cond_set_value(prod, 'locale', 'en-US')  # Default locale.

            # Get url for marketplace
            url = is_empty(
                response.xpath("//div[contains(@class, 'a-box-inner')]/span"
                               "/a/@href |"
                               "//div[contains(@class, 'a-box-inner')]"
                               "//a[contains(@href, '/gp/offer-listing/')]/@href |"
                               "//div[@id='secondaryUsedAndNew']"
                               "//a[contains(@href, '/gp/offer-listing/')]/@href |"
                               "//*[@id='universal-marketplace-glance-features']/.//a/@href"
                               ).extract())
            if url:
                mkt_place_link = urlparse.urljoin(
                    response.url,
                    url
                )
            else:
                asin = is_empty(response.xpath("//form[@id='addToCart']"
                    "/input[@name='ASIN']/@value").extract())
                if not asin:
                    asin = is_empty(re.findall(
                        "\"ASIN\"\:\"([^\"]*)", response.body_as_unicode()))
                if asin:
                    url = "/gp/offer-listing/%s/ref=dp_olp_all_mbc"\
                        "?ie=UTF8&amp;condition=new" % (asin,)
                    mkt_place_link = urlparse.urljoin(response.url, url)
                else:
                    mkt_place_link = None

            meta = response.meta.copy()
            meta['product'] = prod
            prod_id = self._parse_product_id(response.url)
            meta['product_id'] = prod_id
            if mkt_place_link:
                meta["mkt_place_link"] = mkt_place_link

            _avail = response.css('#availability ::text').extract()
            _avail = ''.join(_avail)
            if "nichtauflager" in _avail.lower().replace(' ', ''):
                prod['is_out_of_stock'] = True
            else:
                prod['is_out_of_stock'] = False

            if isinstance(prod['buyer_reviews'], Request):
                result = prod['buyer_reviews'].replace(meta=meta)
            else:
                if prod['buyer_reviews'] != 0:
                    return Request(url=self.REVIEW_DATE_URL.format(product_id=prod_id),
                                   meta=meta,
                                   dont_filter=True,
                                   callback=self.get_last_buyer_review_date)
                result = prod
        elif response.meta.get('captch_solve_try', 0) >= self.captcha_retries:
            self.log("Giving up on trying to solve the captcha challenge after"
                     " %s tries for: %s" % (self.captcha_retries, prod['url']),
                     level=WARNING)
            result = None
        else:
            result = self._handle_captcha(response, self.parse_product)
        return result

    def get_last_buyer_review_date(self, response):

        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self.get_last_buyer_review_date
            )

        product = response.meta['product']
        date = is_empty(response.xpath(
            '//table[@id="productReviews"]/tr/td/div/div/span/nobr/text()'
        ).extract())

        months = {'Januar': 'January',
                  'Februar': 'February',
                  u'M\xe4rz': 'March',
                  'Mai': 'May',
                  'Juni': 'June',
                  'Juli': 'July',
                  'Oktober': 'October',
                  'Dezember': 'December'
                  }

        if date:
            for key in months.keys():
                if key in date:
                    date = date.replace(key, months[key])
            d = datetime.strptime(date.replace('.', ''), '%d %B %Y')
            date = d.strftime('%d/%m/%Y')
            product['last_buyer_review_date'] = date

        new_meta = response.meta.copy()
        new_meta['product'] = product
        if 'mkt_place_link' in response.meta.keys():
                return Request(
                    url=response.meta['mkt_place_link'],
                    callback=self.parse_marketplace,
                    meta=new_meta,
                    dont_filter=True,
                )
        return product

    def _populate_bestseller_rank(self, product, response):
        ranks = {' > '.join(map(unicode.strip,
                                itm.css('.zg_hrsr_ladder a::text').extract())):
                     int(re.sub('[ ,]', '',
                                itm.css('.zg_hrsr_rank::text').re(
                                    '([\d, ]+)')[0]))
                 for itm in response.css('.zg_hrsr_item')}

        prim_a = response.css('#SalesRank::text, #SalesRank .value::text').re(
            '(\d+){0,1}\.{0,1}(\d+) .*en (.+)\(')
        prim = []
        if prim_a:
            if len(prim_a) > 1 and prim_a[0].isdigit() and prim_a[1].isdigit():
                prim.append(prim_a[0] + prim_a[1])
                prim.append(prim_a[2])
            elif len(prim_a) > 1 and prim_a[0].isdigit():
                prim[0].append(prim_a[0])
                prim[1].append(prim_a[1])
        if prim:
            prim = {prim[1].strip(): int(re.sub('[ ,]', '', prim[0]))}
            ranks.update(prim)
        ranks = [{'category': k, 'rank': v} for k, v in ranks.iteritems()]
        cond_set_value(product, 'category', ranks)
        # parse department
        department = amazon_parse_department(ranks)
        if department is None:
            product['department'] = None
        else:
            product['department'], product['bestseller_rank'] \
                = department.items()[0]

    def _populate_from_html(self, response, product):

        related_products = self._parse_related(response)
        cond_set(product, 'related_products', related_products)

        cond_set(product, 'brand', response.css('#brand ::text').extract())
        if not product.get('brand', '').strip():
            brand = response.css('#brand ::text')
            if not brand:
                brand = response.css('#bylineContributor ::text')  # iphone6-mode
            if len(brand) > 1:
                brand = brand.extract()
            else:
                brand = is_empty(brand.extract(), '').strip()
            if not brand:
                # if brand is image
                if response.xpath('//a[@id="brand"]/img'):
                    brand = response.xpath('//a[@id="brand"]/@href').extract()
                    if brand:
                        brand = urlparse.parse_qs(urlparse.urlparse(brand[0]).query)\
                            .get('field-brandtextbin', '')
            if isinstance(brand, (list, tuple)):
                if brand:
                    brand = brand[0]
            if not isinstance(brand, (str, unicode)):
                brand = brand.extract()
            if isinstance(brand, (list, tuple)):
                if brand:
                    brand = brand[0]
            cond_set_value(product, 'brand', brand)
            # check that it's not Author (for Iphone6-mode books)
            if 'iphone' in getattr(self, 'user_agent', '').lower()\
                    or 'ipad' in getattr(self, 'user_agent', '').lower():
                if u'(Autor)' in response.body_as_unicode() \
                        or response.css('#brandByline_feature_div'):
                    product['brand'] = ''

        cond_set(
            product,
            'price',
            response.css(
                '#priceblock_ourprice ::text'
                ', #unqualifiedBuyBox .a-color-price ::text'
                ', #priceblock_saleprice ::text'
                ', #buyNewSection .offer-price ::text'
            ).extract(),
        )
        if not product.get('price', None):
            cond_set(
                product,
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
                    '//span[@id="actualPriceValue"]/text()[normalize-space()]|'
                    '//span[@class="price"]/text()'
                ).extract()
            )
        if not product.get('price', None):
            _price = re.search(
                r'a-color-price aw-nowrap&quot;&gt;EUR ([\d\.\,]+)&lt;/span&gt',
                response.body
            )
            if _price:
                _price = _price.group(1).strip().replace(' ', '')\
                    .replace('.', '').replace(',', '.')
                cond_set(product, 'price', ['EUR ' + _price])

        if not product.get('price', None):
            _price = response.xpath('//*[@id="product-price"]/text()').extract()
            cond_set(product, 'price', [_price])
        if not product.get('price', None):
            _price = response.xpath(
                '//*[contains(@class, "a-color-price")]/text()').extract()
            if _price:
                product['price'] = _price[0].strip()

        if isinstance(product.get('price', None), (list, tuple)):
            if product.get('price', None):
                product['price'] = product['price'][0]

        if product.get('price', None):
            if not u'EUR' in product.get('price', ''):
                self.log('Invalid price at: %s' % response.url, level=WARNING)
            else:
                price = re.findall(FLOATING_POINT_RGEX,
                    product['price'].replace(u'\xa0', '').strip())
                price = re.sub('[, ]', '.', price[0])
                product['price'] = Price(
                    price=price,
                    priceCurrency='EUR'
                )
        else:
            product.pop('price', '')  # remove the key completely

        if 'usverkauft' in response.body_as_unicode().lower().replace(' ', '') \
            or 'ergriffen' in response.body_as_unicode().lower().replace(' ', '') \
            or 'ichtauflager' in response.body_as_unicode().lower().replace(' ', '') \
            or 'ichtamlager' in response.body_as_unicode().lower().replace(' ', ''):
                with open('/tmp/_am_urls', 'a') as fh:
                    fh.write(str(response.url) + '\n')

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
        cond_set(
            product,
            'description',
            description,
        )

        image = response.css(
            '#imgTagWrapperId > img ::attr(data-old-hires)'
        ).extract()
        if not image:
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
                '/img/@src |'
                '//img[@id="imgBlkFront"]/@style'
            ).extract()

        if image and image[0].strip().startswith('http'):
            # sometimes images are coded data
            cond_set(
                product,
                'image_url',
                image
            )

        if not product.get('image_url', ''):
            # try properties first
            cond_set(product, 'image_url', response.xpath(
                '//img[contains(@id, "main-image")]/@data-a-dynamic-image').extract())
            if product.get('image_url', '').strip():
                _url = None
                try:
                    _url = json.loads(product['image_url'])
                except Exception as e:
                    cond_set(product, 'image_url', response.xpath(
                        '//img[contains(@id, "main-image")]/@src').extract())
                if _url:
                    _url = _url.keys()[0]
                    product['image_url'] = _url

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

        if not title:
            title = response.xpath('//span[@id="title"]/text()').extract()
            if not title:
                title = response.xpath('//*[@id="product-title"]/text()').extract()
            if not title:
                title = response.xpath('//h1[@id="title"]/text()').extract()
            title = [title[0].strip()] if title else title

        cond_set(
            product, 'title', title)

        # Some data is in a list (ul element).
        model = None
        for li in response.css('td.bucket > .content > ul > li'):
            raw_keys = li.xpath('b/text()').extract()
            if not raw_keys:
                # This is something else, ignore.
                continue

            key = raw_keys[0].strip(' :').upper()
            if key == 'UPC':
                # Some products have several UPCs.
                raw_upc = li.xpath('text()').extract()[0]
                cond_set_value(
                    product,
                    'upc',
                    raw_upc.strip().replace(' ', ';'),
                )
            elif key == 'ASIN' and model is None or key == 'ITEM MODEL NUMBER':
                model = li.xpath('text()').extract()
        if not product.get('model'):
                model = is_empty(response.xpath(
                    '//div[contains(@class, "content")]/ul/'
                    'li/b[contains(text(), "ASIN")]/../text() |'
                    '//table/tbody/tr/'
                    'td[contains(@class, "label") and contains(text(), "ASIN")]'
                    '/../td[contains(@class, "value")]/text() |'
                    '//div[contains(@class, "content")]/ul/'
                    'li/b[contains(text(), "ISBN-10")]/../text()'
                ).extract())
                if model:
                    cond_set(product, 'model', (model,))

        cond_set(product, 'model', model, conv=string.strip)
        self._populate_bestseller_rank(product, response)
        #revs = self._buyer_reviews_from_html(response)
        #if isinstance(revs, Request):
        #    meta = {"product": product}
        #    product['buyer_reviews'] = revs.replace(meta=meta)
        #else:
        #    product['buyer_reviews'] = revs
        product['buyer_reviews'] = ''

    def _populate_from_js(self, response, product):
        # Images are not always on the same spot...
        img_jsons = response.css(
            '#landingImage ::attr(data-a-dynamic-image)').extract()
        if img_jsons:
            img_data = json.loads(img_jsons[0])
            cond_set_value(
                product,
                'image_url',
                max(img_data.items(), key=lambda (_, size): size[0]),
                conv=lambda (url, _): url)

    def _parse_related(self, response):
        """
        Parses related products
        """
        related_products = []

        # Parse often bought products
        often_bought = response.xpath('//*[@id="fbt-expander-content"]/.//li[position()>1]/./'
                                      '/div[@class="sims-fbt-row-outer"]')

        if often_bought:
            for item in often_bought:
                title = is_empty(item.xpath('.//div[contains(@class,"sims-fbt-title")]/./'
                                            '/div/text()').extract(), '')
                url = is_empty(item.xpath('.//a/@href').extract(), '')

                if url:
                    url = 'http://www.' + self.allowed_domains[0] + url
                    if title:
                        related_products.append(RelatedProduct(
                            title=title.strip(),
                            url=url
                        ))

        return related_products

    def _scrape_results_per_page(self, response):
        num = response.xpath(
            '//*[@id="s-result-count"]/text()').re('1-(\d+) von')
        if num:
            return int(num[0])
        else:
            num = response.xpath(
                '//*[@id="s-result-count"]/text()').re('(\d+) Ergebnissen')
            if num:
                return int(num[0])
        return None

    def _scrape_total_matches(self, response):
        if u'ne correspond à aucun article' in response.body_as_unicode():
            total_matches = 0
        else:
            count_matches = response.xpath(
                '//h2[@id="s-result-count"]/text()').re('sur (.+) r')
            if count_matches and count_matches[-1]:
                total_matches = int(count_matches[-1].replace(
                    u' ', '').replace(u'\xa0', ''))
            else:
                total_matches = None
            if not total_matches:
                count_matches = response.xpath(
                    '//h2[@id="s-result-count"]/text()').re('([\d\.]+) Ergebnisse')
                if count_matches:
                    total_matches = int(
                        count_matches[0].strip().replace('.', ''))
                else:
                    total_matches = None
        if not total_matches:
            total_matches = is_empty(
                response.xpath(
                    '//*[contains(@id, "results")]'
                    '//span[contains(text(), "Ergebnisse")]').extract()
            )
            if total_matches:
                total_matches = re.search(r'[\d\.]+', total_matches)
                if total_matches:
                    total_matches = total_matches.group(0).replace('.', '').strip()
                    if total_matches.isdigit():
                        total_matches = int(total_matches)
                    else:
                        total_matches = None
        return total_matches

    def _scrape_product_links(self, response):
        lis = response.xpath("//ul/li[@class='s-result-item']")
        links = []
        for no, li in enumerate(lis):
            href = li.xpath(
                ".//a[contains(@class,'s-access-detail-page')]"
                "/@href").extract()
            if href:
                href = href[0]
                is_prime = li.xpath(
                    "*/descendant::i[contains(concat(' ',@class,' '),"
                    "' a-icon-premium ')]").extract()
                is_prime_pantry = li.xpath(
                    "*/descendant::i[contains(concat(' ',@class,' '),"
                    "' a-icon-premium-pantry ')]").extract()
                links.append((href, is_prime, is_prime_pantry))
        if not links:
            lis = response.xpath('//*[contains(@id, "results")]'
                                 '//*[contains(@class, "sx-table-item")]')
            if not lis:
                lis = response.xpath('//*[contains(@id, "results")]'
                                     '//*[contains(@class, "s-result-item")]')
            for no, li in enumerate(lis):
                is_prime = li.css('i.a-icon-prime').extract()
                is_prime_pantry = (li.css('i.a-icon-prime-pantry').extract()
                                   or li.css('i.a-icon-primepantry').extract())
                if not is_prime_pantry:
                    is_prime_pantry = bool(li.xpath(
                        "*/descendant::i[contains(concat(' ',@class,' '),"
                        "' a-icon-premium-pantry ')]").extract())
                links.append([
                    is_empty(li.xpath('.//a/@href').extract()),
                    is_prime, is_prime_pantry
                ])
        if not links:
            self.log("Found no product links.", WARNING)
        for link, is_prime, is_prime_pantry in links:
            prime = None
            if is_prime:
                prime = 'Prime'
            if is_prime_pantry:
                prime = 'PrimePantry'
            yield link, SiteProductItem(prime=prime)

    def _scrape_next_results_page_link(self, response):
        next_pages = response.xpath(
            "//a[@id='pagnNextLink']/@href").extract()
        next_page_url = None
        if len(next_pages) == 1:
            next_page_url = next_pages[0]
        elif len(next_pages) > 1:
            self.log("Found more than one 'next page' link.", ERROR)
        if not next_pages:
            next_pages = response.xpath(
                '//ul[contains(@class, "a-pagination")]'
                '//a[contains(text(), "eiter")]/@href').extract()
            if len(next_pages) == 1:
                next_page_url = next_pages[0]
        return next_page_url

    ## Captcha handling functions.

    def _has_captcha(self, response):
        return 'Geben Sie die angezeigten Zeichen im Bild ein:' in\
            response.body_as_unicode()

    def _solve_captcha(self, response):
        forms = response.xpath('//form')
        assert len(forms) == 1, "More than one form found."

        captcha_img = forms[0].xpath(
            '//img/@src').extract()[0]
            #[contains(@src, "opfcaptcha-prod")]

        self.log("Extracted capcha url: %s" % captcha_img, level=DEBUG)
        return self._cbw.solve_captcha(captcha_img)

    def _handle_captcha(self, response, callback):
        # FIXME This is untested and wrong.
        captcha_solve_try = response.meta.get('captcha_solve_try', 0)
        url = response.url
        self.log("Captcha challenge for %s (try %d)."
                 % (url, captcha_solve_try),
                 level=INFO)

        captcha = self._solve_captcha(response)

        _captcha_try = 0
        while captcha is None:
            _captcha_try += 1
            captcha = self._solve_captcha(response)
            if _captcha_try > 20:
                break

        if captcha is None:
            self.log(
                "Failed to guess captcha for '%s' (try: %d)." % (
                    url, captcha_solve_try),
                level=WARNING
            )
            result = None
        else:
            self.log(
                "On try %d, submitting captcha '%s' for '%s'." % (
                    captcha_solve_try, captcha, url),
                level=INFO
            )
            meta = response.meta.copy()
            meta['captcha_solve_try'] = captcha_solve_try + 1
            result = FormRequest.from_response(
                response,
                formname='',
                formdata={'field-keywords': captcha},
                callback=callback,
                dont_filter=True,
                meta=meta)

        return result

    def _buyer_reviews_from_html(self, response):
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

        # For another HTML makeup
        if not total:
            ratings = {}
            average = 0
            total = is_empty(
                response.xpath(
                    "//span[contains(@class, 'tiny')]"
                    "/span[@class='crAvgStars']/a/text()"
                ).re("[\d\.\,]+"),
                0
            )
            if total:
                if isinstance(total, (str, unicode)):
                    total = int(total.replace(',', '').replace('.', '').strip())
            for rev in response.xpath(
                    '//span[contains(@class, "tiny")]'
                    '//div[contains(@class, "custRevHistogramPopId")]/table/tr'):
                star = is_empty(rev.xpath('td/a/text()').re("\d+"), None)
                if star:
                    ratings[star] = is_empty(
                        rev.xpath('td[last()]/text()').re("[\d\.\,]+"), 0)
                    if ratings[star]:
                        if isinstance(ratings[star], (str, unicode)):
                            ratings[star] = int(
                                ratings[star].replace(',', '').replace('.', '').strip()
                            )
            if ratings:
                average = sum(int(k) * int(v) for k, v in
                              ratings.iteritems()) / int(total) if ratings else 0
                average = float("%.2f" % round(average, 2))

        if not ratings:
            buyer_rev_link = response.xpath(
                '//div[@id="summaryContainer"]//table[@id="histogramTable"]'
                '/../a/@href'
            ).extract()
            if buyer_rev_link:
                buyer_rev_req = Request(
                    url=buyer_rev_link[0],
                    callback=self.get_buyer_reviews_from_2nd_page,
                    meta=response.meta.copy()
                )
                return buyer_rev_req
            else:
                return ZERO_REVIEWS_VALUE

        # add missing marks
        for mark in range(1, 6):
            if mark not in ratings:
                if str(mark) not in ratings:
                    if unicode(mark) not in ratings:
                        ratings[unicode(mark)] = 0

        buyer_reviews = BuyerReviews(num_of_reviews=total,
                                     average_rating=average,
                                     rating_by_star=ratings)
        return buyer_reviews

    def get_buyer_reviews_from_2nd_page(self, response):

        if self._has_captcha(response):
            return self._handle_captcha(
                response,
                self.get_buyer_reviews_from_2nd_page
            )

        product = response.meta["product"]
        prod_id = response.meta["product_id"]
        buyer_reviews = {}
        product["buyer_reviews"] = {}
        total_revs = is_empty(response.xpath(
            '//table[@id="productSummary"]'
            '//span[@class="crAvgStars"]/a/text()').extract(), ''
        ).replace(",", "")
        buyer_reviews["num_of_reviews"] = is_empty(
                re.findall(FLOATING_POINT_RGEX, total_revs), 0
            )
        if int(buyer_reviews["num_of_reviews"]) == 0:
            product["buyer_reviews"] = ZERO_REVIEWS_VALUE
            return product

        buyer_reviews["rating_by_star"] = {}
        buyer_reviews = self.get_rating_by_star(response, buyer_reviews)

        product["buyer_reviews"] = BuyerReviews(**buyer_reviews)

        meta = response.meta.copy()
        meta['product'] = product
        if product['buyer_reviews'] != 0:
            return Request(url=self.REVIEW_DATE_URL.format(product_id=prod_id),
                           meta=meta,
                           dont_filter=True,
                           callback=self.get_last_buyer_review_date)

        return product

    def get_rating_by_star(self, response, buyer_reviews):
        table = response.xpath(
                '//table[@id="productSummary"]//'
                'table[@cellspacing="1"]//tr'
            )
        total = 0
        if table:
            for tr in table[:5]:
                rating = is_empty(tr.xpath(
                    'string(.//td[1])').re(FLOATING_POINT_RGEX), '')
                number = is_empty(tr.xpath(
                    'string(.//td[last()])').re(FLOATING_POINT_RGEX), 0)
                is_perc = is_empty(tr.xpath(
                    'string(.//td[last()])').extract(), '')
                if "%" in is_perc:
                    break
                if number:
                    number = int(number.replace(',', ''))
                    buyer_reviews['rating_by_star'][rating] = number
                    total += number*int(rating)
        if total > 0:
            average = float(total)/ float(buyer_reviews['num_of_reviews'])
            buyer_reviews['average_rating'] = round(average, 1)
        return buyer_reviews

    def parse_marketplace(self, response):
        response.meta["called_class"] = self
        response.meta["next_req"] = None
        return self.mtp_class.parse_marketplace(
            response, replace_comma_with_dot=True)

    def _validate_url(self, val):
        if not bool(val.strip()):  # empty
            return False
        if len(val.strip()) > 1500:  # too long
            if not 'redirect' in val:
                return False
            elif len(val.strip()) > 3000:
                return False
        if val.strip().count(u' ') > 5:  # too many spaces
            return False
        if not val.strip().lower().startswith('http'):
            return False
        return True

    def _validate_title(self, val):
        if not bool(val.strip()):  # empty
            return False
        if len(val.strip()) > 1500:  # too long
            return False
        if val.strip().count(u' ') > 300:  # too many spaces
            return False
        if '<' in val or '>' in val:  # no tags
            return False
        return True

    def exit_point(self, product, next_req):
        if next_req:
            next_req.replace(meta={"product": product})
            return next_req
        return product