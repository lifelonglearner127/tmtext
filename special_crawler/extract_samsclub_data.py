#!/usr/bin/python
#  -*- coding: utf-8 -*-

import urllib
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
from spiders_shared_code.samsclub_variants import SamsclubVariants


class SamsclubScraper(Scraper):

    ##########################################
    ############### PREP+
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.samsclub.com/sams/(.+/)?(prod)?<prod-id>.ip or http://www.samsclub.com/sams/(.+/)?<cat-id>.cp or http://www.samsclub.com/sams/pagedetails/content.jsp?pageName=<page-name> for shelf pages"

    reviews_tree = None
    max_score = None
    min_score = None
    review_count = 0
    average_review = None
    reviews = None
    image_urls = None
    image_alt = []
    # This is needed to extract alt-text for images of products
    # from second half of shelf page, loaded via ajax
    ajax_alt_text = {}
    image_count = -1
    price = None
    price_amount = None
    price_currency = None
    video_count = None
    video_urls = None
    pdf_count = None
    pdf_urls = None
    failure_type = None
    items = None
    redirect = 0
    sv = SamsclubVariants()

    def __init__(self, **kwargs):
        Scraper.__init__(self, **kwargs)

        self.HEADERS = {'WM_QOS.CORRELATION_ID': '1470699438773', 'WM_SVC.ENV': 'prod', 'WM_SVC.NAME': 'sams-api', 'WM_CONSUMER.ID': '6a9fa980-1ad4-4ce0-89f0-79490bbc7625', 'WM_SVC.VERSION': '1.0.0', 'Cookie': 'myPreferredClub=6612'}

    def check_url_format(self):
        # http://www.samsclub.com/sams/gold-medal-5552pr-pretzel-oven-combo/136709.ip?searchTerm=278253
        if re.match(r"^http://www\.samsclub\.com/sams/(.+/)?.+\.ip", self.product_page_url):
            return True
        return self._is_shelf_url(self.product_page_url)

    def _is_shelf_url(self, url):
        if re.match(r"^http://www\.samsclub\.com/sams/(.+/)?.+\.cp", url) or \
            re.match(r"^http://www\.samsclub\.com/sams/shop/category.jsp\?categoryId=\d+$", url) or \
            re.match(r"^http://www\.samsclub\.com/sams/pagedetails/content.jsp\?pageName=.+$", url):
            return True

    def _is_shelf(self):
        # default is shelf page
        if not self.tree_html.xpath("//div[@class='container' and @itemtype='http://schema.org/Product']"):
            return True

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        redirect_url = None

        h = requests.head(self.product_page_url)

        if h.status_code == 302:
            redirect_url = h.headers['Location']

        else:
            redirect = self.tree_html.xpath('//meta[@http-equiv="Refresh" or @http-equiv="refresh"]/@content')
            if redirect:
                redirect_url = re.search('URL=(.*)', redirect[0], re.I).group(1)

            if not redirect:
                for javascript in self.tree_html.xpath('//script[@type="text/javascript"]/text()'):
                    javascript = re.sub('[\s\'"\+\;]','',javascript)
                    redirect = re.match('location.href=(.*)', javascript)

                    if redirect:
                        redirect_url = redirect.group(1)
                        if not re.match('https?://.+\.samsclub.com', redirect_url):
                            redirect_url = 'http://www.samsclub.com' + redirect_url

        if redirect_url:
            # do not redirect to homepage or shelf pages from non-shelf pages
            if redirect_url == 'http://www.samsclub.com/sams/' or \
                (not self._is_shelf_url(self.product_page_url) and self._is_shelf_url(redirect_url)):
                self.ERROR_RESPONSE['failure_type'] = '404 Not Found'
                return True

            r = requests.get(redirect_url, headers=self.HEADERS)

            self.redirect = 1

            self.product_page_url = redirect_url
            self.page_raw_text = r.content
            self.tree_html = html.fromstring(self.page_raw_text)

        try:
            self.sv.setupCH(self.tree_html)
        except:
            pass

        return False

    ##########################################
    #### ########### CONTAINER : NONE
    ##########################################

    def _canonical_link(self):
        return self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        if self._is_shelf():
            return None

        try:
            product_id = self.tree_html.xpath("//input[@name='/atg/commerce/order/purchase/CartModifierFormHandler.baseProductId']/@value")[0].strip()
            return product_id
        except:
            pass
        try:
            product_id = self.tree_html.xpath("//input[@id='mbxProductId']/@value")[0].strip()
        except IndexError:
            product_id = self.tree_html.xpath("//div[@id='myShoppingList']/@data-productid")[0].strip()
        return product_id
        # product_id = self.tree_html.xpath("//span[@itemprop='productID']//text()")[0].strip()
        # m = re.findall(r"[0-9]+", product_id)
        # if len(m) > 0:
        #     return m[0]
        # else:
        #     return None

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        if not self._is_shelf():
            return self.tree_html.xpath("//span[@itemprop='name']//text()")[0].strip()

    def _product_title(self):
        if not self._is_shelf():
            return self.tree_html.xpath("//span[@itemprop='name']//text()")[0].strip()

    def _title_seo(self):
        return self.tree_html.xpath("//title//text()")[0].strip()
    
    def _model(self):
        if not self._is_shelf():
            return self.tree_html.xpath("//span[@itemprop='model']//text()")[0].strip()

    def _upc(self):
        if not self._is_shelf():
            return self.tree_html.xpath("//input[@id='mbxSkuId']/@value")[0].strip()

    def _features(self):
        if self._is_shelf():
            return None

        lis = self.tree_html.xpath("//div[contains(@class,'itemFeatures')]//li")
        rows = []
        for li in lis:
            txt = "".join(li.xpath(".//text()"))
            rows.append(txt)
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        if len(rows) < 1:
            trs = self.tree_html.xpath("//div[contains(@class,'itemFeatures')]//table//tr")
            rows = []
            for tr in trs:
                tds = tr.xpath(".//td")
                if len(tds) > 0:
                    row_txt = " ".join([self._clean_text(r) for r in tr.xpath(".//text()") if len(self._clean_text(r)) > 0])
                    rows.append(row_txt)
            if len(rows) < 1:
                return None
        return rows

    def _feature_count(self):
        if self._is_shelf():
            return None

        features = len(self._features())
        if features is None:
            return 0
        return len(self._features())

    def _model_meta(self):
        return None

    def _variants(self):
        if self._is_shelf() or self._no_longer_available():
            return None

        return self.sv._variants()

    def _no_longer_available(self):
        if self._is_shelf():
            return None

        try:
            txt = self.tree_html.xpath("//span[@class='lgFont ft14']/text()")
            txt = "" . join(txt)
            if "We're sorry, this item is not available in your selected Club." in txt:
                return True
        except:
            pass

        return False

    def _description(self):
        if self._is_shelf():
            return None

        try:
            description = self._exclude_javascript_from_description(html.tostring(self.tree_html.xpath("//div[contains(@class,'itemBullets')]")[0]).strip())
        except:
            description = None

        if description:
            return description

        return None

    def _long_description(self):
        if self._is_shelf():
            return None

        try:
            long_description = self._exclude_javascript_from_description(
                html.tostring(self.tree_html.xpath("//span[@itemprop='description']")[0]).strip())
        except:
            try:
                long_description = self._exclude_javascript_from_description(
                    html.tostring(self.tree_html.xpath("//div[@itemprop='description']")[0]).strip())
            except:
                long_description = None

        if long_description:
            return long_description

        return None

    def _assembled_size(self):
        arr = self.tree_html.xpath("//div[contains(@class,'itemFeatures')]//h3//text()")
        if 'Assembled Size' in arr:
            return 1
        return 0

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _mobile_image_same(self):
        return None

    def _meta_description(self):
        if self.tree_html.xpath('//meta[@name="description"]/@content'):
            return 1
        return 0

    def _image_urls(self):
        if self._is_shelf():
            images = []

            background_images = re.findall('background: url\(http://.+\)', self.page_raw_text)
            background_images = map(lambda i: re.search('\((http://.+)\)', i).group(1), background_images)

            images += background_images

            other_images = self.tree_html.xpath('//img[not(parent::figure)]/@src')
            images += other_images

            images = filter(lambda i: re.match('^http://', i), images)

            featured_images = self.tree_html.xpath('//category-carousel[@carousel-type="featured"]//img/@src')

            if self.tree_html.xpath('//div[@class="container" and child::nav]//category-carousel[@carousel-type="featured"]'):
                featured_images = featured_images[:3]
            else:
                featured_images = featured_images[:5]

            featured_images = map(lambda i: i.split('?')[0], featured_images)
            images += featured_images
            for image in map(lambda i: i['image'], self._items()):
                if not image in images:
                    images.append(image)

            self.image_count = len(images)
            image_alts = []
            for im in images:
                image_alt = self.tree_html.xpath('//img[contains(@src, "{}")]/@alt'.format(im))
                if not image_alt:
                    image_alt = self.tree_html.xpath('//img[contains(@src, "{}")]/@title'.format(im))
                if not image_alt:
                    image_alt = self.tree_html.xpath('//img[contains("{}", @src)]/@alt'.format(im))
                if not image_alt:
                    image_alt = self.tree_html.xpath('//img[contains(@src, "{}")]/@alt'.format(im.replace("http:",'')))
                if not image_alt:
                    image_alt = self.tree_html.xpath('//img[contains(@ng-src, "{}")]/@alt'.format(im.replace("http:",'')))
                image_alt = image_alt[0] if image_alt else ''
                if not image_alt:
                    image_alt = self.ajax_alt_text.get(im.replace("http:",''), '')
                image_alts.append(image_alt)
            self.image_alt = image_alts
            if images:
                return images

        if self.image_count == -1:
            self.image_urls = None
            self.image_count = 0
            script = "/n".join(self.tree_html.xpath("//div[@class='container']//script//text()"))
            m = re.findall(r"imageList = '(.+)?'", script)
            imglist = m[0]
            url = "http://scene7.samsclub.com/is/image/samsclub/%s?req=imageset,json&id=init" % imglist
            contents = urllib.urlopen(url).read()
            m2 = re.findall(r'\"IMAGE_SET\"\:\"(.*?)\"', contents)
            img_set = m2[0]
            img_urls = []
            if len(img_set) > 0:
                img_arr = img_set.split(",")
                for img in img_arr:
                    img2 = img.split(";")
                    img_url = "http://scene7.samsclub.com/is/image/%s" % img2[0]
                    if img_url[-1:] not in "0123456789":
                        img_urls.append(img_url)

            if len(img_urls) == 0:
                img_urls = self.tree_html.xpath("//div[contains(@class, 'imgCol')]//div[@id='plImageHolder']//img/@src")
                if len(img_urls) < 1:
                    return None
                try:
                    if self._no_image(img_urls[0]):
                        return None
                except Exception, e:
                    print "WARNING: ", e.message

            img_urls = map(lambda u: u + '?wid=1500&hei=1500&fmt=jpg&qlt=80', img_urls)
            image_alts = []
            for im in img_urls:
                im_c = im.replace("http:", '').split('?')[0]
                image_alt = self.tree_html.xpath('//img[contains(@src, "{}")]/@alt'.format(im_c))
                if not image_alt:
                    image_alt = self.tree_html.xpath('//img[contains(@src, "{}")]/@title'.format(im_c))
                if not image_alt:
                    image_alt = self.tree_html.xpath('//img[contains("{}", @src)]/@alt'.format(im_c))
                if not image_alt:
                    image_alt = self.tree_html.xpath('//img[contains(@src, "{}")]/@alt'.format(im_c))
                if not image_alt:
                    image_alt = self.tree_html.xpath(
                        '//img[contains(@ng-src, "{}")]/@alt'.format(im.replace("http:", '')))
                image_alt = image_alt[0] if image_alt else ''
                image_alts.append(image_alt)
            self.image_alt = image_alts
            self.image_urls = img_urls
            self.image_count = len(img_urls)
            # TODO add image alt extraction for single items as well
            return img_urls
        else:
            return self.image_urls

    def _image_alt_text(self):
        if not self.image_count == -1 or not self.image_alt:
            image_urls = self._image_urls()
        return self.image_alt

    def _image_alt_text_len(self):
        if not self.image_alt:
            image_urls = self._image_urls()
        return [len(i) if i else 0 for i in self.image_alt] if self.image_alt else None

    def _image_count(self):
        if self.image_count == -1:
            image_urls = self.image_urls()
        return self.image_count

    # return True if there is a no-image image and False otherwise
    # Certain products have an image that indicates "there is no image available"
    # a hash of these "no-images" is saved to a json file and new images are compared to see if they're the same
    # def _no_image(self):
    #     #get image urls
    #     head = 'http://scene7.samsclub.com/is/image/'
    #     image_url = self.tree_html.xpath("//section[@class='main-details']//script//text()")[1]
    #     image_url = re.findall("scene7PdpData\.s7ImageSet = '(.*)';", image_url)[0]
    #     image_url = image_url.split(',')
    #     image_url = [head+link for link in image_url]
    #     path = 'no_img_list.json'
    #     no_img_list = []
    #     if os.path.isfile(path):
    #         f = open(path, 'r')
    #         s = f.read()
    #         if len(s) > 1:
    #             no_img_list = json.loads(s)
    #         f.close()
    #     first_hash = str(MurmurHash.hash(self.fetch_bytes(image_url[0])))
    #     if first_hash in no_img_list:
    #         return True
    #     else:
    #         return False
    #
    # #read the bytes of an image
    # def fetch_bytes(self, url):
    #     file = cStringIO.StringIO(urllib.urlopen(url).read())
    #     img = Image.open(file)
    #     b = BytesIO()
    #     img.save(b, format='png')
    #     data = b.getvalue()
    #     return data

    def _video_urls(self):
        if self._is_shelf():
            return None

        if self.video_count is not None:
            return self.video_urls
        self.video_count = 0
        rows = self.tree_html.xpath("//div[@id='tabItemDetails']//a/@href")
        rows = [r for r in rows if "video." in r or "/mediaroom/" in r or ("//media." in r and (".flv" in r or ".mov" in r))]

        url = "http://content.webcollage.net/sc/smart-button?ird=true&channel-product-id=%s" % self._product_id()
        html = urllib.urlopen(url).read()
        # \"src\":\"\/_cp\/products\/1374451886781\/tab-6174b48c-58f3-4d4b-8d2f-0d9bf0c90a63
        # \/552b9366-55ed-443c-b21e-02ede6dd89aa.mp4.mobile.mp4\"
        video_base_url = self._find_between(html, 'data-resources-base=\\"', '\\">').replace("\\", "") + "%s"
        m = re.findall(r'"src":"([^"]*?\.mp4)"', html.replace("\\",""), re.DOTALL)
        for item in m:
            if ".blkbry" in item or ".mobile" in item:
                pass
            else:
                if video_base_url % item not in rows and item.count(".mp4") < 2:
                    rows.append(video_base_url % item)
        m = re.findall(r'"src":"([^"]*?\.flv)"', html.replace("\\",""), re.DOTALL)
        for item in m:
            if ".blkbry" in item or ".mobile" in item:
                pass
            else:
                if video_base_url % item not in rows and item.count(".flv") < 2:
                    rows.append(video_base_url % item)
        if len(rows) < 1:
            return None
        new_rows = [r for r in rows if ("%s.flash.flv" % r) not in rows]
        self.video_urls = list(set(new_rows))
        self.video_count = len(self.video_urls)
        return self.video_urls

    def _video_count(self):
        if self._is_shelf():
            return None

        if self.video_count is None:
            self._video_urls()
        return self.video_count

    def _pdf_urls(self):
        if self._is_shelf():
            return None

        if self.pdf_count is not None:
            return self.pdf_urls
        self.pdf_count = 0
        pdf_hrefs = []
        pdfs = self.tree_html.xpath("//a[contains(@href,'.pdf')]")
        for pdf in pdfs:
            try:
                pdf_hrefs.append(pdf.attrib['href'])
            except KeyError:
                pass
        pdfs = self.tree_html.xpath("//a[contains(@href,'pdfpdf')]")
        for pdf in pdfs:
            try:
                if pdf.attrib['href'] not in pdf_hrefs:
                    pdf_hrefs.append(pdf.attrib['href'])
            except KeyError:
                pass
        pdfs = self.tree_html.xpath("//a[contains(@href,'pdf')]")
        for pdf in pdfs:
            try:
                if pdf.attrib['href'].endswith("pdf") and pdf.attrib['href'] not in pdf_hrefs:
                    pdf_hrefs.append(pdf.attrib['href'])
            except KeyError:
                pass
        pdfs = self.tree_html.xpath("//a[contains(@onclick,'.pdf')]")
        for pdf in pdfs:
            # window.open('http://graphics.samsclub.com/images/pool-SNFRound.pdf','_blank')
            try:
                url = re.findall(r"open\('(.*?)',", pdf.attrib['onclick'])[0]
                if url not in pdf_hrefs:
                    pdf_hrefs.append(url)
            except IndexError:
                pass
        pdfs = self.tree_html.xpath("//a[contains(@onclick,'pdf')]")
        for pdf in pdfs:
            # window.open('http://graphics.samsclub.com/images/pool-SNFRound.pdf','_blank')
            try:
                url = re.findall(r"open\('(.*?)',", pdf.attrib['onclick'])[0]
                if url not in pdf_hrefs and url.endswith("pdf"):
                    pdf_hrefs.append(url)
            except IndexError:
                pass
        # http://content.webcollage.net/sc/smart-button?ird=true&channel-product-id=prod8570143
        url = "http://content.webcollage.net/sc/smart-button?ird=true&channel-product-id=%s" % self._product_id()
        html = urllib.urlopen(url).read()
        # \"src\":\"\/_cp\/products\/1374451886781\/tab-6174b48c-58f3-4d4b-8d2f-0d9bf0c90a63
        # \/552b9366-55ed-443c-b21e-02ede6dd89aa.mp4.mobile.mp4\"
        m = re.findall(r'wcobj="([^\"]*?\.pdf)"', html.replace("\\",""), re.DOTALL)
        pdf_hrefs += m
        pdf_hrefs = [r for r in pdf_hrefs if "JewelryDeliveryTimeline.pdf" not in r]
        if len(pdf_hrefs) < 1:
            return None
        self.pdf_urls = pdf_hrefs
        self.pdf_count = len(self.pdf_urls)
        return pdf_hrefs

    def _pdf_count(self):
        if self._is_shelf():
            return None

        if self.pdf_count is None:
            self._pdf_urls()
        return self.pdf_count

    def _webcollage(self):
        if self._is_shelf():
            return None

        # http://content.webcollage.net/sc/smart-button?ird=true&channel-product-id=prod10740044
        url = "http://content.webcollage.net/sc/smart-button?ird=true&channel-product-id=%s" % self._product_id()
        html = urllib.urlopen(url).read()
        m = re.findall(r'_wccontent = (\{.*?\});', html, re.DOTALL)
        try:
            if ".webcollage.net" in m[0]:
                return 1
        except IndexError:
            pass
        return 0

    # extract htags (h1, h2) from its product product page tree
    def _htags(self):
        htags_dict = {}
        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = filter(None, map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']")))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = filter(None, map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']")))
        return htags_dict

    def _keywords(self):
        try:
            return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]
        except:
            pass

    # Not used after reviews fix
    @staticmethod
    def _return_br_block_for_prod_id(brs, prod_id):
        for key, value in brs['BatchedResults'].items():
            for sub_group in value['Results']:
                if sub_group.get('Id', None) == prod_id:
                    return sub_group
        for key, value in brs['BatchedResults'].items():
            for sub_group_product, sub_group_product_data in value['Includes'].get('Products', {}).items():
                if sub_group_product == prod_id:
                    return sub_group_product_data

    def _get_category_items(self, cat_id, sub=False):
        items = []

        try:
            url = 'http://www.samsclub.com/sams/redesign/common/model/loadDataModel.jsp?dataModelId=' + cat_id + '&dataModelType=categoryDataModel'

            c = requests.get(url, headers=self.HEADERS).content
            h = html.fromstring(c)

            price = None

            try:
                price = float(item.xpath('.//span[@data-price]/@data-price')[0])
            except:
                pass

            for item in h.xpath('//div[contains(@class,"sc-product-card")]')[:5]:
                i = {
                    'image' : 'http:' + item.xpath('.//img/@src')[0].split('?')[0],
                    'price' : price
                }

                items.append(i)

        except Exception as e:
            #print 'EXCEPT', e
            url = 'http://www.samsclub.com/soa/services/v1/catalogsearch/search?searchCategoryId=' + cat_id

            j = json.loads(requests.get(url, headers=self.HEADERS).content)

            records = j['payload'].get('records', [])

            if sub:
                records = records[:5]

            for record in records:
                price = None
                # This is needed to extract alt-text for images of products
                # from second half of shelf page, loaded via ajax
                self.ajax_alt_text[record.get('listImage')] = record.get('productName')
                if record.get('clubPricing') and not record['clubPricing']['forceLoginRequired']:
                    price = record['clubPricing']['finalPrice']['currencyAmount']

                elif record.get('onlinePricing') and not record['onlinePricing']['forceLoginRequired']:
                    price = record['onlinePricing']['finalPrice']['currencyAmount']

                i = {
                    'image': 'http:' + record['listImage'],
                    'price': price
                }

                items.append(i)

        return items

    def _items(self):
        if self.items:
            return self.items

        self.items = []

        # If the original page displays no product cards (e.g. http://www.samsclub.com/sams/pirelli/5950114.cp or http://www.samsclub.com/sams/shocking-values/13450112.cp), then return no items
        if not self.tree_html.xpath('//div[contains(@class,"sc-product-card")]'):
            return self.items

        subcategories = self.tree_html.xpath('//section[starts-with(@id,"catLowFtrdCrsl")]/@ng-controller')

        # If it is a meta-category page
        if subcategories:
            for subcategory in subcategories:
                cat_id = re.search('_(\d+)$', subcategory).group(1)

                self.items += self._get_category_items(cat_id, True)

        # Otherwise it is a normal category page
        else:
            cat_id = re.match('.*/(\d+)\.(cp|ip)', self._url()).group(1)

            self.items += self._get_category_items(cat_id)

        return self.items

    def _results_per_page(self):
        if self._is_shelf():
            return len(self._items())

    def _total_matches(self):
        if self._is_shelf():
            try:
                return int(re.search('\'totalRecords\':\'(\d+)\'', self.page_raw_text).group(1))
            except:
                pass

    def _lowest_item_price(self):
        if self._is_shelf():
            low_price = None

            for item in self._items():
                if item['price'] is None:
                    continue

                if not low_price or item['price'] < low_price:
                    low_price = item['price']

            return low_price

    def _highest_item_price(self):
        if self._is_shelf():
            high_price = None

            for item in self._items():
                if item['price'] is None:
                    continue

                if not high_price or item['price'] > high_price:
                    high_price = item['price']

            return high_price

    def _num_items_price_displayed(self):
        if self._is_shelf():
            n = 0

            for item in self._items():
                if item.get('price'):
                    n += 1

            return n

    def _num_items_no_price_displayed(self):
        if self._is_shelf():
            return self._results_per_page() - self._num_items_price_displayed()

    def _meta_description_count(self):
        try:
            return len(self.tree_html.xpath('//meta[@name="description"]/@content')[0])
        except:
            pass

    def _body_copy(self):
        if self._is_shelf():
            body_copy = ''

            for elem in self.tree_html.xpath('//*[contains(@class,"categoryText")]/*'):
                body_copy += html.tostring(elem)

            if body_copy:
                return body_copy

    def _body_copy_links(self):
        cat_id = re.match('.*/(.+)\.(cp|ip)', self._url()).group(1)

        if not self.tree_html.xpath('//*[contains(@class,"categoryText")]'):
            return None

        links = self.tree_html.xpath('//*[contains(@class,"categoryText")]//a/@href')

        return_links = {'self_links' : {'count': 0},
                        'broken_links' : {'links' : {}, 'count' : 0}}

        for link in links:
            if not re.match('http://www.samsclub.com', link):
                link = 'http://www.samsclub.com' + link

            if re.search(cat_id + '.cp$', link) or re.search(cat_id + '.ip$', link):
                return_links['self_links']['count'] += 1

            else:
                status_code = requests.head(link).status_code

                if not status_code == 200:
                    return_links['broken_links']['links'][link] = status_code
                    return_links['broken_links']['count'] += 1

        return return_links

    def _redirect(self):
        return self.redirect

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    #populate the reviews_tree variable for use by other functions
    def _load_reviews(self):
        try:
            if not self.max_score or not self.min_score:
                # for ex: http://samsclub.ugc.bazaarvoice.com/1337/prod12250457/reviews.djs?format=embeddedhtml
                url = "http://samsclub.ugc.bazaarvoice.com/1337/%s/reviews.djs?format=embeddedhtml" % self._product_id()
                contents = urllib.urlopen(url).read()
                if 'page you have requested cannot be found' in contents.lower():
                    # url = ('http://api.bazaarvoice.com/data/batch.json?passkey=dap59bp2pkhr7ccd1hv23n39x&apiversion=5.5'
                    #        '&displaycode=1337-en_us&resource.q0=products&filter.q0=id%3Aeq%3Aprod16470189'
                    #        '&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews'
                    #        '&filter_questions.q0=contentlocale%3Aeq%3Aen_US&filter_answers.q0=contentlocale%3Aeq%3Aen_US'
                    #        '&filter_reviews.q0=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_US'
                    #        '&resource.q1=reviews&filter.q1=isratingsonly%3Aeq%3Afalse&filter.q1=productid%3Aeq%3A{prod_id}'
                    #        '&filter.q1=contentlocale%3Aeq%3Aen_US&sort.q1=helpfulness%3Adesc%2Ctotalpositivefeedbackcount%3Adesc'
                    #        '&stats.q1=reviews&filteredstats.q1=reviews&include.q1=authors%2Cproducts%2Ccomments'
                    #        '&filter_reviews.q1=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q1=contentlocale%3Aeq%3Aen_US'
                    #        '&filter_comments.q1=contentlocale%3Aeq%3Aen_US&limit.q1=8&offset.q1=0&limit_comments.q1=3'
                    #        '&resource.q2=reviews&filter.q2=productid%3Aeq%3A{prod_id}&filter.q2=contentlocale%3Aeq%3Aen_US'
                    #        '&limit.q2=1&resource.q3=reviews&filter.q3=productid%3Aeq%3A{prod_id}'
                    #        '&filter.q3=isratingsonly%3Aeq%3Afalse&filter.q3=rating%3Agt%3A3'
                    #        '&filter.q3=totalpositivefeedbackcount%3Agte%3A3&filter.q3=contentlocale%3Aeq%3Aen_US'
                    #        '&sort.q3=totalpositivefeedbackcount%3Adesc&include.q3=authors%2Creviews%2Cproducts'
                    #        '&filter_reviews.q3=contentlocale%3Aeq%3Aen_US&limit.q3=1&resource.q4=reviews'
                    #        '&filter.q4=productid%3Aeq%3A{prod_id}&filter.q4=isratingsonly%3Aeq%3Afalse'
                    #        '&filter.q4=rating%3Alte%3A3&filter.q4=totalpositivefeedbackcount%3Agte%3A3'
                    #        '&filter.q4=contentlocale%3Aeq%3Aen_US&sort.q4=totalpositivefeedbackcount%3Adesc'
                    #        '&include.q4=authors%2Creviews%2Cproducts&filter_reviews.q4=contentlocale%3Aeq%3Aen_US'
                    #        '&limit.q4=1&callback=bv_1111_4516')
                    url = "http://api.bazaarvoice.com/data/reviews.json?apiversion=5.5&passkey=dap59bp2pkhr7ccd1hv23n39x" \
                   "&Filter=ProductId:{prod_id}&Include=Products&Stats=Reviews"
                    contents = urllib.urlopen(url.format(prod_id=self._product_id())).read()
                tmp_reviews = re.findall(r'<span class=\\"BVRRHistAbsLabel\\">(.*?)<\\/span>', contents)
                reviews = []
                for review in tmp_reviews:
                    review = review.replace(",", "")
                    m = re.findall(r'([0-9]+)', review)
                    reviews.append(m[0])

                reviews = reviews[:5]

                scores = [v[0] for v in self.reviews if int(v[1]) > 0]
                self.max_score = max(scores)
                self.min_score = min(scores)

                self.reviews = []
                score = 1
                total_review = 0
                review_cnt = 0
                for review in reversed(reviews):
                    self.reviews.append([score, int(review)])
                    total_review += score * int(review)
                    review_cnt += int(review)
                    score += 1
                self.review_count = review_cnt
                self.average_review = total_review * 1.0 / review_cnt
                # self.reviews_tree = html.fromstring(contents)

                if not self.review_count or not self.average_review:
                    raise BaseException  # we have to jump to the version #2
        except:
            if not self.review_count or not self.average_review:
                contents = json.loads(contents)
                incl = contents.get('Includes')
                brs = incl.get('Products').get(self._product_id()) if incl else None
                #import pdb; pdb.set_trace()
                distrib = [(d['RatingValue'], d['Count']) for d in brs['ReviewStatistics']['RatingDistribution']]
                self.reviews = sorted(distrib, key=lambda val: val[0], reverse=True)
                self.review_count = brs['ReviewStatistics']['TotalReviewCount']
                self.average_review = brs['ReviewStatistics']['AverageOverallRating']

                scores = [v[0] for v in self.reviews if int(v[1])>0]
                self.max_score = max(scores)
                self.min_score = min(scores)

    def _average_review(self):
        if self._is_shelf():
            return None

        self._load_reviews()
        return float("%.2f" % self.average_review)

    def _review_count(self):
        if self._is_shelf():
            return None

        self._load_reviews()
        return self.review_count

    def _max_review(self):
        if self._is_shelf():
            return None

        self._load_reviews()
        return self.max_score

    def _min_review(self):
        if self._is_shelf():
            return None

        self._load_reviews()
        return self.min_score

    def _reviews(self):
        if self._is_shelf():
            return None

        self._load_reviews()
        if len(self.reviews) < 1:
            return None
        return self.reviews

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        if self._is_shelf():
            return None

        if self.price:
            return self.price
        try:
            price_amount = self.tree_html.xpath("//span[@class='price']//text()")[0].strip()
            currency = self.tree_html.xpath("//span[@class='superscript']//text()")[0].strip()
            superscript = self.tree_html.xpath("//span[@class='superscript']//text()")[1].strip()
            price = "%s%s.%s" % (currency, price_amount, superscript)
            self.price = price
            return price
        except:
            pass
        try:
            if self._site_online() == 0:
                return "not available online - no price given"
        except:
            pass
        return None

    def _price_amount(self):
        if self._is_shelf():
            return None

        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        return float(price_amount)

    def _price_currency(self):
        if self._is_shelf():
            return None

        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        price_currency = price.replace(price_amount, "")
        if price_currency == "$":
            return "USD"
        return price_currency

    def _in_stores(self):
        '''in_stores - the item can be ordered online for pickup in a physical store
        or it can not be ordered online at all and can only be purchased in a local store,
        irrespective of availability - binary
        '''
        if self._is_shelf():
            return None

        in_stores = None
        rows = self.tree_html.xpath("//div[contains(@class,'moneyBoxContainer')]//div[contains(@class,'moneyBoxBtn')]//text()")
        if "Visit your local Club for pricing & availability" in rows:
            in_stores = 1
        rows = self.tree_html.xpath("//div[@id='itemPageMoneyBox']//span//text()")
        rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        if "Select your Club" in rows and "for price and availability" in rows:
            in_stores = 1
        if in_stores is not None:
            return in_stores
        return 0

    def _marketplace(self):
        '''marketplace: the product is sold by a third party and the site is just establishing the connection
        between buyer and seller. E.g., "Sold by X and fulfilled by Amazon" is also a marketplace item,
        since Amazon is not the seller.
        '''
        if self._is_shelf():
            return None

        return 0

    def _marketplace_sellers(self):
        '''marketplace_sellers - the list of marketplace sellers - list of strings (["seller1", "seller2"])
        '''
        return None

    def _marketplace_lowest_price(self):
        # marketplace_lowest_price - the lowest of marketplace prices - floating-point number
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
        if self._is_shelf():
            return None

        rows = self.tree_html.xpath("//*[@id='addtocartsingleajaxonline']")
        if len(rows) > 0:
            return 1
        rows = self.tree_html.xpath("//div[contains(@class,'biggraybtn')]//text()")
        if "Out of stock online" in rows:
            return 1
        rows = self.tree_html.xpath("//div[contains(@class,'moneyBoxContainer')]//div[contains(@class,'moneyBoxBtn')]//text()")
        if "See online price in cart" in rows:
            return 1
        rows = self.tree_html.xpath("//button[@class='biggreenbtn']//text()")
        if len(rows) > 0:
            return 1
        return 0
        #
        # rows = self.tree_html.xpath("//div[contains(@class,'moneyBoxContainer')]//div[contains(@class,'moneyBoxBtn')]//text()")
        # site_online = None
        # if "Buy online" in rows:
        #     return 1
        # if "Unavailable online" in rows:
        #     site_online = 0
        # rows = self.tree_html.xpath("//div[@id='itemPageMoneyBox']//span//text()")
        # rows = [self._clean_text(r) for r in rows if len(self._clean_text(r)) > 0]
        # if "Select your Club" in rows and "for price and availability" in rows:
        #     site_online = 0
        # if site_online is not None:
        #     return site_online
        # return 1

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        if self._is_shelf():
            return None

        if self._site_online() == 1:
            if self.tree_html.xpath("//*[@itemprop='availability']/@href")[0] == "http://schema.org/OutOfStock":
                return 1

            return 0

        return None

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        if self._is_shelf():
            return None

        if self._in_stores() == 1:
            return 1

        return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        if self._is_shelf():
            all = self.tree_html.xpath("//ol[@id='breadCrumbs']/li/span/a/text()")
        else:
            all = self.tree_html.xpath("//div[@class='breadcrumb-child']/a/span/text()")[1:]

        out = [self._clean_text(r) for r in all]

        if out:
            return out

    def _category_name(self):
        if not self._is_shelf():
            return self._categories()[-1]

    def _brand(self):
        if not self._is_shelf():
            return self.tree_html.xpath("//span[@itemprop='brand']//text()")[0].strip()

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
        "product_id" : _product_id, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "model" : _model, \
        "upc" : _upc,\
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "long_description" : _long_description, \
        "variants": _variants, \
        "no_longer_available": _no_longer_available, \
        "assembled_size": _assembled_size, \

        # CONTAINER : PAGE_ATTRIBUTES
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "mobile_image_same" : _mobile_image_same, \
        "meta_description" : _meta_description, \
        "meta_description_count" : _meta_description_count, \
        "results_per_page" : _results_per_page, \
        "total_matches" : _total_matches, \
        "lowest_item_price" : _lowest_item_price, \
        "highest_item_price" : _highest_item_price, \
        "num_items_price_displayed" : _num_items_price_displayed, \
        "num_items_no_price_displayed" : _num_items_no_price_displayed, \
        "body_copy" : _body_copy, \
        "body_copy_links" : _body_copy_links, \
        "redirect" : _redirect, \
        "image_alt_text": _image_alt_text, \
        "image_alt_text_len": _image_alt_text_len, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "in_stores" : _in_stores, \
        "marketplace": _marketplace, \
        "marketplace_sellers" : _marketplace_sellers, \
        "marketplace_lowest_price" : _marketplace_lowest_price, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \
        "in_stores_out_of_stock" : _in_stores_out_of_stock, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "canonical_link": _canonical_link,
        "brand" : _brand, \

        "loaded_in_seconds": None \
        }


    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        # CONTAINER : PAGE_ATTRIBUTES
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \

         # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \
    }

