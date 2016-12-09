#!/usr/bin/python

import urllib
import urlparse
import re
import sys
import json
import os.path
import urllib, cStringIO
from io import BytesIO
from PIL import Image
import mmh3 as MurmurHash
from lxml import html
from lxml import etree
import time
import requests
from extract_data import Scraper

class TescoScraper(Scraper):
    '''
    NOTES :

    no/broken image example:
        http://www.tesco.com/direct/torch-keychain-1-led/592-8399.prd

    hp no image:
        http://www.tesco.com/direct/nvidia-nvs-310-graphics-card-512mb/436-0793.prd

    '''

    ##########################################
    ############### PREP
    ##########################################
    INVALID_URL_MESSAGE = "Expected URL format is http://www.tesco.com/direct/<part-of-product-name>/<product_id>.prd \
                           or http://www.tesco.com/groceries/product/details/?id=<product_id>"

    #Holds a JSON variable that contains information scraped from a query which Tesco makes through javascript
    pdfs = None
    is_youtube_video_checked = False
    youtube_video_info = None
    is_pdf_checked = False
    pdf_info = None
    is_bazzarvoice_checked = False
    bazaarvoice = None
    version_2_product_json = None

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """
        m = re.match("^http://www.tesco.com/direct/[0-9a-zA-Z-]+/[0-9-]+\.prd$", self.product_page_url)
        n = re.match("^http://www.tesco.com/.*$", self.product_page_url)
        return (not not m) or (not not n)

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        self.scraper_version = self._version()

        try:
            page_title = self.tree_html.xpath("//title/text()")[0]
        except Exception:
            page_title = ""

        if page_title.find('not found')>0 or page_title.find('Error')>0:
            return True
        elif self.scraper_version=="groceries":
            prod_cont = self.tree_html.xpath("//div[@class='productDetailsContainer']")
            if prod_cont == None or len(prod_cont) == 0:
                return True

        if self.scraper_version == "version-2":
            self.extract_version_2_product_json()

        return False

    def extract_version_2_product_json(self):
        product_json = self._find_between(self.page_raw_text, '\noProduct =\n', ',\noSku =')

        try:
            product_json = json.loads(product_json)
        except:
            print "Error occurred while parsing 2nd version product info json."

        sku_json = self._find_between(self.page_raw_text, ',\noSku =\n', ',\noAssetData =')

        try:
            sku_json = json.loads(sku_json)
        except:
            print "Error occurred while parsing 2nd version sku info json."

        asset_json = self._find_between(self.page_raw_text, ',\noAssetData =\n', ';\nwindow.oAppController')

        try:
            asset_json = json.loads(asset_json)
        except:
            print "Error occurred while parsing 2nd version asset info json."

        version_2_product_json = {}

        if product_json:
            version_2_product_json["product"] = product_json

        if sku_json:
            version_2_product_json["sku"] = sku_json

        if asset_json:
            version_2_product_json["asset"] = asset_json

        if version_2_product_json:
            self.version_2_product_json = version_2_product_json


    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        if self.scraper_version=="groceries":
            product_id = self.product_page_url.split('/')[-1][4:]
            return product_id

        product_id = self.product_page_url.split('/')[-1]
        product_id = product_id.split('.')[0]
        return product_id

    def _site_id(self):
        return None

    def _status(self):
        return "success"





    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        if self.scraper_version == "groceries":
            return self.tree_html.xpath("//h1//text()")[0]
        elif self.scraper_version == "version-2":
            return self.version_2_product_json["product"]["displayName"]

        return self.tree_html.xpath("//h1")[0].text

    def _product_title(self):
        if self.scraper_version == "groceries":
            return self.tree_html.xpath("//h1//text()")[0]
        elif self.scraper_version == "version-2":
            return self.version_2_product_json["product"]["displayName"]

        return self.tree_html.xpath("//meta[@property='og:title']/@content")[0]

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        if self.scraper_version == "groceries":
            return None

        self.load_bazaarvoice()

        try:
            m = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['ModelNumbers'][0]
        except:
            m = None
        return m

    def _upc(self):
        if self.scraper_version == "groceries":
            return None
        return self.tree_html.xpath('//meta[@property="og:upc"]/@content')[0]

    def _features(self):
        if self.scraper_version == "groceries":
            fts = self.tree_html.xpath("//div[@class='detailsWrapper'][3]//tbody//tr")
            fs=[]
            for row  in fts:
                a = row.xpath(".//th//text()")[0]
                b = " ".join( row.xpath(".//td//text()"))
                fs.append(a+" "+b)
            if len(fs)==0: return None
            return fs

        features_row_list = self.tree_html.xpath("//div[@id='product-spec-container']//div[@class='product-spec-row']")
        all_features_list = []

        for feature_row in features_row_list:
            all_features_list.append("{0} {1}".format(
                feature_row.xpath(".//div[contains(@class, 'product-spec-label')]/text()")[0].strip(),
                feature_row.xpath(".//div[contains(@class, 'product-spec-value')]/text()")[0].strip()))

        if all_features_list:
            return all_features_list

        #TODO: Needs some logic for deciding when Tesco is displaying one format or the other, the following 2 lines are the currently encountered versions
        #rows = self.tree_html.xpath("//section[@class='detailWrapper']//tr")

        rows = self.tree_html.xpath("//div[@class='product-spec-container']//tr")

        # list of lists of cells (by rows)
        cells = map(lambda row: row.xpath(".//*//text()"), rows)
        # list of text in each row

        rows_text = map(\
            lambda row: " ".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        all_features_list = list(rows_text)

        # return dict with all features info
        return all_features_list if all_features_list else None

    def _feature_count(self):
        f = self._features()

        return len(f) if f else 0

    def _model_meta(self):
        return None

    def _description(self):
        if self.scraper_version == "groceries":
            hide_text_blocks_in_description = self.tree_html.xpath("//div[@class='detailsWrapper']//h2[@class='hide']")

            for hide_block in hide_text_blocks_in_description:
                hide_block.getparent().remove(hide_block)

            return " ".join(self.tree_html.xpath("//div[@class='detailsWrapper'][1]//text()")).strip()

        if self.scraper_version == "version-2":
            description = self.tree_html.xpath("//div[@itemprop='description']/text()")
            return description[0].strip() if description else None

        description = " ".join(self.tree_html.xpath("//ul[@class='features']/li//text()")).strip()
        if len(description) < 4:
            return self._long_description_temp()
        return description

    def _long_description(self):
        if self.scraper_version == "groceries":
            el = self.tree_html.xpath("//div[@class='detailsWrapper'][2]//div[@class='content']")
            if len(el)>0:
                rdata = html.tostring(el[0])
                st = rdata.find('"content">')
                fn = rdata.find('</div>')
                pt1 = pt2 = 0
                if st > 0:
                    st += 10
                    pt1 = rdata.find('<h4>Manufacturer',st)
                    if pt1 > 0:
                        pt2 = rdata.find('</p>',pt1)
                    pt3 = rdata.find('<h4>Return')
                    if pt3 > 0:
                        if pt1 < 0 :
                            pt1 = pt3
                        pt4 = rdata.find('</p>',pt3)
                        if pt4 > 0:
                            pt2 = pt4
                    if pt1 > 0 and pt2 > 0:
                        return rdata[st:pt1] + rdata[pt2:fn]
                    else:
                        return rdata[st:fn]
                else:
                    return  " ".join(self.tree_html.xpath("//div[@class='detailsWrapper'][2]//text()")).strip()

        if self.scraper_version == "version-2":
            return None

        d1 = self._description()
        d2 = self._long_description_temp()

        if d1 == d2:
            return None
        return d2

    def _long_description_temp(self):
        #this first description was written for book description
        description = " ".join(self.tree_html.xpath('//section[@id="product-details-link"]//section//text()')).strip()
        if len(description) > 2:
            return description
        description = " ".join([self._clean_text(x) for x in self.tree_html.xpath('//*[@class="detailWrapper"]//text()')])
        if len(description)>5:
            return description

        self.load_bazaarvoice()

        try:
            content = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['Description']
        except:
            content = None
        return content



    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #extract meta tags exclude http-equiv
    def _meta_tags(self):
        tags = map(lambda x:x.values() ,self.tree_html.xpath('//meta[not(@http-equiv)]'))
        return tags

    def _meta_tag_count(self):
        tags = self._meta_tags()
        return len(tags)

    def check_image_urls(self,img_urls):
        return img_urls
        #speed up
        '''
        pc_headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        res = []
        for img_url in img_urls:
            contents = requests.get(img_url, headers=pc_headers).text
            tree = html.fromstring(contents)
            images = tree.xpath("//title//text()")
            if not (images != None and len(images) > 0 and (images[0].find("not found") > 0 or images[0].find("Error")>=0) ):
                res.append(img_url)
        if len(res)==0 : return None
        return res
        '''

    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        url = self.product_page_url
        mobile_headers = {"User-Agent" : "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5"}
        pc_headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        img_list = []
        if self.scraper_version == "groceries":
            for h in [mobile_headers, pc_headers]:
                contents = requests.get(url, headers=h).text
                tree = html.fromstring(contents)
                image_url = self._image_urls(tree)
            #    print '\n\n\nImage URL:', image_url, '\n\n\n'
                if image_url != None:
                    img_list.extend(image_url)
            if len(img_list) == 2:
                if img_list[0] == img_list[1]: return 1
            return 0

        for h in [mobile_headers, pc_headers]:
            contents = requests.get(url, headers=h).text
            tree = html.fromstring(contents)

            head = 'http://tesco.scene7.com/is/image/'
            image_url = tree.xpath("//section[@class='main-details']//script//text()")[1]
            image_url = re.findall("scene7PdpData\.s7ImageSet = '(.*)';", image_url)[0]
            image_url = image_url.split(',')
            image_url = [head+link for link in image_url]
            image_url = image_url[0]
            img_list.append(image_url)

        if len(img_list) == 2:
            if img_list[0] == img_list[1]: return 1
        return 0

    def _image_urls(self,tree=None):
        if self.scraper_version == "groceries":
            if tree == None:
                tree = self.tree_html
            image_url = tree.xpath("//div[@class='productImage']//img//@src")
            if len(image_url)==0:
                image_url = tree.xpath("//div[@id='productImages']//ul[@class='productImagesList']//a//@href")
            contents = tree.xpath("//script[@id=\"zoomedProductImageTemplate\"]//text()")
            if len(contents) > 0:
                imgtree = html.fromstring(contents[0])
                image_urlz = imgtree.xpath("//ul[@class='zoomedImagesList']//img//@src")
                if len(image_urlz) > len(image_url): image_url = image_urlz
            if len(image_url)==0: return None
            for s in image_url:
                if s.find('noimage')>0:
                    image_url.remove(s)
            if(len(image_url)==0): return None

            return self.check_image_urls(image_url)

        if self.scraper_version == "version-2":
            image_url_list = []

            for asset in self.version_2_product_json["sku"]["mediaAssets"]["skuMedia"]:
                if asset["mediaType"] == "Large":
                    image_url_list.append(urlparse.urljoin("http://www.tesco.com/", asset["src"]))

            return image_url_list if image_url_list else None

        head = 'http://tesco.scene7.com/is/image/'
        image_url = self.tree_html.xpath("//section[@class='main-details']//script//text()")
        if(len(image_url)>0):
            image_url = re.findall("scene7PdpData\.s7ImageSet = '(.*)';", image_url[1])
            if(len(image_url)>0):
                image_url = image_url[0].split(',')
                image_url = [head+link for link in image_url]
                if(len(image_url)>0):
                    return self.check_image_urls(image_url)

        #img id='scene7-placeholder'
        image_url = self.tree_html.xpath('//img[@id="scene7-placeholder"]//@src')
        if(len(image_url)==0): return None
        return self.check_image_urls(image_url)

    def _image_count(self):
        image_urls = self._image_urls()

        return len(image_urls) if image_urls else 0

    def _video_urls(self):
        if self.scraper_version in ["groceries", "version-2"]:
            return None

        try:
            video_url = self.tree_html.xpath("//section[@class='main-details']//script//text()")[1]
            video_url = re.search("\['http.*\.flv\']", video_url.strip()).group()
            video_url = re.findall("'(.*?)'", video_url)
            return video_url
        except:
            return None

    def _video_youtube(self):
        #Find an embedded youtube link
        if self.is_youtube_video_checked:
            return self.youtube_video_info

        self.is_youtube_video_checked = True

        youtube = 0
        url = self.tree_html.xpath('//div[@id="inlineContentURL"]//text()')
        if len(url)>0:
            req = requests.get(url[0]).text
            if len(req)>0 and req.find('youtube.com') > 0:
                youtube = 1

        self.youtube_video_info = youtube

        return self.youtube_video_info

    def _video_count(self):
        if self.scraper_version in ["groceries", "version-2"]:
            return 0

        urls = self._video_urls()
        yt = self._video_youtube()
        vt = 0
        if urls:
            vt = len(urls)
        vt += yt
        if vt > 0:
            return vt
        return 0

    def _pdf_helper(self):
        if self.is_pdf_checked:
            return self.pdf_info

        self.is_pdf_checked = True

        pf = []
        url = self.tree_html.xpath('//div[@id="inlineContentURL"]//text()')
        if len(url)>0:
            req = requests.get(url[0]).text
            if len(req)>10 and req.find('.pdf')>7:
                i=j= len(req)-4
                while i>0:
                    i -= 1
                    if req[i:i+4]=='.pdf':
                        j=i+4
                    if req[i:i+5]=='http:' and j-i > 15 and j-i < 250:
                        pf.append(req[i:j])
                        j = 0

        self.pdf_info = pf

        return self.pdf_info

    def _pdf_urls(self):
        if self.scraper_version in ["groceries", "version-2"]:
            return None

        res = self._pdf_helper()
        if len(res)==0: return None
        return res

    def _pdf_count(self):
        urls = self._pdf_urls()

        return len(urls) if urls else 0

    #populate the bazaarvoice variable for use by other functions
    def load_bazaarvoice(self):
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        # http://api.bazaarvoice.com/data/batch.json?passkey=asiwwvlu4jk00qyffn49sr7tb&apiversion=5.4&displaycode=1235-en_gb&resource.q0=products&filter.q0=id%3Aeq%3A518-7080&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_AU%2Cen_CA%2Cen_DE%2Cen_GB%2Cen_IE%2Cen_NZ%2Cen_US
        # http://api.bazaarvoice.com/data/batch.json?passkey=asiwwvlu4jk00qyffn49sr7tb&apiversion=5.5&displaycode=1235-en_gb&resource.q0=products&filter.q0=id%3Aeq%3A210-0593&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_AU%2Cen_CA%2Cen_DE%2Cen_GB%2Cen_IE%2Cen_NZ%2Cen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_AU%2Cen_CA%2Cen_DE%2Cen_GB%2Cen_IE%2Cen_NZ%2Cen_US&resource.q1=reviews&filter.q1=isratingsonly%3Aeq%3Afalse&filter.q1=productid%3Aeq%3A210-0593&filter.q1=contentlocale%3Aeq%3Aen_AU%2Cen_CA%2Cen_DE%2Cen_GB%2Cen_IE%2Cen_NZ%2Cen_US&sort.q1=submissiontime%3Adesc&stats.q1=reviews&filteredstats.q1=reviews&include.q1=authors%2Cproducts%2Ccomments&filter_reviews.q1=contentlocale%3Aeq%3Aen_AU%2Cen_CA%2Cen_DE%2Cen_GB%2Cen_IE%2Cen_NZ%2Cen_US&filter_reviewcomments.q1=contentlocale%3Aeq%3Aen_AU%2Cen_CA%2Cen_DE%2Cen_GB%2Cen_IE%2Cen_NZ%2Cen_US&filter_comments.q1=contentlocale%3Aeq%3Aen_AU%2Cen_CA%2Cen_DE%2Cen_GB%2Cen_IE%2Cen_NZ%2Cen_US&limit.q1=8&offset.q1=0&limit_comments.q1=3&callback=bv_183_31233
        # sometimes Tesco ID isn't same as Bazaar ID
        # DATA.Bazaar.productID = '210-0593'
        if self.is_bazzarvoice_checked:
            return self.bazaarvoice

        self.is_bazzarvoice_checked = True

        if self.scraper_version == "version-2":
            bazaar_id = self.version_2_product_json["sku"]["id"]
        else:
            bazaar_id = ' '.join(self.tree_html.xpath('//script//text()'))
            bazaar_id = re.findall(r"DATA\.Bazaar\.productID \= '([0-9]{2,5}.[0-9]{2,5})'", bazaar_id)[0]
            bazaar_id = str(bazaar_id)

        url = "http://api.bazaarvoice.com/data/batch.json?passkey=asiwwvlu4jk00qyffn49sr7tb&apiversion=5.4&displaycode=1235-en_gb&resource.q0=products&filter.q0=id%3Aeq%3A" \
        + bazaar_id + \
        "&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_AU%2Cen_CA%2Cen_DE%2Cen_GB%2Cen_IE%2Cen_NZ%2Cen_US"
        req = requests.get(url)

        self.bazaarvoice = req.json()

        return self.bazaarvoice

    def _webcollage(self):
        return None

    # extract htags (h1, h2) from its product product page tree
    def _htags(self):
        htags_dict = {}
        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        if self.scraper_version == "groceries":
            return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]

        return None

    # return True if there is a no-image image and False otherwise
    # Certain products have an image that indicates "there is no image available"
    # a hash of these "no-images" is saved to a json file and new images are compared to see if they're the same
    def _no_image(self):
        #get image urls
        head = 'http://tesco.scene7.com/is/image/'
        image_url = self.tree_html.xpath("//section[@class='main-details']//script//text()")[1]
        image_url = re.findall("scene7PdpData\.s7ImageSet = '(.*)';", image_url)[0]
        image_url = image_url.split(',')
        image_url = [head+link for link in image_url]
        path = 'no_img_list.json'
        no_img_list = []
        if os.path.isfile(path):
            f = open(path, 'r')
            s = f.read()
            if len(s) > 1:
                no_img_list = json.loads(s)
            f.close()
        first_hash = str(MurmurHash.hash(self.fetch_bytes(image_url[0])))
        if first_hash in no_img_list:
            return True
        else:
            return False


    #read the bytes of an image
    def fetch_bytes(self, url):
        file = cStringIO.StringIO(urllib.urlopen(url).read())
        img = Image.open(file)
        b = BytesIO()
        img.save(b, format='png')
        data = b.getvalue()
        return data






    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _average_review(self):
        if self.scraper_version == "groceries":
            return None

        self.load_bazaarvoice()
        average_review = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['AverageOverallRating']
        return average_review

    def _review_count(self):
        if self.scraper_version == "groceries":
            return 0

        self.load_bazaarvoice()

        if self.bazaarvoice['BatchedResults']['q0']['Results']:
            nr_reviews = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['TotalReviewCount']
            return nr_reviews

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

    def _reviews(self):
        self.load_bazaarvoice()

        if self.bazaarvoice['BatchedResults']['q0']['Results']:
            stars = self.bazaarvoice['BatchedResults']['q0']['Results'][0]['FilteredReviewStatistics']['RatingDistribution']
            rev = []

            for s in stars:
                a = s['RatingValue']
                b = s['Count']
                rev.append([a, b])

            showing_mark = [review[0] for review in rev]

            for mark in range(1, 6):
                if mark not in showing_mark:
                    rev.append([mark, 0])

            if len(rev) > 0:
                return sorted(rev, key=lambda x: x[0])

        return None



    ##########################################
    ############### CONTAINER : SELLERS *************************************************************************88
    ##########################################
    def _temp_price_cut(self):
        if self.tree_html.xpath("//div[@class='price-info']//span[@class='saving']"):
            return 1

        if self.scraper_version == "groceries" and\
                self.tree_html.xpath("//a[@class='promotionAlternatives' and "
                                     "starts-with(@href, '/groceries/specialoffers/specialofferdetail/') and "
                                     "starts-with(@title, 'Save')]"):
            return 1

        return 0

    def _price(self):
        if self._owned_out_of_stock() == 1:
            return "out of stock - no price given"
        if self.scraper_version == "groceries":
            meta_price = self.tree_html.xpath("//span[@class='linePrice']//text()")
        elif self.scraper_version == "version-2":
            return u'\u00a3' + self.version_2_product_json["product"]["prices"]["price"]
        else:
            meta_price = self.tree_html.xpath("//p[@class='current-price']//text()")

        if meta_price:
            return meta_price[0].strip()
        else:
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
        if curr == u'\u00a3':
            return "GBP"
        return curr

    def _in_stores_only(self):
        return None

    def _in_stores(self):
        return None

    def _owned(self):
        span_txt = self.tree_html.xpath("//span[@class='available-from']//text()")
        if span_txt:
            if span_txt[0].find("Tesco") < 0:
                return 0
        return 1

    def _marketplace(self):
        span_txt = self.tree_html.xpath("//span[@class='available-from']//text()")
        if span_txt:
            if span_txt[0].find("Tesco") < 0:
                return 1
        return 0

    def _in_stock(self):
        if self._owned_out_of_stock() == 1:
            return 0
        return 1

    def _owned_out_of_stock(self):
        um = self.tree_html.xpath('//p[@class="warning unavailableMsg"]//text()')
        if len(um)>0 and um[0].find("not available")>=0:
            return 1
        return None

    def _site_online_out_of_stock(self):
        if self._site_online() == 0: return None
        um = self.tree_html.xpath('//p[@class="warning unavailableMsg"]//text()')
        if len(um)>0 and um[0].find("not available")>=0:
            return 1
        um = self.tree_html.xpath('//p[@class="not-available-tesco"]//text()')
        if len(um)>0 and um[0].find("Sorry")>=0:
            return 1
        return 0

    def _marketplace_sellers(self):
        a = self.tree_html.xpath('//span[@class="available-from"]//text()')
        if len(a) > 0 and a[0].find("Tesco") < 0:
            return ",".join([b[15:].strip() for b in a])
        return None

    def _marketplace_lowest_price(self):
        return None

    def _marketplace_out_of_stock(self):
        if self._marketplace()==1:
            um = self.tree_html.xpath('//p[@class="warning unavailableMsg"]//text()')
            if len(um)>0 and um[0].find("not available"):
                return 1
            return 0
        return None

    def _site_online(self):
        if self._marketplace()==1: return 0
        return 1





    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        if self.scraper_version == "groceries":
            categories = self.tree_html.xpath("//ul[@id='breadcrumbNav']//li[@class='f']/a//text()")
            return categories

        if self.scraper_version == "version-2":
            categories = self.tree_html.xpath("//div[@id='breadcrumb-v2']//ul/li//span[@itemprop='title']/text()")
            categories = [category.strip() for category in categories]
            return categories[1:-1]

        all = self.tree_html.xpath("//div[@id='breadcrumb']//li//span/text()")
        out = all[1:-1]#the last value is the product itself, and the first value is "home"
        out = [self._clean_text(r) for r in out]
        #out = out[::-1]
        return out

    def _category_name(self):
        dept = self._categories()[-1]
        return dept

    def _brand(self):
        if self.scraper_version == "groceries":
            return None

        if self.scraper_version == "version-2":
            return self.version_2_product_json["product"]["brand"]

        self.load_bazaarvoice()

        return self.bazaarvoice['BatchedResults']['q0']['Results'][0]['Brand']['Name'] \
            if self.bazaarvoice['BatchedResults']['q0']['Results'] else None

    def _version(self):
        """Determines if Tesco groceries page being read
        Returns:
            "groceries" for groceries pages
            "direct" for Tesco direct
        """
         # using url to distinguish between page versions.
        if self.product_page_url.find("/groceries/")>1:
            return "groceries"

        if "PDP-Version2" in self.tree_html.xpath("//body/@class")[0]:
            return "version-2"

        return "direct"

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
        "upc" : _upc,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "model_meta" : _model_meta, \
        "description" : _description, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "meta_tags": _meta_tags,\
        "meta_tag_count": _meta_tag_count,\

        # CONTAINER : SELLERS
        "price" : _price, \
        "temp_price_cut": _temp_price_cut, \
        "price_amount": _price_amount, \
        "price_currency": _price_currency, \
#        "in_stock" : _in_stock, \
        "in_stores_only" : _in_stores_only, \
        "in_stores" : _in_stores, \
#        "owned" : _owned, \
#        "owned_out_of_stock" : _owned_out_of_stock, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "marketplace_out_of_stock" : _marketplace_out_of_stock,\
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock,\
        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "scraper" : _version, \
        "loaded_in_seconds": None \
        }


    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        # CONTAINER : PAGE_ATTRIBUTES
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "mobile_image_same" : _mobile_image_same, \
        "no_image" : _no_image,\

        # CONTAINER : PRODUCT_INFO
        "model" : _model, \
        "long_description" : _long_description, \

        # CONTAINER : REVIEWS
        "average_review" : _average_review, \
        "review_count" : _review_count, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : CLASSIFICATION
        "brand" : _brand, \
    }







    ##########################################
    ################ OUTDATED CODE - probably ok to delete it
    ##########################################

    # def main(args):
    #     # check if there is an argument
    #     if len(args) <= 1:
    #         sys.stderr.write("ERROR: No product URL provided.\nUsage:\n\tpython crawler_service.py <tesco_product_url>\n")
    #         sys.exit(1)

    #     product_page_url = args[1]

    #     # check format of page url
    #     if not check_url_format(product_page_url):
    #         sys.stderr.write("ERROR: Invalid URL " + str(product_page_url) + "\nFormat of product URL should be\n\t http://www.tesco.com/direct/<part-of-product-name>/<product_id>.prd\n")
    #         sys.exit(1)

    #     return json.dumps(product_info(sys.argv[1], ["name", "short_desc", "keywords", "price", "load_time", "anchors", "long_desc"]))
    # def manufacturer_content_body(self):
    #    return None

    # def _anchors_from_tree(self):
    #     # get all links found in the description text
    #     description_node = self.tree_html.xpath("//section[@class='detailWrapper']")[0]
    #     links = description_node.xpath(".//a")
    #     nr_links = len(links)
    #     links_dicts = []
    #     for link in links:
    #         links_dicts.append({"href" : link.xpath("@href")[0], "text" : link.xpath("text()")[0]})
    #     ret = {"quantity" : nr_links, "links" : links_dicts}
    #     return ret

    # def _seller_meta_from_tree(self):
    #     return self.tree_html.xpath("//meta[@itemprop='brand']/@content")[0]

    # def _categories(self):
    #     categories = {}
    #     categories["super_dept"] = self._super_dept()
    #     categories["dept"] = self._dept()
    #     categories["full"] = self._all_depts()
    #     categories["hostname"] = 'Tesco'
    #     return categories

    # # returns 1 if the product is in stock, 0 otherwise
    # def _product_in_stock(self):
    #     return None


