from scrapy.spider import Spider
from scrapy.selector import Selector
from Categories.items import CategoryItem
from Categories.items import ProductItem
from scrapy.http import Request, FormRequest
from scrapy.http import Response

from spiders_utils import Utils
import re

# crawls sitemap and extracts department and categories names and urls (as well as other info)
class TargetSpider(Spider):
    name = "target"
    allowed_domains = ["target.com"]
    start_urls = [
        "http://www.target.com/c/more/-/N-5xsxf#?lnk=fnav_t_spc_3_31"
    ]

    def __init__(self):
	    # level that is considered to contain departments
	    self.DEPARTMENT_LEVEL = 1

	    # only crawl down to this level
	    self.LEVEL_BARRIER = -10

	    # flag indicating whether to compute overall product counts in pipelines phase for this spider.
	    # if on, 'catid' and 'parent_catid' fields need to be implemented
	    self.compute_nrproducts = True

	    # counter for department id, will be used to autoincrement department id
	    self.department_count = 0
	    # counter for category id
	    self.catid = 0

	    # base of urls on this site used to build url for relative links
	    self.BASE_URL = "http://www.target.com"

	    # crawled urls - for an explicit duplicate filter
	    self.crawled_urls = []

    # extract departments and next level categories
    def parse(self, response):
    	sel = Selector(response)

    	departments = sel.xpath("//div[@class='ul-wrapper']/ul/li")

    	for department in departments:

    		# extract departments
    		department_item = CategoryItem()
    		department_item['text'] = department.xpath("a/text()").extract()[0].strip()
    		department_item['url'] = self.build_url(department.xpath("a/@href").extract()[0])

    		department_item['department_text'] = department_item['text']
    		department_item['department_url'] = department_item['url']

    		department_item['level'] = self.DEPARTMENT_LEVEL

    		# assign next available department id
    		self.department_count += 1
    		department_item['department_id'] = self.department_count

    		# assign next available category id
    		self.catid += 1
    		department_item['catid'] = self.catid

    		# send to be parsed further
    		yield Request(department_item['url'], callback = self.parseCategory, meta = {'item' : department_item})

    		# extract its subcategories
    		subcategories = department.xpath(".//li")
    		for subcategory in subcategories:

    			subcategory_item = CategoryItem()

    			subcategory_item['text'] = subcategory.xpath("a/text()").extract()[0].strip()
    			subcategory_item['url'] = self.build_url(subcategory.xpath("a/@href").extract()[0])

    			# its level is one less than its parent's level
    			subcategory_item['level'] = department_item['level'] - 1

    			subcategory_item['department_text'] = department_item['department_text']
    			subcategory_item['department_url'] = department_item['department_url']
    			subcategory_item['department_id'] = department_item['department_id']

    			subcategory_item['parent_text'] = department_item['text']
    			subcategory_item['parent_url'] = department_item['url']
    			subcategory_item['parent_catid'] = department_item['catid']

    			# assign next available category id
    			self.catid += 1
    			subcategory_item['catid'] = self.catid

    			# send to be parsed further
    			yield Request(subcategory_item['url'], callback = self.parseCategory, meta = {'item' : subcategory_item})


    # extract category info given a category page url, extract its subcategories if necessary and return it
    def parseCategory(self, response):

    	#TODO: add extraction of additional category info
    	sel = Selector(response)

    	#TODO: a lot of redirects. maybe for item, set 'url' to the one to which it was redirected? (response.url)
    	item = response.meta['item']

    	# extract description
    	description_texts = sel.xpath("//div[@class='subpart']/p//text()").extract()

    	# second try at finding descriptions
    	if not description_texts:
    		description_texts = sel.xpath("//div[@id='SEO_TEXT']//text()").extract()

    	# replace all whitespace with one space, strip, and remove empty texts; then join them
    	if description_texts:
        	item['description_text'] = " ".join([re.sub("\s+"," ", description_text.strip()) for description_text in description_texts if description_text.strip()])

        	tokenized = Utils.normalize_text(item['description_text'])
        	item['description_wc'] = len(tokenized)

        else:
        	item['description_wc'] = 0


    	#TODO: add description title as category name if no title available?
    	# then also add the keyword/density count


    	# extract item count
    	nr_products_node = sel.xpath("//ul[@class='results']//strong/text()")
    	if nr_products_node:
    		# nr of products is in the second of these nodes
    		nr_products = nr_products_node.extract()[1].strip()
    		item['nr_products'] = int(nr_products)


    	yield item

    	self.crawled_urls.append(item['url'])

    	# extract subcategories (if we haven't reached level barrier)
    	if item['level'] <= self.LEVEL_BARRIER:
    		return

    	parent_item = item

    	# "shop categories" menu
    	subcategories = sel.xpath("//h3[text()='shop categories']/following-sibling::ul/li/a")
    	for subcategory in subcategories:
    		subcategory_item = CategoryItem()

    		subcategory_item['text'] = subcategory.xpath("text()").extract()[0].strip()
    		subcategory_item['url'] = self.build_url(subcategory.xpath("@href").extract()[0])

    		# filter duplicates
    		if subcategory_item['url'] in self.crawled_urls:
    			continue

    		# assign next available category id
    		self.catid += 1
    		subcategory_item['catid'] = self.catid

    		subcategory_item['level'] = parent_item['level'] - 1

    		subcategory_item['parent_url'] = parent_item['url']
    		subcategory_item['parent_text'] = parent_item['text']
    		subcategory_item['parent_catid'] = parent_item['catid']

    		subcategory_item['department_text'] = parent_item['department_text']
    		subcategory_item['department_url'] = parent_item['department_url']
    		subcategory_item['department_id'] = parent_item['department_id']

    		# send this subcategory to be further parsed
    		yield Request(subcategory_item['url'], callback = self.parseCategory, meta = {'item' : subcategory_item})



    # build URL from relative links found on pages: add base url and clean final url
    def build_url(self, url):
    	url = Utils.add_domain(url, self.BASE_URL)
    	url = Utils.clean_url(url, ['#'])
    	return url

