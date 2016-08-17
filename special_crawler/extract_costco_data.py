import urllib
import re
import sys
import json
import random
from lxml import html, etree
import lxml.html
import time
import requests
from extract_data import Scraper


class CostcoScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.costco.com/<product name>.product.<product id>.html"
    WEBCOLLAGE_CONTENT_URL = "http://content.webcollage.net/costco/smart-button?ird=true&channel-product-id={0}"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        self.reviews = None
        self.image_urls = None
        self.prod_help = None
        self.is_webcollage_checked = False
        self.wc_content = None
        self.sp_content = None
        self.is_video_checked = False
        self.video_urls = None
        self.widget_pdfs = None
        self.widget_videos = None
        self.widgets_checked = False

    def check_url_format(self):
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
        return self.product_page_url.split('.')[-2]

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
        return None

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
        short_description = " ".join(self.tree_html.xpath('//div[@class="tireDetails"]//text()[normalize-space()]')).strip()
        if short_description != None and  short_description != "":
            return  self._clean_text(short_description)
        short_description = " ".join(self.tree_html.xpath('//div[@class="features"]//text()[normalize-space()]')).strip()
        if short_description != None and  short_description != "":
            return  self._clean_text(short_description)
        return self._long_description()

    def _long_description(self):

        if filter(None, map((lambda x: x.strip()),self.tree_html.xpath("//div[@id='product-tab1']/*[not(self::div)]//text()"))):
            return self._clean_html(' '.join(map((lambda x: lxml.html.tostring(x)),self.tree_html.xpath("//div[@id='product-tab1']/*[not(self::div)]"))))

        long_description = ""
        html = self._wc_content()
        if html:
            m = re.findall(r'wc-rich-content-description\\">(.*?)<\\/div', html, re.DOTALL)
            if len(m) > 0:
                long_description =  " ".join(m)
            if long_description != None and  long_description != "":
                return  self._clean_text(long_description)
        html = self._sp_content()
        m = re.findall(r'sp_acp_section_text_content">(.*?)</div', html, re.DOTALL)
        if len(m) > 0:
            long_description =  " ".join(m)
        if long_description != None and  long_description != "":
            return  self._clean_text(long_description)
        long_description =  " ".join(self.tree_html.xpath('//div[@id="product-tab1"]//text()[normalize-space()]')).strip()
        if long_description == '[ProductDetailsESpot_Tab1]':
            long_description = None
        if long_description != None and  long_description != "":
            return  self._clean_text(long_description)
        long_description =  " ".join(self.tree_html.xpath('//p[@itemprop="description"]//text()[normalize-space()]')).strip()
        if long_description != None and  long_description != "":
            return  self._clean_text(long_description)
        long_description =  " ".join(self.tree_html.xpath('//div[@class="TireLandDesc"]//text()[normalize-space()]')).strip()
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
        img_link = tree.xpath('//script[contains(@src,"costco-static.com")]/@src')
        if len(img_link) > 0:
            imgs = requests.get(img_link[0]).text
            img_url = re.findall(r"image\:(.+?)\,+?",imgs)
            img_url = ["http://images.costco-static.com/image/media/350-"+b.replace("'","").strip()+".jpg" for b in img_url]
            if len(img_url) > 0:
                self.image_urls = img_url
                return img_url
        img_url = tree.xpath('//div[@class="seasonTire"]//img/@src')
        if len(img_url) > 0:
            self.image_urls = img_url
            return img_url

        if self.tree_html.xpath("//meta[@property='og:image']/@content"):
            return self.tree_html.xpath("//meta[@property='og:image']/@content")

        if a == 1:
            self.image_urls = None
        return None

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
        if self.is_video_checked:
            return self.video_urls

        self.is_video_checked = True
        webcollage_contents = self._wc_content()

        video_urls = []

        if webcollage_contents:
            webcollage_contents = html.fromstring(webcollage_contents)

            if webcollage_contents.xpath("//div[@class='wc-json-data']/text()"):
                wc_video_json = json.loads(webcollage_contents.xpath("//div[@class='wc-json-data']/text()")[0])
                wc_video_base_url = webcollage_contents.xpath("//*[@data-resources-base]/@data-resources-base")[0]

                for video_item in wc_video_json.get("videos", []):
                    video_urls.append(wc_video_base_url + video_item["src"]["src"])

        self._check_widgets()

        if self.widget_videos:
            video_urls.extend(self.widget_videos)

        # liveclicker videos
        dim5 = re.search('LCdim5 = "(\d+)"', html.tostring(self.tree_html))

        if dim5:
            dim5 = dim5.group(1)

            liveclicker = self.load_page_from_url_with_number_of_retries('http://sv.liveclicker.net/service/api?method=liveclicker.widget.getList&account_id=69&dim5=' + dim5)

            widgets = etree.XML( re.sub('encoding="[^"]+"', '', liveclicker))

            for widget in widgets:
                widget_id = widget.find('widget_id').text

                liveclicker = self.load_page_from_url_with_number_of_retries('http://sv.liveclicker.net/service/getXML?widget_id=' + widget_id + '&player_id=2&autoplay=false&player_custom_id=1&share64=Y2xpZW50X2lkPTE3JmlmcmFtZT10cnVlJm9wdGlvbl9pZnJhbWVEaXY9dmlkZW9fMTMxMzMyNjIyMCZwbGF5ZXJfY3VzdG9tX2lkPTEmd2lkZ2V0X2lkPTEzMTMzMjYyMjA=&width=605&height=335&html5=true&format=jsonp')

                video_urls.append( json.loads(liveclicker)['location'])

        if video_urls:
            self.video_urls = video_urls
            return video_urls

        return None

    def _video_count(self):
        '''
        sp = self._sp_content()
        n = 0
        m = sp.count('autoplay=true') / 2

        if self._video_urls():
            n = len(self._video_urls())

        return m + n
        '''
        video_urls = self._video_urls()

        return len(video_urls) if video_urls else 0

    def _check_widgets(self):
        if not self.widgets_checked:
            self.widgets_checked = True

            pdfs = []
            videos = []

            sellpoint = json.loads(requests.get('http://a.sellpoint.net/w/83/l/' + self._product_id() + '.json').content)
            widgets = sellpoint.get('widgets', [])

            for widget in widgets:
                sellpoint = json.loads(requests.get('http://a.sellpoint.net/w/83/w/' + widget + '.json').content)
                widgets2 = sellpoint['widgets']

                for widget2 in widgets2:
                    sellpoint = json.loads(requests.get('http://a.sellpoint.net/w/83/w/' + widget2 + '.json').content)
                    if sellpoint.get('items'):
                        for item in sellpoint['items']:
                            url = item['url'][2:]
                            if not url in pdfs:
                                pdfs.append(url)
                    if sellpoint.get('videos') and not 'callout' in sellpoint['targetSelector']:
                        for video in sellpoint['videos']:
                            mp4 = video['src']['mp4']['res' + str(video['maxresolution'])]
                            if not mp4 in videos:
                                videos.append(mp4)

            if pdfs:
                self.widget_pdfs = pdfs
            if videos:
                self.widget_videos = videos

    # return one element containing the PDF
    def _pdf_urls(self):
        pdf = self.tree_html.xpath("//a[contains(@href,'.pdf')]/@href")
        pdf_list = []

        if len(pdf) > 0:
            pdf = set(pdf)
            pdf_list = ["http://www.costco.com" + p for p in pdf if "Cancellation" not in p and 'Restricted-Zip-Codes' not in p and 'Curbside' not in p]

        self._check_widgets()

        if self.widget_pdfs:
            pdf_list.extend(self.widget_pdfs)

        webcollage_contents = self._wc_content()

        if webcollage_contents:
            pdf_list.extend(html.fromstring(webcollage_contents).xpath("//a[contains(@href, '.pdf')]/@href"))

        if pdf_list:
            return pdf_list

        return None

    def _pdf_count(self):
        urls = self._pdf_urls()
        sp = self._sp_content()
        m = n = 0
        if sp !=None and sp !="":
            m = sp.count('.pdf')
        if urls:
            n = len(urls)

        return m + n

    def _wc_content(self):
        if self.is_webcollage_checked:
            return self.wc_content

        self.is_webcollage_checked = True

        try:
            webcollage_contents = urllib.urlopen(self.WEBCOLLAGE_CONTENT_URL.format(self._site_id())).read()
        except Exception, e:
            webcollage_contents = None

        if webcollage_contents and "_wccontent" in webcollage_contents:
            webcollage_contents = self._find_between(webcollage_contents, 'html: "', "\n")[:-1]
            webcollage_contents = webcollage_contents.decode("unicode-escape")
            webcollage_contents = webcollage_contents.replace("\\", "")
            self.wc_content = webcollage_contents
            return webcollage_contents

        return None

    def _wc_360(self):
        html = self._wc_content()

        if html and "wc-360" in html:
            return 1

        return 0

    def _wc_pdf(self):
        html = self._wc_content()

        if html and ".pdf" in html:
            return 1

        return 0

    def _wc_video(self):
        html = self._wc_content()

        if html and (".mp4" in html or ".flv" in html):
            return 1

        return 0

    def _wc_emc(self):
        html = self._wc_content()

        if html and "wc-aplus" in html:
            return 1

        return 0

    def _wc_prodtour(self):
        return 0

    def _webcollage(self):
        if self._wc_360() == 1 or self._wc_emc() == 1 or self._wc_pdf() == 1 or self._wc_prodtour() == 1 or self._wc_video() == 1:
            return 1

        return 0

    def _sellpoints(self):
        html = self._sp_content()
        if html != None and html != "": return 1
        return 0

    def _sp_content(self):
        if self.sp_content == None:
            url = 'http://sb.sellpoint.net/smart_button/lookup/acp/83_acp.js'
            html = urllib.urlopen(url).read()
            m = re.findall(r'(\{.*?\});', html, re.DOTALL)
            res = ""
            if len(m) > 0:
                hash_table = json.loads(m[0])
                id = self._site_id()
                sp_id = hash_table.get(id,'')
                if sp_id != "":
                    sp = sp_id.split("_")
                    if len(sp) > 2:
                        url = "http://assetsw.sellpoint.net/_acp_/%s/%s/js/acp_content_%s.js" % tuple(sp)
                        res = urllib.urlopen(url).read()
            self.sp_content = res
            return res
        else:
            return self.sp_content

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
    def _load_reviews(self):
        if not self.reviews:
            product_json = json.loads( self.load_page_from_url_with_number_of_retries('http://api.bazaarvoice.com/data/batch.json?passkey=bai25xto36hkl5erybga10t99&apiversion=5.5&displaycode=2070-en_us&resource.q0=products&filter.q0=id%3Aeq%3A' + self._product_id() + '&stats.q0=reviews'))

            self.reviews = product_json['BatchedResults']['q0']['Results'][0]['ReviewStatistics']

    def _average_review(self):
        self._load_reviews()

        if self.reviews:
            return round(self.reviews['AverageOverallRating'], 1)

    def _review_count(self):
        self._load_reviews()

        if self.reviews:
            return self.reviews['TotalReviewCount']

    def _reviews(self):
        self._load_reviews()

        if self.reviews['RatingDistribution']:
            reviews = []

            for i in range(1,6):
                has_value = False

                for review in self.reviews['RatingDistribution']:
                    if review['RatingValue'] == i:
                        reviews.append([i, review['Count']])
                        has_value = True

                if not has_value:
                    reviews.append([i, 0])

            return reviews[::-1]

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
        reviews = self._reviews()

        if reviews:
            for review in reviews:
                if review[1] != 0:
                    return review[0]

    def _min_review(self):
        reviews = self._reviews()

        if reviews:
            for review in reviews[::-1]:
                if review[1] != 0:
                    return review[0]

    ##########################################
    ################ CONTAINER : SELLERS
    ##########################################

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

    def _in_stores(self):
        return 0

    def _site_online(self):
        if self._marketplace() == 1: return 0
        return 1

    def _site_online_out_of_stock(self):
        if self.tree_html.xpath('//span[contains(@class, "out-of-stock")]'):
            return 1

        return 0

    def _marketplace(self):
        return 0


    def _marketplace_sellers(self):
         return None

    def _marketplace_lowest_price(self):
        return None

    def _marketplace_out_of_stock(self):
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

        if len(cats) > 0:
            return cats[1:]

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
        p = re.compile(r'<.*?>')
        text = p.sub(' ',text)
        text = text.replace("\n"," ").replace("\t"," ").replace("\r"," ")
        text = text.replace("\\","")
       	text = re.sub("&nbsp;", " ", text).strip()
        return  re.sub(r'\s+', ' ', text)

    # Get rid of all html except for <ul>, <li> and <br> tags
    def _clean_html(self, html):
        html = html.replace('\\','')
        html = re.sub('[\n\t\r]', '', html)
        html = re.sub('<!--[^>]*-->', '', html)
        html = re.sub('</?(?!(ul|li|br))\w+[^>]*>', '', html)
        html = re.sub('&#160;', ' ', html)
        html = re.sub('\s+', ' ', html)
        return re.sub('> <', '><', html).strip()


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
        "wc_emc" : _wc_emc, \
        "wc_prodtour": _wc_prodtour, \
        "wc_360" : _wc_360, \
        "wc_pdf" : _wc_pdf, \
        "wc_video" : _wc_video, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "sellpoints": _sellpoints, \
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


