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
    
    #http://www.amazon.com/dp/B000JMAVYO
    
    INVALID_URL_MESSAGE = "Expected URL format is http://www.amazon.com/dp/<product-id>"
    
    #Holds a JSON variable that contains information scraped from a query which Tesco makes through javascript
    bazaarvoice = None
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match("^http://www.amazon.com/dp/[a-zA-Z0-9]+$", self.product_page_url)
        return not not m
    
    # TODO:
    #      better way of extracting id now that URL format is more permissive
    #      though this method still seems to work...
    def _extract_product_id(self):
        product_id = self.product_page_url.split('/')[-1]
        return product_id

    # return dictionary with one element containing the video url
    def video_for_url(self):
        video_url = self.tree_html.xpath("//section[@class='main-details']//script//text()")[1]
        video_url = re.search("\['http://embed\.flixfacts\.com/.*\]", video_url.strip()).group()
        video_url = re.findall("'(.*?)'", video_url)
        return video_url

    # return dictionary with one element containing the PDF
    def pdf_for_url(self):
        return None
    
    #populate the bazaarvoice variable for use by other functions
    def load_bazaarvoice(self):
        url = "http://api.bazaarvoice.com/data/batch.json?passkey=asiwwvlu4jk00qyffn49sr7tb&apiversion=5.4&displaycode=1235-en_gb&resource.q0=products&filter.q0=id%3Aeq%3A" \
        + self._extract_product_id() + \
        "&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_AU%2Cen_CA%2Cen_DE%2Cen_GB%2Cen_IE%2Cen_NZ%2Cen_US"
        req = requests.get(url)
        self.bazaarvoice = req.json()
        
    def _image_url(self):
        image_url = self.tree_html.xpath("//span[@class='a-button-text']//img/@src")
        return image_url
        
    def manufacturer_content_body(self):
        if not self.bazaarvoice:
            self.load_bazaarvoice()
        content = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['Description']
        return content
    
    #extract average review, and total reviews  
    def reviews_for_url(self):
        if not self.bazaarvoice:
            self.load_bazaarvoice()
        average_review = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['AverageOverallRating']
    
        return average_review

    def nr_reviews(self):
        if not self.bazaarvoice:
            self.load_bazaarvoice()

        nr_reviews = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['TotalReviewCount']
        return nr_reviews
        
    # extract product name from its product page tree
    # ! may throw exception if not found
    def _product_name_from_tree(self):
        return self.tree_html.xpath('//h1[@id="title"]/span[@id="productTitle"]')[0].text

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_keywords_from_tree(self):
        
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]
        
    # extract meta "brand" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_brand_from_tree(self):
        #<div id="mbc" data-asin="B000JMAVYO" data-brand="Spicy World"
        return self.tree_html.xpath('//div[@id="mbc"]/@data-brand')[0]


    # extract product short description from its product page tree
    # ! may throw exception if not found
    def _short_description_from_tree(self):
        
        short_description = " ".join(self.tree_html.xpath("//*[@id='feature-bullets']//text()")).strip()
        return short_description

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description_from_tree(self):
        #TODO: Needs some logic for deciding when Tesco is displaying one format or the other, the following 2 lines are the currently encountered versions
        #full_description = " ".join(self.tree_html.xpath("//section[@id='product-details-link']/section[@class='detailWrapper']//text()")).strip()
        full_description = " ".join(self.tree_html.xpath('//*[@class="productDescriptionWrapper"]//text()')).strip()
        
        return full_description


    # extract product price from its product product page tree
    def _price_from_tree(self):
        
        meta_price = self.tree_html.xpath("//*[@id='priceblock_ourprice']//text()")
        if meta_price:
            return meta_price[0].strip()
        else:
            return None

    # extract product price from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - test
    #      - is format ok?
    def _anchors_from_tree(self):
        # get all links found in the description text
        description_node = self.tree_html.xpath('//*[@class="productDescriptionWrapper"]')[0]
        links = description_node.xpath(".//a")
        nr_links = len(links)

        links_dicts = []

        for link in links:
            # TODO: 
            #       extract text even if nested in something?
            #       better error handling (on a per link basis)
            links_dicts.append({"href" : link.xpath("@href")[0], "text" : link.xpath("text()")[0]})

        ret = {"quantity" : nr_links, "links" : links_dicts}

        return ret


    # extract htags (h1, h2) from its product product page tree
    def _htags_from_tree(self):
        htags_dict = {}

        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))

        return htags_dict

    # extract product model from its product product page tree
    # ! may throw exception if not found
    def _model_from_tree(self):
        if not self.bazaarvoice:
            self.load_bazaarvoice()
        return self.bazaarvoice['BatchedResults']['q0']['Results'][0]['ModelNumbers'][0]

    # extract product features list from its product product page tree, return as string
    # join all text in spec table; separate rows by newlines and eliminate spaces between cells
    def _features_from_tree(self):
        #TODO: Needs some logic for deciding when Tesco is displaying one format or the other, the following 2 lines are the currently encountered versions
        #rows = self.tree_html.xpath("//section[@class='detailWrapper']//tr")
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

    # extract number of features from tree
    # ! may throw exception if not found
    def _nr_features_from_tree(self):
        # select table rows with more than 2 cells (the others are just headers), count them
        return len(filter(lambda row: len(row.xpath(".//td"))>0, self.tree_html.xpath("//div[@class='content pdClearfix']//tbody//tr")))

    # extract page title from its product product page tree
    # ! may throw exception if not found
    def _title_from_tree(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    # extract product seller meta keyword from its product product page tree
    # ! may throw exception if not found
    def _seller_meta_from_tree(self):
        return self.tree_html.xpath("//meta[@itemprop='brand']/@content")[0]

    # extract product seller information from its product product page tree (using h2 visible tags)
    # TODO:
    #      test this in conjuction with _seller_meta_from_tree; also test at least one of the values is 1
    def _seller_from_tree(self):
        seller_info = {}
        h5_tags = map(lambda text: self._clean_text(text), self.tree_html.xpath("//h5//text()[normalize-space()!='']"))
        
        print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n\n'
        print h5_tags
        seller_info['owned'] = 1 if "fghjg" in h5_tags else 0
        seller_info['marketplace'] = 1 if "Other Sellers on Amazon" in h5_tags else 0

        return seller_info

    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        return re.sub("&nbsp;", " ", text).strip()




    def main(args):
        # check if there is an argument
        if len(args) <= 1:
            sys.stderr.write("ERROR: No product URL provided.\nUsage:\n\tpython crawler_service.py <tesco_product_url>\n")
            sys.exit(1)
    
        product_page_url = args[1]
    
        # check format of page url
        if not check_url_format(product_page_url):
            sys.stderr.write("ERROR: Invalid URL " + str(product_page_url) + "\nFormat of product URL should be\n\t http://www.tesco.com/direct/<part-of-product-name>/<product_id>.prd\n")
            sys.exit(1)
    
        return json.dumps(product_info(sys.argv[1], ["name", "short_desc", "keywords", "price", "load_time", "anchors", "long_desc"]))



    '''
    http://www.amazon.com/Dell-Inspiron-i3531-1200BK-15-6-Inch-Laptop/dp/B00KMRGF28/ref=sr_1_1?ie=UTF8&qid=1409586411&sr=8-1&keywords=dell
    
    x    name
    x    keywords
    x    short
    x    long
    x    price
    x    anchors
    x    htags
    x    features
    x    nr_features
    x    title
        seller
    x    product_id
    x    load_time
    x    image_url
        video_url
        
    x    brand
        model
        manufacturer_content_body
        pdf_url
        average_review
        total_reviews
    
    retail 40%
    licensors 3-10%
    liscensee 97%
    
    
    '''



    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service
    # 
    # data extracted from product page
    # their associated methods return the raw data
    DATA_TYPES = { \
        # Info extracted from product page
        "name" : _product_name_from_tree, \
        "keywords" : _meta_keywords_from_tree, \
        "short_desc" : _short_description_from_tree, \
        "long_desc" : _long_description_from_tree, \
        "price" : _price_from_tree, \
        "anchors" : _anchors_from_tree, \
        "htags" : _htags_from_tree, \
        "features" : _features_from_tree, \
        "nr_features" : _nr_features_from_tree, \
        "title" : _title_from_tree, \
        "seller": _seller_from_tree, \
        "product_id" : _extract_product_id, \
        "load_time": None, \
        "brand" : _meta_brand_from_tree, \
        "image_url" : _image_url, \
        "video_url" : video_for_url \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "model" : _model_from_tree, \
        "manufacturer_content_body" : manufacturer_content_body, \
        "pdf_url" : pdf_for_url, \
        "average_review" : reviews_for_url, \
        "total_reviews" : nr_reviews\
    }






if __name__=="__main__":
    AS = AmazonScraper()
    print AS.main(sys.argv)
