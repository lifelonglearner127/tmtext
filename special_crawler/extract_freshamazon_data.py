import urllib
import re
import sys
import json
import random
from lxml import html
import time
import requests
from extract_data import Scraper

class FreshAmazonScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is https://fresh.amazon.com/product?asin=<product-id>"

    def check_url_format(self):
        m = re.match(r"^https://fresh.amazon.com/product.*$", self.product_page_url)
        self.image_urls = None
        return (not not m)

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''
        return False

   # method that returns xml tree of page, to extract the desired elemets from
    def _extract_page_tree(self):
        """Overwrites parent class method that builds and sets as instance variable the xml tree of the product page
        Returns:
            lxml tree object
        """
        agent = ''
        if self.bot_type == "google":
            print 'GOOOOOOOOOOOOOGGGGGGGLEEEE'
            agent = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        else:
            agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140319 Firefox/24.0 Iceweasel/24.4.0'

        #Set zip code for delivery
        payload = {'zip':'94102'}
        headers ={'User-agent': agent}
        for i in range(self.MAX_RETRIES):
            # Use 'with' to ensure the session context is closed after use.
            with requests.Session() as s:
                s.post('https://fresh.amazon.com/zipEntrySubmit', data=payload)
                # An authorised request.
                response = s.get(self.product_page_url,headers=headers, timeout=5)
                if response != 'Error' and response.ok:
                    contents = response.text
                    try:
                        self.tree_html = html.fromstring(contents.decode("utf8"))
                    except UnicodeError, e:
                        # if string was not utf8, don't deocde it
                        print "Warning creating html tree from page content: ", e.message
                        self.tree_html = html.fromstring(contents)
                    return

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        product_id = self.product_page_url.split("asin=")
        if len(product_id) >0 :
            return product_id[1][0:10]
        return None

    def _site_id(self):
        return None

    def _status(self):
        return 'success'




    ##########################################
    ################ CONTAINER : PRODUCT_INFO
    ##########################################

    def _product_name(self):
        pn = self.tree_html.xpath('//div[@class="buying"]/h1//text()')
        if len(pn)>0:
            return pn[0]
        return None

    def _product_title(self):
        return self.tree_html.xpath("//title//text()")[0].strip()


    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        return None

    # Amazon's version of UPC
    def _asin(self):
        return self.tree_html.xpath("//li[child::strong[contains(text(),'ASIN')]]//text()")

    def _features(self):
        rows = self.tree_html.xpath("//h2[contains(text(),'Product Features')]/following-sibling::ul//li//text()")
        if len(rows)>0:
            return rows
        return None


    def _feature_count(self): # extract number of features from tree
        rows = self._features()
        if rows == None:
            return 0
        return len(rows)


    def _model_meta(self):
        return None


    def _description(self):
        short_description = " ".join(self.tree_html.xpath("//div[contains(@id,'productDescription')]//text()[normalize-space()]")).strip()
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
        with requests.Session() as s:
            s.post('https://fresh.amazon.com/zipEntrySubmit', data={'zip':'94102'})
            response = s.get(self.product_page_url,headers=mobile_headers, timeout=5)
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
        image_url = tree.xpath("//div[@id='thumbnailsWrapper']//span[not(contains(@class,'video'))]//img/@src")

##        #Images in description
##        img_desc = self.tree_html.xpath("//div[contains(@id,'productDescription')]//img/@src")
##        image_url.extend(img_desc)
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
        average_review = self.tree_html.xpath("//div[@class='ratingMinimal']/img/@src")
        if len(average_review) > 0:
            av_review = average_review[0].split("/")[-1].split("-")[0]
            return self._tofloat(av_review)
        return None

    def _review_count(self):
        nr_reviews = self.tree_html.xpath("//div[@class='ratingMinimal']")
        if len(nr_reviews) > 0:
            return self._toint(nr_reviews[0].text_content().strip().replace(")","").replace("(",""))
        return None

    def _reviews(self):
        stars=self.tree_html.xpath("//tr[@class='a-histogram-row']//a//text()")
        rev=[]
        for i in range(len(stars)-1,0,-2):
            a=self._toint(stars[i-1].split()[0])
            b= self._toint(stars[i])
            rev.append([a,b])
        if len(rev) > 0 :  return rev
        stars=self.tree_html.xpath("//div[contains(@class,'histoRow')]")
        for a in stars:
            b=a.text_content().strip().split()
            if len(b)>2:
                b1 = self._toint(b[0])
                b2 =self._toint(b[2])
                rev.append([b1,b2])
        if len(rev) > 0 :
            rev.reverse()
            return rev
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
        price = self.tree_html.xpath("//div[@class='itemPrice']//span[@class='value']//text()")
        if len(price)>0  and len(price[0].strip())<12  and price[0].strip()!="":
            return price[0].strip()
        return None

    def _price_amount(self):
        price = self._price()
        clean = re.sub(r'[^0-9.]+', '', price)
        return float(clean)

    def _price_currency(self):
        price = self._price()
        clean = re.sub(r'[^0-9.]+', '', price)
        curr = price.replace(clean,"").strip()
        if curr=="$":
            return "USD"
        return curr


##    def _in_stock(self):
##        in_stock = self.tree_html.xpath('//div[contains(@id, "availability")]//text()')
##        in_stock = " ".join(in_stock)
##        if 'currently unavailable' in in_stock.lower():
##            return 0
##
##        in_stock = self.tree_html.xpath('//div[contains(@id, "outOfStock")]//text()')
##        in_stock = " ".join(in_stock)
##        if 'currently unavailable' in in_stock.lower():
##            return 0
##
##        in_stock = self.tree_html.xpath("//div[@id='buyBoxContent']//text()")
##        in_stock = " ".join(in_stock)
##        if 'sign up to be notified when this item becomes available' in in_stock.lower():
##            return 0
##        a = self.tree_html.xpath('//div[@class="item"]')
##        if len(a) > 0 and a[0].text_content().find('Out of stock') >=0 : return 0
##        return 1

    def _in_stores_only(self):
        return None

    def _in_stores(self):
        return None

##    def _owned(self):
##        aa = self.tree_html.xpath("//div[@class='buying' or @id='merchant-info']")
##        for a in aa:
##            if a.text_content().find('old by Amazon')>0: return 1
##        s = self._seller_from_tree()
##        return s['owned']

    def _site_online(self):
        if self._marketplace()==1: return 0
        return 1

    def _site_online_out_of_stock(self):
        if self._site_online() == 0: return None
        a = self.tree_html.xpath('//div[contains(@class,"availability")]//text()')
        if len(a) > 0 and a[0].find('Available by') >=0 : return 1
        a = self.tree_html.xpath('//div[@class="item"]')
        if len(a) > 0 and a[0].text_content().find('Out of stock') >=0 : return 1
        return 0

##    def _owned_out_of_stock(self):
##        return None

    def _marketplace(self):
        aa = self.tree_html.xpath("//div[@class='buying' or @id='merchant-info']")
        for a in aa:
            if a.text_content().find('old by Amazon')>=0:
                return 0
            if a.text_content().find('old by ')>0 and a.text_content().find('old by Amazon')<0:
                return 1
            if a.text_content().find('seller') or a.text_content().find('Other products by')>0  :
                return 1
        a = self.tree_html.xpath('//div[@id="availability"]//a//text()')
        if len(a)>0 and a[0].find('seller')>=0: return 1
        s = self._seller_from_tree()
        return s['marketplace']

    def _marketplace_sellers(self):
        a = self.tree_html.xpath('//div[@id="availability"]//a//text()')
        if len(a)>0 and a[0].find('seller')>=0:
            domain=self.product_page_url.split("/")
            url =self.tree_html.xpath('//div[@id="availability"]//a/@href')
            if len(url)>0:
                url = domain[0]+"//"+domain[2]+url[0]
                print "url",url
                h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
                contents = requests.get(url, headers=h).text
                tree = html.fromstring(contents)
                s = tree.xpath("//p[contains(@class,'SellerName')]//text()")
                mps=[p.strip() for p in s if p.strip() != ""]
                if len(mps)>0: return mps
        return None

    def _marketplace_lowest_price(self):
        return None

    def _marketplace_out_of_stock(self):
        if self._marketplace()==1:
            a = self.tree_html.xpath('//div[contains(@class,"availability")]//text()')
            if len(a) > 0 and a[0].find('Available by') >=0 : return 1
            a = self.tree_html.xpath('//div[@class="item"]')
            if len(a) > 0 and a[0].text_content().find('Out of stock') >=0 : return 1
            return 0
        return None

    # extract product seller information from its product product page tree (using h2 visible tags)
    def _seller_from_tree(self):
        seller_info = {}
        h5_tags = map(lambda text: self._clean_text(text), self.tree_html.xpath("//h5//text()[normalize-space()!='']"))
        acheckboxlabel = map(lambda text: self._clean_text(text), self.tree_html.xpath("//span[@class='a-checkbox-label']//text()[normalize-space()!='']"))
        seller_info['owned'] = 1 if "FREE Two-Day" in acheckboxlabel else 0

        a = self.tree_html.xpath('//div[@id="soldByThirdParty"]')
        a = not not a#turn it into a boolean
        seller_info['marketplace'] = 1 if "Other Sellers on Amazon" in h5_tags else 0
        seller_info['marketplace'] = int(seller_info['marketplace'] or a)

        return seller_info




    ##########################################
    ################ CONTAINER : CLASSIFICATION
    ##########################################

    # extract the department which the product belongs to
    def _category_name(self):
        return None

    # extract a hierarchical list of all the departments the product belongs to
    def _categories(self):
        return None

    def _brand(self):
        bn=self.tree_html.xpath('//div[@class="buying"]//*[contains(text(),"by")]/a//text()')
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
        "upc" : _asin,\
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
#        "no_image" : _no_image, \
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
 #       "in_stock" : _in_stock, \
        "in_stores_only" : _in_stores_only, \
        "in_stores" : _in_stores, \
#        "owned" : _owned, \
#        "owned_out_of_stock" : _owned_out_of_stock, \
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

