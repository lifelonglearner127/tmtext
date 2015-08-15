from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from scrapy.http import Response
from scrapy.exceptions import CloseSpider
from search.items import SearchItem
from search.items import WalmartItem
from search.spiders.search_spider import SearchSpider
from scrapy import log

from spiders_utils import Utils
from search.matching_utils import ProcessText

import re
import sys

# spider derived from search spider to search for products on Walmart
class WalmartSpider(SearchSpider):

    name = "walmart"

    # initialize fields specific to this derived spider
    def init_sub(self):
        self.target_site = "walmart"
        self.start_urls = [ "http://www.walmart.com" ]

    def parseResults(self, response):


        hxs = HtmlXPathSelector(response)

        #site = response.meta['origin_site']
        origin_name = response.meta['origin_name']
        origin_model = response.meta['origin_model']

        # if this comes from a previous request, get last request's items and add to them the results

        if 'items' in response.meta:
            items = response.meta['items']
        else:
            items = set()

        # add product URLs to be parsed to this list
        if 'search_results' not in response.meta:
            product_urls = set()
        else:
            product_urls = response.meta['search_results']


        # TODO: check this xpath and extractions
        results = hxs.select("//h4[@class='tile-heading']/a")

        # try xpath for old page version
        if not results:
             results = hxs.select("//div[@class='prodInfo']/div[@class='prodInfoBox']/a[@class='prodLink ListItemLink']")

        for result in results:

            product_url = result.select("@href").extract()[0]
            product_url = Utils.add_domain(product_url, "http://www.walmart.com")
            product_urls.add(product_url)

 
        # extract product info from product pages (send request to parse first URL in list)
        # add as meta all that was received as meta, will pass it on to reduceResults function in the end
        # also send as meta the entire results list (the product pages URLs), will receive callback when they have all been parsed

        # send the request further to parse product pages only if we gathered all the product URLs from all the queries 
        # (there are no more pending requests)
        # otherwise send them back to parseResults and wait for the next query, save all product URLs in search_results
        # this way we avoid duplicates
        if product_urls and ('pending_requests' not in response.meta or not response.meta['pending_requests']):
            request = Request(product_urls.pop(), callback = self.parse_product_walmart, meta = response.meta)
            request.meta['items'] = items

            # this will be the new product_urls list with the first item popped
            request.meta['search_results'] = product_urls

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


        # relevant for extracting products from results page only
        # - deprecated
        # response.meta['items'] = items
        # response.meta['parsed'] = items
        # return self.reduceResults(response)
    
    # extract product info from a product page for walmart
    # keep product pages left to parse in 'search_results' meta key, send back to parseResults_new when done with all
    def parse_product_walmart(self, response):

        hxs = HtmlXPathSelector(response)

        items = response.meta['items']

        #site = response.meta['origin_site']
        origin_url = response.meta['origin_url']

        item = SearchItem()
        item['product_url'] = response.url
        #item['origin_site'] = site
        item['origin_url'] = origin_url
        item['origin_name'] = response.meta['origin_name']

        if 'origin_model' in response.meta:
            item['origin_model'] = response.meta['origin_model']
        if 'origin_upc' in response.meta:
            item['origin_upc'] = response.meta['origin_upc']
        if 'origin_bestsellers_rank' in response.meta:
            item['origin_bestsellers_rank'] = response.meta['origin_bestsellers_rank']

        # assume new design of walmart product page
        product_name_node = hxs.select("//h1[contains(@class, 'product-name')]//text()").extract()

        if not product_name_node:
            # assume old design
            product_name_node = hxs.select("//h1[contains(@class, 'productTitle')]//text()").extract()

        if product_name_node:
            product_name = product_name_node[0].strip()
        else:
            self.log("Error: No product name: " + str(response.url) + " for source product " + origin_url, level=log.ERROR)
            # TODO:is this ok? I think so
            return

        item['product_name'] = product_name

        # extract product model number
        # TODO: use meta? works for both old and new?

        # extract features table for new page version:
        table_node = hxs.select("//div[@class='specs-table']/table").extract()

        if not table_node:
            # old page version:
            table_node = hxs.select("//table[@class='SpecTable']").extract()

        if table_node:
            try:
                product_model = table_node.select(".//td[contains(text(),'Model')]/following-sibling::*/text()").extract()[0]
                item['product_model'] = product_model
            except:
                pass

        upc_node = hxs.select("//meta[@itemprop='productID']/@content")
        if upc_node:
            item['product_upc'] = [upc_node.extract()[0]]


        brand_holder = hxs.select("//meta[@itemprop='brand']/@content").extract()
        if brand_holder:
            item['product_brand'] = brand_holder[0]

        # extract price
        # TODO: good enough for all pages? could also extract from page directly
        price_holder = hxs.select("//meta[@itemprop='price']/@content").extract()
        product_target_price = None
        if price_holder:
            product_target_price = price_holder[0].strip()

        else:
            product_target_price = "".join(hxs.select("//div[@itemprop='price']//text()").extract()).strip()

        # if we can't find it like above try other things:
        if product_target_price:
            # remove commas separating orders of magnitude (ex 2,000)
            product_target_price = re.sub(",","",product_target_price)
            m = re.match("\$([0-9]+\.?[0-9]*)", product_target_price)
            if m:
                item['product_target_price'] = float(m.group(1))
            else:
                self.log("Didn't match product price: " + product_target_price + " " + response.url + "\n", level=log.WARNING)

        else:
            self.log("Didn't find product price: " + response.url + "\n", level=log.INFO)


        # add result to items
        items.add(item)


        product_urls = response.meta['search_results']

        # try to send request to parse next product, try until url for next product url is valid (response not 404)
        # this is needed because if next product url is not valid, this request will not be sent and all info about this match (stored in request meta) will be lost

        # find first valid next product url
        next_product_url = None
        if product_urls:
            next_product_url = product_urls.pop()


        # if a next product url was found, send new request back to parse_product_url
        if next_product_url:
            request = Request(next_product_url, callback = self.parse_product_walmart, meta = response.meta)
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

            return self.reduceResults(response)


# spider that receives a list of Walmart product ids (or of Walmart URLs of the type http://www.walmart.com/<id>)
# and outputs the product's page full URL as found on Walmart
########################
# Run with:
#  scrapy crawl walmart_fullurls -a ids_file=<input_filename> [-a outfile=<output_filename>]
#
#
########################
class WalmartFullURLsSpider(BaseSpider):
    name = "walmart_fullurls"

    allowed_domains = ["walmart.com"]
    start_urls = ["http://www.walmart.com"]

    def __init__(self, ids_file, outfile=None):
        self.ids_file = ids_file
        self.outfile = outfile

        # extract ids from URLs in input file (of type http://www.walmart.com/ip/<id>) and store them in a list
        self.walmart_ids = []
        with open(self.ids_file, "r") as infile:
            for line in infile:
                m = re.match("http://www.walmart.com/ip/([0-9]+)", line.strip())
                if m:
                    walmart_id = m.group(1)
                    self.walmart_ids.append(walmart_id)
                else:
                    self.log("ERROR: Invalid (short) URL file" + "\n", level = log.ERROR)
                    #raise CloseSpider("Invalid (short) URL file")

        # this option is needed in middlewares.py used by all spiders
        self.use_proxy = False

    # build URL for search page with a specific search query. to be used with product ids as queries
    def build_search_page(self, query):
        searchpage_URL = "http://www.walmart.com/search/search-ng.do?ic=16_0&Find=Find&search_query=%s&Find=Find&search_constraint=0" % query
        return searchpage_URL

    # check if URL contains the product's id (therefore is valid)
    def valid_result(self, url, prod_id):
        return "/"+prod_id in url

    def parse(self, response):
        # take every id and pass it to the method that retrieves its URL, build an item for each of it
        for walmart_id in self.walmart_ids:
            item = WalmartItem()
            item['walmart_id'] = walmart_id
            item['walmart_short_url'] = "http://www.walmart.com/ip/" + walmart_id

            # search for this id on Walmart, get the results page
            search_page = self.build_search_page(walmart_id)
            request = Request(search_page, callback = self.parse_resultsPage, meta = {"item": item})
            yield request

    # get URL of first result from search page (search by product id)
    def parse_resultsPage(self, response):
        hxs = HtmlXPathSelector(response)
        item = response.meta['item']
        result = hxs.select("//div[@class='prodInfo']/div[@class='prodInfoBox']/a[@class='prodLink ListItemLink'][position()<2]/@href").extract()
        if result:
            item['walmart_full_url'] = Utils.add_domain(result[0], "http://www.walmart.com")

            # id should be somewhere in the full URL as well
            if self.valid_result(item['walmart_full_url'], item['walmart_id']):
                return item
            else:
                # search again, but select result that contains id
                #OBS: non optimal, should do selecting here
                return Request(response.url, callback = self.parse_resultsPage2, meta = {"item":item})
        else:
            # try to find result by using the product name instead

            # get product name from product page, then search by it
            return Request(item['walmart_short_url'], callback = self.getProductName, meta = {"item":item})
            #self.log("No results for short_url " + item['walmart_short_url'] + "\n", level=log.ERROR)

    def getProductName(self, response):
        hxs = HtmlXPathSelector(response)
        title_holder = hxs.select("//h1[@class='productTitle']/text()").extract()
        if title_holder:
            product_name = title_holder[0]

            # search by product name
            search_query = "+".join(product_name.split())
            search_page = self.build_search_page(search_query)
            return Request(search_page, callback = self.parse_resultsPage2, meta = {"item" : response.meta['item']})

        else:
            self.log("No results for short_url (didn't find product name) " + response.url + "\n", level=log.ERROR)

    # parse results page from search by product name - find URL that contains item id, if any
    def parse_resultsPage2(self, response):
        hxs = HtmlXPathSelector(response)

        item = response.meta['item']
        results = hxs.select("//div[@class='prodInfo']/div[@class='prodInfoBox']/a[@class='prodLink ListItemLink']/@href").extract()
        for result in results:
            # if the result URL contains the id, this is the correct result
            if self.valid_result(item['walmart_id'], result):
                product_url = Utils.add_domain(result, "http://www.walmart.com")
                item['walmart_full_url'] = product_url
                return item


        # no results matching the condition were found
        self.log("No results for short_url (didn't find any URLs containing id) " + item['walmart_short_url'] + "\n", level=log.ERROR)






