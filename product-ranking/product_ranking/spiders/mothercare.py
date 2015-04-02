import json
import re
from urllib import unquote, urlencode
from urlparse import urljoin

from scrapy import Request

from product_ranking.items import Price, RelatedProduct, BuyerReviews
from product_ranking.spiders import cond_set, cond_set_value, \
    cond_replace_value
from product_ranking.spiders.contrib.product_spider import ProductsSpider


class MothercareProductsSpider(ProductsSpider):
    """ mothercare.com product ranking spider.

    `upc` field is missing

    Takes `order` argument with following possible values:

    * `rating` (default)
    * `best`
    * `new`
    * `price_asc`, `price_desc`
    """

    name = 'mothercare_products'

    allowed_domains = [
        'mothercare.com',
        'richrelevance.com',
        'reevoo.com',
        'mark.reevoo.com'
    ]

    SEARCH_URL = "http://www.mothercare.com/on/demandware.store" \
                 "/Sites-MCENGB-Site/default" \
                 "/Search-Show?q={search_term}" \
                 "&srule={sort_mode}&start=0&sz=12" \
                 "&view=grid&format=ajax"

    SORT_MODES = {
        'default': 'Most Popular',
        'best': 'Bestseller',
        'new': 'New Arrivals',
        'price_asc': 'Price [Low - High]',
        'price_desc': 'Price [High - Low]',
        'rating': 'Most Popular'
    }

    RR_URL = "http://recs.richrelevance.com/rrserver" \
             "/p13n_generated.js?a={api_key}" \
             "&p={product_id}&pt=|item_page.recs_1|item_page.recs_2" \
             "|item_page.recs_11|item_page.recs_3&u={user_id}&s={sess_id}" \
             "&sgs=|DesktopCustomer%3ADesktopCustomer|NoPreviousOrders2%3A" \
             "NoPreviousOrders2|SalePreviewExclusions%3ASalePreviewExclusions" \
             "|Unregistered_2%3AUnregistered_2&chi=|{bcrumb_id}" \
             "&cs=|{bcrumb_id}:{bcrumb_t}&flv=11.2.202&l=1&pref={pref}"

    OPTIONAL_REQUESTS = {
        'related_products': True,
        'buyer_reviews': True
    }

    REQ_STRATEGY = re.compile("rr_recs.placements\[(\d+)\].json = ({[^}]+})",
                              re.MULTILINE)

    REQ_ITEM = re.compile(
        "rr_recs.placements\[(\d+)\].json.items.push\(({[^}]+})\)",
        re.MULTILINE)

    ALLOW_RR = '[rR]ecommendations|[pP]eople'

    REVOO_URL = "http://mark.reevoo.com/reevoomark/en-GB/product?sku={sku}" \
                "&trkref=MOT"

    def _total_matches_from_html(self, response):
        total = response.css('.resultshits::text').re('of ([\d ,]+)')
        return int(re.sub(',', '', total[0])) if total else 0

    def _scrape_next_results_page_link(self, response):
        link = response.css('.pagenext::attr(href)').extract()
        return link[0] + '&format=ajax' if link else None

    def _scrape_results_per_page(self, response):
        return response.css('#itemsperpagetop '
                            'option[selected=selected]::text').extract()[0]

    def _fetch_product_boxes(self, response):
        return response.css('.producttile')

    def _link_from_box(self, box):
        return box.css('a::attr(href)')[0].extract()

    def _populate_from_box(self, response, box, product):
        cond_set(product, 'title', box.css('.productname::text').extract(),
                 unicode.strip)
        cond_set_value(product, 'is_out_of_stock', not box.css('.inStock'))
        cond_set(product, 'price', box.css('.salesprice::text').extract())

    def _populate_from_html(self, response, product):
        cond_set(product, 'image_url',
                 response.css('.largeimage::attr(src)').extract())
        cond_set(product, 'title',
                 response.css('.productname::text').extract())
        cond_set(product, 'brand',
                 response.css('.productbrand [itemprop=name]::text').extract())
        delivery_opts = response.css('.deliverycallout li')
        delivery_opts = [bool(do.css('.available')) for do in delivery_opts]
        opt_len = len(filter(None, delivery_opts))
        if opt_len:
            cond_set_value(product, 'is_in_store_only',
                           delivery_opts[1] and opt_len == 1)
        else:
            cond_set_value(product, 'is_out_of_stock', False)
        cond_set(product, 'price',
                 response.css('[itemprop=price]::text').extract(),
                 unicode.strip)
        cond_set(product, 'model',
                 response.css('[itemprop=model]::text').extract())

        price = product.get('price')
        price = re.findall(u'\xa3 *\d[\d, .]*', price)
        if price:
            price = re.sub(u'[\xa3, ]+', '', price[0])
            cond_replace_value(product, 'price', Price(priceCurrency='GBP',
                                                       price=price))

        xpath = '//div[@id="pdpTab1"]/node()[normalize-space()]'
        cond_set_value(product, 'description', response.xpath(xpath).extract(),
                       ''.join)
        product['url'] = product['url'].rsplit('#', 1)[0]

    def _request_related_products(self, response):
        url = "http://recs.richrelevance.com/rrserver/p13n_generated.js?"
        api_key = re.search("setApiKey\('([^']+)'\);", response.body).group(1)
        user_id = re.search("setUserId\('([^']+)'\);", response.body).group(1)
        sess_id = re.search(
            "setSessionId\('([^']+)'\);", response.body).group(1)
        product_id = re.search(
            "R3_ITEM\.setId\('([^']+)'\);", response.body).group(1)
        cs = re.search("addCategory\('([^']+)', '([^']+)'", response.body)
        cs = '%s:%s' % (cs.group(1), cs.group(2))
        chi = re.search("addCategoryHintId\('([^']+)'\);",
                        response.body).group(1)
        pref = 'http://www.mothercare.com/on/demandware.store' \
               '/Sites-MCENGB-Site/default/Search-Show?q={search_term}' \
            .format(search_term=response.meta['search_term'])
        data = {
            'a': api_key,
            'chi': '|%s' % chi,
            'cs': '|%s' % cs,
            'flv': '11.2.202',
            'l': 1,
            'p': product_id,
            'pref': pref,
            'pt': '	|item_page.recs_1|item_page.recs_2|item_page.recs_11'
                  '|item_page.recs_3',
            's': sess_id,
            'sgs': '|DesktopCustomer:DesktopCustomer|NoPreviousOrders2'
                   ':NoPreviousOrders2|SalePreviewExclusions'
                   ':SalePreviewExclusions|Unregistered_2:Unregistered_2',
            'u': user_id
        }
        url = url + urlencode(data)
        response.meta['alsoviewed'] = response.css('.rr-recs-items-page')
        return url

    def _parse_related_products(self, response):
        product = response.meta['product']
        rp = {}
        for id_, stategy in self.REQ_STRATEGY.findall(
                response.body_as_unicode()):
            message = json.loads(stategy)['strategy_message']
            if re.match('[Rr]ecently [Vv]iewed', message):
                continue
            if response.meta['alsoviewed']:
                if re.match('[Rr]ecommended *[Ff]or', message):
                    continue
            elif re.match('[Pp]eople *[Aa]lso', message):
                continue
            rp[message] = []
            for iid, data in self.REQ_ITEM.findall(response.body):
                if not iid == id_:
                    continue
                # fix json syntax
                data = re.sub(', *}', '}', data)
                data = json.loads(data)
                title = data['ProductName']
                url = data['ProductUrl']
                url = unquote(re.search('&ct=([^&]+)', url).group(1))
                rp[message].append(RelatedProduct(title=title, url=url))
        cond_set_value(product, 'related_products', rp)


    def _request_buyer_reviews(self, response):
        anonim_reviews = response.xpath('//div[@class="reevooReview"]')
        if anonim_reviews:
            total = len(anonim_reviews)
            stars = {}
            for review in anonim_reviews:
                regex = 'Score is (\d+)'
                count = review.xpath('//div[@class="unverified_stars"]/@title').re(regex)[0]
                if count in stars.keys():
                    stars[count] += 1
                else:
                    stars[count] = 1
            sum = 0
            for k, v in stars.iteritems():
                sum += int(k)*v
            avg = float(sum)/float(total)
            res = BuyerReviews(num_of_reviews=total, average_rating=avg,
                               rating_by_star=stars)
            response.meta['product']['buyer_reviews'] = res
        else:
            sku = response.css('p.productid::attr(class)').re('p_(\d+)')
            sku = sku[0] if sku else re.search('.+/([^,]+)', response.url).group(1)
            url = self.REVOO_URL.format(sku=sku)
            return url

    def _scrape_review_summary(self, response):
        regex = 'Score is ([\d.]+) out of \d+ from (\d+)'
        avg, total = response.css('.average_score::attr(title)').re(regex)
        return avg, total

    def _parse_buyer_reviews(self, response):
        scores = response.meta.get('scores', [])
        css = '.overall_score_stars::attr(title)'
        scores.extend(map(int, response.css(css).extract()))
        response.meta['scores'] = scores
        next_url = response.css('.next_page::attr(href)')
        if next_url:
            next_url = urljoin(response.url, next_url[0].extract())
            return Request(next_url, self._parse_buyer_reviews,
                           meta=response.meta)
        try:
            avg, total = self._scrape_review_summary(response)
        except ValueError:
            return
        if not total:
            return
        avg = float(avg)
        total = int(total)
        by_star = {score: scores.count(score) for score in scores}
        total_calculated = len(scores)
        avg_calculated = round(float(sum(scores)) / total, 1)
        assert total_calculated == total
        assert avg_calculated == avg
        res = BuyerReviews(num_of_reviews=total, average_rating=avg,
                           rating_by_star=by_star)
        response.meta['product']['buyer_reviews'] = res