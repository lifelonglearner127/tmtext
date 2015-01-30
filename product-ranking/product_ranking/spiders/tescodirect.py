from __future__ import division, absolute_import, unicode_literals
from future_builtins import *

import re
import sys
import json
import urllib
import urllib2
import urlparse

# from collections import Iterable

from scrapy.selector import Selector
from scrapy.item import Item
from scrapy.log import ERROR
from scrapy import Request

from product_ranking.guess_brand import guess_brand_from_first_words
from product_ranking.items import SiteProductItem, \
    Price, RelatedProduct, BuyerReviews
from product_ranking.spiders import BaseProductsSpider, \
    cond_set_value, cond_set, FLOATING_POINT_RGEX

is_empty = lambda x: x[0] if x else None


class TescoDirectProductsSpider(BaseProductsSpider):
    """This site have MARKETPLACE, but it does not implemented
    """

    name = 'tescodirect_products'
    allowed_domains = ["www.tesco.com"]

    pages_count = 0
    product_iteration = 1

    tot_matches = 0

    stack = []
    stack_total = []

    link_begin = "http://www.tesco.com"

    # TODO: change the currency if you're going to support different countries
    #  (only UK and GBP are supported now)
    SEARCH_URL = "http://www.tesco.com/direct/search-results/" \
       "results.page?_DARGS=/blocks/common/flyoutSearch.jsp"
    def __init__(self, *args, **kwargs):
        self.search = kwargs["searchterms_str"]
        super(TescoDirectProductsSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        """Generate Requests from the SEARCH_URL and the search terms."""
        #IMPORTANT!!!!!!
        #Here we takes data - from POST request(search form)
        data = "%2Fcom%2Ftesco" \
            "%2Fbns%2FformHandlers%2FBasicSearchFormHandler" \
            ".snpSrchResURL=%2Fdirect%2Fsearch-results%2Fresults" \
            ".page&_D%3A%2Fcom%2Ftesco%2Fbns%2FformHandlers%2F" \
            "BasicSearchFormHandler.snpSrchResURL=+&%2Fcom%2F" \
            "tesco%2Fbns%2FformHandlers%2FBasicSearchFormHandler" \
            ".snpZeroResURL=%2Fdirect%2Fsearch-results%2Fzero-" \
            "results.page&_D%3A%2Fcom%2Ftesco%2Fbns%2FformHandlers" \
            "%2FBasicSearchFormHandler.snpZeroResURL=+&%2Fcom" \
            "%2Ftesco%2Fbns%2FformHandlers%2FBasicSearchFormHandler" \
            ".currentUrl=catId%3D4294960317&_D%3A%2Fcom%2Ftesco%2F" \
            "bns%2FformHandlers%2FBasicSearchFormHandler." \
            "currentUrl=+&%2Fcom%2Ftesco%2Fbns%2FformHandlers" \
            "%2FBasicSearchFormHandler.snpBuyingGuideURL=%2F" \
            "direct%2Fsearch-help%2Fsearch-results-help.page" \
            "&_D%3A%2Fcom%2Ftesco%2Fbns%2FformHandlers%2F" \
            "BasicSearchFormHandler.snpBuyingGuideURL=+&%2Fcom" \
            "%2Ftesco%2Fbns%2FformHandlers%2FBasicSearchFormHandler" \
            ".Search=Search&_D%3A%2Fcom%2Ftesco%2Fbns%2FformHandlers" \
            "%2FBasicSearchFormHandler.Search=+&%2Fcom%2Ftesco%2Fbns" \
            "%2FformHandlers%2FBasicSearchFormHandler.strSrchIntrface" \
            "=Entire+Site%7C%7C4294967294&_D%3A%2Fcom%2Ftesco%2Fbns" \
            "%2FformHandlers%2FBasicSearchFormHandler.strSrchIntrface" \
            "=+&_D%3Asearch=+&_DARGS=%2Fblocks%2Fcommon" \
            "%2FflyoutSearch.jsp&search=" + str(self.search)
        for st in self.searchterms:
            yield Request(
                self.url_formatter.format(
                    self.SEARCH_URL,
                    search_term=urllib.quote_plus(st.encode('utf-8')),
                ),
                method="POST",
                meta={'search_term': st, 'remaining': self.quantity},
                body=data,
                headers={'Content-type':'application/x-www-form-urlencoded'},
                callback=self.handler,
            )

    def handler(self, response):
        self.first_response = response
        for i in self.get_pages_for_total_matches(response):
            yield i
    
    def parse(self, response):
        self.category_finished = False
        if self._search_page_error(response):
            remaining = response.meta['remaining']
            search_term = response.meta['search_term']

            self.log("For search term '%s' with %d items remaining,"
                     " failed to retrieve search page: %s"
                     % (search_term, remaining, response.request.url),
                     ERROR)
        else:
            prods_count = -1  # Also used after the loop.
            for prods_count, request_or_prod in enumerate(
                    self._get_products(response)):
                yield request_or_prod
            prods_count += 1  # Fix counter.
            request = self._get_next_products_page(response, prods_count)
            if request is not None:
                yield request
            else:
                remaining = response.meta.get('remaining', sys.maxint)
                yield self.next_stack_request(remaining)

    def getResponse(self, response):
        if self.push_to_stack_category(response, self.stack):
            remaining = response.meta.get("remaining", sys.maxint)
            yield self.next_stack_request(remaining)
        else:
            for item in self.parse(response):
                yield item

    #Crawl next category
    def next_stack_request(self, remaining=sys.maxint):
        if self.stack:
            next_url = self.stack.pop(0)
            return Request(
                    self.link_begin + next_url,
                    meta = {
                        'search_term': self.search,
                        'remaining': remaining
                    },
                    callback=self.getResponse,
            )

    #Push categories to stack
    def push_to_stack_category(self, response, stack):
        categories = self.get_visual_nav(response)
        stack[:0] = categories
        return categories

    #Get categories from response
    def get_visual_nav(self, response):
        visual_nav = response.xpath(
            '//div[@id="visual-nav"]/ul/li/a/@href'
        ).extract()
        brandwall = response.xpath(
            '//div[@class="brandwall"]/a/@href').extract()
        if visual_nav:
            return visual_nav
        elif brandwall:
            for i in range(0, len(brandwall)):
                rep = re.findall("/direct/.*", brandwall[i])
                if rep:
                    brandwall[i] = rep[0]
            return brandwall
        return []

    def parse_product(self, response):
        product = response.meta["product"]
        product["total_matches"] = self.tot_matches

        title = response.xpath(
            '//h1[@class="page-title"]/text()').extract()
        cond_set(product, 'title', title)

        if title:
            brand = guess_brand_from_first_words(title[0])
            cond_set(product, 'brand', (brand,))

        price = response.xpath(
            '//p[@class="current-price"]/text()').re(FLOATING_POINT_RGEX)
        if price:
            product["price"] = Price(price=price[0], priceCurrency="GBP")

        desc = response.xpath(
            '//section[@class="detailWrapper"]').extract()
        cond_set(product, 'description', desc)

        image_url = response.xpath(
            '//div[@class="static-product-image scene7-enabled"]' \
            '/img[@itemprop="image"]/@src'
        ).extract()          
        cond_set(product, 'image_url', image_url)

        file1 = open("file.html", "w")
        file1.write(response.body)
        file1.close()

        resc_url = "http://recs.richrelevance.com/rrserver/p13n_generated.js?"
        apiKey = re.findall("setApiKey\(\'(\w+)", response.body)
        if apiKey:
            apiKey = "a=" + apiKey[0]
        pt = re.findall("addPlacementType\(\'(.*)\'", response.body)
        if pt:
            if len(pt) > 1:
                pt = "&pt=|" + pt[0] + "|" + pt[1]
            else:
                pt = "&pt=|" + pt[0]
        l = "&l=1"
        chi = re.findall("addCategoryHintId\(\'(.*)\'", response.body)
        if chi:
            chi = "&chi=|" + chi[0] 
        resc_url = resc_url + apiKey + pt + l + chi
        ajax = urllib2.urlopen(resc_url)
        resp = ajax.read()
        ajax.close()

        print resc_url
        
        rp = []
        sel_all = re.findall('html:(\s+){0,1}\'([^\}]*)', resp)
        if sel_all:
            for item in sel_all:
                for el in item:
                    if not el:
                        continue
                    get = Selector(text=el).xpath(
                        '//div[@class="title-author-format"]/h3/a')
                    title = get.xpath('text()').extract()
                    url = get.xpath('@href').extract()
                    title = [title.strip() for title in title]
                    for i in range(0, len(title)):
                        rp.append(
                            RelatedProduct(
                                title=title[i],
                                url=url[i]
                            )
                        )
                    product["related_products"] = {"recommended": rp}

        #buyer_reviews
        # upc = response.xpath('//meta[@property="og:upc"]/@content').extract()
        # if upc:
        #     rating_url = "http://api.bazaarvoice.com/data/batch.json?" \
        #         "passkey=asiwwvlu4jk00qyffn49sr7tb" \
        #         "&apiversion=5.5" \
        #         "&displaycode=1235-en_gb" \
        #         "&resource.q0=products" \
        #         "&stats.q0=reviews" \
        #         "&resource.q1=reviews" \
        #         "&stats.q1=reviews" \
        #         "&filteredstats.q1=reviews" \
        #         "&include.q1=authors%2Cproducts%2Ccomments" \
        #         "&limit_comments.q1=3"
        #     rating_url += "&filter.q0=id%3Aeq%3A" + str(upc[0])
        #     rating_url += "&filter.q1=productid%3Aeq%3A" + str(upc[0])

        #     ajax = urllib2.urlopen(rating_url)
        #     resp = ajax.read()
        #     ajax.close()

        #     data = json.loads(resp)
        #     try:
        #         num_of_reviews = data["BatchedResults"] \
        #             ["q0"]["Results"] \
        #             [0]["ReviewStatistics"] \
        #             ["TotalReviewCount"]
        #     except Exception:
        #         num_of_reviews = None
            
        #     try:
        #         #average_rating = data["BatchedResults"] \
        #         #    ["q0"]["Results"]["Rating"]
        #             # [0]["ReviewStatistics"] \
        #             # ["SecondaryRatingsAverages"] \
        #             # ["Value"]["AverageRating"]
        #         print "-"*50
        #         print rating_url
        #         print "SOME"
        #         print data["BatchedResults"]["q0"]["Includes"]["Products"][upc[0]]["ReviewStatistics"]["AverageOverallRating"]
        #         print "SOME"
        #         print "-"*50
        #     except Exception:
        #         average_rating = None
          
            # rating_by_star = None
           
            # product["buyer_reviews"] = BuyerReviews(
            #     average_rating=average_rating,
            #     num_of_reviews=num_of_reviews,
            #     rating_by_star=rating_by_star,
            # )

        product["locale"] = "en_GB"

        return product

    #Sum total_matches from all Categories
    def next_total_stack_request(self):
        if self.stack_total:
            next_url = self.stack_total.pop(0)
            yield Request(
                    self.link_begin + next_url,
                    meta = {
                        'search_term': self.search,
                        'remaining': sys.maxint
                    },
                    callback=self.get_pages_for_total_matches,
                    dont_filter=True,
            )
        else:
            for req in self.getResponse(self.first_response):
                yield req

    #Crawl pages to sum total_matches
    def get_pages_for_total_matches(self, response):
        if self.push_to_stack_category(response, self.stack_total):
            next_req =  self.next_total_stack_request()
        else:
            next_req = self.sum_total_matches(response)
        
        return next_req
    
    def sum_total_matches(self, response):
        if "0 results found" in response.body_as_unicode():
            total_matches = 0
        else:
            total_matches = response.xpath(
                '//div[@class="filter-productCount"]/b/text()'
            ).extract()

        if total_matches:
            self.tot_matches += int(total_matches[0])
        next_req =  self.next_total_stack_request()
        return next_req


    def _scrape_total_matches(self, response):
        if "0 results found" in response.body_as_unicode():
            total_matches = 0
        else:
            total_matches = response.xpath(
                '//div[@class="filter-productCount"]/b/text()'
            ).extract()

        if not total_matches:
            return 0
        self.pages_count = int(round(
            (int(total_matches[0]) / 20) + 0.5
        ))
        total_matches = is_empty(total_matches)

        return int(total_matches)
        
    def _scrape_product_links(self, response):
        links = response.xpath('//ul[@class="products"]/' \
            'li[contains(@class, "product-tile")]' \
            '/div[contains(@class, "product")]/a[1]/@href'
        ).extract()
        for link in links:
            if link != '#':
                link = self.link_begin + link
                yield link, SiteProductItem()

    def _scrape_next_results_page_link(self, response):
        if self.pages_count >= self.product_iteration:#search and
            offset = "&offset=" + str(self.product_iteration * 20)
            if re.search("&offset=\d+", response.url):
                url = re.sub("&offset=\d+", offset, response.url)
            else:
                url = response.url + offset
            link = url
            self.product_iteration += 1
            return link
        self.product_iteration = 1
        return None
