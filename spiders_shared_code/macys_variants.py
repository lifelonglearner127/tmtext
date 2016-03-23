import json

import lxml.html
import itertools
import re


class MacysVariants(object):
    IMAGE_BASE_URL = "http://slimages.macysassets.com/is/image/MCY/products/"

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _extract_product_info_json(self):
        try:
            return json.loads(self.tree_html.xpath('//script[@id="productMainData" or @id="pdpMainData"]/text()')[0])
        except:
            print "Parsing error of product info json"
        return None

    def _get_prod_id(self):
        product_id = self.tree_html.xpath('//*[contains(@id, "productId")]/@value')
        if not product_id:
            product_id = self.tree_html.xpath('//*[contains(@class,"productID")]'
                                              '[contains(text(), "Web ID:")]/text()')
            if product_id:
                product_id = [''.join([c for c in product_id[0] if c.isdigit()])]
        if product_id:
            return product_id[0]

    def _get_color_to_price_and_url(self, product_info_json):
        colors_information = {}

        colorwayPricingSwatches = product_info_json.get('colorwayPricingSwatches', None)
        # Product With Multiples Colors
        if colorwayPricingSwatches:
            # Get all variants images
            images_by_color = {}
            colorwayPrimaryImages = product_info_json['images'].get('colorwayPrimaryImages', {})
            for color in colorwayPrimaryImages:
                url_list = images_by_color.get(color,[])
                url_list.append(colorwayPrimaryImages[color])
                images_by_color[color] = url_list

            colorwayAdditionalImages = product_info_json['images'].get('colorwayAdditionalImages', {})
            for color in colorwayAdditionalImages:
                url_list = images_by_color.get(color,[]) + colorwayAdditionalImages[color].split(',')
                images_by_color[color] = url_list

            # Get prices
            for price in colorwayPricingSwatches:
                for color in colorwayPricingSwatches[price]:
                    colors_information[color] = {}
                    colors_information[color]['price'] = float(price.replace("$",""))                
                    if images_by_color:
                        colors_information[color]['img_urls'] = [self.IMAGE_BASE_URL+url for url in images_by_color[color]]
        
        # Single Color Product
        else:
            selected_color = product_info_json.get('selectedColor', None)
            colors_information[selected_color] = {}
            price = self.tree_html.xpath('//*[@id="productHeader"]//meta[@itemprop="price"]/@content')[0]
            colors_information[selected_color]['price'] = float(price.replace("$",""))
        return colors_information

    def __fill_variant(self, variant, colors_information):
            vr = {}
            vr['properties'] = {'color': variant['color'], 'size': variant['size']}
            vr['in_stock'] = True if variant.get('isAvailable',None) == "true" else False
            vr['price'] = colors_information[variant['color']]['price']
            
            if variant.get('upc',None):
                vr['upc'] = variant['upc']
            if colors_information[variant['color']].get('img_urls', None):
                vr['img_urls'] = colors_information[variant['color']]['img_urls']
            if variant.get('type',False):
                vr['type'] = variant['type']
            return vr

    def _variants(self):
            variants = []

            # Load product data
            product_info_json = self._extract_product_info_json()

            # Get sizes
            sizes = product_info_json.get('sizesList', None)

            # Get dict of key:color, value: {price, img_urls}
            colors_information = self._get_color_to_price_and_url(product_info_json)
            
            # Calculate all variants crossing sizes with colors
            variation_values_list = [sizes, colors_information.keys()]
            variation_values_crossed = set(itertools.product(*variation_values_list))

            # Product in stock
            upcMap = product_info_json.get('upcMap', [])
            for variant in upcMap[self._get_prod_id()]:
                vr = self.__fill_variant(variant, colors_information)
                variation_values_crossed.discard((variant['size'], variant['color']))
                variants.append(vr)

            # Product not in stock
            for size,color in variation_values_crossed:
                vr = self.__fill_variant({'color': color, 'size':size}, colors_information)
                variants.append(vr)

            return variants
