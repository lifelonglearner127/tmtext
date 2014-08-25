#!/usr/bin/python

import urllib
import re
import sys
import json

from lxml import html
import time

from extract_data import Scraper

class TescoScraper(Scraper):
    #TODO
    """
        DATA_TYPES = { \
        # Info extracted from product page
        "name" :         done
        "keywords" :     *Tesco does not seem to have meta name="Keywords"
        "brand" :        *Tesco does not seem to have meta name="Brand"
        "short_desc" :   done
        "long_desc" :    done, using Product Details, and NOT Product Specifications
        "price" :        done, passes through currency symbol
        "anchors" :      done, *I couldn't find examples on Tesco where product descriptions had links, but if one does, the updated code should catch them
        "htags" :        done
        "model" :        *Tesco does not seem to include model numbers, I searched maybe 2 dozen different products, and they only have a Tesco ID #
        "features" :     done
        "title" :        done
        "seller":        done
        "reviews":       *ratings container is coming up empty, help?

        "load_time":     done
        }
    """
    
    # TODO:
    #      better way of extracting id now that URL format is more permissive
    #      though this method still seems to work...
    def _extract_product_id(self):
        product_id = self.product_page_url.split('/')[-1]
        return product_id

    def _video_url(self):
        request_url = self.BASE_URL_VIDEOREQ + self._extract_product_id()

        #TODO: handle errors
        response_text = urllib.urlopen(request_url).read()

        # get first "src" value in response
        video_url_candidates = re.findall("src: \"([^\"]+)\"", response_text)
        if video_url_candidates:
            # remove escapes
            #TODO: better way to do this?
            video_url_candidate = re.sub('\\\\', "", video_url_candidates[0])

            # if it ends in flv, it's a video, ok
            if video_url_candidate.endswith(".flv"):
                return video_url_candidate

            # if it doesn't, it may be a url to make another request to, to get customer reviews video
            new_response = urllib.urlopen(video_url_candidate).read()
            video_id_candidates = re.findall("param name=\"video\" value=\"(.*)\"", new_response)

            if video_id_candidates:
                video_id = video_id_candidates[0]

                video_url_req = "http://client.expotv.com/vurl/%s?output=mp4" % video_id
                video_url = urllib.urlopen(video_url_req).url

                return video_url

        return None

    # return dictionary with one element containing the video url
    def video_for_url(self):
        video_url = self._video_url()
        results = {'video_url' : video_url}
        return results

    def _pdf_url(self):
        request_url = self.BASE_URL_PDFREQ + self._extract_product_id()

        response_text = urllib.urlopen(request_url).read().decode('string-escape')

        pdf_url_candidates = re.findall('(?<=")http[^"]*media\.webcollage\.net[^"]*[^"]+\.pdf(?=")', response_text)
        if pdf_url_candidates:
            # remove escapes
            pdf_url = re.sub('\\\\', "", pdf_url_candidates[0])

            return pdf_url

        else:
            return None

    # return dictionary with one element containing the PDF
    def pdf_for_url(self):
        results = {"pdf_url" : self._pdf_url()}
        return results

    # Deprecated
    def media_for_url(self):
        # create json object with video and pdf urls
        results = {'video_url' : _video_url(self.product_page_url), \
                    'pdf_url' : _pdf_url(self.product_page_url)}
        return results

    def reviews_for_url(self):
        request_url = self.BASE_URL_REVIEWSREQ.format(self._extract_product_id())
        content = urllib.urlopen(request_url).read()
        try:
            reviews_count = re.findall(r"BVRRNonZeroCount\\\"><span class=\\\"BVRRNumber\\\">([0-9,]+)<", content)[0]
            average_review = re.findall(r"class=\\\"BVRRRatingNormalOutOf\\\"> <span class=\\\"BVRRNumber BVRRRatingNumber\\\">([0-9\.]+)<", content)[0]
        except Exception, e:
            return {"reviews" : {"total_reviews": None, "average_review": None}}
        return {"reviews" : {"total_reviews": reviews_count, "average_review": average_review}}


    # extract product name from its product page tree
    # ! may throw exception if not found
    def _product_name_from_tree(self, tree_html):
        return tree_html.xpath("//h1")[0].text

    # extract meta "keywords" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_keywords_from_tree(self, tree_html):
        return tree_html.xpath("//meta[@name='Keywords']/@content")[0]

    # extract meta "brand" tag for a product from its product page tree
    # ! may throw exception if not found
    def _meta_brand_from_tree(self, tree_html):
        return tree_html.xpath("//meta[@itemprop='brand']/@content")[0]


    # extract product short description from its product page tree
    # ! may throw exception if not found
    def _short_description_from_tree(self, tree_html):
        short_description = " ".join(tree_html.xpath("//ul[@class='features']/li//text()")).strip()
        return short_description

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description_from_tree(self, tree_html):
        full_description = " ".join(tree_html.xpath("//section[@id='product-details-link']/section[@class='detailWrapper']//text()")).strip()
        # TODO: return None if no description
        return full_description


    # extract product price from its product product page tree
    def _price_from_tree(self, tree_html):
        meta_price = tree_html.xpath("//p[@class='current-price']//text()")
        if meta_price:
            return meta_price[0].strip()
        else:
            return None

    # extract product price from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - test
    #      - is format ok?
    def _anchors_from_tree(self, tree_html):
        # get all links found in the description text
        description_node = tree_html.xpath("//section[@class='detailWrapper']")[0]
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
    def _htags_from_tree(self, tree_html):
        htags_dict = {}

        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), tree_html.xpath("//h2//text()[normalize-space()!='']"))

        return htags_dict

    # extract product model from its product product page tree
    # ! may throw exception if not found
    def _model_from_tree(self, tree_html):
        return tree_html.xpath("//table[@class='SpecTable']//td[contains(text(),'Model')]/following-sibling::*/text()")[0]

    # extract product features list from its product product page tree, return as string
    def _features_from_tree(self, tree_html):
        # join all text in spec table; separate rows by newlines and eliminate spaces between cells
        rows = tree_html.xpath("//section[@class='detailWrapper']//tr")
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
        return {"features_list": all_features_text, "nr_features": self._nr_features_from_tree(tree_html)}

    # extract number of features from tree
    # ! may throw exception if not found
    def _nr_features_from_tree(self, tree_html):
        # select table rows with more than 2 cells (the others are just headers), count them
        return len(filter(lambda row: len(row.xpath(".//td"))>0, tree_html.xpath("//section[@class='detailWrapper']//tr")))

    # extract page title from its product product page tree
    # ! may throw exception if not found
    def _title_from_tree(self, tree_html):
        return tree_html.xpath("//title//text()")[0].strip()

    # extract product seller meta keyword from its product product page tree
    # ! may throw exception if not found
    def _seller_meta_from_tree(self, tree_html):
        return tree_html.xpath("//meta[@itemprop='brand']/@content")[0]

    # extract product seller information from its product product page tree (using h2 visible tags)
    # TODO:
    #      test this in conjuction with _seller_meta_from_tree; also test at least one of the values is 1
    def _seller_from_tree(self, tree_html):
        seller_info = {}
        h2_tags = map(lambda text: self._clean_text(text), tree_html.xpath("//h2//text()"))
        seller_info['owned'] = 1 if "Buy on Tesco Direct from:" in h2_tags else 0
        seller_info['marketplace'] = 1 if "more buying option(s) from:" in h2_tags else 0

        return seller_info

    # extract product reviews information from its product page
    # ! may throw exception if not found
    #TODO: For Tesco, the BVRRSummaryContainer is coming up empty for some reason.
    def _reviews_from_tree(self, tree_html):
        reviews_info_node = tree_html.xpath("//div[@id='BVRRSummaryContainer']")[0]
        
        '''
        print "--------"
        print html.tostring(tree_html.xpath("//div[@class='details-container']")[0])
        #print html.tostring(reviews_info_node)
        print "--------"
        '''
        
        average_review = (reviews_info_node.xpath("//span[@itemprop='ratingValue']/text()")[0])
        nr_reviews = (reviews_info_node.xpath("//span[@itemprop='reviewCount']/text()")[0])

        return {'total_reviews' : nr_reviews, 'average_review' : average_review}


    # clean text inside html tags - remove html entities, trim spaces
    def _clean_text(self, text):
        return re.sub("&nbsp;", " ", text).strip()


    # TODO: fix to work with restructured code
    def main(args):
        print 'main'
        # check if there is an argument
        if len(args) <= 1:
            sys.stderr.write("ERROR: No product URL provided.\nUsage:\n\tpython extract_walmart_media.py <walmart_product_url>\n")
            sys.exit(1)

        product_page_url = args[1]

        # check format of page url
        if not check_url_format(product_page_url):
            sys.stderr.write("ERROR: Invalid URL " + str(product_page_url) + "\nFormat of product URL should be\n\t http://www.walmart.com/ip/<product_id>\n")
            sys.exit(1)

        return json.dumps(product_info(sys.argv[1], ["name", "short_desc", "keywords", "price", "load_time", "anchors", "long_desc"]))

        # create json object with video and pdf urls
        #return json.dumps(media_for_url(product_page_url))
    #    return json.dumps(reviews_for_url(product_page_url))



    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service
    # 
    # data extracted from product page
    # their associated methods return the raw data
    DATA_TYPES = { \
        # Info extracted from product page
        "name" : _product_name_from_tree, \
        "keywords" : _meta_keywords_from_tree, \
        "brand" : _meta_brand_from_tree, \
        "short_desc" : _short_description_from_tree, \
        "long_desc" : _long_description_from_tree, \
        "price" : _price_from_tree, \
        "anchors" : _anchors_from_tree, \
        "htags" : _htags_from_tree, \
        "model" : _model_from_tree, \
        "features" : _features_from_tree, \
        "title" : _title_from_tree, \
        "seller": _seller_from_tree, \
        "reviews": _reviews_from_tree, \

        "load_time": None \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "video_url" : video_for_url, \
        "pdf_url" : pdf_for_url, \
    #    "reviews" : reviews_for_url \
    }


if __name__=="__main__":
    WD = WalmartScraper()
    print WD.main(sys.argv)

## TODO:
## Implemented:
##     - name
##  - meta keywords
##  - short description
##  - long description
##  - price
##  - url of video
##  - url of pdf
##  - anchors (?)
##  - H tags 
##  - page load time (?)
##  - number of reviews
##  - model
##  - list of features
##  - meta brand tag
##  - page title
##  - number of features
##  - sold by walmart / sold by marketplace sellers

##  
## To implement:
##     - number of images, URLs of images
##  - number of videos, URLs of videos if more than 1
##  - number of pdfs
##  - category info (name, code, parents)
##  - minimum review value, maximum review value
