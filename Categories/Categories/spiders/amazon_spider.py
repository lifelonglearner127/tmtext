from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from Categories.items import CategoryItem
from Categories.items import ProductItem
from scrapy.http import Request, FormRequest
from scrapy.http import Response
import re
import sys
import datetime

from spiders_utils import Utils
from captcha_solver import CaptchaBreakerWrapper

################################
# Run with 
#
# scrapy crawl amazon
#
################################

# crawls sitemap and extracts department and categories names and urls (as well as other info)
class AmazonSpider(BaseSpider):
    name = "amazon"
    allowed_domains = ["amazon.com"]
    start_urls = [
        "http://www.amazon.com/gp/site-directory/ref=sa_menu_top_fullstore"
    ]

    def __init__(self, outfile=None):
        self.outfile = outfile

        # level that is considered to contain departments
        self.DEPARTMENT_LEVEL = 2

        # hardcoded toplevel categories (level 1 and 2) urls to replace/supplement some of the ones found on the sitemap above (point to the same category, but have different page content. they were found manually)
        # reason: they provide more info regarding product count than the ones found on the sitemap
        # keys are categories names as found in the sitemap, values are URLs associated with them, that will replace/supplement the links found on the sitemap
        self.extra_toplevel_categories_urls = {"Baby" : "http://www.amazon.com/s/ref=lp_166835011_ex_n_1?rh=n%3A165796011&bbn=165796011&ie=UTF8&qid=1393338541", \
                                    "Electronics & Computers" : "http://www.amazon.com/s/ref=lp_172659_ex_n_1?rh=n%3A172282&bbn=172282&ie=UTF8&qid=1393338741", \
                                    "Home, Garden & Tools" : "http://www.amazon.com/s/ref=lp_284507_ex_n_1?rh=n%3A1055398&bbn=1055398&ie=UTF8&qid=1393338782",\
                                    "Kindle E-readers & Books" : "http://www.amazon.com/s/ref=lp_154606011_ex_n_1?rh=n%3A133140011&bbn=133140011&ie=UTF8&qid=1395704970", \
                                    "Apps & Games" : "http://www.amazon.com/b/ref=sd_allcat_fire_apps_games?ie=UTF8&node=3427287011", \
                                    "Movies & TV" : "http://www.amazon.com/action-adventure-dvd-bluray/b/ref=MoviesHPBB_Genres_Action?ie=UTF8&node=2650363011&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-left-2&pf_rd_r=0GAWFEZ3EXP8PEYCM6X3&pf_rd_t=101&pf_rd_p=1753817742&pf_rd_i=2625373011", \
                                    "All Beauty" : "http://www.amazon.com/s/ref=lp_11059031_ex_n_1?rh=n%3A3760911&bbn=3760911&ie=UTF8&qid=1395793680",\
                                    "Health, Household & Baby Care" : "http://www.amazon.com/s/ref=lp_6183682011_ex_n_1?rh=n%3A3760901&bbn=3760901&ie=UTF8&qid=1395822180", \
                                    "Tires & Wheels" : "http://www.amazon.com/s/ref=lp_353609011_ex_n_1?rh=n%3A15684181%2Cn%3A%2115690151%2Cn%3A15706571&bbn=15706571&ie=UTF8&qid=1395824546", \
                                    "Motorcycle & Powersports" : "http://www.amazon.com/s/ref=sr_ex_n_1?rh=n%3A15684181%2Cn%3A%2115690151%2Cn%3A346333011&bbn=346333011&ie=UTF8&qid=1395824599"
                                    }


        # flag indicating whether to compute overall product counts in pipelines phase for this spider.
        # if on, 'catid' and 'parent_catid' fields need to be implemented
        self.compute_nrproducts = True

        # counter for department id, will be used to autoincrement department id
        self.department_count = 0
        # counter for category id
        self.catid = 0

        # level to stop crawling (don't extract subcategories below this level)
        self.LEVEL_BARRIER = -2

        # maximum number of retries when presented with captcha form
        self.MAX_CAPTCHA_RETRY = 10


        # dictionarties associating department names with other attributes - to use for setting parent category info for level 1 categories
        # associates department names with their ids
        self.departments_ids = {}
        # associates department names with their urls (will be available only for extra_categories)
        self.department_urls = {}
        # associate department names with their category ids
        self.departments_cat_ids = {}

        # captcha breaker
        self.CB = CaptchaBreakerWrapper()


    # solve the captcha on this page and redirect back to method that sent us here (callback)
    def solve_captcha_and_redirect(self, response, callback):
        hxs = HtmlXPathSelector(response)

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

        # redirect to initial URL
        #return [FormRequest.from_response(response, callback = callback, formdata={'field-keywords' : captcha_text})]
        meta = response.meta
        # decrease count for retry times left. if not set yet, this is first attempt, set it to MAX_CAPTCHA_RETRY
        response.meta['retry_count'] = response.meta['retry_count'] - 1 if 'retry_count' in response.meta else self.MAX_CAPTCHA_RETRY
        return FormRequest.from_response(response, callback = callback, formdata={'field-keywords' : captcha_text}, meta=meta)

    # test if page is form containing captcha
    def has_captcha(self, body):
        return '.images-amazon.com/captcha/' in body


    # check if 2 catgory names are the same
    # does some normalization of the names and compares the words in them
    # to be used for identifying extra_toplevel_categories_urls when they occur in the sitemap
    def is_same_name(self, name1, name2):
        # eliminate non-word characters
        name1 = re.sub("[^a-zA-Z]", " ", name1).lower()
        name2 = re.sub("[^a-zA-Z]", " ", name2).lower()

        name1_words = name1.split()
        name2_words = name2.split()

        return set(name1_words) == set(name2_words)

    # find key in dict using is_same_name as equality function (return key from dict where is_same_name returns true for given target_key)
    def find_matching_key(self, target_key, dictionary):
        for key in dictionary:
            if self.is_same_name(target_key, key):
                return key

        return None

    # start parsing of top level categories extracted from sitemap; pass them to parseCategory
    def parse(self, response):

        hxs = HtmlXPathSelector(response)

        # if there is a captcha to solve, and we haven't exhausted our retries, try to solve it
        if self.has_captcha(response.body) and ('retry_count' not in response.meta or response.meta['retry_count'] > 0):
            yield self.solve_captcha_and_redirect(response, self.parse) # meta of response will contain number of retries left if set
            return

        links_level1 = hxs.select("//div[@id='siteDirectory']//table//a")
        titles_level1 = hxs.select("//div//table//h2")

        # add level 1 categories to items

        # first one is a special category ("Unlimited Instant Videos"), add it separately
        special_item = CategoryItem()
        special_item['text'] = titles_level1[0].select('text()').extract()[0]
        special_item['level'] = 2
        special_item['special'] = 1
        special_item['department_text'] = special_item['text']
        special_item['department_id'] = self.department_count
        self.department_count += 1

        special_item['catid'] = self.catid
        self.catid += 1

        self.departments_ids[special_item['text']] = special_item['department_id']
        self.departments_cat_ids[special_item['text']] = special_item['catid']


        #items.append(special_item)
        yield special_item

        # the rest of the titles are not special
        for title in titles_level1[1:]:
            item = CategoryItem()
            item['text'] = title.select('text()').extract()[0]
            item['level'] = 2
            item['department_text'] = item['text']
            item['department_id'] = self.department_count
            self.department_count += 1

            item['catid'] = self.catid
            self.catid += 1

            self.departments_ids[item['text']] = item['department_id']
            self.departments_cat_ids[item['text']] = item['catid']

            # if item is found among extra_toplevel_categories_urls, add info from that url
            extra_category = self.find_matching_key(item['text'], self.extra_toplevel_categories_urls)
            if extra_category:
                item['url'] = self.extra_toplevel_categories_urls[extra_category]
                item['department_url'] = item['url']
                self.department_urls[item['text']] = item['url']

                # collect number of products from this alternate URL
                yield Request(item['url'], callback = self.extract_nrprods_and_subcats, meta = {'item' : item})

            else:
                yield item

        # add level 1 categories to items
        for link in links_level1:
            item = CategoryItem()
            item['text'] = link.select('text()').extract()[0]
            root_url = "http://www.amazon.com"
            item['url'] = root_url + link.select('@href').extract()[0]
            item['level'] = 1

            parent = link.select("parent::node()/parent::node()/preceding-sibling::node()")
            parent_text = parent.select('text()').extract()

            # category should have a parent (its department) and that parent should have been extracted earlier (above) and put in the ids dictionary, necessary for getting the department id
            assert parent_text
            assert parent_text[0] in self.departments_ids
            if parent_text:
                item['parent_text'] = parent_text[0]
                item['department_text'] = item['parent_text']
                item['department_id'] = self.departments_ids[item['department_text']]
                item['parent_catid'] = self.departments_cat_ids[item['department_text']]
                item['catid'] = self.catid
                self.catid += 1

                # get department url from department_urls, will be availble only for extra_categories
                if item['department_text'] in self.department_urls:
                    assert self.find_matching_key(item['department_text'], self.extra_toplevel_categories_urls)
                    item['department_url'] = self.department_urls[item['department_text']]
                    item['parent_url'] = item['url']

                # if its parent is the special category, mark this one as special too
                if (item['parent_text'] == special_item['text']):
                    item['special'] = 1
                    special = True
                else:
                    special = False

            # department_id = self.department_count
            # self.department_count += 1

            # item['department_text'] = item['text']
            # item['department_url'] = item['url']
            # item['department_id'] = department_id

            yield Request(item['url'], callback = self.parseCategory, meta = {'item' : item})


    # parse category and return item corresponding to it (for categories where URL available - level 2 and lower)
    def parseCategory(self, response):

        # if we are getting blocked by captcha, solve and redirect back here
        # if there is a captcha to solve, and we haven't exhausted our retries, try to solve it
        if self.has_captcha(response.body) and ('retry_count' not in response.meta or response.meta['retry_count'] > 0):
            yield self.solve_captcha_and_redirect(response, self.parseCategory) # meta of response will contain number of retries left if set
            return


        hxs = HtmlXPathSelector(response)

        # extract additional info for received parent and return it
        item = response.meta['item']

        # extract product count if available and not already extracted (in extract_itemcount_and_subcategories, from menu of the left, without crawling the actual url)
        if 'nr_products' not in item:
            prod_count_holder = hxs.select("//h2[@class='resultCount']/span/text()").extract()
            if prod_count_holder:
                prod_count = prod_count_holder[0]
                # extract number
                m = re.match(".*\s*of\s*([0-9,]+)\s*Results\s*", prod_count)
                if m:
                    item['nr_products'] = int(re.sub(",","",m.group(1)))

        # extract description if available
        # only extracts descriptions that contain a h2. is that good?
        desc_holders = hxs.select("//div[@class='unified_widget rcmBody'][descendant::h2][last()]")
        # select the one among these with the most text
        #TODO: another idea: check if the holder has a h2 item
        if desc_holders:
            maxsize = 0
            max_desc_holder = desc_holders[0]
            for desc_holder in desc_holders:
                size = len(" ".join(desc_holder.select(".//text()").extract()))

                if size > maxsize:
                    maxsize = size
                    max_desc_holder = desc_holder
            desc_holder = max_desc_holder
            desc_title = desc_holder.select("h2/text()").extract()
            if desc_title:
                item['description_title'] = desc_title[0].strip()
            
            description_texts = desc_holder.select(".//text()[not(ancestor::h2)]").extract()

            # if the list is not empty and contains at least one non-whitespace item
            # if there is a description title or the description body is large enough
            size_threshold = 50
            if (description_texts and reduce(lambda x,y: x or y, [line.strip() for line in description_texts])):# and \
            #(desc_title or len(" ".join(description_texts.select(".//text()").extract()) > size_threshold)):
                # replace all whitespace with one space, strip, and remove empty texts; then join them
                item['description_text'] = " ".join([re.sub("\s+"," ", description_text.strip()) for description_text in description_texts if description_text.strip()])

                tokenized = Utils.normalize_text(item['description_text'])
                item['description_wc'] = len(tokenized)

                if desc_title:
                    (item['keyword_count'], item['keyword_density']) = Utils.phrases_freq(item['description_title'], item['description_text'])
            
            else:
                item['description_wc'] = 0

        else:
            item['description_wc'] = 0


        # if item is found among extra_toplevel_categories_urls, and no product count was found, add info from that url
        extra_category = self.find_matching_key(item['text'], self.extra_toplevel_categories_urls)

        
        # crawl lower level categories
        if item['level'] > self.LEVEL_BARRIER:
            if extra_category:
            
                # collect number of products from this alternate URL
                # this will also extract subcategories and their count
                yield Request(self.extra_toplevel_categories_urls[extra_category], callback = self.extract_nrprods_and_subcats, meta = {'item' : item})

            else:
                # extract subcategories and their count for category even if not in extra_...
                yield Request(item['url'], callback = self.extract_nrprods_and_subcats, meta = {'item' : item})
        else:
            yield item


    # extract item count for a certain category, then yield item received in meta
    # also extract and yield subcategories (and their subcategories, down to a certain level)
    # use menu on left side of the page on the category page
    # will mainly be used for categories in extra_toplevel_categories_urls

    # after subcategories extracted, send them to parseCategory to extract description as well
    # Obs: it's not exhaustive. if page doesn't match what it expects, it gives up
    def extract_nrprods_and_subcats(self, response):

        # if there is a captcha to solve, and we haven't exhausted our retries, try to solve it
        if self.has_captcha(response.body) and ('retry_count' not in response.meta or response.meta['retry_count'] > 0):
            yield self.solve_captcha_and_redirect(response, self.extract_nrprods_and_subcats) # meta of response will contain number of retries left if set
            return

        hxs = HtmlXPathSelector(response)

        item = response.meta['item']

        # extract nr_products if not already extracted. necessary for extra_categories
        if 'nr_products' not in item:
            prod_count_holder = hxs.select("//h2[@class='resultCount']/span/text()").extract()
            if prod_count_holder:
                #print "DIDN'T HAVE PRODUCT COUNT", response.url
                prod_count = prod_count_holder[0]
                # extract number
                m = re.match(".*\s*of\s*([0-9,]+)\s*Results\s*", prod_count)
                if m:
                    item['nr_products'] = int(re.sub(",","",m.group(1)))

        yield item

        parent_item = item

        # extract subcategories, if level is above barrier
        # currently extracting subcategories for categories on any level, for level 2 this may cause duplicates (we already extract level 1)
        # extract subcategories from first menu on the left, assume this is the subcategories menu
        #TODO: test or make more robust

        if item['level'] > self.LEVEL_BARRIER:
            # TODO: make it work for Kids' Clothing as well
            subcategories = hxs.select("//h2[contains(text(),'Department')]/following-sibling::ul[1]/li/a")
            for subcategory in subcategories:
                # if we have a subcategory URL and product count with the expected format extract it, otherwise move on
                if not subcategory.select("span[@class='refinementLink']"):
                    continue
                subcategory_url = Utils.add_domain(subcategory.select("@href").extract()[0], "http://www.amazon.com")
                subcategory_text = subcategory.select("span[@class='refinementLink']//text()").extract()[0].strip()
                # extract product count, clean it of commas and parantheses
                subcategory_prodcount_holder = subcategory.select("span[@class='narrowValue']/text()").extract()

                # if there's also product count available in the menu, extract it
                if subcategory_prodcount_holder:
                    subcategory_prodcount = subcategory_prodcount_holder[0].replace(";nbsp&"," ").strip()

                    m = re.match("\(([0-9,]+)\)", subcategory_prodcount)
                    if m:
                        subcategory_prodcount = m.group(1).replace(",","")
                else:
                    subcategory_prodcount = None

                

                item = CategoryItem()
                item['url'] = subcategory_url
                item['text'] = subcategory_text
                item['catid'] = self.catid
                self.catid += 1

                if subcategory_prodcount:
                    item['nr_products'] = int(subcategory_prodcount)

                item['parent_text'] = parent_item['text']
                item['parent_url'] = parent_item['url']
                item['parent_catid'] = parent_item['catid']

                # considering departments to be level 2 categories (top level) - so every category must have a department text
                assert 'department_text' in parent_item
                if 'department_text' in parent_item:
                    item['department_text'] = parent_item['department_text']
                    #item['department_url'] = parent_item['department_url']
                    item['department_id'] = parent_item['department_id']

                # only level 2 categories in extra_categories have department_url
                if 'department_url' in parent_item:
                    item['department_url'] = parent_item['department_url']
                else:
                    assert not self.find_matching_key(item['department_text'], self.extra_toplevel_categories_urls)

                # else:
                #     # the parent must be a level 2 category - so this will be considered department
                #     assert parent_item['level'] == 2
                #     item['department_text'] = item['text']
                #     #item['department_url'] = item['url']
                #     item['department_id'] = self.department_count
                #     self.department_count += 1

                item['level'] = parent_item['level'] - 1

                # # no description extracted
                # item['description_wc'] = 0


                # send to parseCategory to extract description as well
                yield Request(item['url'], callback = self.parseCategory, meta = {'item' : item})


                # # extract their subcategories as well (needed for "Home Improvement")
                # # stop at a certain level
                # if item['level'] > self.LEVEL_BARRIER:
                #     #yield Request(item['url'], callback = self.extract_nrprods_and_subcats, meta = {'item' : item})
                #     yield Request(item['url'], callback = self.parseCategory, meta = {'item' : item})

                # else:
                #     # stop here, yield the item
                #     yield item




    #############################################
    # Trying to automatically extract better (that have product count) category landing pages through some twisted naviation - leave for later. replaced with some hardcoded pages in extra_toplevel_categories_urls
    #     # if no product count try to find the correct landing page for this category:
    #     # try to find a link to an "All ..." page (will point to a subcategory of this one), then on that page try to find the link to the department page (so an alternate link for this subcategory)
    #     if not prod_count_holder and item['level']==1:
    #         # find a subcategory link
    #         subcategory = hxs.select("//p[@class='seeMore']/a/@href").extract()
    #         if subcategory:
    #             print "FOUND SUBCATEGORY OF", response.url, ": ", subcategory[0]
    #             yield Request(url = Utils.add_domain(subcategory[0], "http://www.amazon.com"), callback = self.extractCatURL, meta = response.meta)
    #         else:
    #             print "NO SUBCATEGORY", response.url

    #         #yield Request(callback )

    # # try to extract better category page, with product count available (linked to from a subcategory)
    # # receives subcategory page URL and tries to find link to top level category
    # def extractCatURL(self, response):
    #     hxs = HtmlXPathSelector(response)

    #     # find "Department" in submenu and get link below it - will link to top level category
    #     department_link = hxs.select("//h2[contains(text(),'Department')]/following-sibling::ul[1]/li/a")
    #     if department_link:
    #         department_url = Utils.add_domain(department_link.select("@href").extract()[0], "http://www.amazon.com")
    #         department_text = department_link.select("./text() | ./span/text()").re("[a-zA-Z ]+")[0]

    #         print "YES DEPARTMENT LINK", response.url, department_text

    #         yield Request(department_url, callback = self.parseCategory, meta=response.meta)
    #     else:
    #         print "NO DEPARTMENT LINK", response.url
