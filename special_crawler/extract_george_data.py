import urllib
import re
import sys
import json
import random
from lxml import html
import time
import requests
from extract_data import Scraper

class GeorgeScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://direct.asda.com/george/<category>/<sub-category>/<type>/<product id>,default,pd.html"

    def check_url_format(self):
        m = re.match(r"^http://direct.asda.com/george.*$", self.product_page_url.lower())
        self.image_urls = None
        return (not not m)

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''
        if self.product_page_url.find(",pd.html") < 0: return True
        return False


    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        product_id = self.product_page_url.split("/")
        if len(product_id) > 0 :
            return product_id[-1].split(",")[0]
        return None

    def _site_id(self):
        return None

    def _status(self):
        return 'success'


    ##########################################
    ################ CONTAINER : PRODUCT_INFO
    ##########################################

    def _product_name(self):
        pn = self.tree_html.xpath('//h1[@id="productName"]//text()')
        if len(pn)>0:
            return pn[0]
        return None

    def _product_title(self):
        return self.tree_html.xpath("//title//text()")[0].strip()


    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        return None

    def _features(self):
        rows = self.tree_html.xpath("//table[@id='fullSpec']//tr")
        cells=[]
        for row in rows:
            r = row.xpath(".//*[not(self::script)]//text()")
            rc =",".join([c.strip() for c in r])
            cells.append(rc)
        if len(cells)>0:
            return cells
        return None


    def _feature_count(self): # extract number of features from tree
        rows = self._features()
        if rows == None:
            return 0
        return len(rows)


    def _model_meta(self):
        return None


    def _description(self):
        short_description = " ".join(self.tree_html.xpath("//div[contains(@class,'Description')]//text()[normalize-space()]")).strip()
        if short_description==None or  short_description=="":
            sd = self.tree_html.xpath('//*[@id="tabContentsProduct"]//div[@class="description"]//text()[normalize-space()]')
            if len(sd) > 0:
                short_description = self._clean_text(sd[0])
        if short_description is not None and len(short_description)>0:
            return short_description.replace("\n"," ")
        return self._long_description_helper()


    def _long_description(self):
        return None



    def _long_description_helper(self):
         return None





    ##########################################
    ################ CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #extract meta tags exclude http-equiv
    def _meta_tags(self):
        tags = map(lambda x:x.values() ,self.tree_html.xpath('//meta[not(@http-equiv)]'))
        return tags

    def _meta_tag_count(self):
        tags = self._meta_tags()
        return len(tags)

    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        url = self.product_page_url
        #Get images for mobile device
        mobile_headers = {"User-Agent" : "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5"}
        response = requests.get(self.product_page_url,headers=mobile_headers, timeout=5)
        if response != 'Error' and response.ok:
            contents = response.text
            try:
                tree = html.fromstring(contents.decode("utf8"))
            except UnicodeError, e:
                tree = html.fromstring(contents)
        img_list = []
        ii=0
        tree = html.fromstring(contents)
        image_url_m = self._image_urls(tree)
        image_url_p = self._image_urls()
        return image_url_p == image_url_m

    def _image_urls(self, tree = None):
        a = 0
        if tree == None:
            if self.image_urls != None:
                return self.image_urls
            a = 1
            tree = self.tree_html

        #The small images are below the big image
        image_url = tree.xpath("//div[@id='imageSlide']//img/@src")
        if a == 1:
            self.image_urls = image_url
        if image_url is not None and len(image_url)>0 and self.no_image(image_url)==0:
            return image_url
        return None

    def _image_helper(self):
        return []


    def _mobile_image_url(self, tree = None):
        if tree == None:
            tree = self.tree_html
        image_url = self._image_urls(tree)
        return image_url

    def _image_count(self):
        iu = self._image_urls()
        if iu ==None:
            return 0
        return len(iu)

    # return 1 if the "no image" image is found
    def no_image(self,image_url):
        try:
            if len(image_url)>0 and image_url[0].find("no-img")>0:
                return 1
            if self._no_image(image_url[0]):
                return 1
        except Exception, e:
            print "image_urls WARNING: ", e.message
        return 0

    def _video_urls(self):
        video_url = self.tree_html.xpath("//div[@id='thumbnailsWrapper']//span[contains(@class,'video')]/img/@src")
        if len(video_url) > 0: return video_url
        return None


    def _video_count(self):
        if self._video_urls()==None: return 0
        return len(self._video_urls())

    # return one element containing the PDF
    def _pdf_urls(self):
        return None

    def _pdf_count(self):
        urls = self._pdf_urls()
        if urls:
            return len(urls)
        return None

    def _webcollage(self):
        return None

    # extract htags (h1, h2) from its product product page tree
    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]





    ##########################################
    ################ CONTAINER : REVIEWS
    ##########################################

    def _average_review(self):
        average_review = self.tree_html.xpath("//span[@itemprop='ratingValue']//text()")
        if len(average_review) > 0:
            av_review = average_review[0]
            return self._tofloat(av_review)
        return None

    def _review_count(self):
        nr_reviews = self.tree_html.xpath("//span[@class='BVRRNumber']//text()")
        if len(nr_reviews) > 0:
            return self._toint(nr_reviews[0].strip())
        return None

    def _reviews(self):
        return None

    def _tofloat(self,s):
        try:
            t=float(s)
            return t
        except ValueError:
            return 0.0

    def _toint(self,s):
        try:
            s = s.replace(',','')
            t=int(s)
            return t
        except ValueError:
            return 0

    def _max_review(self):
        rv = self._reviews()
        if rv !=None and len(rv)>0:
            return rv[-1][0]
        return None

    def _min_review(self):
        rv = self._reviews()
        if rv !=None and len(rv)>0:
            return rv[0][0]
        return None


    ##########################################
    ################ CONTAINER : SELLERS
    ##########################################

    # extract product price from its product product page tree
    def _price(self):
        price = self.tree_html.xpath("//p[@id='productPrice']/span/span")
        if len(price)>0  :
            return price[0].text_content().strip()
        return None

    def _price_amount(self):
        price = self._price()
        clean = re.sub(r'[^0-9.]+', '', price)
        return float(clean)

    def _price_currency(self):
        bn=self.tree_html.xpath('//meta[@itemprop="priceCurrency"]/@content')
        if len(bn)>0  and bn[0]!="":
            return bn[0]
        price = self._price()
        clean = re.sub(r'[^0-9.]+', '', price)
        curr = price.replace(clean,"").strip()
        if curr=="$":
            return "USD"
        return "GBP"

    def _in_stores_only(self):
        return None

    def _in_stores(self):
        return None

    def _site_online(self):
        if self._marketplace()==1: return 0
        return 1

    def _site_online_out_of_stock(self):
        if self._site_online() == 0: return None
        a = self.tree_html.xpath('//select[contains(@id,"quantity") and @disabled]')
        if len(a)>0 : return 1
        return 0

    def _marketplace(self):
         return 0

    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
        return None

    def _marketplace_out_of_stock(self):
        return None

    # extract product seller information from its product product page tree (using h2 visible tags)
    def _seller_from_tree(self):
        return None




    ##########################################
    ################ CONTAINER : CLASSIFICATION
    ##########################################

    # extract the department which the product belongs to
    def _category_name(self):
        bn=self.tree_html.xpath('//div[@id="navBread"]//a//text()')
        if len(bn)>0:
            return bn[-1]
        return None

    # extract a hierarchical list of all the departments the product belongs to
    def _categories(self):
        bn=self.tree_html.xpath('//div[@id="navBread"]//a//text()')
        if len(bn)>0:
            return bn[1:]
        return None

    def _brand(self):
        bn=self.tree_html.xpath('//meta[@itemprop="brand"]/@content')
        if len(bn)>0  and bn[0]!="":
            return bn[0]
        return None

    def _upc(self):
        bn=self.tree_html.xpath('//meta[@property="og:upc"]/@content')
        if len(bn)>0  and bn[0]!="":
            return bn[0]
        return None

    def _version(self):
        """Determines if Amazon.co.uk page being read
        Returns:
            "uk" for Amazon.co.uk
            "com" for Amazon.com
        """
        return None

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################

    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        text = text.replace("<br />"," ").replace("\n"," ")
        return re.sub("&nbsp;", " ", text).strip()



    ##########################################
    ################ RETURN TYPES
    ##########################################
    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service

    DATA_TYPES = { \
        # CONTAINER : NONE
        "url" : _url, \
        "event" : _event, \
        "product_id" : _product_id, \
        "site_id" : _site_id, \
        "status" : _status, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "model" : _model, \
        "upc" : _upc,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "model_meta" : _model_meta, \
        "description" : _description, \
        "long_description" : _long_description, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "meta_tags": _meta_tags,\
        "meta_tag_count": _meta_tag_count,\

        # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount": _price_amount, \
        "price_currency": _price_currency, \
         "in_stores_only" : _in_stores_only, \
        "in_stores" : _in_stores, \
        "marketplace" : _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "marketplace_out_of_stock" : _marketplace_out_of_stock,\
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock,\
        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \



        "loaded_in_seconds" : None, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
    }

