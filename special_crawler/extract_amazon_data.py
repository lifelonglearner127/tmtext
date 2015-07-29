#!/usr/bin/python


import urllib, urllib2
import re
import sys
import json
import lxml

from lxml import html
import time
import requests
from extract_data import Scraper
import os
from PIL import Image
import cStringIO # *much* faster than StringIO
from pytesseract import image_to_string

sys.path.append(os.path.abspath('../search'))
import captcha_solver
import compare_images

from spiders_shared_code.amazon_variants import AmazonVariants

class AmazonScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.amazon.com/dp/<product-id> or http://www.amazon.co.uk/dp/<product-id>"

    CB = captcha_solver.CaptchaBreakerWrapper()
    # special dir path to store the captchas, so that the service has permissions to create it on the scraper instances
    CB.CAPTCHAS_DIR = '/tmp/captchas'
    CB.SOLVED_CAPTCHAS_DIR = '/tmp/solved_captchas'

    MAX_CAPTCHA_RETRIES = 10

    marketplace_prices = None
    marketplace_sellers = None

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        self.av = AmazonVariants()
        self.is_review_checked = False
        self.review_list = None
        self.max_review = None
        self.min_review = None

    # method that returns xml tree of page, to extract the desired elemets from
    # special implementation for amazon - handling captcha pages
    def _extract_page_tree(self, captcha_data=None, retries=0):
        """Builds and sets as instance variable the xml tree of the product page
        :param captcha_data: dictionary containing the data to be sent to the form for captcha solving
        This method will be used either to get a product page directly (null captcha_data),
        or to solve the form and get the product page this way, in which case it will use captcha_data
        :param retries: number of retries to solve captcha so far; relevant only if solving captcha form
        Returns:
            lxml tree object
        """

        # TODO: implement maximum number of retries
        if captcha_data:
            data = urllib.urlencode(captcha_data)
            request = urllib2.Request(self.product_page_url, data)
        else:
            request = urllib2.Request(self.product_page_url)

        # set user agent to avoid blocking
        agent = ''
        if self.bot_type == "google":
            print 'GOOOOOOOOOOOOOGGGGGGGLEEEE'
            agent = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        else:
            agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140319 Firefox/24.0 Iceweasel/24.4.0'
        request.add_header('User-Agent', agent)

        for i in range(self.MAX_RETRIES):
            try:
                contents = urllib2.urlopen(request).read()

            # handle urls with special characters
            except UnicodeEncodeError, e:

                if captcha_data:
                    request = urllib2.Request(self.product_page_url.encode("utf-8"), data)
                else:
                    request = urllib2.Request(self.product_page_url.encode("utf-8"))
                request.add_header('User-Agent', agent)
                contents = urllib2.urlopen(request).read()

            except IncompleteRead, e:
                continue


            try:
                # replace NULL characters
                contents = self._clean_null(contents)

                self.tree_html = html.fromstring(contents.decode("utf8"))
            except UnicodeError, e:
                # if string was not utf8, don't deocde it
                print "Warning creating html tree from page content: ", e.message

                # replace NULL characters
                contents = self._clean_null(contents)

                self.tree_html = html.fromstring(contents)

            # it's a captcha page
            if self.tree_html.xpath("//form[contains(@action,'Captcha')]") and retries <= self.MAX_CAPTCHA_RETRIES:
                image = self.tree_html.xpath(".//img/@src")
                if image:
                    captcha_text = self.CB.solve_captcha(image[0])

                # value to use if there was an exception
                if not captcha_text:
                    captcha_text = ''

                retries += 1
                return self._extract_page_tree(captcha_data={'field-keywords' : captcha_text}, retries=retries)

            # if we got it we can exit the loop and stop retrying
            return


            # try getting it again, without catching exception.
            # if it had worked by now, it would have returned.
            # if it still doesn't work, it will throw exception.
            # TODO: catch in crawler_service so it returns an "Error communicating with server" as well

            contents = urllib2.urlopen(request).read()
            # replace NULL characters
            contents = self._clean_null(contents)
            self.tree_html = html.fromstring(contents)



    def check_url_format(self):
        m = re.match(r"^http://www.amazon.com/([a-zA-Z0-9\-\%\_]+/)?(dp|gp/product)/[a-zA-Z0-9]+(/[a-zA-Z0-9_\-\?\&\=]+)?$", self.product_page_url)
        n = re.match(r"^http://www.amazon.co.uk/([a-zA-Z0-9\-]+/)?(dp|gp/product)/[a-zA-Z0-9]+(/[a-zA-Z0-9_\-\?\&\=]+)?$", self.product_page_url)
        o = re.match(r"^http://www.amazon.ca/([a-zA-Z0-9\-]+/)?(dp|gp/product)/[a-zA-Z0-9]+(/[a-zA-Z0-9_\-\?\&\=]+)?$", self.product_page_url)
        l = re.match(r"^http://www.amazon.co.uk/.*$", self.product_page_url)
        self.scraper_version = "com"

        if (not not n) or (not not l): self.scraper_version = "uk"
        if (not not o): self.scraper_version = "ca"

        return (not not m) or (not not n) or (not not l) or (not not o)

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        self.av.setupCH(self.tree_html)

        if self.tree_html.xpath("//form[contains(@action,'Captcha')]"):
            return True
        return False


    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _event(self):
        return None

    def _product_id(self):
        if self.scraper_version == "uk":
            product_id = re.match("^http://www.amazon.co.uk/([a-zA-Z0-9\-]+/)?(dp|gp/product)/([a-zA-Z0-9]+)(/[a-zA-Z0-9_\-\?\&\=]+)?$", self.product_page_url).group(3)
        elif self.scraper_version == "ca":
            product_id = re.match("^http://www.amazon.ca/([a-zA-Z0-9\-]+/)?(dp|gp/product)/([a-zA-Z0-9]+)(/[a-zA-Z0-9_\-\?\&\=]+)?$", self.product_page_url).group(3)
        else:
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
        pn = self.tree_html.xpath('//h1[@id="title"]/span[@id="productTitle"]')
        if len(pn)>0:
            return pn[0].text
        pn = self.tree_html.xpath('//h1[@class="parseasinTitle " or @class="parseasinTitle"]/span[@id="btAsinTitle"]//text()')
        if len(pn)>0:
            return " ".join(pn).strip()
        pn = self.tree_html.xpath('//h1[@id="aiv-content-title"]//text()')
        if len(pn)>0:
            return self._clean_text(pn[0])
        pn = self.tree_html.xpath('//div[@id="title_feature_div"]/h1//text()')
        return pn[0].strip()

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
        rows = self.tree_html.xpath("//div[@class='content pdClearfix'][1]//tbody//tr")
        if len(rows)==0:
            rows = self.tree_html.xpath("//div[@id='dv-center-features']//table//tr")
        if len(rows)==0:
            rows = self.tree_html.xpath("//table[@id='aloha-ppd-glance-table']//tr")
        # list of lists of cells (by rows)
        cells=[]
        for row in rows:
            r = row.xpath(".//*[not(self::script)]//text()")
            if len(r)>0 and len(r[0])>1 and r[0].find('Customer Review') < 0 \
               and r[0].find('function(') < 0 and  r[0].find('Delivery') < 0 \
               and r[0].find('Date ') < 0 and r[0].find('Best Seller') < 0 \
               and r[0].find('Manufacturer ref') < 0 and r[0].find('ASIN') < 0:
                cells.append(r)
#            cells = map(lambda row: row.xpath(".//*[not(self::script)]//text()"), rows)
        # list of text in each row
        rows_text = map(\
            lambda row: ":".join(\
                map(lambda cell: cell.strip(), row)\
                ), \
            cells)
        all_features_text = "\n".join(rows_text)
        # return dict with all features info
     #   return all_features_text
        return rows_text


    def _feature_count(self): # extract number of features from tree
        rows = self._features()
        return len(rows)
        # select table rows with more than 2 cells (the others are just headers), count them
    #    return len(filter(lambda row: len(row.xpath(".//td"))>0, self.tree_html.xpath("//div[@class='content pdClearfix']//tbody//tr")))

    def _model_meta(self):
        return None


    def _description(self):
        short_description = " ".join(self.tree_html.xpath("//*[contains(@id,'feature-bullets')]//text()[normalize-space()]")).strip()
        if short_description is not None and len(short_description)>0:
            return short_description.replace("\n"," ")
        short_description=" ".join(self.tree_html.xpath("//div[@class='dv-simple-synopsis dv-extender']//text()")).strip()
        if short_description is not None and len(short_description)>0:
            return short_description.replace("\n"," ")

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
        pd = self.tree_html.xpath("//h2[contains(text(),'Product Description')]/following-sibling::*//text()")
        if len(pd)>0:
            desc = " ".join(pd).strip()
            if desc is not None and len(desc)>0:
                return  self._clean_text(desc)
        desc = '\n'.join(self.tree_html.xpath('//script//text()'))
        desc = re.findall(r'var iframeContent = "(.*)";', desc)
        desc = urllib.unquote_plus(str(desc))
        desc = html.fromstring(desc)
        dsw = desc.xpath('//div[@class="productDescriptionWrapper"]')
        res = ""
        for d in dsw:
            if len(d.xpath('.//div[@class="aplus"]'))==0:
                res += self._clean_text(' '.join(d.xpath('.//text()')))+" "
        if res != "" :
            return res
        return None


    def _apluscontent_desc(self):
        res = self._clean_text(' '.join(self.tree_html.xpath('//div[@id="aplusProductDescription"]//text()')))
        if res != "" : return res
        desc = '\n'.join(self.tree_html.xpath('//script//text()'))
        desc = re.findall(r'var iframeContent = "(.*)";', desc)
        desc = urllib.unquote_plus(str(desc))
        desc = html.fromstring(desc)
        res = self._clean_text(' '.join(desc.xpath('//div[@id="aplusProductDescription"]//text()')))
        if res != "" : return res
        res = self._clean_text(' '.join(desc.xpath('//div[@class="productDescriptionWrapper"]/div[@class="aplus"]//text()')))
        if res != "" : return res
        return None

    def _variants(self):
        return self.av._variants()

    def _ingredients(self):
        page_raw_text = html.tostring(self.tree_html)

        try:
            ingredients = re.search('<b>Ingredients</b><br>(.+?)<br>', page_raw_text).group(1)
            ingredients = ingredients.split(",")

            ingredients = [ingredient.strip() for ingredient in ingredients]

            if ingredients:
                return ingredients
        except:
            desc = '\n'.join(self.tree_html.xpath('//script//text()'))
            desc = re.findall(r'var iframeContent = "(.*)";', desc)
            desc = urllib.unquote_plus(str(desc))
            ingredients = re.search('Ingredients:(.+?)(\\n|\.)', desc).group(1)

            if "</h5>" in ingredients:
                return None

            ingredients = ingredients.split(",")

            ingredients = [ingredient.strip() for ingredient in ingredients]

            if ingredients:
                return ingredients

        return None

    def _ingredient_count(self):
        if self._ingredients():
            return len(self._ingredients())

        return 0

    def _nutrition_facts(self):
        try:
            desc = '\n'.join(self.tree_html.xpath('//script//text()'))
            desc = re.findall(r'var iframeContent = "(.*)";', desc)
            desc = urllib.unquote_plus(str(desc))
            nutrition_facts = re.search('<h5>Nutritional Facts and Ingredients:</h5> <p>(.+?)(</p>|<br>)', desc).group(1)
            nutrition_facts = nutrition_facts.split(",")
            nutrition_facts = [nutrition_fact.strip() for nutrition_fact in nutrition_facts]

            if nutrition_facts:
                return nutrition_facts
        except:
            pass

        return None

    def _nutrition_fact_count(self):
        if self._nutrition_facts():
            return len(self._nutrition_facts())

        return 0

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

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        if canonical_link.startswith("http://www.amazon.com"):
            return canonical_link
        else:
            return "http://www.amazon.com" + canonical_link

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
            img_list.extend(image_url)
        if len(img_list) == 2:
            return img_list[0] == img_list[1]
        return None

    def     _image_urls(self, tree = None):
        allimg = self._image_helper()
        n = len(allimg)
        vurls = self._video_urls()
        if vurls==None: vurls=[]
        if tree == None:
            tree = self.tree_html
        #The small images are to the left of the big image
        image_url = tree.xpath("//span[@class='a-button-text']//img/@src")
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return [m for m in image_url if m.find("player")<0 and m.find("video")<0 and m not in vurls]

        #The small images are below the big image
        image_url = tree.xpath("//div[@id='thumbs-image']//img/@src")
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            res = [m for m in image_url if m.find("player")<0 and m.find("video")<0 and m not in vurls]
            return res

        #Amazon instant video
        image_url = tree.xpath("//div[@class='dp-meta-icon-container']//img/@src")
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return image_url

        image_url = tree.xpath("//td[@id='prodImageCell']//img/@src")
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return image_url

        image_url = tree.xpath("//div[contains(@id,'thumb-container')]//img/@src")
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return [m for m in image_url if m.find("player")<0 and m.find("video")<0 and m not in vurls]

        image_url = tree.xpath("//div[contains(@class,'imageThumb')]//img/@src")
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return image_url

        image_url = tree.xpath("//div[contains(@id,'coverArt')]//img/@src")
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return image_url

        image_url = tree.xpath('//img[@id="imgBlkFront"]')
        if image_url is not None and len(image_url)>n and self.no_image(image_url)==0:
            return ["inline image"]

        if len(allimg) > 0 and self.no_image(allimg) == 0:
            if len(allimg) > 7:
                allimg = allimg[:7]

                if vurls:
                    allimg = allimg[:-1]

            return allimg
        return None

    def _image_helper(self):
        res = []
        try:
            all_scripts = self.tree_html.xpath('//script[@type="text/javascript"]//text()')
            for s in all_scripts:
                st = s.find('data["colorImages"]')
                if st > 0:
                    colors = self.tree_html.xpath('//div[@id="variation_color_name"]//span[@class="selection"]//text()')
                    pack = self.tree_html.xpath('//div[@id="variation_item_package_quantity"]//span[@class="selection"]//text()')
                    style = self.tree_html.xpath('//div[@id="variation_style_name"]//span[@class="selection"]//text()')
                    color=""
                    if len(colors)>0:
                        color=colors[0].strip()
                    if len(pack)>0:
                        color=pack[0].strip() + " " + color
                    if  len(style)>0:
                        color=style[0].strip()
                    st = s.find("{",st)
                    e = s.find(";",st)
                    if st>=e: continue
                    imdata=json.loads(s[st:e])

                    if type(imdata) is dict and len(imdata)>0:
                        if color=="" or not imdata.has_key(color):
                            color =imdata.keys()[0]
                        for t in imdata[color]:
                            res.append(t['large'])
                        return res
                st = s.find("'colorImages':")
                if len(res)==0 and st > 0:
                    while s[st]!="{" and st>0:
                        st -= 1
                    e = s.find("};",st)+1
                    if st>=e: continue
                    imdata=json.loads(s[st:e].replace("'",'"'))
                    if type(imdata) is dict and len(imdata)>0  and imdata.has_key('colorImages')\
                     and imdata['colorImages'].has_key('initial'):
                        for d in imdata['colorImages']['initial']:
                            imu = d.get("large","")
                            if len(imu)>10:
                                res.append(imu)
                        return res
                st = s.find("var colorImages")
                if len(res)==0 and st > 0:
                    st = s.find("{",st)
                    e = s.find("};",st)+1
                    if st>=e: continue
                    imdata=json.loads(s[st:e].replace("'",'"'))
                    if type(imdata) is dict and len(imdata)>0  and imdata.has_key('initial'):
                        for d in imdata['initial']:
                            imu = d.get("large","")
                            if len(imu)>10:
                                res.append(imu)
                        return res
        except:
            return []
        return res

    def _mobile_image_url(self, tree = None):
        if tree == None:
            tree = self.tree_html
        image_url = tree.xpath("//span[@class='a-button-text']//img/@src")
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
        video_url = self.tree_html.xpath('//script')  #[@type="text/javascript"]
        temp = []
        for v in video_url:
            st=str(v.xpath('.//text()'))
            r = re.findall("[\'\"]url[\'\"]:[\'\"](http://.+?\.mp4)[\'\"]", st)
            if r:
                temp.extend(r)
            ii=st.find("kib-thumb-container-")
            if ii > 0:
                ij=st.find('"',ii+19)
                if ij-ii<25:
                    vid = st[ii:ij]
                    viurl = self.tree_html.xpath('//div[@id="%s"]//img/@src' % vid)
                    if len(viurl)>0:
                        temp.append(viurl[0])

        #Find video among the  small images.
        image_url = self.tree_html.xpath("//span[@class='a-button-text']//img/@src")
        if len(image_url)==0:
            image_url = self.tree_html.xpath("//div[@id='thumbs-image']//img/@src")
        for v in image_url:
            if v.find("player")>0 :
                temp.append(v)
        if len(temp)==0: return None
        return temp#",".join(temp)

    def _video_count(self):
        if self._video_urls()==None: return 0
        return len(self._video_urls())#.split(','))

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
        average_review = self.tree_html.xpath("//span[@id='acrPopover']/@title")
        if len(average_review) == 0:
            average_review = self.tree_html.xpath("//div[@class='gry txtnormal acrRating']//text()")
        if len(average_review) == 0:
            average_review = self.tree_html.xpath("//div[@id='avgRating']//span//text()")
        average_review = re.findall("([0-9]\.?[0-9]?) out of 5 stars", average_review[0])[0]
        return self._tofloat(average_review)

    def _review_count(self):
        nr_reviews = self.tree_html.xpath("//span[@id='acrCustomerReviewText']//text()")
        if len(nr_reviews) > 0:
            nr_review = re.findall("([0-9,]+) customer reviews", nr_reviews[0])
            if len(nr_review) == 0:
                nr_review = re.findall("([0-9]+) customer review", nr_reviews[0])
            if len(nr_review) > 0:
                return self._toint(nr_review[0])
        nr_reviews = self.tree_html.xpath("//div[@class='fl gl5 mt3 txtnormal acrCount']//text()")
        if len(nr_reviews) > 1:
            return self._toint(nr_reviews[1])
        nr_reviews = self.tree_html.xpath("//a[@class='a-link-normal a-text-normal product-reviews-link']//text()")
        if len(nr_reviews) > 1:
            return self._toint(nr_reviews[0].replace('(','').replace(')','').replace(',',''))
        if self.scraper_version == "uk":
            nr_reviews = self.tree_html.xpath("//span[@class='crAvgStars']/a//text()")
            if len(nr_reviews) > 0:
                res = nr_reviews[0].split()
                return self._toint(res[0])
        return 0

    def _reviews(self):
        if self.is_review_checked:
            return self.review_list

        self.is_review_checked = True

        if not self._review_count() or self._review_count() == 0:
            self.review_list = None
            return self.review_list

        review_list = []
        review_link = self.tree_html.xpath("//a[contains(@class, 'a-link-normal a-text-normal product-reviews-link')]/@href")[0]
        review_link = review_link[:review_link.rfind("sortBy=")]

        mark_list = ["one", "two", "three", "four", "five"]

        for index, mark in enumerate(mark_list):
            review_link_mark_star = review_link.replace("cm_cr_dp_qt_see_all_top", "cm_cr_pr_viewopt_sr") + "sortBy=helpful&reviewerType=all_reviews&formatType=all_formats&filterByStar=" + mark + "_star&pageNumber=1"
            h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            b = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('http://', a)
            s.mount('https://', b)
            contents = s.get(review_link_mark_star, headers=h, timeout=5).text

            if "Sorry, no reviews match your current selections." in contents:
                review_list.append([index + 1, 0])
            else:
                if not self.max_review or self.max_review < index + 1:
                    self.max_review = index + 1

                if not self.min_review or self.min_review > index + 1:
                    self.min_review = index + 1

                review_html = html.fromstring(contents)
                review_count = review_html.xpath("//div[@id='cm_cr-review_list']//div[contains(@class, 'a-section a-spacing-medium')]//span[@class='a-size-base']/text()")[0]
                review_count = int(re.search('of (.*) reviews', review_count).group(1))
                review_list.append([index + 1, review_count])

        if not review_list:
            self.review_list = None
            return self.review_list

        self.review_list = review_list

        return self.review_list

    def _tofloat(self,s):
        try:
            s = s.replace(",", "")
            s = re.findall(r"[\d\.]+", s)[0]
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
        self._reviews()

        return self.max_review

    def _min_review(self):
        self._reviews()

        return self.min_review

    ##########################################
    ################ CONTAINER : SELLERS
    ##########################################
    def _price_amount(self):
        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        return float(price_amount)

    def _price_currency(self):
        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        price_currency = price.replace(price_amount, "")
        if price_currency == "$":
            return "USD"
        return price_currency

    # extract product price from its product product page tree
    def _price(self):
        price = self.tree_html.xpath("//span[@id='actualPriceValue']/b/text()")
        if len(price)>0  and len(price[0].strip())<12  and price[0].strip()!="":
            return price[0].strip()
        price = self.tree_html.xpath("//*[@id='priceblock_ourprice']//text()")#
        if len(price)>0 and len(price[0].strip())<12  and price[0].strip()!="":
            return price[0].strip()
        price = self.tree_html.xpath("//*[contains(@id, 'priceblock_')]//text()")#priceblock_ can usually have a few things after it
        if len(price)>0 and len(price[0].strip())<12  and price[0].strip()!="":
            return price[0].strip()
        price = self.tree_html.xpath("//*[contains(@class, 'offer-price')]//text()")
        if len(price)>0  and len(price[0].strip())<12  and price[0].strip()!="":
            return price[0].strip()

        pid=self._product_id()
        price = self.tree_html.xpath("//button[@value='"+pid+"']//text()")
 #       price = self.tree_html.xpath("//span[@id='actualPriceValue']//text()")
        if len(price)>0  and price[0].strip()!="":
            p=price[0].split()
            return p[-1]
        price = self.tree_html.xpath("//div[@id='"+pid+"']//a[@class='a-button-text']/span//text()")
        if len(price)>0  and len(price[0].strip())<12  and price[0].strip()!="":
            return price[0]

        price = self.tree_html.xpath("//div[@id='unqualifiedBuyBox']//span[@class='a-color-price']//text()")
        if len(price)>0  and len(price[0].strip())<12  and price[0].strip()!="":
            return price[0]

        price = self.tree_html.xpath("//*[contains(@class, 'price')]//text()")
        if len(price)>0  and len(price[0].strip())<12  and price[0].strip()!="":
            return price[0].strip()
        return None

    def _in_stock(self):
        in_stock = self.tree_html.xpath('//div[contains(@id, "availability")]//text()')
        in_stock = " ".join(in_stock)
        if 'currently unavailable' in in_stock.lower():
            return 0

        in_stock = self.tree_html.xpath('//div[contains(@id, "outOfStock")]//text()')
        in_stock = " ".join(in_stock)
        if 'currently unavailable' in in_stock.lower():
            return 0

        in_stock = self.tree_html.xpath("//div[@id='buyBoxContent']//text()")
        in_stock = " ".join(in_stock)
        if 'sign up to be notified when this item becomes available' in in_stock.lower():
            return 0

        return 1

    def _in_stores(self):
        return 0

    def _owned(self):
        aa = self.tree_html.xpath("//div[@class='buying' or @id='merchant-info']")
        for a in aa:
            if a.text_content().find('old by Amazon')>0: return 1
        s = self._seller_from_tree()
        return s['owned']

    def _owned_out_of_stock(self):
        return None

    def _marketplace(self):
        aa = self.tree_html.xpath("//div[@class='buying' or @id='merchant-info']")
        for a in aa:
            if a.text_content().find('old by ')>0 and a.text_content().find('old by Amazon')<0:
                return 1
            if a.text_content().find('seller')>0 :
                return 1
        a = self.tree_html.xpath('//div[@id="availability"]//a//text()')
        if len(a)>0 and a[0].find('seller')>=0: return 1
        s = self._seller_from_tree()
        return s['marketplace']

    def img_parse(self, img_url):
        file = urllib.urlopen(img_url)
        im = cStringIO.StringIO(file.read()) # constructs a StringIO holding the image
        img = Image.open(im)
        txt = image_to_string(img)
        return txt


    def _marketplace_sellers(self):
        if self.marketplace_sellers != None:
            return self.marketplace_sellers

        self.marketplace_prices = []
        mps = []
        mpp = []
        path = '/tmp/amazon_sellers.json'

        try:
            with open(path, 'r') as fp:
                amsel = json.load(fp)
        except:
            amsel = {}

        h = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}
        domain=self.product_page_url.split("/")

        try:
            url = domain[0] + "//" + domain[2] + "/gp/offer-listing/" + self.tree_html.xpath("//input[@id='ASIN']/@value")[0] + "/ref=olp_tab_all"
        except:
            url = domain[0] + "//" + domain[2] + "/gp/offer-listing/" + self._product_id() + "/ref=olp_tab_all"
        fl = 0

        while len(url) > 10:
            contents = requests.get(url, headers=h).text
            tree = html.fromstring(contents)
            sells = tree.xpath('//div[@class="a-row a-spacing-mini olpOffer"]')

            for s in sells:
                price = s.xpath('.//span[contains(@class,"olpOfferPrice")]//text()')
                sname = s.xpath('.//p[contains(@class,"olpSellerName")]/span/a/text()')

                if len(price) > 0:
                    seller_price = self._tofloat(price[0])
                    seller_name = ""

                    if len(sname) > 0 and sname[0].strip() != "":
                        seller_name = sname[0].strip()
                    else:
                        seller_link = s.xpath(".//p[@class='a-spacing-small']/a/@href")

                        if len(seller_link) > 0:
                            sd=seller_link[0].split("/")
                            seller_id = ""

                            if len(sd) > 4:
                                seller_id = sd[4]
#                                print "seller_id",seller_id

                                if seller_id != "" and seller_id in amsel:
                                    seller_name = amsel[seller_id]
#                                    print "seller_name",seller_name

                            if seller_name == "":
                                if seller_link[0].startswith("http://www.amazon."):
                                    seller_content = requests.get(seller_link[0], headers=h).text
                                else:
                                    if self.scraper_version == "uk":
                                        seller_content = requests.get("http://www.amazon.co.uk" + seller_link[0], headers=h).text
                                    elif self.scraper_version == "ca":
                                        seller_content = requests.get("http://www.amazon.ca" + seller_link[0], headers=h).text
                                    else:
                                        seller_content = requests.get("http://www.amazon.com" + seller_link[0], headers=h).text

                                seller_tree = html.fromstring(seller_content)
                                seller_names = seller_tree.xpath("//h2[@id='s-result-count']/span/span//text()")

                                if len(seller_names) > 0:
                                    seller_name = seller_names[0].strip()
                                else:
                                    seller_names = seller_tree.xpath("//title//text()")

                                    if len(seller_names) > 0:
                                        if seller_names[0].find(":")>0:
                                            seller_name = seller_names[0].split(":")[1].strip()
                                        else:
                                            seller_name = seller_names[0].split("@")[0].strip()

                            if seller_name != "" and seller_id != "":
                                amsel[seller_id] = seller_name
                                fl = 1

                    if seller_name != "":
                        mps.append(seller_name)
                        mpp.append(seller_price)

                        if len(mps) > 20:
                            break

            if len(mps) > 20:
                break

            urls = tree.xpath(".//ul[contains(@class,'a-pagination')]//li[contains(@class,'a-last')]//a/@href")

            if len(urls)>0:
                url = domain[0]+"//"+domain[2]+urls[0]
            else:
                url = ""

        if len(mps)>0:
            if fl == 1:
                try:
                    with open(path, 'w') as fp:
                        json.dump(amsel, fp)
                except Exception as ex:
                    print ex

            self.marketplace_prices = mpp
            self.marketplace_sellers = mps

            return mps

        return None

    def _marketplace_prices(self):
        if self.marketplace_prices is None :
            self._marketplace_sellers()
        if len(self.marketplace_prices) > 0:
            return self.marketplace_prices
        return None

    def _marketplace_lowest_price(self):
        if self.marketplace_prices is None:
            self._marketplace_sellers()
        if len(self.marketplace_prices) > 0:
            return min(self.marketplace_prices)
        return None

    def _marketplace_out_of_stock(self):
        """Extracts info on whether currently unavailable from any marketplace seller - binary
        Uses functions that work on both old page design and new design.
        Will choose whichever gives results.
        Returns:
            1/0
        """
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

    def _site_online(self):
        # site_online: the item is sold by the site (e.g. "sold by Amazon") and delivered directly, without a physical store.
        return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        if self._site_online() == 0:
            return None
        if self._in_stock() == 0:
            return 1
        return 0

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        return None

    ##########################################
    ################ CONTAINER : CLASSIFICATION
    ##########################################

    # extract the department which the product belongs to
    def _category_name(self):
        categories = self._categories()

        if not categories:
            return None

        return categories[-1]

    # extract a hierarchical list of all the departments the product belongs to
    def _categories(self):
        categories = self.tree_html.xpath("//div[@id='wayfinding-breadcrumbs_feature_div']//ul//a[@class='a-link-normal a-color-tertiary']/text()")
        categories = [category.strip() for category in categories]

        if not categories:
            return None

        return categories

    def _brand(self):
        bn=self.tree_html.xpath('//div[@id="mbc"]/@data-brand')
        if len(bn)>0 and bn[0]!="":
            return bn[0]
        bn=self.tree_html.xpath('//a[@id="brand"]//text()')
        if len(bn)>0 and bn[0]!="":
            return bn[0]
        bn=self.tree_html.xpath('//div[@class="buying"]//span[contains(text(),"by")]/a//text()')
        if len(bn)>0  and bn[0]!="":
            return bn[0]
        bn=self.tree_html.xpath('//a[contains(@class,"contributorName")]//text()')
        if len(bn)>0  and bn[0]!="":
            return bn[0]
        bn=self.tree_html.xpath('//a[contains(@id,"contributorName")]//text()')
        if len(bn)>0  and bn[0]!="":
            return bn[0]
        bn=self.tree_html.xpath('//span[contains(@class,"author")]//a//text()')
        if len(bn)>0  and bn[0]!="":
            return bn[0]
        fts = self._features()
        for f in fts:
            if f.find("Studio:")>=0 or f.find("Network:")>=0:
                bn = f.split(':')[1]
                return bn
        bn=self.tree_html.xpath('//div[@id="ArtistLinkSection"]//text()')
        if len(bn)>0:
            return "".join(bn).strip()
        return None


    def _version(self):
        """Determines if Amazon.co.uk page being read
        Returns:
            "uk" for Amazon.co.uk
            "com" for Amazon.com
        """
         # using url to distinguish between page versions.
        if self.product_page_url.find(".co.uk")>1:
            return "uk"
        return "com"

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
        "upc" : _asin,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "model_meta" : _model_meta, \
        "description" : _description, \
        "long_description" : _long_description, \
        "apluscontent_desc" : _apluscontent_desc, \
        "variants": _variants, \
        "ingredients": _ingredients, \
        "ingredient_count": _ingredient_count, \
        "nutrition_facts": _nutrition_facts, \
        "nutrition_fact_count": _nutrition_fact_count, \

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
        "canonical_link": _canonical_link,

        # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "in_stores" : _in_stores, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_prices" : _marketplace_prices, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "marketplace_out_of_stock" : _marketplace_out_of_stock, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \
        "in_stores_out_of_stock" : _in_stores_out_of_stock, \
        "in_stock" : _in_stock, \
        "owned" : _owned, \
        "owned_out_of_stock" : _owned_out_of_stock, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \
        "scraper" : _version, \


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
