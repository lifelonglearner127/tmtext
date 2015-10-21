# -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy.http import TextResponse
from scrapy.http import Response
from scrapy.exceptions import CloseSpider
from search.items import SearchItem
from search.spiders.search_spider import SearchSpider
from scrapy import log

from spiders_utils import Utils
from search.matching_utils import ProcessText

import re
import sys
import os

import captcha_solver
import urllib2


class AmazonSpider(SearchSpider):

    name = "amazon"
    handle_httpstatus_list = [404]

    # initialize fields specific to this derived spider
    def init_sub(self):
        self.target_site = "amazon"
        self.start_urls = [ "http://www.amazon.com" ]
        self.domain = "http://www.amazon.com"

        # captcha solver - will be used when encountering blocked page from amazon
        self.CB = captcha_solver.CaptchaBreakerWrapper()

        # maximum number of captcha retries
        self.MAX_CAPTCHA_RETRIES = 3

    # check if a certain URL is valid or gets a 404 response
    def is_valid_url(self, URL):
        # this causes 404s
        if URL == "http://www.amazon.com/gp/slredirect/redirect.html":
            return False
        if URL.startswith("http://www.amazon.co.uk/gp/slredirect/redirect.html"):
            return False
        return True

    # parse results page for amazon, extract info for all products returned by search (keep them in "meta")
    def parseResults(self, response):
        hxs = HtmlXPathSelector(response)

        # print "PARSE AMAZON FOR", response.meta['origin_url'], "RESULTS PAGE", response.url

        if 'items' in response.meta:
            items = response.meta['items']
        else:
            items = set()

        # add product URLs to be parsed to this list
        if 'search_results' not in response.meta:
            product_urls = set()
        else:
            product_urls = response.meta['search_results']

        origin_product_id = response.meta['origin_product_id']
        current_query = response.meta['query']

        # all product urls from all queries
        items2 = sum(map(lambda q: self.results[origin_product_id]['search_requests'][q]['product_items'], \
            self.results[origin_product_id]['search_requests']), [])
        # all product urls from all queries
        product_urls2 = sum(map(lambda q: self.results[origin_product_id]['search_requests'][q]['search_results'], \
            self.results[origin_product_id]['search_requests']), [])
        product_urls2 = set(product_urls2)

        ############
        # TEST
        assert len(items) == len(items2)
        assert len(product_urls) == len(product_urls2)


        # get search results for received results page and add them to product_urls to be parsed
        # Note: xpath below ignores Sponsored links (which is good)
        results = hxs.select("//div[@class='a-row a-spacing-small']/a")
        for result in results:
            product_url = result.select("@href").extract()[0]
                
            # remove the part after "/ref" containing details about the search query
            m = re.match("(.*)/ref=(.*)", product_url)
            if m:
                product_url = m.group(1)

            product_url = Utils.add_domain(product_url, self.domain)

            product_urls.add(product_url)
            product_urls2.add(product_url)
            self.results[origin_product_id]['search_requests'][current_query]['search_results'].append(product_url)


        # extract product info from product pages (send request to parse first URL in list)
        # add as meta all that was received as meta, will pass it on to reduceResults function in the end
        # also send as meta the entire results list (the product pages URLs), will receive callback when they have all been parsed

        # send the request further to parse product pages only if we gathered all the product URLs from all the queries 
        # (there are no more pending requests)
        # otherwise send them back to parseResults and wait for the next query, save all product URLs in search_results
        # this way we avoid duplicates
        if product_urls and ('pending_requests' not in response.meta or not response.meta['pending_requests']):
            next_product_url = product_urls.pop() 
            next_product_url2 = product_urls2.pop() 
            request = Request(next_product_url, callback = self.parse_product_amazon, meta = response.meta)
            request.meta['items'] = items

            # this will be the new product_urls list with the first item popped
            request.meta['search_results'] = product_urls
            self.remove_result_from_queue(origin_product_id, next_product_url2)

            return request

        # if there were no results, the request will never get back to reduceResults
        # so send it from here so it can parse the next queries
        # add to the response the URLs of the products to crawl we have so far, items (handles case when it was not created yet)
        # and field 'parsed' to indicate that the call was received from this method (was not the initial one)
        else:
            response.meta['items'] = items
            response.meta['parsed'] = True
            response.meta['search_results'] = product_urls
            # only send the response we have as an argument, no need to make a new request

            # print "RETURNING TO REDUCE RESULTS", response.meta['origin_url']
            return self.reduceResults(response)

    # extract product info from a product page for amazon
    # keep product pages left to parse in 'search_results' meta key, send back to parseResults_new when done with all
    def parse_product_amazon(self, response):

        # print "PARSE AMAZON PRODUCT FOR", response.meta['origin_url'], response.url


        hxs = HtmlXPathSelector(response)

        items = response.meta['items']

        #site = response.meta['origin_site']
        origin_url = response.meta['origin_url']

        origin_product_id = response.meta['origin_product_id']
        current_query = response.meta['query']

        item = SearchItem()
        item['product_url'] = response.url
        for field in self.results[origin_product_id]['origin_product'].keys():
            item[field] = self.results[origin_product_id]['origin_product'][field]
        
        product_urls = response.meta['search_results']


        # all product urls from all queries
        items2 = sum(map(lambda q: self.results[origin_product_id]['search_requests'][q]['product_items'], \
            self.results[origin_product_id]['search_requests']), [])
        # all product urls from all queries
        product_urls2 = sum(map(lambda q: self.results[origin_product_id]['search_requests'][q]['search_results'], \
            self.results[origin_product_id]['search_requests']), [])
        product_urls2 = set(product_urls2)

        ############
        # TEST
        assert len(items) == len(items2)
        assert len(product_urls) == len(product_urls2)


        # item['origin_url'] = origin_url
        # item['origin_name'] = response.meta['origin_name']

        # if 'origin_model' in response.meta:
        #     item['origin_model'] = response.meta['origin_model']

        # if 'origin_upc' in response.meta:
        #     item['origin_upc'] = response.meta['origin_upc']

        # if 'origin_brand' in response.meta:
        #     item['origin_brand'] = response.meta['origin_brand']

        # if 'origin_bestsellers_rank' in response.meta:
        #     item['origin_bestsellers_rank'] = response.meta['origin_bestsellers_rank']

        # extract product name
        #TODO: id='title' doesn't work for all, should I use a 'contains' or something?
        # extract titles that are not empty (ignoring whitespace)
        # eliminate "Amazon Prime Free Trial"

        #TODO: to test this
        #product_name = filter(lambda x: not x.startswith("Amazon Prime"), hxs.select("//div[@id='title_feature_div']//h1//text()[normalize-space()!='']").extract())
        product_name_node = hxs.select('//h1[@id="title"]/span[@id="productTitle"]/text()').extract()
        product_name = None
        if not product_name_node:
            product_name_node = hxs.select('//h1[@id="aiv-content-title"]//text()').extract()
        if not product_name_node:
            product_name_node = hxs.select('//div[@id="title_feature_div"]/h1//text()').extract()

        if product_name_node:
            product_name = product_name_node[0].strip()
        else:
            # needs special treatment
            product_name_node = hxs.select('//h1[@class="parseasinTitle " or @class="parseasinTitle"]/span[@id="btAsinTitle"]//text()').extract()
            if product_name_node:
                product_name = " ".join(product_name_node).strip()

        if not product_name:

            # log this error:
            # if number of retries were not exhausted, it might just be a captcha page, not an insurmonutable error
            if 'captcha_retries' in response.meta and response.meta['captcha_retries'] <= self.MAX_CAPTCHA_RETRIES:
                
                self.log("Error: No product name: " + str(response.url) + " for walmart product " + origin_url, level=log.WARNING)
            else:
                # if it comes from a solved captcha page, then it's an error if it's still not found                
                self.log("Error: No product name: " + str(response.url) + " for walmart product " + origin_url, level=log.ERROR)

                # try this: don't remove captcha_retries from meta, may cause infinite loops, works
                # if response.meta['captcha_retries'] > self.MAX_CAPTCHA_RETRIES:
                    # del response.meta['captcha_retries']
            # if we have reached maximum number of retries, do nothing (item just won't be added to the "items" list)


            # if we haven't reached maximum retries, try again
            if 'captcha_retries' not in response.meta \
                or 'captcha_retries' in response.meta and response.meta['captcha_retries'] <= self.MAX_CAPTCHA_RETRIES:

                # assume there is a captcha to crack
                # check if there is a form on the page - that means it's probably the captcha form
                forms = hxs.select("//form")
                if forms:
                    
                    # solve captcha
                    captcha_text = None
                    image = hxs.select(".//img/@src").extract()
                    if image:
                        captcha_text = self.CB.solve_captcha(image[0])

                    # value to use if there was an exception
                    if not captcha_text:
                        captcha_text = ''


                    # create a FormRequest to this same URL, with everything needed in meta
                    # items, cookies and search_urls not changed from previous response so no need to set them again
        
                    # redo the entire request (no items will be lost)
                    meta = response.meta
                    # flag indicating how many times we already retried to solve captcha
                    if 'captcha_retries' in meta:
                        meta['captcha_retries'] += 1
                    else:
                        meta['captcha_retries'] = 1
                    return [FormRequest.from_response(response, callback = self.parse_product_amazon, formdata={'field-keywords' : captcha_text}, meta = meta)]

        else:
            item['product_name'] = product_name

            # extract product model number
            model_number_holder = hxs.select("""//tr[@class='item-model-number']/td[@class='value']/text() |
             //li/b/text()[normalize-space()='Item model number:']/parent::node()/parent::node()/text() |
             //span/text()[normalize-space()='Item model number:']/parent::node()/parent::node()/span[2]/text()""").extract()
            if model_number_holder:
                item['product_model'] = model_number_holder[0].strip()
            # if no product model explicitly on the page, try to extract it from name
            else:
                product_model_extracted = ProcessText.extract_model_from_name(item['product_name'])
                if product_model_extracted:
                    item['product_model'] = product_model_extracted
                ## print "MODEL EXTRACTED: ", product_model_extracted, " FROM NAME ", item['product_name'].encode("utf-8")
                
            upc_node = hxs.select("//li/b/text()[normalize-space()='UPC:']/parent::node()/parent::node()/text()").extract()
            if upc_node:
                upc = upc_node[0].strip().split()
                item['product_upc'] = upc

            manufacturer_code_node = hxs.select("//li/b/text()[normalize-space()='Manufacturer reference:']/parent::node()/parent::node()/text()").extract()
            if manufacturer_code_node:
                manufacturer_code = manufacturer_code_node[0].strip()
                item['manufacturer_code'] = manufacturer_code

            try:
                # for lowest level category:
                # TODO: test the xpath for the second type of page (see second type of xpath for top-level category)
                # bestsellers_rank = hxs.select("//tr[@id='SalesRank']/td[@class='value']/ul/li/span/text()" + \
                # "| //li[@id='SalesRank']/ul/li/span/text()").re("#[0-9,]+")[0]

                # for top-level category:
                bestsellers_rank = hxs.select("//tr[@id='SalesRank']/td[@class='value']/text()" + 
                    " | //li[@id='SalesRank']/text()").re("#[0-9,]+")[0]
                item['bestsellers_rank'] = int(re.sub(",", "", "".join(bestsellers_rank[1:])))
            except Exception, e:
                if self.output==6 or self.bestsellers_link:
                    self.log("Didn't find product rank: " + str(e) + " " + response.url + "\n", level=log.INFO)

            asin_node = hxs.select("//li/b/text()[normalize-space()='ASIN:']/parent::node()/parent::node()/text()").extract()
            if asin_node:
                item['product_asin'] = asin_node[0].strip()

            brand_holder = hxs.select("//div[@id='brandByline_feature_div']//a/text() | //a[@id='brand']/text()").extract()
            if brand_holder:
                item['product_brand'] = brand_holder[0]
            else:
                pass
                #sys.stderr.write("Didn't find product brand: " + response.url + "\n")

            # extract price
            #! extracting list price and not discount price when discounts available?
            price_holder = hxs.select("//span[contains(@id,'priceblock')]/text() | //span[@class='a-color-price']/text() " + \
                "| //span[@class='listprice']/text() | //span[@id='actualPriceValue']/text() | //b[@class='priceLarge']/text() | //span[@class='price']/text()").extract()

            # if we can't find it like above try other things:
            if not price_holder:
                # prefer new prices to used ones
                # TODO: doesn't work for amazon.co.uk (pounds), but isn't needed bery often
                price_holder = hxs.select("//span[contains(@class, 'olp-new')]//text()[contains(.,'$')]").extract()
            if price_holder:
                product_target_price = price_holder[0].strip()
                # remove commas separating orders of magnitude (ex 2,000)
                product_target_price = re.sub(",","",product_target_price)
                m = re.match("(\$|\xa3)([0-9]+\.?[0-9]*)", product_target_price)
                if m:
                    item['product_target_price'] = float(m.group(2))
                    currency = m.group(1)
                    if currency != "$":
                        item['product_target_price'] = Utils.convert_to_dollars(item['product_target_price'], currency)
                else:
                    self.log("Didn't match product price: " + product_target_price + " " + response.url + "\n", level=log.WARNING)

            else:
                self.log("Didn't find product price: " + response.url + "\n", level=log.INFO)


            # add result to items
            items.add(item)
            self.results[origin_product_id]['search_requests'][current_query]['product_items'].append(item)


        # print "STILL IN parse_product FOR", response.url

        product_urls = response.meta['search_results']

        # try to send request to parse next product, try until url for next product url is valid (response not 404)
        # this is needed because if next product url is not valid, this request will not be sent and all info about this match (stored in request meta) will be lost

        # find first valid next product url
        next_product_url = None
        if product_urls:
            next_product_url = product_urls.pop()
            next_product_url2 = product_urls2.pop()
            self.remove_result_from_queue(origin_product_id, next_product_url2)

        while (product_urls and not self.is_valid_url(next_product_url)):
            # print "404 FROM", next_product_url
            next_product_url = product_urls.pop()
            next_product_url2 = product_urls2.pop()
            self.remove_result_from_queue(origin_product_id, next_product_url2)


        # handle corner case of bad next product url
        if not product_urls and next_product_url and not self.is_valid_url(next_product_url):
            next_product_url = None

        # if a next product url was found, send new request back to parse_product_url
        if next_product_url:
            request = Request(next_product_url, callback = self.parse_product_amazon, meta = response.meta)
            request.meta['items'] = items
            # eliminate next product from pending list (this will be the new list with the first item popped)
            request.meta['search_results'] = product_urls

            return request

        # if no next valid product url was found
        else:
            # we are done, send a the response back to reduceResults (no need to make a new request)
            # add as meta newly added items
            # also add 'parsed' field to indicate that the parsing of all products was completed and they cand be further used
            # (actually that the call was made from this method and was not the initial one, so it has to move on to the next request)

            response.meta['parsed'] = True
            response.meta['items'] = items

            # print "RETURNING FROM PARSE AMAZON PRODUCT TO reduce_results FOR", response.meta['origin_url'], response.url

            return self.reduceResults(response)