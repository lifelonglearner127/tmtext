from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Walmart.items import CategoryItem
from Walmart.items import ProductItem
from scrapy.http import Request
import sys
import re
import datetime

from nltk.util import ngrams
from nltk.corpus import stopwords

################################
# Run with 
#
# scrapy crawl walmart
#
################################

# scrape sitemap and extract categories
class WalmartSpider(BaseSpider):
    name = "walmart"
    allowed_domains = ["walmart.com"]
    start_urls = [
        "http://www.walmart.com/cp/All-Departments/121828",
    ]
    root_url = "http://www.walmart.com"

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        links = hxs.select("//div[@class='MidContainer']/div[3]//a[@class='NavM']")
        parent_links = hxs.select("//div[@class='MidContainer']/div[3]//a[@class='NavXLBold']")

        for link in links:
            item = CategoryItem()

            # search for the category's parent
            parents = []

            # select the preceding siblings that are a category title (have a child that is an a tag with a certain class)
            parents = link.select('parent::node()').select('preceding-sibling::node()').select('child::a[@class=\'NavXLBold\']')

            # if we found such siblings, get the last one to be the parent
            if parents:
                item['parent_text'] = parents[-1].select('text()').extract()[0]
                item['parent_url'] = parents[-1].select('@href').extract()[0]

                item['parent_url'] = Utils.add_domain(item['parent_url'], self.root_url)

            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            # add domain if relative URL
            item['url'] = Utils.add_domain(item['url'], self.root_url)

            item['level'] = 0

            # to avoid duplicates, only extract highest level categories in this function (so don't return if level 0)
            #yield item

            
            # #TODO: check this
            # item['nr_products'] = -1
            # yield item
            #yield Request(item['url'], callback = self.parseCategory, meta = {'item' : item})

        for link in parent_links:
            item = CategoryItem()

            item['text'] = link.select('text()').extract()[0]
            item['url'] = link.select('@href').extract()[0]

            # add domain if relative URL
            item['url'] = Utils.add_domain(item['url'], self.root_url)

            item['level'] = 1

            #yield item

            # send category page to parseCategory function to extract description and number of products and add them to the item
            yield Request(item['url'], callback = self.parseCategory, meta = {'item' : item})

    # parse category page and extract description and number of products
    def parseCategory(self, response):
        hxs = HtmlXPathSelector(response)
        item = response.meta['item']

        # Extract description title, text, wordcount, and keyword density (if any)

        description_holder = hxs.select("//div[@id='detailedPageDescriptionCopyBlock']")

        # try to find description title in <b> tag in the holder;
        # if it's not find, try to find it in the first <p> if the description
        # if fund there, exclude it from the description body
        description_title = description_holder.select(".//b/text()").extract()
        if description_title:
            item['description_title'] = description_title[0]

        description_texts = description_holder.select("./div[position()<2]//p/text()[not(ancestor::b)] | ./p/text()[not(ancestor::b)]").extract()

        # if the list is not empty and contains at least one non-whitespace item
        if description_texts and reduce(lambda x,y: x or y, [line.strip() for line in description_texts]):

            # replace all whitespace with one space, strip, and remove empty texts; then join them
            item['description_text'] = " ".join([re.sub("\s+"," ", description_text.strip()) for description_text in description_texts if description_text.strip()])

        if 'description_text' in item:
            tokenized = Utils.normalize_text(item['description_text'])
            item['description_wc'] = len(tokenized)

            # sometimes here there is no description title because of malformed html
            # if we can find description text but not description title, title is probably malformed - get first text in div instead
            if 'description_title' not in item:
                desc_texts = description_holder.select("./text()").extract()
                desc_texts = [text for text in desc_texts if text.strip()]
                item['description_title'] = desc_texts[0]

            (item['keyword_count'], item['keyword_density']) = Utils.phrases_freq(item['description_title'], item['description_text'])

        else:
            item['description_wc'] = 0



        # find if there is a wc field on the page
        wc_field = hxs.select("//div[@class='mrl mod-toggleItemCount']/span/text()").extract()
        if wc_field:
            m = re.match("([0-9]+) Results", wc_field[0])
            if m:
                item['nr_products'] = int(m.group(1))
            yield item
        # # find if there are any products on this page
        # product_holders = hxs.select("//a[@class='prodLink ListItemLink']").extract()
        # if product_holders:
        #     # parse every page and collect total number of products
        #     #print "URL ", response.url, " HAS PRODUCTS"

        #     # item['nr_products'] = 1
        #     #yield item
        #     yield Request(response.url, callback = self.parsePage, meta = {'item' : item})

        else:
            # look for links to subcategory pages in menu
            subcategories_links = hxs.select("//div[@class='G1001 LeftNavRM']/div[@class='yuimenuitemlabel browseInOuter leftnav-item leftnav-depth-1']/a[@class='browseIn']")

            if not subcategories_links:
            # # if we haven't found them, try to find subcategories in menu on the left under a "Shop by Category" header
            #     subcategories_links = hxs.select("//div[@class='MainCopy']/div[@class='Header' and text()='\nShop by Category']/following-sibling::node()//a")

            # if we haven't found them, try to find subcategories in menu on the left - get almost anything
            #TODO: because of this there are some problems with the level, there are -6 which could be -2 (extracting same stuff from all sorts of related cats)
                subcategories_links = hxs.select("//div[@class='MainCopy']/div[@class='Header' and text()!='\nRelated Categories' and text()!='\nSpecial Offers' and text()!='\nView Top Registry Items' and text()!='\nFeatured Content']/following-sibling::node()//a")
            
            # if we found them, create new category for each and parse it from the beginning
            if subcategories_links:

                # new categories are subcategories of current one - calculate and store their level
                parent_item = item
                level = parent_item['level'] - 1

                #print "URL ", response.url, " CALLING PARSEPAGE"
                for subcategory in subcategories_links:

                    item = CategoryItem()
                    item['text'] = subcategory.select("text()").extract()[0].strip()

                    # # take care of unicode
                    # item['text'] = item['text'].encode("utf-8", errors=ignore)

                    item['url'] = Utils.add_domain(subcategory.select("@href").extract()[0], self.root_url)
                    item['level'] = level

                    #item['nr_products'] = 1
                    #parent_item['nr_products'] = 1

                    # temporary
                    item['parent_text'] = parent_item['text']
                    item['parent_url'] = parent_item['url']

                    # #TODO: i don't even know this
                    # item['description_wc'] = 0
                    # yield item
                    yield Request(item['url'], callback = self.parseCategory, meta = {'item' : item})

                # idea for sending parent and collecting nr products. send all of these subcats as a list in meta, pass it on, when list becomes empty, yield the parent
                yield parent_item
                    #yield Request(item['url'], callback = self.parsePage, meta = {'item' : item, 'parent_item' : parent_item})




            # if we can't find either products on the page or subcategory links
            else:
                #print "URL", response.url, " NO SUBCATs"
                #item['nr_products'] = 0
                yield item


    # parse a product page and calculate number of products, accumulate them from all pages
    def parsePage(self, response):

        #print "IN PARSEPAGE"
        hxs = HtmlXPathSelector(response)
        item = response.meta['item']

        if 'parent_item' in response.meta:
            parent_item = response.meta['parent_item']
            item['parent_text'] = parent_item['text']
            item['parent_url'] = parent_item['url']
            if 'parent_text' in parent_item:
                item['grandparent_text'] = parent_item['parent_text']
                item['grandparent_url'] = parent_item['parent_url']
            if 'nr_products' not in parent_item:
                parent_nr_products = 0
            else:
                parent_nr_products = parent_item['nr_products']

        # initialize product URL list
        if 'products' not in response.meta:
            products = []
        else:
            products = response.meta['products']

        # # if this is the first page, initialize number of products
        # if 'nr_products' not in item:
        #     old_nr_products = 0
        # else:
        #     old_nr_products = item['nr_products']

        # find number of products on this page
        product_links = hxs.select("//a[@class='prodLink ListItemLink']/@href").extract()

        # gather all products in this (sub)category
        products += product_links

        #this_nr_products = len(product_links)

        #item['nr_products'] = old_nr_products + this_nr_products
        # if 'parent_item' in response.meta:
        #     parent_item['nr_products'] = parent_nr_products + item['nr_products']
        # find URL to next page, parse it as well
        next_page = hxs.select("//a[@class='link-pageNum' and text()=' Next ']/@href").extract()
        if next_page:
            page_url = Utils.add_domain(next_page[0], self.root_url)
            request = Request(url = page_url, callback = self.parsePage, meta = {'item' : item, 'products' : products})
            if 'parent_item' in response.meta:
                request.meta['parent_item'] = parent_item
            yield request

        # if no next page, return current results; and return parent category page
        else:

            item['nr_products'] = len(set(products))
            yield item

            # #TODO: this is not good - when should we yield parent category?
            # if 'parent_item' in response.meta:
            #     yield parent_item



class Utils():

    # append domain name in front of relative URL if it's missing
    @staticmethod
    def add_domain(url, root_url):
        if not re.match("http:.*", url):
            url = root_url + url
        return url

    # find frequency of phrases from a text in another text, and density (% of length of text)
    # (will be used with description title and description text)
    @staticmethod
    def phrases_freq(phrases_from, freq_in):
        #TODO: stem?

        stopset = set(stopwords.words('english'))
        ngrams_list = []
        phrases_from_tokens = Utils.normalize_text(phrases_from)
        freq_in = " ".join(Utils.normalize_text(freq_in))
        for l in range(1, len(phrases_from_tokens) + 1):
            for ngram in ngrams(phrases_from_tokens, l):
                # if it doesn't contain only stopwords
                
                # if it doesn't contain any stopwords in the beginning or end
                if ngram[0] not in stopset and ngram[-1] not in stopset:
                    # append as string to the ngram list
                    ngrams_list.append(" ".join(ngram))

        freqs = {}
        for ngram in ngrams_list:
            freqs[ngram] = freq_in.count(ngram)

        # eliminate smaller phrases that are contained in larger ones
        for k in freqs:
            for k2 in freqs:
                if k in k2 and k != k2 and freqs[k] <= freqs[k2]:
                    freqs[k] = 0

        # eliminate zeros
        freqs = dict((k,v) for (k,v) in freqs.iteritems() if v!=0)

        len_text = len(Utils.normalize_text(freq_in))
        density = {}
        for ngram in freqs:
            len_ngram = len(Utils.normalize_text(ngram))
            density[ngram] = format((float(len_ngram)*freqs[ngram])/len_text*100, ".1f")

        return (freqs, density)


    # normalize text to lowercase and eliminate non-word characters.
    # return normalized string
    @staticmethod
    def normalize_text(text):
        # tokenize
        tokens = filter(None, re.split("[^\w\.,]+", text))

        # lowercase and eliminate non-character words. eliminating punctuation marks will make so that matches can cross sentence boundaries & stuff
        #tokens = [re.sub("[^\w,\.?!:]", "", token.lower()) for token in tokens]
        tokens = [re.sub("[^\w]", "", token.lower()) for token in tokens]

        #return " ".join(tokens)
        return tokens

# scrape bestsellers lists and extract products
class BestsellerSpider(BaseSpider):
    name = "bestseller"
    allowed_domains = ["walmart.com"]
    start_urls = [
        "http://www.walmart.com/cp/Best-Sellers/1095979",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        # select list of bestsellers departments
        dept_list = hxs.select("//div[@class='MainCopy']")[1]

        # select departments
        departments = dept_list.select("ul/li/a")

        for department in departments:

            # extract departments and pass them to parseDepartment function to parse list for each of them
            dept = department.select("text()").extract()[0]
            dept_url = department.select("@href").extract()[0]

            url = self.root_url + dept_url
            request = Request(url, callback = self.parseDepartment)
            request.meta['department'] = dept

            yield request

    def parseDepartment(self, response):

        # some of the products are duplicates across departments, they will only appear once on the final list

        hxs = HtmlXPathSelector(response)

        department = response.meta['department']

        #TODO: what if there is pagination? haven't encountered it so far

        products = hxs.select("//div[@class='prodInfo']")

        # counter to keep track of product's rank
        rank = 0

        for product in products:
            item = ProductItem()

            rank += 1
            item['rank'] = str(rank)

            product_link = product.select("div[@class='prodInfoBox']/a[@class='prodLink ListItemLink']")

            product_name = product_link.select("text()").extract()
            product_url = product_link.select("@href").extract()

            if product_name:
                item['list_name'] = product_name[0]

            if product_url:
                item['url'] = self.root_url + product_url[0]
            else:
                # if there's no url move on to the next product
                continue

            item['department'] = department

            #TODO: some of the products have the "From" prefix before the price, should I include that?
            price_div = product.select(".//div[@class='camelPrice'] | .//span[@class='camelPrice']")
            price1 = price_div.select("span[@class='bigPriceText2']/text()").extract()
            price2 = price_div.select("span[@class='smallPriceText2']/text()").extract()

            if price1 and price2:
                item['price'] = price1[0] + price2[0]

            #TODO: include out of stock products? :
            else:
                price1 = price_div.select("span[@class='bigPriceTextOutStock2']/text()").extract()
                price2 = price_div.select("span[@class='smallPriceTextOutStock2']/text()").extract()

                if price1 and price2:
                    item['price'] = price1[0] + price2[0]

            #TODO: are list prices always retrieved correctly?
            listprice = product.select(".//div[@class='PriceMLtgry']/text").extract()
            if listprice:
                item['listprice'] = listprice[0]

            item['bspage_url'] = response.url

            # pass the item to the parseProduct method
            request = Request(item['url'], callback = self.parseProduct)
            request.meta['item'] = item

            yield request

    def parseProduct(self, response):
        hxs = HtmlXPathSelector(response)

        item = response.meta['item']

        product_name = hxs.select("//h1[@class='productTitle']/text()").extract()[0]
        item['product_name'] = product_name

        page_title = hxs.select("//title/text()").extract()[0]

        # remove "Walmart.com" suffix from page title
        m = re.match("(.*) [:-] Walmart\.com", page_title, re.UNICODE)
        if m:
            page_title = m.group(1).strip()


        # there are other more complicated formul as as well, we're not removing them anymore, the product name is enough on this case
        # "Purchase the ... for a low price at Walmart.com"
        # m1 = re.match("(.*) for less at Walmart\.com\. Save money\. Live better\.", page_title, re.UNICODE)
        # if m1:
        #     page_title = m1.group(1).strip()

        # m2 = re.match("(.*) at an always low price from Walmart\.com\. Save money\. Live better\.", page_title, re.UNICODE)
        # if m2:
        #     page_title = m2.group(1).strip()

        # m3 = re.match("(.*) at Walmart\.com\. Save money\. Live better\.", page_title, re.UNICODE)
        # if m3:
        #     page_title = m3.group(1).strip()

        item['page_title'] = page_title

        # add date
        item['date'] = datetime.date.today().isoformat()

        yield item