#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html
import time
import requests
from extract_data import Scraper

class TescoScraper(Scraper):
    '''Josh's TODO
    PDF & VIDEO------------------------------------------------------------
    For PDFs and Videos, what you're really looking for is "content provided by manufacturer
    PDFs and Videos as their own items are of value, but the higher level tag is good too.
    
    pdf example   -
    video example - http://www.tesco.com/direct/hudl-7-16gb-wi-fi-android-tablet-purple/275-3055.prd?skuId=275-3055
                    http://www.tesco.com/direct/kindle-fire-hd-7-16gb-wifi-2013/157-2058.prd
                    http://www.tesco.com/direct/kindle-paperwhite-2013-wi-fi/538-8448.prd
    link example  - http://www.tesco.com/direct/hudl-7-16gb-wi-fi-android-tablet-purple/275-3055.prd?skuId=275-3055
    no image example -  the following are probably not really no-image examples
                        ??? http://www.tesco.com/direct/canford-card-a1/228-1822.prd
                        ??? http://www.tesco.com/direct/nvidia-quadro-410-graphics-card-512mb/538-8755.prd
                        ??? http://www.tesco.com/direct/canford-card-a1/228-1822.prd
    
    PRODUCT DESCRIPTION------------------------------------------------------------
    separating the product description into description (as we have now) and "manufacturer provided description"?
    The former is the stuff obviously native to the site, the latter is the stuff dynamically loaded and provided 
    by manufacturer. Give it a name like "manufacturer_content" binary, and if there is text, send it back as 
    "manufacturer_content_body" if easy.
    
    GENERIC TODO---------------------------------------------------------------
    1) Finish tesco crawler. Which means we need to talk about image detection.
        x video
        x image
        - pdf
        x description / manufacturer description
    
    2) Amazon Crawler.
    
    3) How to guide
    
    4) Other crawlers
    
    IMAGE DETECTION------------------------------------------------------------
    OK, so, here's what we found.
    
    You need to find a page with no product image.
    
    You need to take that image, and when you do the comparison, you actually have to hash the image data itself after loading it. If you hash the file information they all show up different because of meta-data. 
    
    Does that make sense?
    [3:47:44 PM] Josh Freckleton: not quite. Am i scraping image hashes to compare the hashes just to see if it's the same picture? or what exactly? I'd imagine you'd want image urls at least
    [3:49:41 PM] jeff green: So, if the site uses a single URL, that's great. You can just check if it's the no image url.
    
    But most seem to be somewhat dynamic and generate different urls. 
    
    When this happens, the picture loaded is created at a different time.
    [3:50:02 PM] jeff green: So, you have to load the image into memory, and hash the image data, rather than just check location, or hash file data after crawl before load.
    [3:50:12 PM] jeff green: Let's continue this chat tomorrow.
    
    
    
    '''
    
    #Holds a JSON variable that contains information scraped from a query which Tesco makes through javascript
    bazaarvoice = None
    
    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match("^http://www.tesco.com/direct/[0-9a-zA-Z-]+/[0-9-]+\.prd$", self.product_page_url)
        return not not m
    
    # TODO:
    #      better way of extracting id now that URL format is more permissive
    #      though this method still seems to work...
    def _extract_product_id(self):
        product_id = self.product_page_url.split('/')[-1]
        product_id = product_id.split('.')[0]
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
        head = 'http://tesco.scene7.com/is/image/'
        image_url = self.tree_html.xpath("//section[@class='main-details']//script//text()")[1]
        image_url = re.findall("scene7PdpData\.s7ImageSet = '(.*)';", image_url)[0]
        image_url = image_url.split(',')
        image_url = [head+link for link in image_url]
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
        nr_reviews = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['TotalReviewCount']
    
        return {'average_review' : average_review, 'nr_reviews' : nr_reviews}


    # extract product name from its product page tree
    # ! may throw exception if not found
    def _product_name_from_tree(self):
        return self.tree_html.xpath("//h1")[0].text

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_keywords_from_tree(self):
        return None

    # extract meta "brand" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_brand_from_tree(self):
        if not self.bazaarvoice:
            self.load_bazaarvoice()
        return self.bazaarvoice['BatchedResults']['q0']['Results'][0]['Brand']['Name']


    # extract product short description from its product page tree
    # ! may throw exception if not found
    def _short_description_from_tree(self):
        short_description = " ".join(self.tree_html.xpath("//ul[@class='features']/li//text()")).strip()
        return short_description

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description_from_tree(self):
        #TODO: Needs some logic for deciding when Tesco is displaying one format or the other, the following 2 lines are the currently encountered versions
        #full_description = " ".join(self.tree_html.xpath("//section[@id='product-details-link']/section[@class='detailWrapper']//text()")).strip()
        full_description = " ".join(self.tree_html.xpath('//section[@id="product-details"]//text()')).strip()
        
        return full_description


    # extract product price from its product product page tree
    def _price_from_tree(self):
        meta_price = self.tree_html.xpath("//p[@class='current-price']//text()")
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
        description_node = self.tree_html.xpath("//section[@class='detailWrapper']")[0]
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
        rows = self.tree_html.xpath("//div[@class='product-spec-container']//tr")
        
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
        return {"features_list": all_features_text, "nr_features": self._nr_features_from_tree()}

    # extract number of features from tree
    # ! may throw exception if not found
    def _nr_features_from_tree(self):
        # select table rows with more than 2 cells (the others are just headers), count them
        return len(filter(lambda row: len(row.xpath(".//td"))>0, self.tree_html.xpath("//div[@class='product-spec-container']//tr")))

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
        h2_tags = map(lambda text: self._clean_text(text), self.tree_html.xpath("//h2//text()"))
        seller_info['owned'] = 1 if "Buy on Tesco Direct from:" in h2_tags else 0
        seller_info['marketplace'] = 1 if "more buying option(s) from:" in h2_tags else 0

        return seller_info

    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        return re.sub("&nbsp;", " ", text).strip()


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
        "title" : _title_from_tree, \
        "seller": _seller_from_tree, \
        "product_id" : _extract_product_id, \
        "load_time": None, \
        "image_url" : _image_url, \
        "video_url" : video_for_url \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "brand" : _meta_brand_from_tree, \
        "model" : _model_from_tree, \
        "manufacturer_content_body" : manufacturer_content_body, \
        "pdf_url" : pdf_for_url, \
        "reviews" : reviews_for_url \
    }


if __name__=="__main__":
    WD = WalmartScraper()
    print WD.main(sys.argv)
