from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.http import TextResponse
from scrapy.http import Response
from scrapy.exceptions import CloseSpider
from search.items import SearchItem
from scrapy import log

from spiders_utils import Utils
from search.matching_utils import ProcessText

import re
import sys
import json
import csv
import urllib

# from selenium import webdriver
# import time

################################
# Run with 
#
#   scrapy crawl <site> -a product_name="<name>" [-a output="<option(1/2)>"] [-a threshold=<value>] [a outfile="<filename>"] [-a fast=0]
#      -- or --
#   scrapy crawl <site> -a product_url="<url>" [-a output="<option(1/2)>"] [-a threshold=<value>] [a outfile="<filename>""] [-a fast=0]
#      -- or --
#   scrapy crawl <site> -a product_urls_file="<filename>" [-a output="<option(1/2)>"] [-a threshold=value] [a outfile="<filename>"] [-a fast=0]
#      -- or --
#   scrapy crawl <site> -a walmart_ids_file="<filename>" [-a output="<option(1/2)>"] [-a threshold=value] [a outfile="<filename>"] [-a fast=0]
# 
# where <site> is the derived spider corresponding to the site to search on 
#
# Usage example:
#
# scrapy crawl amazon -a product_urls_file="../sample_output/walmart_televisions_urls.txt" -a output=2 -a outfile="search_results_1.4.txt" -a threshold=1.4 -s LOG_ENABLED=1 2>search_log_1.4.out
#
################################


# search for a product in all sites, using their search functions; give product as argument by its name or its page url
class SearchSpider(BaseSpider):

    name = "search"
    # amazon_cookie_header = "x-wl-uid=1Y9x3Q0Db5VX3Xvh1wKV9kdGsDEeLDkceSgPK5Hq+AhrYZKCWSHWq6CeCiAwA7BsYZQ58tkG8c3c=; session-token=JPU0C93JOc0DMIZwsQTlpZFJAADURltK2s5Cm22nmFGmaGRwiOPKdvd+ALLsrWay07GVVQtBquy/KpNSTFb5e0HfWeHAq92jFhXz5nQouwyqMLtEC3MUu2TWkIRGps4ppDXQfMP/r96gq0QfRR8EdPogbQ9RzEXoIKf3tj3klxeO2mT6xVQBTfpMPbQHQtv8uyFjWgkLtp6upe4eWorbpd/KyWlBSQXD4eiyfQLIC480TxbOvCBmDhGBOqf6Hk0Nprh2OO2EfrI=; x-amz-captcha-1=1391100438353490; x-amz-captcha-2=+EDhq9rcotSRn783vYMxdQ==; csm-hit=337.71|1391093239619; ubid-main=188-7820618-3817319; session-id-time=2082787201l; session-id=177-0028713-4113141"
    # amazon_cookies = {"x-wl-uid" : "1Y9x3Q0Db5VX3Xvh1wKV9kdGsDEeLDkceSgPK5Hq+AhrYZKCWSHWq6CeCiAwA7BsYZQ58tkG8c3c=", \
    # "session-token" : "JPU0C93JOc0DMIZwsQTlpZFJAADURltK2s5Cm22nmFGmaGRwiOPKdvd+ALLsrWay07GVVQtBquy/KpNSTFb5e0HfWeHAq92jFhXz5nQouwyqMLtEC3MUu2TWkIRGps4ppDXQfMP/r96gq0QfRR8EdPogbQ9RzEXoIKf3tj3klxeO2mT6xVQBTfpMPbQHQtv8uyFjWgkLtp6upe4eWorbpd/KyWlBSQXD4eiyfQLIC480TxbOvCBmDhGBOqf6Hk0Nprh2OO2EfrI=",\
    # "x-amz-captcha-1" : "1391100438353490" , "x-amz-captcha-2" : "+EDhq9rcotSRn783vYMxdQ==", "csm-hit" : "337.71|1391093239619", "ubid-main" : "188-7820618-3817319",\
    # "session-id-time" : "2082787201l", "session-id" : "177-0028713-4113141"}

    allowed_domains = ["amazon.com", "walmart.com", "bloomingdales.com", "overstock.com", "wayfair.com", "bestbuy.com", "toysrus.com",\
                       "bjs.com", "sears.com", "staples.com", "newegg.com", "ebay.com", "target.com", "sony.com", "samsung.com", \
                       "boots.com", "ocado.com", "tesco.com", "maplin.co.uk", "amazon.co.uk", "currys.co.uk", "pcworld.co.uk", "ebay.co.uk", \
                       "argos.co.uk", "ebuyer.com", "ebuyer.co.uk", "firebox.com", "rakuten.co.uk", "uk.rs-online.com", "screwfix.com",
                       "macys.com", "kohls.com"]

    # pass product as argument to constructor - either product name or product URL
    # arguments:
    #                product_name - the product's name, for searching by product name
    #                product_url - the product's page url in the source site, for searching by product URL
    #                product_urls_file - file containing a list of product pages URLs
    #                bestsellers_link - link to list of bestseller products
    #                output - integer(1/2/3/4) option indicating output type (either result URL (1), or result URL and source product URL (2))
    #                         3 - same as 2 but with extra field representing confidence score
    #                         4 - same as 3 but with origin products represented by UPC instead of URL
    #                         5 - same as 3 but with product name as well, on first column (name from source site)
    #                         6 - same as 3 but additionally with bestsellers rank (origin and target) - to be used
    #                             in combination with the input bestsellers_link option
    #                         7 - completely custom, using list of output fields in fields.json
    #                threshold - parameter for selecting results (the lower the value the more permissive the selection)
    def __init__(self, product_name = None, products_file = None, product_url = None, product_urls_file = None, bestsellers_link = None, bestsellers_range = '0', \
        walmart_ids_file = None, output = 2, threshold = 1.0, \
        outfile = "search_results.csv", outfile2 = "not_matched.csv", fast = 0, use_proxy = False, manufacturer_site = None, cookies_file = None):#, by_id = False):

        # call specific init for each derived class
        self.init_sub()

        self.version = "edead362dff971c1202f1b98f11ff1ac6f800519"

        self.product_url = product_url
        self.products_file = products_file
        self.product_name = product_name
        self.bestsellers_link = bestsellers_link
        self.bestsellers_range = self.parse_bestsellers_range(bestsellers_range)
        self.output = int(output)
        self.product_urls_file = product_urls_file
        self.walmart_ids_file = walmart_ids_file
        self.threshold = float(threshold)
        self.outfile = outfile
        self.outfile2 = outfile2
        self.fast = fast
        self.use_proxy = use_proxy
        self.manufacturer_site = manufacturer_site
        #self.by_id = by_id

        # set cookies
        self.cookies_file = cookies_file
        if cookies_file:
            self.cookies = json.load(open(cookies_file, "r"))
            self.amazon_cookies = self.cookies['amazon_cookies']
            amazon_cookie_header = ""
            for cookie in self.amazon_cookies:
                amazon_cookie_header += cookie + "=" + self.amazon_cookies[cookie] + "; "
            self.amazon_cookie_header = amazon_cookie_header


        # parseURL functions, one for each supported origin site
        self.parse_url_functions = {'staples' : self.parseURL_staples, \
                                    'walmart' : self.parseURL_walmart, \
                                    'newegg' : self.parseURL_newegg,\
                                    'boots' : self.parseURL_boots, \
                                    'ocado' : self.parseURL_ocado, \
                                    'tesco' : self.parseURL_tesco, \
                                    'amazon' : self.parseURL_amazon, \
                                    'target' : self.parseURL_target, \
                                    'maplin' : self.parseURL_maplin, \
                                    'wayfair' : self.parseURL_wayfair
                                    }

        # parse_bestsellers functions, for each supported origin site
        self.parse_bestsellers_functions = {'amazon' : self.parse_bestsellers_amazon, \
                                            'walmart' : self.parse_bestsellers_walmart
                                            }


    def build_search_pages(self, search_query):
        # build list of urls = search pages for each site
        search_pages = {
                        "amazon" : "http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + search_query, \
                        "amazoncouk" : "http://www.amazon.co.uk/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + search_query, \
                        "walmart" : "http://www.walmart.com/search/search-ng.do?ic=16_0&Find=Find&search_query=%s&Find=Find&search_constraint=0" % search_query, \
                        "bloomingdales" : "http://www1.bloomingdales.com/shop/search?keyword=%s" % search_query, \
                        "overstock" : "http://www.overstock.com/search?keywords=%s" % search_query, \
                        "wayfair" : "http://www.wayfair.com/keyword.php?keyword=%s" % search_query, \
                        # #TODO: check this URL
                        "bestbuy" : "http://www.bestbuy.com/site/searchpage.jsp?_dyncharset=ISO-8859-1&_dynSessConf=-26268873911681169&id=pcat17071&type=page&st=%s&sc=Global&cp=1&nrp=15&sp=&qp=&list=n&iht=y&fs=saas&usc=All+Categories&ks=960&saas=saas" % search_query, \
                        "toysrus": "http://www.toysrus.com/search/index.jsp?kw=%s" % search_query, \
                        # #TODO: check the keywords, they give it as caps
                        # "bjs" : "http://www.bjs.com/webapp/wcs/stores/servlet/Search?catalogId=10201&storeId=10201&langId=-1&pageSize=40&currentPage=1&searchKeywords=%s&tASearch=&originalSearchKeywords=lg+life+is+good&x=-1041&y=-75" % search_query, \
                        # #TODO: check this url
                        # "sears" : "http://www.sears.com/search=%s" % search_query}
                        # #TODO: staples?
                        "ebay": "http://www.ebay.com/sch/i.html?_trksid=p2050601.m570.l1313&_nkw=%s" % search_query, \
                        "ebaycouk": "http://www.ebay.co.uk/sch/i.html?_trksid=p2050601.m570.l1313&_nkw=%s" % search_query, \
                        "sony": "http://store.sony.com/search?SearchTerm=%s" % search_query, \
                        "samsung": "http://www.samsung.com/us/function/search/espsearchResult.do?input_keyword=%s" % search_query, \
                        "target" : "http://www.target.com/s?searchTerm=" + search_query + "&category=0%7CAll%7Cmatchallpartial%7Call+categories&lnk=snav_sbox_" + search_query, \
                        "ocado" : "http://www.ocado.com/webshop/getSearchProducts.do?clearTabs=yes&isFreshSearch=true&entry=%s" % search_query,
                        "tesco" : "http://www.tesco.com/direct/search-results/results.page?catId=4294967294&searchquery=%s" % search_query,
                        "boots" : "http://www.boots.com/webapp/wcs/stores/servlet/EndecaSearchListerView?storeId=10052&searchTerm=%s" % search_query,
                        "currys" : "http://www.currys.co.uk/gbuk/search-keywords/xx_xx_xx_xx_xx/%s/xx-criteria.html" % search_query,
                        "pcworld" : "http://www.pcworld.co.uk/gbuk/search-keywords/xx_xx_xx_xx_xx/%s/xx-criteria.html" % search_query,
                        "maplin" : "http://www.maplin.co.uk/search?text=%s" % search_query, \
                        "argos" : "http://www.argos.co.uk/static/Search/searchTerm/%s.htm" % search_query, \
                        "ebuyer" : "http://www.ebuyer.com/search?q=%s" % search_query, \
                        "firebox" : "http://www.firebox.com/firebox/search?searchstring=%s" % search_query, \
                        "rakuten" : "http://www.rakuten.co.uk/search/%s/" % search_query, \
                        "rscomponents" : "http://uk.rs-online.com/web/c/?searchTerm=%s" % search_query, \
                        "screwfix" : "http://www.screwfix.com/search?search=%s" % search_query, \
                        "macys" : "http://www1.macys.com/shop/search?keyword=%s" % search_query, \
                        "kohls": "http://www.kohls.com/search.jsp?search=%s" % search_query
                        }

        return search_pages

    def build_search_query(self, product_name):
        # put + instead of spaces, lowercase all words
        search_query = "+".join(ProcessText.normalize(product_name, stem=False, exclude_stopwords=False))
        return search_query

    def parse_bestsellers_range(self, bestsellers_range_string):
        '''Parse input string bestsellers range into a tuple of integers
        representing the range of bestsellers to extract for this spider
        :param bestsellers_range_string: bestsellers range as string of the form
        [x-y] or 0
        '''

        if bestsellers_range_string == '0':
            return []
        else:
            return map(lambda x: int(x), bestsellers_range_string.split("-"))

    def parse_products_file(self, products_file):
        '''Parse input csv containing the needed columns for the source product,
        instead of using the input url and scraping for them
        '''
        products = []
        with open(products_file) as f:
            # skip first line
            # f.readline()

            # TODO: make this more general
            # for line in f:
     
                # product['product_name'] = product_info[0]
                # product['product_price'] = product_info[-1]
                # if product['product_price'].startswith('$'):
                #     product['product_price'] = product['product_price'][1:]
                # product['product_price'] = float(product['product_price'])

                # # for target, get DCPI column as model number
                # # TODO: horrible hack
                # if self.target_site == 'target':
                #     product['product_upc'] = product_info[1]

                reader = csv.DictReader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                
                while True:
                    try:
                        data = next(reader)
                        product = {}
                        try:
                            product['product_name'] = data['Product_Name']
                        except Exception:
                            self.log("No product name in csv for row " + str(data) + "\n", level=log.INFO)
                        try:
                            product['product_upc'] = data['UPC']
                        except Exception:
                            self.log("No UPC in csv for row " + str(data) + "\n", level=log.INFO)
                        try:
                            product['product_price'] = float(data['Product_Price'])
                        except Exception:
                            # exclude currency
                            try:
                                product['product_price'] = float(data['Product_Price'][1:])
                            except Exception:
                                pass
                        try:
                            product['product_model'] = data['Product_Model']
                        except Exception:
                            pass
                        try:
                            product['product_ASIN'] = data['ASIN']
                        except Exception:
                            pass
                        try:
                            product['product_brand'] = data['Brand']
                        except Exception:
                            pass
                        try:
                            product['product_url'] = data['URL']
                        except Exception:
                            pass
                        products.append(product)
                    except StopIteration, e:
                        break

        return products

    # parse input and build list of URLs to find matches for, send them to parseURL
    def parse(self, response):

        # log spider version - will match commit number of last change
        self.log("Spider version: " + self.version + "\n", level=log.INFO)

        if self.product_name:

            # can inly use this option if self.target_site has been initialized (usually true for spiders for retailers sites, not true for manufacturer's sites)
            if not self.target_site:
                self.log("You can't use the product_name option without setting the target site to search on\n", level=log.ERROR)
                raise CloseSpider("\nYou can't use the product_name option without setting the target site to search on\n")

            search_query = self.build_search_query(self.product_name)
            search_pages = self.build_search_pages(search_query)

            request = Request(search_pages[self.target_site], callback = self.parseResults)

            # set amazon cookies
            if (self.target_site == 'amazon' and self.cookies_file):
                request.cookies = self.amazon_cookies
                request.headers['Cookies'] = self.amazon_cookie_header
                #request.meta['dont_merge_cookies'] = True
                ## print "SET AMAZON COOKIES"

            request.meta['origin_name'] = self.product_name
            request.meta['query'] = search_query

            # just use empty product model and url, for compatibility, also pending_requests
            request.meta['origin_model']  = ''
            request.meta['origin_url'] = ''
            request.meta['pending_requests'] = []

            yield request

        # TODO: code below (in this if) is duplicated with parseURL. should deduplicate
        if self.products_file:
            # TODO: is this necessary?
            if not self.target_site:
                self.log("You can't use the product_name option without setting the target site to search on\n", level=log.ERROR)
                raise CloseSpider("\nYou can't use the product_name option without setting the target site to search on\n")

            products_info = self.parse_products_file(self.products_file)
            for product_info in products_info:
                product_name = product_model = product_price = None
                if 'product_name' in product_info:
                    product_name = product_info['product_name']
                else:
                    product_name = ''
                if 'product_price' in product_info:
                    product_price = product_info['product_price']
                if 'product_model' in product_info:
                    product_model = product_info['product_model']
                else:
                    if product_name:
                        product_model = ProcessText.extract_model_from_name(product_name)
                if not product_model:
                    # for correctly logging
                    product_model = ''
                if 'product_upc' in product_info:
                    product_upc = product_info['product_upc']
                else:
                    product_upc = None
                if 'product_brand' in product_info:
                    product_brand = product_info['product_brand']
                else:
                    product_brand = None
                if 'product_url' in product_info:
                    product_url = product_info['product_url']
                    if not product_model:
                        product_model = ProcessText.extract_model_from_url(product_url)
                    if not product_model:
                        product_model = ''
                else:
                    product_url = ''
                if 'product_manufacturer_code' in product_info:
                    product_manufacturer_code = product_info['product_manufacturer_code']
                else:
                    product_manufacturer_code = None

                # if there is no product brand, get first word in name, assume it's the brand
                product_brand_extracted = ""
                #product_name_tokenized = ProcessText.normalize(product_name)
                if product_name:
                    product_name_tokenized = [word.lower() for word in product_name.split(" ")]
                    #TODO: maybe extract brand as word after 'by', if 'by' is somewhere in the product name
                    if len(product_name_tokenized) > 0 and re.match("[a-z]*", product_name_tokenized[0]):
                        product_brand_extracted = product_name_tokenized[0].lower()


                request = None
                pending_requests = []

                # 1) Search by UPC
                if product_upc:
                    query0 = self.build_search_query(product_upc)
                    search_pages0 = self.build_search_pages(query0)
                    #page1 = search_pages1[self.target_site]
                    page0 = search_pages0[self.target_site]

                    request0 = Request(page0, callback = self.parseResults)

                    request0.meta['query'] = query0
                    request0.meta['target_site'] = self.target_site
                    
                    if not request:
                        request = request0
                    else:
                        pending_requests.append(request0)

                

                # 2) Search by model number
                if product_model:

                    #TODO: model was extracted with ProcessText.extract_model_from_name(), without lowercasing, should I lowercase before adding it to query?
                    query1 = self.build_search_query(product_model)
                    search_pages1 = self.build_search_pages(query1)
                    #page1 = search_pages1[self.target_site]
                    page1 = search_pages1[self.target_site]

                    request1 = Request(page1, callback = self.parseResults)

                    request1.meta['query'] = query1
                    request1.meta['target_site'] = self.target_site
                    
                    if not request:
                        request = request1
                    else:
                        pending_requests.append(request1)

                # 3) Search by model number + brand/first word
                if product_model:

                    #TODO: model was extracted with ProcessText.extract_model_from_name(), without lowercasing, should I lowercase before adding it to query?
                    if product_brand:
                        query2 = self.build_search_query(product_model + " " + product_brand)
                    else:
                        query2 = self.build_search_query(product_model + " " + ProcessText.normalize(product_name)[0])
                    search_pages2 = self.build_search_pages(query2)
                    page2 = search_pages2[self.target_site]

                    request2 = Request(page2, callback = self.parseResults)

                    request2.meta['query'] = query2
                    request2.meta['target_site'] = self.target_site
                    
                    if not request:
                        request = request2
                    else:
                        pending_requests.append(request2)


                # 4) Search by product full name
                if product_name:
                    query3 = self.build_search_query(product_name)
                    search_pages3 = self.build_search_pages(query3)
                    #page2 = search_pages2[self.target_site]
                    page3 = search_pages3[self.target_site]
                    request3 = Request(page3, callback = self.parseResults)

                    request3.meta['query'] = query3
                    request3.meta['target_site'] = self.target_site

                    if not request:
                        request = request3
                    else:
                        pending_requests.append(request3)

                    # 5) Search by combinations of words in product's name
                    # create queries

                    for words in ProcessText.words_combinations(product_name, fast=self.fast):
                        query4 = self.build_search_query(" ".join(words))
                        search_pages4 = self.build_search_pages(query4)
                        #page3 = search_pages3[self.target_site]
                        page4 = search_pages4[self.target_site]
                        request4 = Request(page4, callback = self.parseResults)

                        request4.meta['query'] = query4
                        request4.meta['target_site'] = self.target_site


                        pending_requests.append(request4)

                request.meta['pending_requests'] = pending_requests
                #request.meta['origin_site'] = 
                # product page from source site
                #TODO: clean this URL? for walmart it added something with ?enlargedsearch=True
                request.meta['origin_url'] = product_url

                request.meta['origin_name'] = product_name
                request.meta['origin_model'] = product_model
                request.meta['origin_upc'] = [product_upc]
                if product_price:
                    request.meta['origin_price'] = product_price
                request.meta['origin_brand'] = product_brand
                request.meta['origin_brand_extracted'] = product_brand_extracted
                request.meta['origin_manufacturer_code'] = product_manufacturer_code

                yield request

        if self.bestsellers_link:
            origin_site = Utils.extract_domain(self.bestsellers_link)
            yield Request(self.bestsellers_link, callback=self.parse_bestsellers_functions[origin_site])

        # if we have product URLs, pass them to parseURL to extract product names (which will pass them to parseResults)
        product_urls = []
        # if we have a single product URL, create a list of URLs containing it
        if self.product_url:
            product_urls.append(self.product_url)

        # if we have a file with a list of URLs, create a list with URLs found there
        if self.product_urls_file:
            f = open(self.product_urls_file, "r")
            for line in f:
                product_urls.append(line.strip())
            f.close()

        for product_url in product_urls:
            # extract site domain
            
            # m = re.match("http://www1?\.([^\.]+)\.com.*", product_url)
            # origin_site = ""
            # if m:
            #     origin_site = m.group(1)
            # else:
            #     sys.stderr.write('Can\'t extract domain from URL.\n')
            origin_site = Utils.extract_domain(product_url)
            
            request = Request(product_url, callback = self.parseURL)
            request.meta['origin_site'] = origin_site
            if origin_site == 'staples':
                zipcode = "12345"
                request.cookies = {"zipcode": zipcode}
                request.meta['dont_redirect'] = True
            yield request

        # if we have a file with Walmart ids, create a list of the ids there
        if self.walmart_ids_file:
            walmart_ids = []
            f = open(self.walmart_ids_file, "r")
            for line in f:
                if "," in line:
                    id_string = line.strip().split(",")[0]
                else:
                    id_string = line.strip()
                if re.match("[0-9]+", id_string):
                    walmart_ids.append(id_string)
            f.close()        

            self.by_id = True

            for walmart_id in walmart_ids:
                # create Walmart URLs based on these IDs
                walmart_url = Utils.add_domain(walmart_id, "http://www.walmart.com/ip/")
                request = Request(walmart_url, callback = self.parseURL)
                #request.meta['origin_site'] = 'walmart'
                yield request

    def parse_bestsellers_amazon(self, response):
        '''Parse input bestsellers link to extract all bestseller products,
        and pass them over to parseURL to start matching with these as
        origin urls
        '''
        # e.g.
        # http://www.amazon.com/Best-Sellers-Electronics-Televisions/zgbs/electronics/172659/ref=zg_bs_nav_e_2_1266092011

        hxs = HtmlXPathSelector(response)
        product_links = hxs.select("//div[@class='zg_title']/a/@href").extract()

        if 'last_index' not in response.meta:
            last_index = 0
        else:
            last_index = response.meta['last_index']

        # index of product in bestsellers lists
        index = last_index

        for product_link in product_links:
            # start matching for this product
            index = index + 1
            # only consider products in the range given as input
            if self.bestsellers_range and self.bestsellers_range[0] <= index < self.bestsellers_range[1]:
                yield Request(product_link.strip(), callback=self.parseURL, meta={'origin_site' : 'amazon', 'origin_bestsellers_rank' : index})
            pass

        # go to next page
        # if we're already past the index range, skip further pages
        if not self.bestsellers_range or index <= self.bestsellers_range[1]:
            try:
                next_page_link = hxs.select("//ol[@class='zg_pagination']/li[@class='zg_page zg_selected']/following-sibling::li[1]/a/@href")\
                .extract()[0]
                yield Request(next_page_link, callback=self.parse_bestsellers_amazon, meta={'last_index' : index})
            except Exception, e:
                pass

    def parse_bestsellers_walmart(self, response):
        '''Parse input bestsellers link to extract all bestseller products,
        and pass them over to parseURL to start matching with these as
        origin urls
        '''
        # e.g.
        # http://www.walmart.com/browse/electronics/tvs/3944_1060825_447913

        hxs = HtmlXPathSelector(response)
        product_links = hxs.select("//div[@class='js-tile tile-grid-unit']/a[@class='js-product-title']/@href").extract()

        if 'last_index' not in response.meta:
            last_index = 0
        else:
            last_index = response.meta['last_index']
        index = last_index

        for product_link in product_links:
            # start matching for this product
            product_link = "http://www.walmart.com" + product_link.strip()
            index = index + 1
            
            # only consider products in the range given as input
            if self.bestsellers_range and self.bestsellers_range[0] <= index < self.bestsellers_range[1]:
                yield Request(product_link, callback=self.parseURL, meta={'origin_site' : 'walmart', 'origin_bestsellers_rank' : index})

        # go to next page
        # if we're already past the index range, skip further pages
        if not self.bestsellers_range or index <= self.bestsellers_range[1]:
            try:
                next_page_link = hxs.select("//a[@class='paginator-btn paginator-btn-next']/@href").extract()[0]
                base_url = urllib.splitquery(response.url)[0]
                next_page_link = base_url + next_page_link
                yield Request(next_page_link, callback=self.parse_bestsellers_walmart, meta={'last_index' : index})
            except Exception, e:
                pass


    # parse a product page (given its URL) and extract product's name;
    # create queries to search by (use model name, model number, and combinations of words from model name), then send them to parseResults
    #TODO: refactor
    def parseURL(self, response):

        site = response.meta['origin_site']
        hxs = HtmlXPathSelector(response)

        # parse results page, handle each site separately

        # recieve requests for search pages with queries as:
        # 1) product upc (if available)
        # 2) product model (if available)
        # 3) product name
        # 4) parts of product's name


        #############################################################
        # Extract product attributes (differently depending on site)


        if site in self.parse_url_functions:
            (product_name, product_model, product_price, product_upc, product_manufacturer_code, product_brand) = self.parse_url_functions[site](hxs)

        else:
            raise CloseSpider("Unsupported site: " + site)

        # product_manufacturer_code = None # temporary
        # replace None attributes with the empty string - for output purposes (log mainly)
        for attribute in (product_name, product_model, product_price, product_upc, product_manufacturer_code):
            if not attribute:
                attribute = ""

        #
        # Log errors and return empty matches if no name was found
        #
        # if no product name, abort and send the item like it is (no match)
        if not product_name:
            sys.stderr.write("Broken product page link (can't find item title): " + response.url + "\n")
            # return the item as a non-matched item
            item = SearchItem()
            #item['origin_site'] = site
            item['origin_url'] = response.url
            item['origin_name'] = ''

            #TODO: move this somewhere more relevant
            # remove unnecessary parameters for walmart links
            m = re.match("(.*)\?enlargedSearch.*", item['origin_url'])
            if m:
                item['origin_url'] = m.group(1)
            #item['origin_id'] = self.extract_walmart_id(item['origin_url'])


            if self.name != 'manufacturer':
                # don't return empty matches in manufacturer spider
                yield item
            return

        # for walmart price extraction is implemented, so warn if it's not found
        if not product_price and site=='walmart':
            self.log("Didn't find product price: " + response.url + "\n", level=log.DEBUG)

        if site == 'staples':
            zipcode = "12345"
            cookies = {"zipcode": zipcode}
        else:
            cookies = {}


        #######################################################################
        # Create search queries to the second site, based on product attributes

        request = None

        #TODO: search by alternative model numbers?

        #TODO: search by model number extracted from product name? Don't I do that implicitly? no, but in combinations

        # if there is no product model, try to extract it
        if not product_model and product_name:
            product_model = ProcessText.extract_model_from_name(product_name)

            if not product_model:
                product_model = ProcessText.extract_model_from_url(response.url)

            # for logging purposes, set this back to the empty string if it wasn't found (so was None)
            if not product_model:
                product_model = ""

            # product_model_index = ProcessText.extract_model_nr_index(product_name)
            # if product_model_index >= 0:
            #     product_model = product_name[product_model_index]
                
            ## print "MODEL EXTRACTED: ", product_model, " FROM NAME ", product_name

        # if there is no product brand, get first word in name, assume it's the brand
        product_brand_extracted = ""
        #product_name_tokenized = ProcessText.normalize(product_name)
        product_name_tokenized = [word.lower() for word in product_name.split(" ")]
        #TODO: maybe extract brand as word after 'by', if 'by' is somewhere in the product name
        if len(product_name_tokenized) > 0 and re.match("[a-z]*", product_name_tokenized[0]):
            product_brand_extracted = product_name_tokenized[0].lower()

        # if we are in manufacturer spider, set target_site to manufacturer site

        # for manufacturer spider set target_site of request to brand extracted from name for this particular product
        if self.name == 'manufacturer':

            #TODO: restore commented code; if brand not found, try to search for it on every manufacturer site (build queries fo every supported site)
            # hardcode target site to sony`
            #self.target_site = 'sony'
            #self.target_site = product_brand_extracted

            #target_site = product_brand_extracted

            # can only go on if site is supported
            # (use dummy query)
            #if target_site not in self.build_search_pages("").keys():
            if product_brand_extracted not in self.build_search_pages("").keys():

                product_brands_extracted = set(self.build_search_pages("").keys()).intersection(set(product_name_tokenized))
                
                if product_brands_extracted:
                    product_brand_extracted = product_brands_extracted.pop()
                    #target_site = product_brand_extracted
                else:
                    # give up and return item without match
                    self.log("Manufacturer site not supported (" + product_brand_extracted + ") or not able to extract brand from product name (" + product_name + ")\n", level=log.ERROR)

                    ## comment lines below to: don't return anything if you can't search on manufacturer site
                    # item = SearchItem()
                    # item['origin_url'] = response.url
                    # item['origin_name'] = product_name
                    # if product_model:
                    #     item['origin_model'] = product_model
                    # yield item
                    return

            # if specific site is not set, search on manufacturer site as extracted from name
            if not self.manufacturer_site:
                target_site = product_brand_extracted
            else:
                # if it's set, continue only if it matches extracted brand
                if self.manufacturer_site!= product_brand_extracted:
                    self.log("Will abort matching for product, extracted brand does not match specified manufacturer option (" + product_brand_extracted + ")\n", level=log.INFO)

                    ## comment lines below to: don't return anything if you can't search on manufacturer site
                    # item = SearchItem()
                    # item['origin_url'] = response.url
                    # item['origin_name'] = product_name
                    # if product_model:
                    #     item['origin_model'] = product_model
                    # yield item
                    return

                else:
                    target_site = product_brand_extracted


                    # # try to match it without specific site (manufacturer spider will try to search on all manufacturer sites)
                    # target_site = None



        # for other (site specific) spiders, set target_site of request to class variable self.target_site set in class "constructor" (init_sub)
        else:
            target_site = self.target_site

        pending_requests = []

        # 1) Search by UPC
        if product_upc:
            # TODO: search by multiple UPCs if there are more than 1?
            query1 = self.build_search_query(product_upc)
            search_pages1 = self.build_search_pages(query1)
            #page1 = search_pages1[self.target_site]
            page1 = search_pages1[target_site]

            request1 = Request(page1, callback = self.parseResults)

            # set amazon cookies
            if (self.target_site == 'amazon' and self.cookies_file):
                request1.cookies = self.amazon_cookies
                request1.headers['Cookies'] = self.amazon_cookie_header
                #request1.meta['dont_merge_cookies'] = True
                ## print "SET AMAZON COOKIES"

            request1.meta['query'] = query1
            request1.meta['target_site'] = target_site
            
            if not request:
                request = request1
            else:
                pending_requests.append(request1)


        # 2) Search by model number
        if product_model:

            #TODO: model was extracted with ProcessText.extract_model_from_name(), without lowercasing, should I lowercase before adding it to query?
            query2 = self.build_search_query(product_model)
            search_pages2 = self.build_search_pages(query2)
            #page1 = search_pages1[self.target_site]
            page2 = search_pages2[target_site]

            request2 = Request(page2, callback = self.parseResults)

            # set amazon cookies
            if (self.target_site == 'amazon' and self.cookies_file):
                request2.cookies = self.amazon_cookies
                request2.headers['Cookies'] = self.amazon_cookie_header
                #request1.meta['dont_merge_cookies'] = True
                ## print "SET AMAZON COOKIES"

            request2.meta['query'] = query2
            request2.meta['target_site'] = target_site
            
            if not request:
                request = request2
            else:
                pending_requests.append(request2)

        # 3) Search by model number + brand/first word
        if product_model:

            #TODO: model was extracted with ProcessText.extract_model_from_name(), without lowercasing, should I lowercase before adding it to query?
            if product_brand:
                query3 = self.build_search_query(product_model + " " + product_brand)
            else:
                query3 = self.build_search_query(product_model + " " + ProcessText.normalize(product_name)[0])
            search_pages3 = self.build_search_pages(query3)
            page3 = search_pages3[target_site]

            request3 = Request(page3, callback = self.parseResults)

            request3.meta['query'] = query3
            request3.meta['target_site'] = target_site
            
            if not request:
                request = request3
            else:
                pending_requests.append(request3)


        # 4) Search by product full name
        query4 = self.build_search_query(product_name)
        search_pages4 = self.build_search_pages(query4)
        #page2 = search_pages2[self.target_site]
        page4 = search_pages4[target_site]
        request4 = Request(page4, callback = self.parseResults)

        request4.meta['query'] = query4
        request4.meta['target_site'] = target_site

        if not request:
            request = request4
        else:
            pending_requests.append(request4)

        # 5) Search by combinations of words in product's name
        # create queries

        for words in ProcessText.words_combinations(product_name, fast=self.fast):
            query5 = self.build_search_query(" ".join(words))
            search_pages5 = self.build_search_pages(query5)
            page5 = search_pages5[target_site]
            request5 = Request(page5, callback = self.parseResults)

            request5.meta['query'] = query5
            request5.meta['target_site'] = target_site


            pending_requests.append(request5)

        request.meta['pending_requests'] = pending_requests
        #request.meta['origin_site'] = 
        # product page from source site
        #TODO: clean this URL? for walmart it added something with ?enlargedsearch=True
        request.meta['origin_url'] = response.url

        request.meta['origin_name'] = product_name
        request.meta['origin_model'] = product_model
        request.meta['origin_upc'] = [product_upc]
        request.meta['origin_brand'] = product_brand
        request.meta['origin_manufacturer_code'] = product_manufacturer_code
        if product_price:
            request.meta['origin_price'] = product_price
        if 'origin_bestsellers_rank' in response.meta:
            request.meta['origin_bestsellers_rank'] = response.meta['origin_bestsellers_rank']

        # origin product brand as extracted from name (basically the first word in the name)
        request.meta['origin_brand_extracted'] = product_brand_extracted

        # if self.by_id:
        #     request.meta['origin_id'] = self.extract_walmart_id(response.url)

        #self.target_site = product_brand_extracted
        #TODO: should this be here??
        target_site = product_brand_extracted

        # print "SENDING REQUEST FOR ", product_name, response.url

        yield request


    ####################
    # Site-specific parseURL functions - for extracting attributes origin products (to be matched)
    # return tuples of (product_name, product_model, product_price, product_upc) or the empty string if it was not found

    def parseURL_staples(self, hxs):

        product_name = hxs.select("//h1/text()").extract()[0]

        model_nodes = hxs.select("//p[@class='itemModel']/text()").extract()

        product_model = None
        if model_nodes:
            model_node = model_nodes[0]

            model_node = re.sub("\W", " ", model_node, re.UNICODE)
            m = re.match("(.*)Model:(.*)", model_node.encode("utf-8"), re.UNICODE)
            
            
            if m:
                product_model = m.group(2).strip()

        return (product_name, product_model, None, None, None, None)



    def parseURL_walmart(self, hxs):

        product_name_holder = hxs.select("//h1[contains(@class, 'product-name')]//text()").extract()

        # try for old page version
        if not product_name_holder:
            product_name_holder = hxs.select("//h1[@class='productTitle']//text()").extract()

        if product_name_holder:
            product_name = "".join(product_name_holder).strip()
        else:
            product_name = None

        product_price_node = hxs.select("//meta[@itemprop='price']/@content").extract()
        # remove currency and , (e.g. 1,000)
        if product_price_node:
            product_price = float(re.sub("[\$,]", "", product_price_node[0]))
        else:
            product_price = None

        # # Not relevant anymore:
        # # TODO: figure out what this list of prices contained
        # # get integer part of product price
        # try for old page version

        if not product_price_node:
            product_price_big = hxs.select("//span[@class='bigPriceText1']/text()").extract()

            # if there is a range of prices take their average
            if len(product_price_big) > 1:

                # remove $ and .
                product_price_min = re.sub("[\$\.,]", "", product_price_big[0])
                product_price_max = re.sub("[\$\.,]", "", product_price_big[-1])

                #TODO: check if they're ints?
                product_price_big = (int(product_price_min) + int(product_price_max))/2.0

            elif product_price_big:
                product_price_big = int(re.sub("[\$\.,]", "", product_price_big[0]))

            # get fractional part of price
            #TODO - not that important

            if product_price_big:
                product_price = product_price_big
            else:
                product_price = None


        product_model_holder = hxs.select("//div[@class='specs-table']/table//td[contains(text(),'Model')]/following-sibling::*/text()").extract()

        # try for old page version
        if not product_model_holder:
            product_model_holder = hxs.select("//td[contains(text(),'Model')]/following-sibling::*/text()").extract()

        if product_model_holder:
            product_model = product_model_holder[0].strip()
        else:
            product_model = None

        upc = None
        product_upc_holder = hxs.select("//meta[@itemprop='productID']/@content").extract()
        if product_upc_holder:
            upc = product_upc_holder[0].strip()

        brand_holder = hxs.select("//meta[@itemprop='brand']/@content | //span[@itemprop='brand']/text()").extract()
        if brand_holder:
            product_brand = brand_holder[0]
        else:
            product_brand = None

        return (product_name, product_model, product_price, upc, None, product_brand)

    def parseURL_wayfair(self, hxs):

        product_name_holder = hxs.select("//span[@class='title_name']/text()").extract()

        if product_name_holder:
            product_name = product_name_holder[0].strip()
        else:
            product_name = None

        product_price_node = hxs.select("//span[contains(@class,'product_price')]//text()").extract()
        product_price_raw = "".join(product_price_node)
        # remove currency and , (e.g. 1,000)
        if product_price_node:
            product_price = float(re.sub("[\$,]", "", product_price_raw))
        else:
            product_price = None

        brand_holder = hxs.select("//span[@class='manu_name']/a/text()").extract()
        if brand_holder:
            product_brand = brand_holder[0].strip()
        else:
            product_brand = None

        return (product_name, None, product_price, None, None, product_brand)

#TODO: for the sites below, complete with missing logic, for not returning empty elements in manufacturer spider
    def parseURL_newegg(self, hxs):

        product_name_holder = hxs.select("//span[@itemprop='name']/text()").extract()
        if product_name_holder:
            product_name = product_name_holder[0].strip()
        else:
            product_name = None

        # else:
        #     sys.stderr.write("Broken product page link (can't find item title): " + response.url + "\n")
        #     item = SearchItem()
        #     #item['origin_site'] = site
        #     item['origin_url'] = response.url
        #     yield item
        #     return
        product_model_holder = hxs.select("//dt[text()='Model']/following-sibling::*/text()").extract()
        if product_model_holder:
            product_model = product_model_holder[0]
        else:
            product_model = None

        return (product_name, product_model, None, None, None, None)

    #TODO: add price info? product model? brand?
    def parseURL_boots(self, hxs):
        product_name_holder = hxs.select("//div[@class='pd_productName']/h2/span[@itemprop='name']/text()").extract()

        if product_name_holder:
            product_name = product_name_holder[0]
        else:
            product_name = None

        return (product_name, None, None, None)

    #TODO: add price info? product model? brand?
    def parseURL_ocado(self, hxs):
        # extract all text in this node, including product name and quantity and concatenate it to one string
        product_name = " ".join(map(lambda x: x.strip(), hxs.select("//h1[@class='productTitle']//text()").extract()))
        # if it's the empty string, set it to None
        if not product_name:
            product_name = None

        return (product_name, None, None, None, None, None)

    #TODO: add price info? product model? brand
    def parseURL_tesco(self, hxs):
        product_name_holder = hxs.select("//h1[@class='page-title']/text()").extract()

        if product_name_holder:
            product_name = product_name_holder[0].strip()
        else:
            product_name_holder = None

        return (product_name, None, None, None, None, None)

    def parseURL_amazon(self, hxs):
        # works for amazon.com and amazon.co.uk
        product_name = product_model = price = None

        product_name_node = hxs.select('//h1[@id="title"]/span[@id="productTitle"]/text()').extract()
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

        # extract product model number
        model_number_holder = hxs.select("""//tr[@class='item-model-number']/td[@class='value']/text() |
         //li/b/text()[normalize-space()='Item model number:']/parent::node()/parent::node()/text()""").extract()
        if model_number_holder:
            model_number = model_number_holder[0].strip()
        # if no product model explicitly on the page, try to extract it from name
        else:
            # TODO: do I try this here or is it tried somewhere down the line again?
            if product_name:
                product_model_extracted = ProcessText.extract_model_from_name(product_name)
                if product_model_extracted:
                    model_number = product_model_extracted

        brand_holder = hxs.select("//div[@id='brandByline_feature_div']//a/text() | //a[@id='brand']/text()").extract()
        if brand_holder:
            brand = brand_holder[0]
        else:
            brand = None
            #sys.stderr.write("Didn't find product brand: " + response.url + "\n")

        # extract price
        #! extracting list price and not discount price when discounts available?
        # TODO: test. it extracts more than one price
        price_holder = hxs.select("//span[contains(@id,'priceblock')]/text() | //span[@class='a-color-price']/text() " + \
            "| //span[@class='listprice']/text() | //span[@id='actualPriceValue']/text() | //b[@class='priceLarge']/text() | //span[@class='price']/text()").extract()

        # if we can't find it like above try other things:
        if not price_holder:
            # prefer new prices to used ones
            price_holder = hxs.select("//span[contains(@class, 'olp-new')]//text()[contains(.,'$')]").extract()
        if price_holder:
            product_target_price = price_holder[0].strip()
            # remove commas separating orders of magnitude (ex 2,000)
            product_target_price = re.sub(",","",product_target_price)
            m = re.match("(\$|\xa3)([0-9]+\.?[0-9]*)", product_target_price)
            if m:
                price = float(m.group(2))
                currency = m.group(1)
                if currency != "$":
                    price = Utils.convert_to_dollars(price, currency)
            else:
                self.log("Didn't match product price: " + product_target_price + " (" + str(product_name) + ")\n", level=log.WARNING)

        else:
            self.log("Didn't find product price: (" + str(product_name) + ")\n", level=log.INFO)

        return (product_name, product_model, price, None, None, brand)

    def parseURL_target(self, hxs):
        product_name_holder = hxs.select("//h2[@class='product-name item']/span[@itemprop='name']/text()").extract()

        if product_name_holder:
            product_name = product_name_holder[0].strip()
        else:
            product_name = None

        price_holder = hxs.select("//span[@class='offerPrice']/text()").extract()

        price = None
        if price_holder:
            product_target_price = price_holder[0].strip()
            # remove commas separating orders of magnitude (ex 2,000)
            product_target_price = re.sub(",","",product_target_price)
            m = re.match("\$([0-9]+\.?[0-9]*)", product_target_price)
            if m:
                price = float(m.group(1))
            else:
                sys.stderr.write("Didn't match product price: " + product_target_price + "\n")

        # as source site, we are only interested in the UPC, not the DPCI.
        # We won't be searching on other sites by DPCI.
        upc = None

        upc_node = hxs.select("//meta[@property='og:upc']/@content").extract()
        if upc_node:
            upc = upc_node[0]

        return (product_name, None, price, upc, None, None)


    def parseURL_maplin(self, hxs):
        product_name_holder = hxs.select("//h1[@itemprop='name']/text()").extract()

        if product_name_holder:
            product_name = product_name_holder[0].strip()
        else:
            product_name = None

        price_holder = hxs.select("//meta[@itemprop='price']/@content").extract()

        price = None
        if price_holder:
            product_target_price = price_holder[0].strip()
            if product_target_price:
                # remove commas separating orders of magnitude (ex 2,000)
                product_target_price = re.sub(",","",product_target_price)
                price = float(product_target_price)

                try:
                    currency = hxs.select("//meta[@itemprop='priceCurrency']/@content").extract()[0].strip()
                    if currency == 'GBP':
                        # convert to dollars
                        price = Utils.convert_to_dollars(price, u'\xa3')
                except Exception, e:
                    self.log("Error extracting currency: " + str(e), level=log.DEBUG)

        upc = None

        try:
            product_code = hxs.select("//span[@itemprop='sku']/text()").extract()[0]
        except Exception:
            self.log("No code for product " + str(product_name), level=log.WARNING)
            product_code = None

        return (product_name, None, price, upc, product_code, None)


    # accumulate results for each (sending the pending requests and the partial results as metadata),
    # and lastly select the best result by selecting the best match between the original product's name and the result products' names
    def reduceResults(self, response):

        # print "IN REDUCE RESULTS"

        items = response.meta['items']
        #site = response.meta['origin_site']

        #TODO: do we still need this?
        if 'parsed' not in response.meta:

            # pass to specific prase results function (in derived class)
            return self.parseResults(response)

        else:
            del response.meta['parsed']


        ## print stuff
        if 'origin_upc' not in response.meta:
            origin_upc = ''
        else:
            origin_upc = str(response.meta['origin_upc'])
        if 'origin_manufacturer_code' not in response.meta:
            origin_manufacturer_code = ''
        else:
            origin_manufacturer_code = str(response.meta['origin_manufacturer_code'])
        origin_brand = ''
        if 'origin_brand' in response.meta:
            if response.meta['origin_brand']:
                origin_brand = response.meta['origin_brand']
        self.log("PRODUCT: " + response.meta['origin_name'].decode("utf-8") + " MODEL: " + response.meta['origin_model'].decode("utf-8") +\
         " UPC: " + origin_upc.decode("utf-8") + " MANUFACTURER_CODE: " + origin_manufacturer_code.decode("utf-8") + \
         " BRAND: " + origin_brand.decode("utf-8"), level=log.DEBUG)
        self.log( "QUERY: " + response.meta['query'], level=log.DEBUG)
        self.log( "MATCHES: ", level=log.DEBUG)
        for item in items:
            try:
                self.log( item['product_name'].decode("utf-8"), level=log.DEBUG)
            except UnicodeEncodeError, e:
                self.log( item['product_name'], level=log.DEBUG)

        self.log( '\n', level=log.DEBUG)


        # if there is a pending request (current request used product model, and pending request is to use product name),
        # continue with that one and send current results to it as metadata
        if 'pending_requests' in response.meta:
            # yield first request in queue and send the other ones as metadata
            pending_requests = response.meta['pending_requests']

            if pending_requests:
                # print "PENDING REQUESTS FOR", response.meta['origin_url'], response.meta['origin_name']
                request = pending_requests[0]

                # update pending requests
                request.meta['pending_requests'] = pending_requests[1:]

                request.meta['items'] = items

                #request.meta['origin_site'] = response.meta['origin_site']
                # product page from source site
                request.meta['origin_url'] = response.meta['origin_url']
                request.meta['origin_name'] = response.meta['origin_name']
                request.meta['origin_model'] = response.meta['origin_model']
                if 'origin_price' in response.meta:
                    request.meta['origin_price'] = response.meta['origin_price']
                request.meta['origin_brand_extracted'] = response.meta['origin_brand_extracted']
                if 'origin_upc' in response.meta:
                    request.meta['origin_upc'] = response.meta['origin_upc']
                if 'origin_brand' in response.meta:
                    request.meta['origin_brand'] = response.meta['origin_brand']
                if 'threshold' in response.meta:
                    request.meta['threshold'] = response.meta['threshold']
                if 'origin_manufacturer_code' in response.meta:
                    request.meta['origin_manufacturer_code'] = response.meta['origin_manufacturer_code']
                if 'origin_bestsellers_rank' in response.meta:
                    request.meta['origin_bestsellers_rank'] = response.meta['origin_bestsellers_rank']

                # if 'origin_id' in response.meta:
                #     request.meta['origin_id'] = response.meta['origin_id']
                #     assert self.by_id
                # else:
                #     assert not self.by_id

                # used for result product URLs
                if 'search_results' in response.meta:
                    request.meta['search_results'] = response.meta['search_results']

                return request

            # if there are no more pending requests, use cumulated items to find best match and send it as a result
            else:

                # print "DONE FOR ", response.meta['origin_url'], response.meta['origin_name']

                best_match = None

                if items:

                    # from all results, select the product whose name is most similar with the original product's name
                    # if there was a specific threshold set in request, use that, otherwise, use the class variable
                    if 'threshold' in response.meta:
                        threshold = response.meta['threshold']
                    else:
                        threshold = self.threshold

                    if 'origin_price' in response.meta:
                        product_price = response.meta['origin_price']
                        ## print "PRICE:", product_price
                    else:
                        product_price = None

                    if 'origin_upc' in response.meta:
                        origin_upc = response.meta['origin_upc']
                    else:
                        origin_upc = None

                    if 'origin_brand' in response.meta:
                        origin_brand = response.meta['origin_brand']
                    else:
                        origin_brand = None

                    if 'origin_manufacturer_code' in response.meta:
                        origin_manufacturer_code = response.meta['origin_manufacturer_code']
                    else:
                        origin_manufacturer_code = None

                        ## print "NO PRICE"
                    best_match = ProcessText.similar(response.meta['origin_name'], response.meta['origin_model'],\
                     product_price, origin_upc, origin_manufacturer_code, origin_brand, items, threshold)

                    # #self.log( "ALL MATCHES: ", level=log.WARNING)                    
                    # for item in items:
                    #     ## print item['product_name'].encode("utf-8")
                    # ## print '\n'

                self.log( "FINAL: " + str(best_match), level=log.WARNING)
                self.log( "\n----------------------------------------------\n", level=log.WARNING)

                if not best_match:
                    # if there are no results but the option was to include original product URL, create an item with just that
                    # output item if match not found for either output type
                    #if self.output == 2:
                    item = SearchItem()
                    #item['origin_site'] = site
                    
                    item['origin_url'] = response.meta['origin_url']
                    item['origin_name'] = response.meta['origin_name']
                    if 'origin_model' in response.meta:
                        item['origin_model'] = response.meta['origin_model']

                    if 'origin_upc' in response.meta:
                        item['origin_upc'] = response.meta['origin_upc']
                    if 'origin_manufacturer_code' in response.meta:
                        item['origin_manufacturer_code'] = response.meta['origin_manufacturer_code']
                    if 'origin_bestsellers_rank' in response.meta:
                        item['origin_bestsellers_rank'] = response.meta['origin_bestsellers_rank']
                    if 'origin_brand' in response.meta:
                        item['origin_brand'] = response.meta['origin_brand']

                    # if 'origin_id' in response.meta:
                    #     item['origin_id'] = response.meta['origin_id']
                    #     assert self.by_id
                    # else:
                    #     assert not self.by_id
                    return [item]

                return best_match

        else:
            # output item if match not found
            item = SearchItem()
            #item['origin_site'] = site

            # print "DONE FOR ", response.meta['origin_name']
            
            item['origin_url'] = response.meta['origin_url']
            item['origin_name'] = response.meta['origin_name']

            # if 'origin_id' in response.meta:
            #     item['origin_id'] = response.meta['origin_id']
            #     assert self.by_id
            # else:
            #     assert not self.by_id

            #TODO: uncomment below - it should not have been in if/else branch!

            self.log( "FINAL: " + str(item), level=log.WARNING)
            self.log( "\n----------------------------------------------\n", level=log.WARNING)

            return [item]

    def extract_walmart_id(self, url):
        m = re.match(".*/ip/([0-9]+)", url)
        if m:
            return m.group(1)