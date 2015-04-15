import urllib
import re
import sys
import json
import random
from lxml import html
import time
import requests
from extract_data import Scraper

class CostcoScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.costco.com/<product name>.product.<product id>.html"

    def check_url_format(self):
        self.image_urls = None
        self.prod_help = None
        url = self.product_page_url.lower()
        if url.find('costco.com') > 0 and url.find('product.') > 0:
            return True
        return False

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''
        pid = self.tree_html.xpath('//h1[text()="Product Not Found"]//text()')
        if len(pid) > 0: return True
        return False


    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        pid = self.tree_html.xpath('//*[@itemprop="sku"]//text()')
        return pid[0]

    def _site_id(self):
        site_id = self.product_page_url.split("product.")
        site_id = site_id[-1]
        ft = site_id.find(".html")
        if ft>0:
            return site_id[0:ft]
        else:
            ft = site_id.find("?ItemNo=")
            if ft>0:
                return site_id[ft+8:]
        return None


    def _status(self):
        return 'success'


    ##########################################
    ################ CONTAINER : PRODUCT_INFO
    ##########################################

    def _product_name(self):
        pn = self.tree_html.xpath('//h1[@itemprop="name"]//text()')
        if len(pn)>0:
            return pn[0].strip()
        return None

    def _product_title(self):
        return self.tree_html.xpath("//title//text()")[0].strip()



    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()


    def _model(self):
        if self.prod_help==None:
            self.prod_help = self._product_helper()
        return self.prod_help.get('product_model',None)


    def _features(self):
        rws = self.tree_html.xpath('//div[@id="product-tab2"]//li')
        if len(rws)>0:
            return [r.text_content().replace(':',',').strip() for r in rws]
        return None


    def _feature_count(self): # extract number of features from tree
        rows = self._features()
        if rows == None:
            return 0
        return len(rows)


    def _model_meta(self):
        return None


    def _description(self):
        short_description = " ".join(self.tree_html.xpath('//div[@class="features"]//text()[normalize-space()]')).strip()
        if short_description != None and  short_description != "":
            return  self._clean_text(short_description)
        return self._long_description()


    def _long_description(self):
        long_description =  " ".join(self.tree_html.xpath('//p[@itemprop="description"]//text()[normalize-space()]')).strip()
        if long_description != None and  long_description != "":
            return  self._clean_text(long_description)
        long_description =  " ".join(self.tree_html.xpath('//div[@id="product-tab1"]//text()[normalize-space()]')).strip()
        if long_description != None and  long_description != "":
            return  self._clean_text(long_description)
        return None



    def _long_description_helper(self):
        return None


    def _apluscontent_desc(self):
        res = self._clean_text(' '.join(self.tree_html.xpath('//div[@id="wc-aplus"]//text()')))
        if res != "" : return res



    ##########################################
    ################ CONTAINER : PAGE_ATTRIBUTES
    ##########################################


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
        img_link = tree.xpath('//script[contains(@src,"costco-static.com")]/@src')[0]
        imgs = requests.get(img_link).text
        img_url = re.findall(r"image\:(.+?)\,+?",imgs)
        img_url = ["http://images.costco-static.com/image/media/"+b.replace("'","").strip()+".jpg" for b in img_url]
        if len(img_url) > 0:
            self.image_urls = img_url
            return img_url
        if a == 1:
            self.image_urls = None
        return None


    def _image_helper(self, tree):
        res = {}
        try:
            all_scripts = tree.xpath('//script[@type="text/javascript"]//text()')
            for s in all_scripts:
                st = s.find('imgGalleryConfig.BaseUrlForS7')
                if st >= 0:
                    st = s.find('"',st)
                    if st > 0:
                        ft =s.find('";',st+1)
                        if ft > st:
                            res["BaseUrlForS7"] = s[st+1:ft]

                st = s.find('imgGalleryConfig.SmallImageUrl')
                if st >= 0:
                    st = s.find('"',st)
                    if st > 0:
                        ft =s.find('";',st+1)
                        if ft > st:
                            res["SmallImageUrl"] = s[st+1:ft]
                st = s.find('var imgGalleryConfig')
                if st >= 0:
                    st = s.find('imgGalleryConfig.Items',st)
                    if st >= 0:
                        st = s.find('[{',st)
                        if st >= 0:
                            ft = s.find('}];',st)
                            if ft > st:
                                itm = s[st:ft+2]
                                items = json.loads(itm)
                                res['Items'] = items
                                return res
                                break
        except Exception as ex:
            print ex
        return res


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
            if len(image_url)>0 and self._no_image(image_url[0]):
                return 1
        except Exception, e:
            print "image_urls WARNING: ", e.message
        return 0

    def _video_urls(self):
        vu = self.tree_html.xpath("//a[@class='video-link']/@href")
        if len(vu)>0:
            return vu
        return None

    def _video_count(self):
        if self._video_urls()==None: return 0
        return len(self._video_urls())

    # return one element containing the PDF
    def _pdf_urls(self):
        pdf = self.tree_html.xpath("//a[contains(@href,'.pdf')]/@href")
        if len(pdf)>0 :
            pdf = set(pdf)
            return ["http://www.costco.com/wcsstore"+p for p in pdf if "Cancellation" not in p]
        return None

    def _pdf_count(self):
        urls = self._pdf_urls()
        if urls:
            return len(urls)
        return 0

    def _webcollage(self):
        wbc = self.tree_html.xpath("//img[contains(@src,'webcollage.net')]")
        if len(wbc) > 0 : return 1
        return 0

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
        avr = self.tree_html.xpath('//meta[@itemprop="ratingValue"]/@content')
        if len(avr) > 0:
            return self._tofloat(avr[0])
        return None


    def _review_count(self):
        avr = self.tree_html.xpath('//meta[@itemprop="reviewCount"]/@content')
        if len(avr) > 0:
            return self._toint(avr[0])
        return None


    def _reviews(self):
        res = []
        for i in range(1,6):
            rvm = self.tree_html.xpath('//span[@id="reviewNumber%s"]//text()' % i)
            if len(rvm) > 0 and  self._toint(rvm[0]) > 0:
                res.append([i, self._toint(rvm[0])])
        if len(res) > 0: return res
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
        avr = self.tree_html.xpath('//meta[@itemprop="bestRating"]/@content')
        if len(avr) > 0:
            return self._toint(avr[0])
        return None

    def _min_review(self):
        rv = self._reviews()
        if rv !=None and len(rv)>0:
            return rv[0][0]
        return None


    ##########################################
    ################ CONTAINER : SELLERS
    ##########################################

    # extract product information from javascript
    def _product_helper(self):
        res = {}
        try:
            all_scripts = self.tree_html.xpath('//script[@type="text/javascript"]//text()')
            for s in all_scripts:
                st = s.find('scp.sellerName')
                if st > 0:
                    st = s.find('"',st)
                    if st > 0:
                        st +=1
                        ft = s.find('"',st)
                        if ft > st:
                            res['seller'] = s[st:ft]
                st = s.find('var utag_data = {')
                if st >= 0:
                    price = self._get_param(s,'product_sale_price:',st)
                    price_currency = self._get_param(s,'site_currency:',st,False)
                    res['category'] = self._get_param(s,'product_category_name',st)
                    res['subcategory'] = self._get_param(s,'product_subcategory_name',st)
                    res['product_id'] = self._get_param(s,'product_id',st)
                    res['product_web_id'] = self._get_param(s,'product_web_id',st)
                    res['product_title'] = self._get_param(s,'product_title',st)
                    res['product_manufacture'] = self._get_param(s,'product_manufacture',st)
                    res['product_model'] = self._get_param(s,'product_model',st)
                    res['product_instock'] = self._get_param(s,'product_instock',st)
                    res['page_name'] = self._get_param(s,'page_name',st,False)
                    res['page_type'] = self._get_param(s,'page_type',False)
                    res['price_amount'] = self._tofloat(price)
                    res['price_currency'] = price_currency
                    res['price'] = price
                    break
        except Exception as ex:
            print ex
        return res


    def _get_param(self,s,param,st,inlist=True):
        #get a parameter from a string in javascript
        bt = s.find(param,st)
        res = ""
        if bt >= 0:
            if inlist:
                bt = s.find("['",bt) + 2
                ft = s.find("']",bt)
            else:
                bt = s.find("'",bt) + 1
                ft = s.find("'",bt)
            if ft > bt:
                res = s[bt:ft]
        return res

    # extract product price
    def _price(self):
        pr = self.tree_html.xpath('//div[@class="your-price"]//span[@class="currency"]//text()')
        if len(pr) > 0:
            return pr[0]
        pr = self.tree_html.xpath('//li[@class="final_instane_Price"]//span[@class="red_price"]/span//text()')
        if len(pr) > 0:
            return pr[0]
        return None


    def _price_amount(self):
        price = self._price()
        clean = re.sub(r'[^0-9.]+', '', price)
        return float(clean)


    def _price_currency(self):
        price = self._price()
        clean = re.sub(r'[^0-9,.]+', '', price)
        curr = price.replace(clean,"").strip()
        if curr=="$":
            return "USD"
        return curr


    def _in_stores_only(self):
        return None

    def _in_stores(self):
        return 0

    def _site_online(self):
        if self._marketplace() == 1: return 0
        return 1

    def _site_online_out_of_stock(self):
        if self.prod_help==None:
            self.prod_help = self._product_helper()
        if self._marketplace() == 1: return None
        in_stock = self.prod_help.get('product_instock','')
        if in_stock == '0' : return 1
        return 0

    def _marketplace(self):
        if self.prod_help==None:
            self.prod_help = self._product_helper()
        seller = self.prod_help.get('seller','')
        if len(seller) > 0 : return 1
        return 0


    def _marketplace_sellers(self):
        if self.prod_help==None:
            self.prod_help = self._product_helper()
        seller = self.prod_help.get('seller','')
        if seller != "":
            return seller.split(',')
        return None

    def _marketplace_lowest_price(self):
        return None

    def _marketplace_out_of_stock(self):
        if self._marketplace() == 0: return None
        in_stock = self.prod_help.get('product_instock','')
        if in_stock == '0' : return 1
        return 0



    ##########################################
    ################ CONTAINER : CLASSIFICATION
    ##########################################

    # extract the department which the product belongs to
    def _category_name(self):
        cats = self._categories()
        if cats != None and len(cats) > 0:
            return cats[-1]
        return None

    # extract a hierarchical list of all the departments the product belongs to
    def _categories(self):
        cats = self.tree_html.xpath('//*[@itemprop="breadcrumb"]//text()')
        cats = [self._clean_text(c) for c in cats if self._clean_text(c) != '']
        if len(cats)>0:
            return cats
        return None


    def _brand(self):
        rws = self.tree_html.xpath('//div[@id="product-tab2"]//li[child::*[contains(text(),"Brand")]]')
        if len(rws)>0:
            return rws[0].text_content().replace('Brand:','').strip()
        return None


    def _upc(self):
        bn=self.tree_html.xpath('//meta[@property="og:upc"]/@content')
        if len(bn)>0  and bn[0]!="":
            return bn[0]
        return None


    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################

    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        text = text.replace("<br />"," ").replace("\n"," ").replace("\t"," ").replace("\r"," ")
       	text = re.sub("&nbsp;", " ", text).strip()
        return  re.sub(r'\s+', ' ', text)



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


