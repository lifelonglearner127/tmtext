#!/usr/bin/python

import urllib
import re
import json
import os.path
import requests
from lxml import html

from extract_data import Scraper
from spiders_shared_code.bestbuy_variants import BestBuyVariants
from requests.auth import HTTPProxyAuth

class BestBuyScraper(Scraper):
    
    ##########################################
    ############### PREP
    ##########################################
    INVALID_URL_MESSAGE = "Expected URL format is http://www.bestbuy.com/site/<product-name>/<product-id>.*"

    feature_count = None
    features = None
    video_urls = None
    video_count = None
    pdf_urls = None
    pdf_count = None
    wc_content = None
    wc_video = None
    wc_pdf = None
    wc_prodtour = None
    wc_360 = None

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

    def check_url_format(self):
        """Checks product URL format for this scraper instance is valid.
        Returns:
        True if valid, False otherwise
        """
        m = re.match(r"^http://www\.bestbuy\.com/site/[a-zA-Z0-9%\-\%\_]+/[a-zA-Z0-9]+\.p(\?id=[a-zA-Z0-9]+(&skuId=\d+)?)?$", self.product_page_url)
        return not not m

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        if not self.tree_html.xpath("//meta[@property='og:type' and @content='product']"):
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
        prod_id = self.tree_html.xpath('//div[@id="pdp-model-data"]/@data-product-id')[0]
        return prod_id

    def _site_id(self):
        site_id = re.findall("id=\d+", self.product_page_url)[0][3:]
        return site_id

    def _status(self):
        return "success"

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.tree_html.xpath('//meta[@itemprop="name"]/@content')[0]
    
    def _product_title(self):
        return self.tree_html.xpath('//meta[@itemprop="name"]/@content')[0]

    def _title_seo(self):
        return self.tree_html.xpath('//meta[@itemprop="name"]/@content')[0]

    def _model(self):
        return self.tree_html.xpath('//span[@id="model-value"]/text()')[0]

    def _upc(self):
        return self._specs()['UPC']

    def _specs(self):
        # http://www.bestbuy.com/site/sony-65-class-64-1-2-diag--led-2160p-smart-3d-4k-ultra-hd-tv-black/5005015.p;template=_specificationsTab
        feature_urls = []
        data_tabs = self.tree_html.xpath("//div[@id='pdp-model-data']/@data-tabs")
        jsn = json.loads(data_tabs[0])

        for tab in jsn:
            if tab["id"] == "specifications" or "Details" in tab["id"]:
                url = tab["fragmentUrl"]
                feature_urls.append("http://www.bestbuy.com%s" % url)

        specs = {}

        if feature_urls:
            for url in feature_urls:
                contents = urllib.urlopen(url).read()
                tree = html.fromstring(contents)

                groups = tree.xpath("//div[contains(@class, 'specification-group')]")

                if not groups:
                    groups = tree.xpath("//div[@class='specifications']")

                for group in groups:
                    rows = group.xpath("./ul/li")

                    if rows:
                        for index, r in enumerate(rows):
                            name = r.xpath("./div[@class='specification-name']")[0].text_content().strip()

                            value = r.xpath("./div[@class='specification-value']")[0].text_content().strip()

                            specs[name] = value

        if specs:
            return specs

    def _features(self):
        features = []

        for f in self.tree_html.xpath('//div[@class="feature"]'):
            title = f.xpath('./h4/text()')[0]
            value = f.xpath('./p/text()')[0]

            if title == 'Need more information?':
                continue

            features.append(title + ': ' + value)

        if features:
            return features

    def _feature_count(self):
        if self._features():
            return len(self._features())

    def _model_meta(self):
        return None

    def _description_helper(self):
        rows = self.tree_html.xpath("//div[@itemprop='description']//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        description = "\n".join(rows)
        return description

    def _description(self):
        description = self._description_helper()
        if len(description) < 1:
            return self._long_description_helper()
        return description

    def _long_description_helper(self):
        rows = self.tree_html.xpath("//div[@id='features']//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        description = "\n".join(rows)
        return description

    def _long_description(self):
        description = self._description_helper()
        if len(description) < 1:
            return None
        return self._long_description_helper()

    def _variants(self):
            self.variants = BestBuyVariants()
            self.variants.setupCH(self.tree_html, self.product_page_url)
            variants =  self.variants._variants()

            # Search for variants with Sku
            variants_with_skuId = {}
            for variant in variants:
                if 'skuId' in variant:
                    variants_with_skuId[variant['skuId']] = variant

            # Request prices for those skus
            api_prices_url = 'http://www.bestbuy.com/api/1.0/carousel/prices?skus=%s' % ','.join(variants_with_skuId.keys()) 
            prices_ajax = requests.get(api_prices_url, headers={'User-Agent':'*'})  
            for price_ajax in prices_ajax.json():
                
                # Update price
                vr = variants_with_skuId[price_ajax['skuId']]
                index = variants.index(vr)
                vr['price'] = price_ajax.get('currentPrice',None) or price_ajax.get('regularPrice',None)
                # Replace
                variants.pop(index)
                variants.insert(index,vr)

            return variants


    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_urls = self.tree_html.xpath('//div[contains(@class,"image-wrapper")]/img/@data-src')
        image_urls += self.tree_html.xpath('//div[contains(@class,"image-wrapper")]//img/@data-img-path')
        image_urls = filter(lambda i: not 'default_movies_l.jpg' in i, image_urls)
        if image_urls:
            return map(lambda u: u.split(';')[0], image_urls)
    
    def _image_count(self):
        return len(self._image_urls())

    def _video_urls(self):
        if self.video_count is not None:
            return self.video_urls
        self.video_count = 0
        self.wc_video = 0

        url = self.tree_html.xpath("//ul[@id='media-links']//a/@href")
        if len(url) == 0:
            return None

        video_urls = []
        if "www.bestbuy.com" in url[0]:
            video_urls.append(url[0])
        elif "media.flixcar.com" in url[0]:
            contents = urllib.urlopen(url[0]).read()
            tree = html.fromstring(contents)
            rows = tree.xpath("//div[@id='minisite_multiple_videos']//object/@data")
            rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
            video_urls.append(rows)
        elif "content.webcollage.net" in url[0]:
            redirect_contents = self._wc_content()
            redirect_tree = html.fromstring(redirect_contents)
            tabs = redirect_tree.xpath("//div[@class='wc-ms-navbar']//li//a")
            for tab in tabs:
                tab_txt = ""
                try:
                    tab_txt = tab.xpath(".//span/text()")[0].strip()
                except IndexError:
                    continue
                if '360 view video' == tab_txt.lower() \
                        or 'videos' == tab_txt.lower() \
                        or 'video' == tab_txt.lower() \
                        or 'product tour' == tab_txt.lower():
                    redirect_link2 = tab.xpath("./@href")[0]
                    redirect_link2 = "http://content.webcollage.net" + redirect_link2
                    redirect_contents2 = urllib.urlopen(redirect_link2).read()
                    redirect_tree2 = html.fromstring(redirect_contents2)
                    jsn = json.loads(redirect_tree2.xpath("//div[contains(@class,'wc-json-data')]//text()")[0])
                    for video in jsn["videos"]:
                        try:
                            video_url = video["src"]["src"]
                            if len(video_url) > 0:
                                if not video_url.startswith("http"):
                                    video_url = "http://content.webcollage.net%s" % video_url
                                video_urls.append(video_url)
                                self.wc_video = 1
                        except KeyError:
                            continue
        elif "syndicate.sellpoint.net" in url[0]:
            # contents = urllib.urlopen(url[0]).read()
            # tree = html.fromstring(contents)
            # rows = tree.xpath("//div[@id='minisite_multiple_videos']//object/@data")
            # rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
            # video_urls.append(rows)
            self.video_count = 1

        if len(video_urls) < 1:
            return None
        self.video_urls = video_urls
        self.video_count = len(self.video_urls)
        return video_urls

    def _video_count(self):
        if self.video_count is None:
            self._video_urls()
        return self.video_count

    def _pdf_urls(self):
        if self.pdf_count is not None:
            return self.pdf_urls
        self.pdf_count = 0
        self.wc_pdf = 0
        pdfs = self.tree_html.xpath("//div[@id='pdp-content']//a[contains(@href,'.pdf')]")
        pdf_hrefs = []
        for pdf in pdfs:
            pdf_url_txts = [self._clean_text(r) for r in pdf.xpath(".//text()") if len(self._clean_text(r)) > 0]
            if len(pdf_url_txts) > 0:
                pdf_hrefs.append(pdf.attrib['href'])

        redirect_contents = self._wc_content()
        redirect_tree = html.fromstring(redirect_contents)
        tabs = redirect_tree.xpath("//div[@class='wc-ms-navbar']//li//a")
        for tab in tabs:
            tab_txt = ""
            try:
                tab_txt = tab.xpath(".//span/text()")[0].strip()
            except IndexError:
                continue
            if 'more info' == tab_txt.lower():
                redirect_link2 = tab.xpath("./@href")[0]
                redirect_link2 = "http://content.webcollage.net" + redirect_link2
                redirect_contents2 = urllib.urlopen(redirect_link2).read()
                redirect_tree2 = html.fromstring(redirect_contents2)
                rows = redirect_tree2.xpath("//div[@id='wc-pc-content']//a[contains(@class,'wc-document-view-link')]/@data-asset-url")
                rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
                rows = list(set(rows))
                rows = ["http://content.webcollage.net%s" % r for r in rows]
                if len(rows) > 0:
                    pdf_hrefs += rows
                    self.wc_pdf = 1

        if len(pdf_hrefs) < 1:
            return None
        self.pdf_count = len(pdf_hrefs)
        self.pdf_urls = pdf_hrefs
        return pdf_hrefs
    
    def _pdf_count(self):
        if self.pdf_count is None:
            self._pdf_urls()
        return self.pdf_count

    def _wc_content(self):
        if self.wc_content == None:
            url = self.tree_html.xpath("//ul[@id='media-links']//a/@href")
            if len(url) == 0:
                return ""
            if "webcollage.net" in url[0]:
                contents = urllib.urlopen(url[0]).read()
                tree = html.fromstring(contents)
                redirect_link = tree.xpath("//div[@id='slow-reporting-message']//a/@href")[0]
                redirect_contents = urllib.urlopen(redirect_link).read()
                self.wc_content = redirect_contents.replace("\\","")
                return self.wc_content
        return self.wc_content

    def _wc_360(self):
        if self.wc_360 is None:
            self._wc_prodtour()
        return self.wc_360

    def _wc_pdf(self):
        if self.pdf_count is None:
            self._pdf_urls()
        return self.wc_pdf

    def _wc_video(self):
        if self.video_count is None:
            self._video_urls()
        return self.wc_video

    def _wc_emc(self):
        if self._webcollage() == 1:
            return 1
        return 0

    def _wc_prodtour(self):
        if self.wc_prodtour is not None:
            return self.wc_prodtour
        redirect_contents = self._wc_content()
        redirect_tree = html.fromstring(redirect_contents)
        tabs = redirect_tree.xpath("//div[@class='wc-ms-navbar']//li//a")
        self.wc_prodtour = 0
        self.wc_360 = 0
        for tab in tabs:
            redirect_link2 = tab.xpath("./@href")[0]
            redirect_link2 = "http://content.webcollage.net" + redirect_link2
            redirect_contents2 = urllib.urlopen(redirect_link2).read()
            redirect_tree2 = html.fromstring(redirect_contents2)
            if len(redirect_tree2.xpath("//div[contains(@class,'wc-tour-inner-inline')]")) > 0:
                self.wc_prodtour = 1
            if len(redirect_tree2.xpath("//div[contains(@class,'wc-threeSixty')]")) > 0:
                self.wc_360 = 1
        return self.wc_prodtour

    def _flixmedia(self):
        url = self.tree_html.xpath("//ul[@id='media-links']//a/@href")
        if len(url) > 0:
            if "flixcar.com" in url[0]:
                return 1
        return 0

    def _webcollage(self):
        content = self._wc_content()
        if content is not None and len(content) > 0:
            return 1
        return 0

    def _sellpoints(self):
        url = self.tree_html.xpath("//ul[@id='media-links']//a/@href")
        if len(url) > 0:
            if "sellpoint.net" in url[0]:
                return 1
        return 0

    def _htags(self):
        htags_dict = {}
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        return self.tree_html.xpath('//meta[@name="keywords"]/@content')[0]

    # extracts whether the first product image is the "no-image" picture
    def _no_image(self):
        None

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _average_review(self):
        if self._review_count() > 0:
            return float(self.tree_html.xpath('//span[@itemprop="ratingValue"]//text()')[0])

        return None

    def _review_count(self):
        if not self.tree_html.xpath('//meta[@itemprop="reviewCount"]/@content'):
            return 0

        return int(self.tree_html.xpath('//meta[@itemprop="reviewCount"]/@content')[0].replace(',', ''))
 
    def _max_review(self):
        if self._review_count() == 0:
            return None

        reviews = self._reviews()

        for review in reviews:
            if review[1] > 0:
                return review[0]

    def _min_review(self):
        if self._review_count() == 0:
            return None

        reviews = self._reviews()
        reviews = reviews[::-1]

        for review in reviews:
            if review[1] > 0:
                return review[0]

    def _reviews(self):
        if not self.tree_html.xpath('//div[@class="ratings-tooltip-content"]/div[@class="star-breakdowns"]'):
            return None

        reviews = [5, 4, 3, 2, 1]
        review_count_list = self.tree_html.xpath('//div[@class="ratings-tooltip-content"]/div[@class="star-breakdowns"]')[0].\
            xpath('div[@class="star-breakdown"]/div[@class="star-count"]/text()')

        for i, review_count in enumerate(review_count_list):
            review_count_list[i] = int(re.findall("\d+", review_count)[0])

        reviews = [list(a) for a in zip(reviews, review_count_list)]

        return reviews

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        meta_price = self.tree_html.xpath('//meta[@itemprop="price"]//@content')
        if meta_price:
            return meta_price[0].strip()
        else:
            return None

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

    def _in_stores(self):
        rows = self.tree_html.xpath("//a[contains(@title,'Add to Registry')]")
        if len(rows) > 0:
            return 1
        return 0

    def _marketplace(self):
        rows = self.tree_html.xpath("//div[contains(@class,'marketplace-puck')]//a//text()")
        rows = [r for r in rows if "Marketplace" in r]
        if len(rows) > 0:
            return 1
        return 0

    def _marketplace_sellers(self):
        if self._marketplace() == 1:
            rows = self.tree_html.xpath("//div[contains(@class,'marketplace-featured')]/a//text()")
            rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
            return rows
        return None

    def _marketplace_lowest_price(self):
        return None

    def _marketplace_out_of_stock(self):
        """Extracts info on whether currently unavailable from any marketplace seller - binary
        Uses functions that work on both old page design and new design.
        Will choose whichever gives results.
        Returns:
            1/0
        """
        return None

    def _site_online(self):
        # site_online: the item is sold by the site (e.g. "sold by Amazon") and delivered directly, without a physical store.
        return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        if self._site_online() == 0:
            return None
        rows = self.tree_html.xpath("//div[contains(@class,'cart-button')]/@data-add-to-cart-message")
        if "Sold Out Online" in rows:
            return 1
        return 0

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        if self._in_stores() == 0:
            return None
        return 0

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################    
    def _categories(self):
        categories = self.tree_html.xpath("//ol[@id='breadcrumb-list']/li/a/text()")[1:]

        if categories:
            return categories

        return None

    def _category_name(self):
        return self._categories()[-1]
    
    def _brand(self):
        if self.tree_html.xpath('//meta[@id="schemaorg-brand-name"]/@content'):
            return self.tree_html.xpath('//meta[@id="schemaorg-brand-name"]/@content')[0]
    
        if self.tree_html.xpath('//span[@id="publisher-value"]/text()'):
            return self.tree_html.xpath('//span[@id="publisher-value"]/text()')[0]

        return None

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
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
        "upc" : _upc,\
        "model_meta" : _model_meta, \
        "description" : _description, \
        "long_description" : _long_description, \
        "variants": _variants, \
        
        # CONTAINER : PAGE_ATTRIBUTES
        "image_count" : _image_count,\
        "image_urls" : _image_urls, \
        "no_image" : _no_image, \
        "htags" : _htags, \
        "keywords" : _keywords, \

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
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "marketplace_out_of_stock" : _marketplace_out_of_stock, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \
        "in_stores_out_of_stock" : _in_stores_out_of_stock, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \

        "loaded_in_seconds" : None, \
        }

    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        # CONTAINER : PRODUCT_INFO
        "specs" : _specs, \
        "features" : _features, \
        "feature_count" : _feature_count, \

        # CONTAINER : PAGE_ATTRIBUTES
        "mobile_image_same" : _mobile_image_same, \
        "webcollage" : _webcollage, \
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "wc_emc" : _wc_emc, \
        "wc_360" : _wc_360, \
        "wc_video" : _wc_video, \
        "wc_pdf" : _wc_pdf, \
        "wc_prodtour" : _wc_prodtour, \
        "flixmedia" : _flixmedia, \
        "sellpoints": _sellpoints, \
    }