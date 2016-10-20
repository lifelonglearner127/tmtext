#!/usr/bin/python
#  -*- coding: utf-8 -*-

from lxml import html
import re, json, requests
from extract_data import Scraper


class SearsScraper(Scraper):

    ##########################################
    ############### PREP
    ##########################################

    INVALID_URL_MESSAGE = "Expected URL format is http://www.sears.com/<product-name>/p-<product-id>"

    def __init__(self, **kwargs):# **kwargs are presumably (url, bot)
        Scraper.__init__(self, **kwargs)
        self.product_info_json = {}
        self.variant_info_jsons = {}

    def check_url_format(self):
        if re.match(r"^http://www\.sears\.com/.+/p-\w+$", self.product_page_url):
            return True
        return False

    def _extract_product_info_json(self, product_id=None):
        if product_id is None:
            product_id = re.search('p-(\w+)$', self.product_page_url).group(1)
            json_info_container = self.product_info_json
        else:
            json_info_container = self.variant_info_jsons.setdefault(product_id, {})

        if not json_info_container:
            url = 'http://www.sears.com/content/pdp/config/products/v1/products/' + product_id

            h = requests.get(
                url,
                # proxies=self.proxy_config["proxies"] if self.proxy_config else None,
                # auth=self.proxy_config["proxy_auth"] if self.proxy_config else None
            ).content

            json_info_container.update(json.loads(re.search('{.*}', h).group(0))['data'])

        return json_info_container


    def not_a_product(self):
        """Checks if current page is not a valid product page
        (an unavailable product page or other type of method)
        Overwrites dummy base class method.
        Returns:
            True if it's an unavailable product page
            False otherwise
        """

        self._extract_product_info_json()

        if self.product_info_json['productstatus']['isDeleted']:
            return True

        return False

    ##########################################
    ############### CONTAINER : NONE
    ##########################################

    def _url(self):
        return self.product_page_url

    def _product_id(self):
        return self.product_info_json['product']['id']

    ##########################################
    ############### CONTAINER : PRODUCT_INFO
    ##########################################
    def _product_name(self):
        return self.product_info_json['product']['name']

    def _product_title(self):
        return self.tree_html.xpath('//div[@class="product-content"]/h1/text()')[0]

    def _title_seo(self):
        return self.product_info_json['product']['seo']['title']
    
    def _model(self):
        if self.product_info_json.get('offer'):
            return self.product_info_json['offer']['modelNo']
        else:
            return self.product_info_json['product']['mfr']['modelNo']

    def _upc(self):
        if self.product_info_json.get('offer'):
            return self.product_info_json['offer']['altIds']['upc']

    def _specs(self):
        specs = {}

        for group in self.product_info_json['product']['specs']:
            for attr in group['attrs']:
                specs[attr['name']] = attr['value']

        if specs:
            return specs

    def _features(self):
        features = []

        if self.product_info_json['product'].get('curatedContents'):
            for g in self.product_info_json['product']['curatedContents']['curatedGrp']:
                for c in g['content']:
                    if c['type'] == 'copy':
                        features.append(c['name'] + ': ' + c['data'])

        if features:
            return features

    def _feature_count(self):
        features = self._features()

        if features:
            return len(features)

        return 0

    def _description(self):
        return self.product_info_json['product']['desc'][0]['val']

    def _long_description(self):
        return self.product_info_json['product']['desc'][1]['val']

    def _variants(self):
        variants = []

        if self.product_info_json.get('attributes'):
            for variant in self.product_info_json['attributes']['variants']:
                v = {
                    'in_stock': variant['isAvailable'],
                    'price': self._price_amount(),
                    'properties': {},
                    'selected': False
                    }

                for attribute in variant['attributes']:
                    v['properties'][attribute['name']] = attribute['value']

                variants.append(v)

        else:
            for swatch in self.product_info_json['offer']['assocs']['linkedSwatch']:
               
                variant = {
                    # 'product_id': swatch['id'],
                    'price': self._price_amount(),
                    'properties': {},
                    'selected': False,
                    # 'url': 'http://www.sears.com' + swatch['url'] + '/p-' + swatch['id']
                    }

                info = self._extract_product_info_json(swatch['id'])

                variant['in_stock'] = (
                    info['offerstatus']['isAvailable'] if info.get('offerstatus') else
                    (
                        any(info['offermapping']['fulfillment'].values()) if
                        info.get('offermapping', {}).get('fulfillment') else False
                    )
                )

                # image_urls = []
                # for group in info['product']['assets']['imgs']:
                #     for image in group['vals']:
                #         image_urls.append(image['src'])
                # if image_urls:
                #     variant['image_urls'] = image_urls
                #     variant['image_count'] = len(image_urls)

                # videos = []
                # for video in info['product']['assets'].get('videos', []):
                #     videos.append(video['link']['attrs']['href'])
                # if videos:
                #     variant['video_urls'] = videos
                #     variant['video_count'] = len(videos)

                # variant['model'] = info['offer']['modelNo']

                # variant['product_title'] = info['offer']['brandName'] + ' ' + info['offer']['name']
                # variant['product_name'] = info['offer']['name']

                for spec in info['product']['specs']:
                    if 'color' in spec['grpName'].lower():
                        for attr in spec['attrs']:
                            if attr['name'].lower().startswith('color'):
                                variant['properties']['color'] = attr['val']
                                break
                        break

                variants.append(variant)

        if variants:
            return variants

    def _swatches(self):
        swatches = []

        if not self.product_info_json.get('attributes'):
            return

        for attribute in self.product_info_json['attributes']['attributes']:
            if attribute['name'] == 'Color':
                for value in attribute['values']:
                    s = {
                        'color' : value['name'],
                        'hero' : 1,
                        'hero_image' : value['primaryImage']['src'],
                        'swatch_name' : 'color',
                        'thumb' : 1,
                        'thumb_image' : value['swatchImage']['src']
                    }

                    swatches.append(s)

        if swatches:
            return swatches

    ##########################################
    ############### CONTAINER : PAGE_ATTRIBUTES
    ##########################################
    def _canonical_link(self):
        return self.tree_html.xpath('//link[@rel="canonical"]/@href')[0]

    def _image_urls(self):
        images = []

        for group in self.product_info_json['product']['assets']['imgs']:
            for image in group['vals']:
                images.append(image['src'])

        if images:
            return images

    def _image_count(self):
        images = self._image_urls()

        if images:
            return len(images)

        return 0

    def _video_urls(self):
        videos = []

        for video in self.product_info_json['product']['assets'].get('videos', []):
            videos.append(video['link']['attrs']['href'])

        if videos:
            return videos

    def _video_count(self):
        video_urls = self._video_urls()

        if video_urls:
            return len(video_urls)

        return 0

    def _pdf_urls(self):
        pdfs = []

        for pdf in self.product_info_json['product']['assets'].get('attachments', []):
            pdfs.append(pdf['link']['attrs']['href'])

        if pdfs:
            return pdfs

    def _pdf_count(self):
        urls = self._pdf_urls()

        if urls:
            return len(urls)

        return 0

    def _webcollage(self):
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
        return self.tree_html.xpath("//meta[@name='keywords']/@content")[0]

    ##########################################
    ############### CONTAINER : REVIEWS
    ##########################################
    def _reviews(self):
        reviews = []

        i = 5

        for value in self.tree_html.xpath('//ul[@class="ratings-graph"]/li/a/text()'):
            reviews.append([i, re.match('\((\d+)\)', value).group(1)])
            i -= 1

        if reviews:
            return reviews

    def _review_count(self):
        return int( self.tree_html.xpath('//span[@itemprop="reviewCount"]/text()')[0])

    def _average_review(self):
        return float( self.tree_html.xpath('//meta[@itemprop="ratingValue"]/@content')[0])

    def _max_review(self):
        return int( self.tree_html.xpath('//meta[@itemprop="bestRating"]/@content')[0])

    def _min_review(self):
        return int( self.tree_html.xpath('//meta[@itemprop="worstRating"]/@content')[0])

    ##########################################
    ############### CONTAINER : SELLERS
    ##########################################
    def _price(self):
        try:
            return '$' + self.tree_html.xpath('//meta[@itemprop="price"]/@content')[0]
        except:
            return self.tree_html.xpath('//li[@class="product-price-big"]//span[@class="price-wrapper"]/text()')[0]

    def _price_amount(self):
        return float(self._price()[1:])

    def _price_currency(self):
        return "USD"

    def _marketplace(self):
        '''marketplace: the product is sold by a third party and the site is just establishing the connection
        between buyer and seller. E.g., "Sold by X and fulfilled by Amazon" is also a marketplace item,
        since Amazon is not the seller.
        '''
        return 0

    def _home_delivery(self):
        if self.product_info_json.get('attributes'):
            if self.product_info_json['attributes']['variants'][0].get('isDeliveryAvail'):
                return 1
            return 0
        elif self.product_info_json['offermapping']['fulfillment']['delivery']:
            return 1
        return 0

    def _in_stores(self):
        '''in_stores - the item can be ordered online for pickup in a physical store
        or it can not be ordered online at all and can only be purchased in a local store,
        irrespective of availability - binary
        '''
        if self.product_info_json.get('attributes'):
            if (
                self.product_info_json['attributes']['variants'][0].get('isPickupAvail')
                # not self.product_info_json['attributes']['variants'][0].get('isShipAvail')
            ):
                return 1
            return 0
        elif self.product_info_json['offermapping']['fulfillment']['storepickup']:
            return 1
        return 0

    def _in_stores_out_of_stock(self):
        '''in_stores_out_of_stock - currently unavailable for pickup from a physical store - binary
        (null should be used for items that can not be ordered online and the availability may depend on location of the store)
        '''
        if self._in_stores() == 0:
            return None

    def _site_online(self):
        # site_online: the item is sold by the site (e.g. "sold by Amazon") and delivered directly, without a physical store.
        if self.product_info_json.get('attributes'):
            if self.product_info_json['attributes']['variants'][0].get('isShipAvail'):
                return 1
            return 0
        elif self.product_info_json['offerstatus']['isOnline']:
            return 1
        return 0

    def _site_online_out_of_stock(self):
        #  site_online_out_of_stock - currently unavailable from the site - binary
        if not self._site_online():
            return None

        if self.product_info_json.get('attributes'):
            if self.product_info_json['attributes']['variants'][0].get('isAvailable'):
                return 0
            return 1
        elif self.product_info_json['offerstatus']['isAvailable']:
            return 0
        return 1

    ##########################################
    ############### CONTAINER : CLASSIFICATION
    ##########################################
    def _categories(self):
        return map(lambda c: c['name'], self.product_info_json['productmapping']['primaryWebPath'])

    def _category_name(self):
        return self._categories()[-1]

    def _brand(self):
        if self.product_info_json.get('offer'):
            return self.product_info_json['offer']['brandName']
        else:
            return self.product_info_json['product']['brand']['name']


    ##########################################
    ################ HELPER FUNCTIONS
    ##########################################
    # clean text inside html tags - remove html entities, trim spaces

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
        "specs" : _specs, \
        "features" : _features, \
        "feature_count" : _feature_count, \
        "description" : _description, \
        "model" : _model, \
        "long_description" : _long_description, \
        "variants" : _variants, \
        "swatches" : _swatches, \

        # CONTAINER : PAGE_ATTRIBUTES
        "canonical_link" : _canonical_link, \
        "image_urls" : _image_urls, \
        "image_count" : _image_count, \
        "pdf_urls" : _pdf_urls, \
        "pdf_count" : _pdf_count, \
        "video_urls" : _video_urls, \
        "video_count" : _video_count, \
        "webcollage" : _webcollage, \
        "htags" : _htags, \
        "keywords" : _keywords, \

        # CONTAINER : SELLERS
        "price" : _price, \
        "price_amount" : _price_amount, \
        "price_currency" : _price_currency, \
        "marketplace": _marketplace, \
        "home_delivery" : _home_delivery, \
        "in_stores" : _in_stores, \
        "in_stores_out_of_stock" : _in_stores_out_of_stock, \
        "site_online" : _site_online, \
        "site_online_out_of_stock" : _site_online_out_of_stock, \

         # CONTAINER : REVIEWS
        "review_count" : _review_count, \
        "average_review" : _average_review, \
        "max_review" : _max_review, \
        "min_review" : _min_review, \
        "reviews" : _reviews, \

        # CONTAINER : CLASSIFICATION
        "categories" : _categories, \
        "category_name" : _category_name, \
        "brand" : _brand, \

        "loaded_in_seconds": None \
        }


    # special data that can't be extracted from the product page
    # associated methods return already built dictionary containing the data
    DATA_TYPES_SPECIAL = { \
    }
