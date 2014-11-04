#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html
import time
import requests
from extract_data import Scraper

class AmazonScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################
        
    INVALID_URL_MESSAGE = "Expected URL format is http://www.amazon.com/dp/<product-id>"
    
    def check_url_format(self):
        m = re.match(r"^http://www.amazon.com/([a-zA-Z0-9\-]+/)?(dp|gp/product)/[a-zA-Z0-9]+(/[a-zA-Z0-9_\-\?\&\=]+)?$", self.product_page_url)
        return not not m




    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url
    
    def _event(self):
        return None

    def _product_id(self):
        product_id = re.match("^http://www.amazon.com/([a-zA-Z0-9\-]+/)?(dp|gp/product)/([a-zA-Z0-9]+)(/[a-zA-Z0-9_\-\?\&\=]+)?$", self.product_page_url).group(3)
        return product_id

    def _site_id(self):
        return None

    def _status(self):
        return 'success'




    ##########################################
    ################ CONTAINER : PRODUCT_INFO
    ##########################################

    def _product_name(self):
        return self.tree_html.xpath('//h1[@id="title"]/span[@id="productTitle"]')[0].text

    def _product_title(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
        #return None

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        model = self.tree_html.xpath("//tr[@class='item-model-number']/td[@class='value']//text()")[0]
        return model

    # Amazon's version of UPC
    def _asin(self):
        return self.tree_html.xpath("//input[@name='ASIN']/@value")[0]

    def _features(self):
        rows = self.tree_html.xpath("//div[@class='content pdClearfix']//tbody//tr")
        
        # list of lists of cells (by rows)
        cells = map(lambda row: row.xpath(".//*//text()"), rows)
        # list of text in each row
        
        rows_text = map(\
            lambda row: ":".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        all_features_text = "\n".join(rows_text)

        # return dict with all features info
        return all_features_text

    def _feature_count(self): # extract number of features from tree
        # select table rows with more than 2 cells (the others are just headers), count them
        return len(filter(lambda row: len(row.xpath(".//td"))>0, self.tree_html.xpath("//div[@class='content pdClearfix']//tbody//tr")))

    def _model_meta(self):
        return None 


    def _description(self):
        short_description = " ".join(self.tree_html.xpath("//*[@id='feature-bullets']//text()")).strip()
        if short_description is not None and len(short_description)>0:
            return short_description
        return self._long_description_helper()


    def _long_description(self):
        d1 = self._description()
        d2 = self._long_description_helper()
        if d1 == d2:
            return None
        return d2


    def _long_description_helper(self):
        desc = " ".join(self.tree_html.xpath('//*[@class="productDescriptionWrapper"]//text()')).strip()
        if desc is not None and len(desc)>5:
            return desc

        desc = " ".join(self.tree_html.xpath('//div[@id="psPlaceHolder"]/preceding-sibling::noscript//text()')).strip()
        if desc is not None and len(desc)>5:
            return desc

        desc = '\n'.join(self.tree_html.xpath('//script//text()'))
        desc = re.findall(r'var iframeContent = "(.*)";', desc)
        desc = urllib.unquote_plus(str(desc))
        desc = html.fromstring(desc)
        desc = self._clean_text(' '.join(desc.xpath('//div[@class="productDescriptionWrapper"]//text()')))
        
        return desc




    ##########################################
    ################ CONTAINER : PAGE_ATTRIBUTES
    ##########################################

    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        url = self.product_page_url
        mobile_headers = {"User-Agent" : "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5"}
        pc_headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        img_list = []
        for h in [mobile_headers, pc_headers]:
            contents = requests.get(url, headers=h).text
            tree = html.fromstring(contents)
            image_url = self._image_urls(tree)
            print '\n\n\nImage URL:', image_url, '\n\n\n'
            img_list.extend(image_url)
        if len(img_list) == 2:
            return img_list[0] == img_list[1]
        return None

    def _image_urls(self, tree = None):
        if tree == None:
            tree = self.tree_html
        image_url = tree.xpath("//span[@class='a-button-text']//img/@src")
        if image_url is not None and len(image_url)>0:
            return image_url

        image_url = tree.xpath('//img[@id="imgBlkFront"]')
        if image_url is not None and len(image_url)>0:
            return ["inline image"]
    
    def _mobile_image_url(self, tree = None):
        if tree == None:
            tree = self.tree_html
        image_url = tree.xpath("//span[@class='a-button-text']//img/@src")
        return image_url

    def _image_count(self):
        return len(self._image_urls())
    
    # return 1 if the "no image" image is found
    def _no_image(self):
        return None

    def _video_urls(self):
        video_url = self.tree_html.xpath('//script[@type="text/javascript"]') 
        temp = []
        for v in video_url:
            r = re.findall("[\'\"]url[\'\"]:[\'\"](http://.+?\.mp4)[\'\"]", str(v.xpath('.//text()')))
            if r:
                temp.extend(r)
        return ",".join(temp)

    def _video_count(self):
        return len(self._video_urls().split(','))

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
        average_review = self.tree_html.xpath("//span[@id='acrPopover']/@title")[0]
        average_review = re.findall("([0-9]\.?[0-9]?) out of 5 stars", average_review)[0]
        return average_review

    def _review_count(self):
        nr_reviews = self.tree_html.xpath("//span[@id='acrCustomerReviewText']//text()")[0]
        nr_reviews = re.findall("([0-9]+) customer reviews", nr_reviews)[0]
        return nr_reviews

    def _max_review(self):
        return None

    def _min_review(self):
        return None





    ##########################################
    ################ CONTAINER : SELLERS
    ##########################################
        
    # extract product price from its product product page tree
    def _price(self):
        price = self.tree_html.xpath("//*[contains(@id, 'priceblock_')]//text()")#priceblock_ can usually have a few things after it
        if price:
            return price[0].strip()

        price = self.tree_html.xpath("//*[contains(@class, 'offer-price')]//text()")
        if price:
            return price[0].strip()

        return None

    def _in_stores_only(self):
        return None

    def _in_stores(self):
        return None

    def _owned(self):
        s = self._seller_from_tree()
        return s['owned']

    def _owned_out_of_stock(self):
        return None

    def _marketplace(self):
        s = self._seller_from_tree()
        return s['marketplace']

    def _marketplace_sellers(self):
        return None

    def _marketplace_lowest_price(self):
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
        all = self.tree_html.xpath("//div[@class='detailBreadcrumb']/li[@class='breadcrumb']/a//text()")
        all = map(lambda t: self._clean_text(t), all)
        return all[1]
    
    # extract a hierarchical list of all the departments the product belongs to
    def _categories(self):
        all = self.tree_html.xpath("//div[@class='detailBreadcrumb']/li[@class='breadcrumb']/a//text()")
        all = map(lambda t: self._clean_text(t), all)
        return all

    def _brand(self):
        return self.tree_html.xpath('//div[@id="mbc"]/@data-brand')[0]




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
        "no_image" : _no_image, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \

        # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "in_stores_only" : _in_stores_only, \
        "in_stores" : _in_stores, \
        "owned" : _owned, \
        "owned_out_of_stock" : _owned_out_of_stock, \
        "marketplace" : _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \

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
















    ##########################################
    ################ OUTDATED CODE - probably ok to delete it
    ##########################################

    # def manufacturer_content_body(self):
    #     full_description = " ".join(self.tree_html.xpath('//*[@class="productDescriptionWrapper"]//text()')).strip()
    #     return full_description

    # def _anchors_from_tree(self):
    #     '''get all links found in the description text'''
    #     description_node = self.tree_html.xpath('//*[@class="productDescriptionWrapper"]')[0]
    #     links = description_node.xpath(".//a")
    #     nr_links = len(links)
    #     links_dicts = []
    #     for link in links:
    #         links_dicts.append({"href" : link.xpath("@href")[0], "text" : link.xpath("text()")[0]})
    #     ret = {"quantity" : nr_links, "links" : links_dicts}
    #     return ret

    # def _meta_description(self):
    #     return self.tree_html.xpath("//meta[@name='description']/@content")[0]
    
    # def _meta_keywords(self):
    #     return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]
  
    # def main(args):
    #     # check if there is an argument
    #     if len(args) <= 1:
    #         sys.stderr.write("ERROR: No product URL provided.\nUsage:\n\tpython crawler_service.py <amazon_product_url>\n")
    #         sys.exit(1)
    
    #     product_page_url = args[1]
    
    #     # check format of page url
    #     if not check_url_format(product_page_url):
    #         sys.stderr.write(INVALID_URL_MESSAGE)
    #         sys.exit(1)
    
    #     return json.dumps(product_info(sys.argv[1], ["name", "short_desc", "keywords", "price", "load_time", "anchors", "long_desc"]))
