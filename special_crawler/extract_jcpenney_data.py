# -*- coding: utf-8 -*-

#!/usr/bin/python

import re
import lxml
import lxml.html
import requests
import json
import ast

from itertools import groupby

from lxml import html, etree
from extract_data import Scraper
from spiders_shared_code.jcpenney_variants import JcpenneyVariants


class JcpenneyScraper(Scraper):
    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.jcpenney\.com/.*/prod\.jump\?ppId=.+$"
    REVIEW_URL = "http://jcpenney.ugc.bazaarvoice.com/1573-en_us/{}/reviews.djs?format=embeddedhtml"
    REVIEW_URL_ALTER = "http://sephora.ugc.bazaarvoice.com/8723jcp/{}/reviews.djs?format=embeddedhtml"
    STOCK_STATUS_URL = "http://www.jcpenney.com/jsp/browse/pp/graphical/graphicalSKUOptions.jsp?fromEditBag=&" \
                       "fromEditFav=&grView=&_dyncharset=UTF-8&_dynSessConf=-{0}&sucessUrl=%2Fjsp" \
                       "%2Fbrowse%2Fpp%2Fgraphical%2FgraphicalSKUOptions.jsp%" \
                       "3FfromEditBag%3D%26fromEditFav%3D%26grView%3D&_D%3AsucessUrl=+&" \
                       "ppType=regular&_D%3AppType=+&shipToCountry=US&_D%3AshipToCountry=+&" \
                       "ppId={1}&_D%3AppId=+&selectedLotValue=1+OZ+EAU+DE+PARFUM&_D%3AselectedLotValue=+" \
                       "&_DARGS=%2Fdotcom%2Fjsp%2Fbrowse%2Fpp%2Fgraphical%2FgraphicalLotSKUSelection.jsp"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        # whether product has any webcollage media
        self.review_json = None
        self.review_list = None
        self.is_review_checked = False
        self.price_json = None
        self.jv = JcpenneyVariants()
        self.is_analyze_media_contents = False
        self.video_urls = None
        self.video_count = 0
        self.pdf_urls = None
        self.pdf_count = 0
        self.wc_emc = 0
        self.wc_prodtour = 0
        self.wc_360 = 0
        self.wc_video = 0
        self.wc_pdf = 0

        self.no_longer_available = 0

    def _extract_page_tree(self):
        Scraper._extract_page_tree(self)

        if self.ERROR_RESPONSE["failure_type"] == "HTTP 404 - Page Not Found":
            self.ERROR_RESPONSE["failure_type"] = None

            self.no_longer_available = 1

            contents = self.load_page_from_url_with_number_of_retries(self.product_page_url)

            self.page_raw_text = contents
            self.tree_html = html.fromstring(contents)

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
            True if valid, False otherwise
        """

        m = re.match(r"^http://www\.jcpenney\.com/.*/prod\.jump\?ppId=.+$", self.product_page_url)

        return not not m

    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """
        try:
            self.jv.setupCH(self.tree_html)

            if self.no_longer_available:
                return False

            itemtype = self.tree_html.xpath('//div[@class="pdp_details"]')

            if not itemtype:
                self.ERROR_RESPONSE["failure_type"] = "Not a product"

                if self.tree_html.xpath("//div[@class='product_row bottom_border flt_wdt']"):
                    self.ERROR_RESPONSE["failure_type"] = "Bundle"

                raise Exception()


        except Exception:
            return True

        self.analyze_media_contents()

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _canonical_link(self):
        canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

        return canonical_link

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        return re.search('prod\.jump\?ppId=(.+?)$', self.product_page_url).group(1)

    def _site_id(self):
        return re.findall(r"\d+", self.tree_html.xpath("//div[@id='productWebId']/text()")[0])[0]

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        if not self._no_longer_available():
            return self.tree_html.xpath('//meta[@property="og:title"]/@content')[0].strip()

    def _product_title(self):
        return self._product_name()

    def _title_seo(self):
        return self._product_name()

    def _model(self):
        return None

    def _features(self):
        return None

    def _feature_count(self):
        return 0

    def _description(self):
        if self.tree_html.xpath("//div[@id='longCopyCont']"):
            description_html_text = html.tostring(self.tree_html.xpath("//div[@id='longCopyCont']")[0])

            if description_html_text.startswith('<div id="longCopyCont" class="pdp_brand_desc_info" itemprop="description">'):
                short_description_start_index = len('<div id="longCopyCont" class="pdp_brand_desc_info" itemprop="description">')
            else:
                short_description_start_index = 0

            if description_html_text.find('<div style="page-break-after: always;">') > 0:
                short_description_end_index = description_html_text.find('<div style="page-break-after: always;">')
            elif description_html_text.find('<ul>') > 0:
                short_description_end_index = description_html_text.find('<ul>')
            elif description_html_text.find('<p>&#9679;') > 0:
                short_description_end_index = description_html_text.find('<p>&#9679;')
            elif short_description_start_index > 0:
                short_description_end_index = description_html_text.rfind("</div>")
            else:
                short_description_end_index = len(description_html_text)

            return description_html_text[short_description_start_index:short_description_end_index].strip()

        return None

    # extract product long description from its product product page tree
    # ! may throw exception if not found
    # TODO:
    #      - keep line endings maybe? (it sometimes looks sort of like a table and removing them makes things confusing)
    def _long_description(self):
        if self.tree_html.xpath("//div[@id='longCopyCont']"):
            description_html_text = html.tostring(self.tree_html.xpath("//div[@id='longCopyCont']")[0])

            if description_html_text.find('<div style="page-break-after: always;">') > 0:
                long_description_start_index = description_html_text.find('<div style="page-break-after: always;">')
                long_description_start_index = description_html_text.find('</div>', long_description_start_index) + len("</div>")

            elif description_html_text.find('<ul>') > 0:
                long_description_start_index = description_html_text.find('<ul>')

            elif description_html_text.find('<p>&#9679;') > 0:
                long_description_start_index = description_html_text.find('<p>&#9679;')

            if long_description_start_index:
                long_description_end_index = description_html_text.rfind("</div>")
                return self._clean_text( description_html_text[long_description_start_index:long_description_end_index])

        return None

    def _ingredients(self):
        return None

    def _ingredients_count(self):
        return 0

    def _variants(self):
        return self.jv._variants()

    def _swatches(self):
        return self.jv.swatches()

    def _no_longer_available(self):
        return self.no_longer_available

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        pass
        
    def _image_urls(self):
        image_ids = re.search('var imageName = "(.+?)";', html.tostring(self.tree_html)).group(1)
        image_ids = image_ids.split(",")

        image_urls = []

        for id in image_ids:
            url = "http://s7d2.scene7.com/is/image/JCPenney/%s?fmt=jpg&op_usm=.4,.8,0,0&resmode=sharp2" % id
            if not url in image_urls:
                image_urls.append(url)

        swatches = self._swatches()
        swatches = swatches if swatches else []

        for swatch in swatches:
            if not swatch["hero_image"]:
                continue

            for img in swatch["hero_image"]:
                if not img in image_urls:
                    image_urls.append(img)

        if image_urls:
            return image_urls

        return None

    def _image_count(self):
        if self._image_urls():
            return len(self._image_urls())

        return 0

    def analyze_media_contents(self):
        if self.is_analyze_media_contents:
            return

        self.is_analyze_media_contents = True

        page_raw_text = html.tostring(self.tree_html)

        #check pdf
        try:
            pdf_urls = re.findall(r'href="(.+\.pdf?)"', page_raw_text)

            if not pdf_urls:
                raise Exception

            for index, url in enumerate(pdf_urls):
                if not url.startswith("http://"):
                    pdf_urls[index] = "http://www.jcpenney.com" + url

            self.pdf_urls = pdf_urls
            self.pdf_count = len(self.pdf_urls)
        except:
            pass

        video_urls_list = None

        try:
            video_urls_list = re.findall('videoIds.push\((.*?)\);\n', html.tostring(self.tree_html), re.DOTALL)
            video_urls_list = [ast.literal_eval(video_url)["url"] for video_url in video_urls_list]
        except:
            video_urls_list = None

        #check media contents window existence
        if self.tree_html.xpath("//a[@class='InvodoViewerLink']"):

            media_contents_window_link = self.tree_html.xpath("//a[@class='InvodoViewerLink']/@onclick")[0]
            media_contents_window_link = re.search("window\.open\('(.+?)',", media_contents_window_link).group(1)

            contents = self.load_page_from_url_with_number_of_retries(media_contents_window_link)

            #check media contents
            if "webapps.easy2.com" in media_contents_window_link:
                try:
                    media_content_raw_text = re.search('Demo.instance.data =(.+?)};\n', contents).group(1) + "}"
                    media_content_json = json.loads(media_content_raw_text)

                    video_lists = re.findall('"Path":"(.*?)",', media_content_raw_text)

                    video_lists = [media_content_json["UrlAddOn"] + url for url in video_lists if url.strip().endswith(".flv") or url.strip().endswith(".mp4/")]
                    video_lists = list(set(video_lists))

                    if not video_lists:
                        raise Exception

                    self.video_urls = video_lists
                    self.video_count = len(self.video_urls)
                except:
                    pass
            elif "content.webcollage.net" in media_contents_window_link:
                webcollage_link = re.search("document\.location\.replace\('(.+?)'\);", contents).group(1)
                contents = self.load_page_from_url_with_number_of_retries(webcollage_link)
                webcollage_page_tree = html.fromstring(contents)

                try:
                    webcollage_media_base_url = re.search('<div data-resources-base="(.+?)"', contents).group(1)

                    videos_json = '{"videos":' + re.search('{"videos":(.*?)]}</div>', contents).group(1) + ']}'
                    videos_json = json.loads(videos_json)

                    video_lists = [webcollage_media_base_url + videos_json["videos"][0]["src"]["src"][1:]]
                    self.wc_video = 1
                    self.video_urls = video_lists
                    self.video_count = len(self.video_urls)
                except:
                    pass

                try:
                    if webcollage_page_tree.xpath("//div[@class='wc-ms-navbar']//span[text()='360 Rotation']") or webcollage_page_tree.xpath("//div[@class='wc-ms-navbar']//span[text()='360/Zoom']"):
                        self.wc_360 = 1
                except:
                    pass

                try:
                    if webcollage_page_tree.xpath("//ul[contains(@class, 'wc-rich-features')]"):
                        self.wc_emc = 1
                except:
                    pass

            elif "bcove.me" in media_contents_window_link:
                try:
                    brightcove_page_tree = html.fromstring(contents)
                    video_lists = [brightcove_page_tree.xpath("//meta[@property='og:video']/@content")[0]]
                    self.video_urls = video_lists
                    self.video_count = len(self.video_urls)
                except:
                    pass

        try:
            if video_urls_list:
                if not self.video_urls:
                    self.video_urls = video_urls_list
                    self.video_count = len(video_urls_list)
                else:
                    self.video_urls.extend(video_urls_list)
                    self.video_count = self.video_count + len(video_urls_list)
        except:
            pass

    def _video_urls(self):
        return self.video_urls

    def _video_count(self):
        return self.video_count

    # return dictionary with one element containing the PDF
    def _pdf_urls(self):
        return self.pdf_urls

    def _pdf_count(self):
        return self.pdf_count

    def _wc_emc(self):
        return self.wc_emc

    def _wc_prodtour(self):
        return self.wc_prodtour

    def _wc_360(self):
        return self.wc_360

    def _wc_video(self):
        return self.wc_video

    def _wc_pdf(self):
        return self.wc_pdf

    def _webcollage(self):
        if self._wc_360() == 1 or self._wc_prodtour() == 1 or self._wc_pdf() == 1 or self._wc_emc() == 1 or self._wc_360():
            return 1

        return 0

    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))

        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0].strip()

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################

    def _extract_price_json(self):
        try:
            price_json= re.search('var jcpPPJSON = (.+?);\njcpDLjcp\.productPresentation = jcpPPJSON;', html.tostring(self.tree_html)).group(1)
            self.price_json = json.loads(price_json)
        except:
            self.price_json = None


    def _average_review(self):
        if self._review_count() == 0:
            return None

        average_review = round(float(self.review_json["jsonData"]["attributes"]["avgRating"]), 1)

        if str(average_review).split('.')[1] == '0':
            return int(average_review)
        else:
            return float(average_review)

    def _review_count(self):
        self._reviews()

        if not self.review_json:
            return 0

        return int(self.review_json["jsonData"]["attributes"]["numReviews"])

    def _max_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(self.review_list):
            if review[1] > 0:
                return 5 - i

    def _min_review(self):
        if self._review_count() == 0:
            return None

        for i, review in enumerate(reversed(self.review_list)):
            if review[1] > 0:
                return i + 1

    def _reviews(self):
        if self.is_review_checked:
            return self.review_list

        self.is_review_checked = True

        review_id = self._find_between(html.tostring(self.tree_html), 'reviewIdNew = "', '";').strip()
        contents = self.load_page_from_url_with_number_of_retries(self.REVIEW_URL.format(review_id))
        contents_alter = self.load_page_from_url_with_number_of_retries(self.REVIEW_URL_ALTER.format(review_id))

        for content in [contents, contents_alter]:
            try:
                start_index = content.find("webAnalyticsConfig:") + len("webAnalyticsConfig:")
                end_index = content.find(",\nwidgetInitializers:initializers", start_index)

                self.review_json = content[start_index:end_index]
                self.review_json = json.loads(self.review_json)
            except:
                self.review_json = None

            review_html = html.fromstring(re.search('"BVRRSecondaryRatingSummarySourceID":" (.+?)"},\ninitializers={', content).group(1))
            reviews_by_mark = review_html.xpath("//*[contains(@class, 'BVRRHistAbsLabel')]/text()")
            reviews_by_mark = reviews_by_mark[:5]
            review_list = [[5 - i, int(re.findall('\d+', mark)[0])] for i, mark in enumerate(reviews_by_mark)]

            if not review_list:
                review_list = None

            if review_list:
                break

        self.review_list = review_list

        return self.review_list

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        if self.tree_html.xpath("//div[@id='priceDetails']//span[@class='gallery_page_price flt_wdt comparisonPrice']"):
            price = self.tree_html.xpath("//div[@id='priceDetails']//span[@class='gallery_page_price flt_wdt comparisonPrice']")[0].text_content().strip().replace(",", "")
            price = re.search(ur'([$])([\d,]+(?:\.\d{2})?)', price).groups()
            price = price[0] + price[1]

            return price

        if self.tree_html.xpath("//span[contains(@class, 'gallery_page_price') and @itemprop='price']"):
            price = self.tree_html.xpath("//span[contains(@class, 'gallery_page_price') and @itemprop='price']")[0].text_content().strip()
            price = re.search(ur'([$])([\d,]+(?:\.\d{2})?)', price).groups()
            price = price[0] + price[1]

            return price

        return None

    def _price_amount(self):
        return float(re.findall(r"\d*\.\d+|\d+", self._price().replace(",", ""))[0])

    def _price_currency(self):
        currency = self._price()[0]

        if currency == "$":
            return "USD"

        return None

    def _marketplace(self):
        return 0

    def _site_online(self):
        return 1

    def _in_stores(self):
        if self.tree_html.xpath("//input[@class='bp-pp-btn-check-availability']"):
            return 1

        return 0

    def _site_online_out_of_stock(self):
        try:
            session_value = self.tree_html.xpath("//input[@name='_dynSessConf']/@value")[0]
            stock_status_json = self.load_page_from_url_with_number_of_retries(self.STOCK_STATUS_URL.format(session_value, self._product_id()))
            stock_status_json = json.loads(stock_status_json)

            if "Out of stock online." in stock_status_json["estimatedDeliveryMsg"]:
                return 1
        except:
            pass

        return 0
    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################    
    def _categories(self):
        categoryies = self.tree_html.xpath("//div[@id='breadcrumb']/ul/li/a/text()")

        if categoryies[0].strip() == "jcpenney":
            categoryies = categoryies[1:]

        if categoryies[-1].strip() == "return to product results":
            categoryies = categoryies[:-1]

        return categoryies if categoryies else None

    def _category_name(self):
        categories = self._categories()

        return categories[-1] if categories else None

    def _brand(self):
        self._extract_price_json()

        if not self.price_json:
            return None

        return self.price_json["products"][0]["lots"][0]["brandName"]

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    def _clean_text(self, text):
        return re.sub(' +', ' ', re.sub("&nbsp;|&#160;", " ", text)).strip()

    ##########################################
    ################ RETURN TYPES
    ##########################################

    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service

    DATA_TYPES = { \
        # CONTAINER : NONE
        "url" : _url, \
        "product_id" : _product_id, \
        "site_id" : _site_id, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "model" : _model, \
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "long_description" : _long_description, \
        "ingredients": _ingredients, \
        "ingredient_count": _ingredients_count,
        "variants": _variants,
        "swatches": _swatches,
        "no_longer_available": _no_longer_available,

        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "video_count" : _video_count, \
        "video_urls" : _video_urls, \
        "pdf_count" : _pdf_count, \
        "pdf_urls" : _pdf_urls, \
        "webcollage" : _webcollage, \
        "wc_360": _wc_360, \
        "wc_emc": _wc_emc, \
        "wc_pdf": _wc_pdf, \
        "wc_prodtour": _wc_prodtour, \
        "wc_video": _wc_video, \
        "htags" : _htags, \
        "keywords" : _keywords, \
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
        "marketplace" : _marketplace, \
        "site_online": _site_online, \
        "site_online_out_of_stock": _site_online_out_of_stock, \
        "in_stores" : _in_stores, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        "mobile_image_same" : _mobile_image_same, \
    }
