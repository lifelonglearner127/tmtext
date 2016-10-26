#!/usr/bin/python
#  -*- coding: utf-8 -*-

import re
import json
import urllib
import requests
from lxml import html

from extract_data import Scraper
from spiders_shared_code.target_variants import TargetVariants

class TargetScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www\.target\.com/p/([a-zA-Z0-9\-]+)/-/A-([0-9A-Za-z]+)"

    max_score = None
    min_score = None
    review_count = None
    average_review = None
    reviews = None

    WEBCOLLAGE_CHANNEL_URL = "http://content.webcollage.net/target/product-content-page?channel-product-id={0}"
    WEBCOLLAGE_CHANNEL_URL1 = "http://content.webcollage.net/target/power-page?ird=true&channel-product-id={0}"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)

        self.version = None

        self.tv = TargetVariants()
        self.product_json = None
        self.image_json = None

        self.item_info = None
        self.parent_item_info = None
        self.item_info_checked = False

        self.categories = []
        self.categories_checked = False

        self.no_longer_available = 0

        self.wc_360 = 0
        self.wc_emc = 0
        self.wc_video = 0
        self.wc_pdf = 0
        self.wc_prodtour = 0
        self.is_webcollage_contents_checked = False
        self.is_video_checked = False
        self.video_urls = []

    def check_url_format(self):
        # for ex: http://www.target.com/p/skyline-custom-upholstered-swoop-arm-chair/-/A-15186757#prodSlot=_1_1
        m = re.match(r"^http://(www|intl)\.target\.com/p/(([a-zA-Z0-9\-]+)/)?-/A-([0-9A-Za-z]+)", self.product_page_url)
        return not not m

    def not_a_product(self):
        '''Overwrites parent class method that determines if current page
        is not a product page.
        Currently for Amazon it detects captcha validation forms,
        and returns True if current page is one.
        '''

        if len(self.tree_html.xpath("//h2[starts-with(@class, 'product-name item')]/span/text()")) < 1:
            self.version = 2
            try:
                self._get_item_info()

                # parent_item_info might be null, that's ok that means there are no variants
                self.tv.setupCH(self.tree_html, item_info=self.parent_item_info, selected_tcin=self._tcin())
            except Exception as e:
                print e
                self.no_longer_available = 1

        else:
            self.version = 1
            self._extract_product_json()
            self.tv.setupCH(self.tree_html)

        return False

    def _extract_product_json(self):
        if self.tree_html.xpath("//script[contains(text(), 'Target.globals.refreshItems =')]/text()"):
            product_json = self.tree_html.xpath("//script[contains(text(), 'Target.globals.refreshItems =')]/text()")[0]
            start_index = product_json.find("Target.globals.refreshItems =") + len("Target.globals.refreshItems =")
            product_json = product_json[start_index:]
            product_json = json.loads(product_json)
        else:
            product_json = None

        try:
            page_raw_text = html.tostring(self.tree_html)
            start_index = page_raw_text.find("Target.globals.AltImagesJson =") + len("Target.globals.AltImagesJson =")
            end_index = page_raw_text.find("\n", start_index)
            image_json = json.loads(page_raw_text[start_index:end_index])
        except:
            image_json = None

        self.product_json = product_json
        self.image_json = image_json

        return self.product_json

    def _item_info_helper(self, id):
            url = 'http://redsky.target.com/v1/pdp/tcin/' + id + '?excludes=taxonomy&storeId=2791'
            return json.loads( requests.get(url).content)['product']

    def _get_item_info(self):
        if not self.item_info_checked:
            self.item_info_checked = True
            self.item_info = self._item_info_helper( self._product_id())

            if self.item_info['item'].get('parent_items') and type(self.item_info['item']['parent_items']) is not list:
                self.parent_item_info = self._item_info_helper( self.item_info['item']['parent_items'])

            # if the item itself has children, it is a parent item
            elif self.item_info['item'].get('child_items'):
                self.parent_item_info = self.item_info

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        if self.version == 1:
            return str( self.tree_html.xpath("//input[@id='omniPartNumber']/@value")[0])

        # else get it from the url
        return re.search('A-(\d+)', self.product_page_url).group(1)

    def _tcin(self):
        if self.version == 2:
            return self.item_info['item']['tcin']

        tcin = re.search('Online Item #:[^\d]*(\d+)', self.page_raw_text)

        if tcin:
            return tcin.group(1)

        return self._product_id()

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        if self.version == 2:
            return self._product_title()

        return self.tree_html.xpath("//h2[starts-with(@class, 'product-name item')]/span/text()")[0].strip()

    def _product_title(self):
        if self.version == 2:
            return self.item_info['item']['product_description']['title']

        return self.tree_html.xpath("//h2[starts-with(@class, 'product-name item')]/span/text()")[0].strip()

    def _title_seo(self):
        if self.version == 2:
            return self._product_title()

        return self.tree_html.xpath("//title//text()")[0].strip()

    def _model(self):
        return None

    def _upc(self):
        if self.version == 2:
            return self.item_info['item'].get('upc')

        return self.tree_html.xpath("//meta[@property='og:upc']/@content")[0].strip()

    def _features(self):
        if self.version == 2:
            features = self.item_info['item']['product_description']['bullet_description']
            features = map(lambda f : re.sub('<.*?>', '', f).strip(), features)
            if features:
                return features

        rows = self.tree_html.xpath("//ul[@class='normal-list']//li")
        feature_list = []

        for row in rows:
            feature_list.append( self._clean_html( row.text_content()))

        if feature_list:
            return feature_list

        return None

    def _feature_count(self):
        features = len(self._features())
        if features is None:
            return 0
        return len(self._features())

    def _model_meta(self):
        return None

    def _description(self):
        if self.version == 2:
            return self.item_info['item']['product_description']['downstream_description']

        description = "".join(self.tree_html.xpath("//span[@itemprop='description']//text()")).strip()
        description_copy = "".join(self.tree_html.xpath("//div[@class='details-copy']//text()")).strip()
        if description in description_copy:
            description = description_copy
        rows = self.tree_html.xpath("//ul[@class='normal-list']//li")
        lis = []
        for r in rows:
            try:
                strong = r.xpath(".//strong//text()")[0].strip()
                if strong[-1:] == ":":
                    break
            except IndexError:
                pass
            #not feature
            row_txt = " ".join([self._clean_text(i) for i in r.xpath(".//text()") if len(self._clean_text(i)) > 0]).strip()
            row_txt = row_txt.replace("\t", "")
            row_txt = row_txt.replace("\n", "")
            row_txt = row_txt.replace(" , ", ", ")
            lis.append(row_txt)
        description_2nd = "\n".join(lis)
        if len(description_2nd) > 0:
            description += description_2nd

        return description if description else None

    def _color(self):
        return self.tv._color()

    def _size(self):
        return self.tv._size()

    def _style(self):
        return self.tv._style()

    def _color_size_stockstatus(self):
        return self.tv._color_size_stockstatus()

    def _stockstatus_for_variants(self):
        return self.tv._stockstatus_for_variants()

    def _variants(self):
        return self.tv._variants()

    def _swatches(self):
        return self.tv._swatches()

    def _long_description(self):
        if self.version == 2:
            return None

        long_desc_block = self.tree_html.xpath("//ul[starts-with(@class,'normal-list reduced-spacing-list')]")[0]

        return self._clean_text(html.tostring(long_desc_block))

    def _details(self):
        if self.version == 2:
            return self._description()

        details = self.tree_html.xpath('//div[@class="details-copy"]')[0]
        return self._clean_html(html.tostring(details))

    def _mta(self):
        if self.version == 2:
            return ''.join( self.item_info['item']['product_description']['bullet_description'])

        mta = self.tree_html.xpath('//div[@class="details-copy"]/following-sibling::ul')[0]
        return self._clean_html(html.tostring(mta))

    def _no_longer_available(self):
        return self.no_longer_available

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    #returns 1 if the mobile version is the same, 0 otherwise
    def _canonical_link(self):
        return self.item_info['item']['buy_url']

    def _mobile_image_same(self):
        return None

    def _image_urls(self):
        image_urls = []

        if self.version == 2:
            for images in self.item_info['item']['enrichment']['images']:
                base_url = images['base_url']

                image_urls.append(base_url + images['primary'])
                for alt in images.get('alternate_urls', []):
                    image_urls.append(base_url + alt)

            return map( lambda i: i + '?scl=1', image_urls)

        start_index = self.product_page_url.find("/-/A-") + len("/-/A-")
        end_index = self.product_page_url.rfind("?")

        if start_index > end_index:
            product_id = self.product_page_url[start_index:]
        else:
            product_id = self.product_page_url[start_index:end_index]

        for item in self.image_json:
            if product_id in item.keys():
                image_urls = [alt[alt.keys()[0]]["altImage"] for alt in item[product_id]["items"]]
                break

        if image_urls:
            return image_urls

        return None

    def _image_count(self):
        image_urls = self._image_urls()
        return len(image_urls)

    def _video_urls(self):
        if self.is_video_checked:
            return self.video_urls

        self.is_video_checked = True

        self._extract_webcollage_contents()

        video_url = self.tree_html.xpath("//div[@class='videoblock']//div//a/@href")
        video_url = [("http://www.target.com%s" % r) for r in video_url]
        video_url2 = video_url[:]
        video_url = []

        for item in video_url2:
            contents = urllib.urlopen(item).read()
            tree = html.fromstring(contents)
            links = tree.xpath("//ul[@class='media-thumbnails']//a/@href")
            flag = False

            for link in links:
                try:
                    link = re.findall(r'^(.*?),', link)[0]
                    video_url.append(link)
                    flag = True
                except:
                    pass

        if video_url:
            self.video_urls.extend(video_url)

        if self.video_urls:
            self.video_urls = list(set(self.video_urls))
        else:
            self.video_urls = None

        return self.video_urls

    def _video_count(self):
        if self._video_urls():
            return len(self._video_urls())

        return 0

    def _pdf_urls(self):
        pdfs = self.tree_html.xpath("//a[contains(@href,'.pdf')]")
        pdf_hrefs = []
        for pdf in pdfs:
            pdf_hrefs.append(pdf.attrib['href'])

        # get from webcollage
        url = "http://content.webcollage.net/target/smart-button?ird=true&channel-product-id=%s" % self._product_id()
        contents = urllib.urlopen(url).read()
        wc_pdfs = re.findall(r'href=\\\"([^ ]*?\.pdf)', contents, re.DOTALL)
        wc_pdfs = [r.replace("\\", "") for r in wc_pdfs]
        pdf_hrefs += wc_pdfs

        return pdf_hrefs if pdf_hrefs else None

    def _pdf_count(self):
        urls = self._pdf_urls()
        if urls is not None:
            return len(urls)
        return 0

    def _extract_webcollage_contents(self):
        if self.is_webcollage_contents_checked:
            return

        self.is_webcollage_contents_checked = True

        try:
            webcollage_page_contents = self.load_page_from_url_with_number_of_retries(self.WEBCOLLAGE_CHANNEL_URL1.format(self._product_id()))

            if "_wccontent" not in webcollage_page_contents:
                raise Exception

            self.wc_emc = 1

            webcollage_page_contents = self._find_between(webcollage_page_contents, 'html: "', '"\n').decode('string_escape')
            webcollage_page_contents = html.fromstring(webcollage_page_contents)

            if webcollage_page_contents.xpath("//div[@class='wc-json-data']/text()"):
                wc_json_data = json.loads(webcollage_page_contents.xpath("//div[@class='wc-json-data']/text()")[0])

                if wc_json_data.get("videos", {}):
                    base_video_url = webcollage_page_contents.xpath("//*[@data-resources-base]/@data-resources-base")[0].replace("\/", "/")
                    self.video_urls.extend([base_video_url + video["src"]["src"] for video in wc_json_data["videos"]])
                    self.wc_video = 1
                elif wc_json_data.get("tourViews", {}):
                    self.wc_prodtour = 1

            if webcollage_page_contents.xpath("//*[contains(@class, 'wc-media wc-iframe') and @data-asset-url]/@data-asset-url"):
                data_asset_url = webcollage_page_contents.xpath("//*[contains(@class, 'wc-media wc-iframe') and @data-asset-url]/@data-asset-url")[0].replace("\/", "/")
                data_asset_contents = html.fromstring(self.load_page_from_url_with_number_of_retries(data_asset_url))
                video_id_list = data_asset_contents.xpath("//*[contains(@class, 'video_slider_item interactive_click_action')]/@video_id")
                base_video_url = "http://client.expotv.com/vurl/"
                self.video_urls.extend([base_video_url + video_id for video_id in video_id_list])
                self.wc_video = 1
        except:
            pass

        return

    def _wc_360(self):
        self._extract_webcollage_contents()
        return self.wc_360

    def _wc_emc(self):
        self._extract_webcollage_contents()
        return self.wc_emc

    def _wc_video(self):
        self._extract_webcollage_contents()
        return self.wc_video

    def _wc_pdf(self):
        self._extract_webcollage_contents()
        return self.wc_pdf

    def _wc_prodtour(self):
        self._extract_webcollage_contents()
        return self.wc_prodtour

    def _webcollage(self):
        self._extract_webcollage_contents()

        if self.wc_video == 1 or self.wc_emc or self.wc_360 == 1 or self.wc_pdf == 1 or self.wc_prodtour == 1:
            return 1

        atags = self.tree_html.xpath("//a[contains(@href, 'webcollage.net/')]")

        if len(atags) > 0:
            return 1

        return 0

    # extract htags (h1, h2) from its product product page tree
    def _htags(self):
        htags_dict = {}
        # add h1 tags text to the list corresponding to the "h1" key in the dict
        htags_dict["h1"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h1//text()[normalize-space()!='']"))
        # add h2 tags text to the list corresponding to the "h2" key in the dict
        htags_dict["h2"] = map(lambda t: self._clean_text(t), self.tree_html.xpath("//h2//text()[normalize-space()!='']"))
        return htags_dict

    def _keywords(self):
        if self.version == 1:
            return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _load_reviews(self):
        try:
            if not self.max_score or not self.min_score:
                url = 'http://api.bazaarvoice.com/data/batch.json?passkey=lqa59dzxi6cbspreupvfme30z&apiversion=5.4&resource.q0=products&filter.q0=id%3Aeq%3A' + self._tcin() + '&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_US'

                contents = urllib.urlopen(url).read()
                jsn = json.loads(contents)
                review_info = jsn['BatchedResults']['q0']['Results'][0]['ReviewStatistics']
                self.review_count = review_info['TotalReviewCount']
                self.average_review = review_info['AverageOverallRating']
                self.reviews = None

                min_ratingval = None
                max_ratingval = None

                if self.review_count > 0:
                    self.reviews = [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0]]

                    for review in review_info['RatingDistribution']:
                        if min_ratingval == None or review['RatingValue'] < min_ratingval:
                            if review['Count'] > 0:
                                min_ratingval = review['RatingValue']
                        if max_ratingval == None or review['RatingValue'] > max_ratingval:
                            if review['Count'] > 0:
                                max_ratingval = review['RatingValue']

                        self.reviews[int(review['RatingValue']) - 1][1] = int(review['Count'])

                self.min_score = min_ratingval
                self.max_score = max_ratingval
        except Exception as e:
            print e
            raise

    def _average_review(self):
        self._load_reviews()
        return self.average_review

    def _review_count(self):
        self._load_reviews()
        return self.review_count

    def _max_review(self):
        self._load_reviews()
        return self.max_score

    def _min_review(self):
        self._load_reviews()
        return self.min_score

    def _reviews(self):
        self._load_reviews()
        return self.reviews

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _temp_price_cut(self):
        if self.version == 2:
            if self.item_info['price']['offerPrice']['eyebrow'] == 'OnSale':
                return 1
            return 0

        temp_price_cut = self.tree_html.xpath("//div[@id='price_main']//div[contains(@class,'price')]//ul//li[contains(@class,'eyebrow')]//text()")
        if "TEMP PRICE CUT" in temp_price_cut:
            return 1
        return 0

    def _price(self):
        if self.version == 2:
            return self.item_info['price']['offerPrice']['formattedPrice']

        return self.tree_html.xpath("//span[@itemprop='price']//text()")[0].strip()

    def _price_amount(self):
        if self.version == 2:
            return self.item_info['price']['offerPrice']['price']

        price = self._price()
        price = price.replace(",", "")
        price_amount = re.findall(r"[\d\.]+", price)[0]
        return float(price_amount)

    def _price_currency(self):
        return 'USD'

    def _in_stores(self):
        '''in_stores - the item can be ordered online for pickup in a physical store
        or it can not be ordered online at all and can only be purchased in a local store,
        irrespective of availability - binary
        '''

        if self.version == 2:
            try:
                if self.item_info['available_to_promise_store']['products'][0]['availability'] == 'AVAILABLE':
                    return 1
            except:
                # if any child product is out of stock, this product is out of stock
                for child in self.item_info['item']['child_items']:
                    if child['available_to_promise_store']['products'][0]['availability'] == 'AVAILABLE':
                        return 1
            return 0

        if self.product_json:
            for item in self.product_json:
                if item["Attributes"]["callToActionDetail"]["soldInStores"] == True:
                    return 1

        return 0

    def _marketplace(self):
        '''marketplace: the product is sold by a third party and the site is just establishing the connection
        between buyer and seller. E.g., "Sold by X and fulfilled by Amazon" is also a marketplace item,
        since Amazon is not the seller.
        '''
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
        if self.version == 2:
            try:
                if self.item_info['available_to_promise_network']['availability'] == 'AVAILABLE':
                    return 1
            except:
                # if any child product is online, this product is online
                for child in self.item_info['item']['child_items']:
                    if child['available_to_promise_network']['availability'] == 'AVAILABLE':
                        return 1
            return 0

        if self.product_json:
            for item in self.product_json:
                if item["Attributes"]["callToActionDetail"]["soldOnline"] == True:
                    return 1

        return 0

    def _site_online_out_of_stock(self):
        if self.version == 2:
            if self._site_online() == 1:
                try:
                    if self.item_info['available_to_promise_network']['availability_status'] != 'OUT_OF_STOCK':
                        return 0
                except:
                    # if any child product is NOT out of stock, this product is NOT out of stock
                    for child in self.item_info['item']['child_items']:
                        if child['available_to_promise_network']['availability_status'] != 'OUT_OF_STOCK':
                            return 0
                return 1

            else:
                return None

        #  site_online_out_of_stock - currently unavailable from the site - binary
        if self._site_online() == 1:
            if (self.tree_html.xpath("//div[contains(@class,'buttonmsgcontainer')]//p[contains(@class,'availmsg')]")
                and "out of stock online" in self.tree_html.xpath("//div[contains(@class,'buttonmsgcontainer')]//p[contains(@class,'availmsg')]")[0].text_content()):
                return 1

            if self.tree_html.xpath("//div[@class='shipping']//span[starts-with(@class, 'pdpOneButton-')]") and \
                            "not available" in self.tree_html.xpath("//div[@class='shipping']//span[starts-with(@class, 'pdpOneButton-')]")[0].text_content():
                return 1

            return 0
        else:
            return None

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        if self.version == 2:
            if self._in_stores() == 1:
                try:
                    if self.item_info['available_to_promise_store']['products'][0]['availability_status'] != 'OUT_OF_STOCK':
                        return 0
                except:
                    # if any child product is NOT out of stock, this product is NOT out of stock
                    for child in self.item_info['item']['child_items']:
                        if child['available_to_promise_store']['products'][0]['availability_status'] != 'OUT_OF_STOCK':
                            return 0
                return 1

            else:
                return None

        if self._in_stores() == 1:
            if self.tree_html.xpath("//div[contains(@class,'buttonmsgcontainer')]//p[contains(@class,'availmsg')]") and \
                            "out of stock in stores" in self.tree_html.xpath("//div[contains(@class,'buttonmsgcontainer')]//p[contains(@class,'availmsg')]")[0].text_content():
                return 1

            return 0
        else:
            return None

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        if self.version == 2:
            if not self.categories_checked:
                self.categories_checked = True

                url = 'http://www.target.com/api/content-publish/taxonomy/v1/seo?url=' + urllib.quote_plus(self._url()) + '&children=true&breadcrumbs=true'

                seo = json.loads(requests.get(url).content)

                for i in range(1, len(seo['breadcrumbs'][0])):
                    self.categories.append( seo['breadcrumbs'][0][i]['seo_data']['seo_keywords'])

            return self.categories

        all = self.tree_html.xpath("//div[contains(@id, 'breadcrumbs')]//a/text()")
        out = [self._clean_text(r) for r in all]
        return out[1:] if out else None

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        if self.version == 2:
            return self.item_info['item']['product_brand']['manufacturer_brand']

        # http://www.target.com/s?searchTerm=Target+toys+outdoor+toys+lawn+games+Wubble+Bubble
        url = "http://www.target.com/s?searchTerm=%s" % self._product_name()
        contents = urllib.urlopen(url.encode('utf8')).read()
        tree = html.fromstring(contents)
        lis = tree.xpath("//ul[contains(@class,'productsListView')]//li[contains(@class,'tile standard')]")
        for li in lis:
            try:
                title = li.xpath("//a[contains(@class,'productTitle')]//text()")[0].strip()
                title = title.replace("...", "")
                if title in self._product_name():
                    brand = li.xpath("//a[contains(@class,'productBrand')]//text()")[0].strip()
                    return brand
            except:
                pass
        return None

    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces
#    def _clean_text(self, text):
#        return re.sub("&nbsp;", " ", text).strip()

    def _clean_html(self, content):
        content = re.sub('[\n\t]', ' ', content)
        content = re.sub('<![^>]+>', '', content)
        content = re.sub(' (class|itemprop)="[^"]+"', '', content)
        content = re.sub('\s+', ' ', content)
        content = re.sub('> <', '><', content)

        return content.strip()

    ##########################################
    ################ RETURN TYPES
    ##########################################
    # dictionaries mapping type of info to be extracted to the method that does it
    # also used to define types of data that can be requested to the REST service
    DATA_TYPES = { \
        # CONTAINER : NONE
        "url" : _url, \
        "product_id" : _product_id, \
        "upc" : _upc, \
        "tcin" : _tcin, \

        # CONTAINER : PRODUCT_INFO
        "product_name" : _product_name, \
        "product_title" : _product_title, \
        "title_seo" : _title_seo, \
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "model" : _model, \
        "long_description" : _long_description, \
        "variants": _variants, \
        "swatches": _swatches, \
        "details": _details, \
        "mta": _mta, \
        "no_longer_available": _no_longer_available, \

        # CONTAINER : PAGE_ATTRIBUTES
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "wc_360": _wc_360, \
        "wc_emc": _wc_emc, \
        "wc_video": _wc_video, \
        "wc_pdf": _wc_pdf, \
        "wc_prodtour": _wc_prodtour, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \
        "mobile_image_same" : _mobile_image_same, \
        "canonical_link" : _canonical_link, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "temp_price_cut" : _temp_price_cut, \
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
        "brand" : _brand, \

        "loaded_in_seconds": None \
        }


    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
        # CONTAINER : CLASSIFICATION
         # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : PAGE_ATTRIBUTES
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
    }

