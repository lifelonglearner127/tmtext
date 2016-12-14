import json

import lxml.html
import itertools
import re, copy

def normalize_product_json_string(product_json_string):
    #1st issue pattern ex ----> "\tRustic Woodland":
    product_json_string = product_json_string.replace('"\t', '"')

    return product_json_string


class MacysVariants(object):
    IMAGE_BASE_URL = "http://slimages.macysassets.com/is/image/MCY/products/"

    def setupSC(self, response, is_bundle=False):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)
        self.is_bundle = is_bundle

    def setupCH(self, tree_html, is_bundle=False):
        """ Call it from CH spiders """
        self.tree_html = tree_html
        self.is_bundle = is_bundle

    def _extract_product_info_json(self):
        try:
            return json.loads(normalize_product_json_string(self.tree_html.xpath('//script[@id="productMainData" or @id="pdpMainData"]/text()')[0]))
        except:
            print "Parsing error of product info json"
        return None

    def _get_prod_id(self):
        product_id = self.tree_html.xpath('//*[contains(@class,"productID")]'
                                          '[contains(text(), "Web ID:")]/text()')
        if product_id:
            product_id = ''.join([c for c in product_id[0] if c.isdigit()])
        return product_id

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
                    if images_by_color and images_by_color.get(color,None):
                        colors_information[color]['img_urls'] = [self.IMAGE_BASE_URL+url for url in images_by_color.get(color)]
        
        # Single Color Product
        else:
            selected_color = product_info_json.get('selectedColor', None)
            if not selected_color:
                # Sometimes selectedColor is empty, getting color from upcMap
                prod_id = product_info_json.get('id', None)
                try:
                    color_list = product_info_json.get('upcMap', None).get(prod_id, None)
                    selected_color = list(set([l.get('color') for l in color_list]))
                    selected_color = selected_color[0] if len(selected_color)==1 else None
                except BaseException:
                    print "Unable to get single color for product id {}".format(prod_id)
                    selected_color = None
            colors_information[selected_color] = {}
            price = self.tree_html.xpath('//*[@id="productHeader"]//meta[@itemprop="price"]/@content')
            colors_information[selected_color]['price'] = float(price[0].replace("$","")) if price else None
        return colors_information

    def __fill_variant(self, variant, colors_information):
            vr = {}

            variant_color = variant['color']
            if variant_color == 'Bleach Wash':
                variant_color = 'Bleached Wash'

            vr['properties'] = {'color': variant_color, 'size': variant['size']}
            vr['in_stock'] = True if variant.get('isAvailable',None) == "true" else False
            try:
                vr['price'] = colors_information[variant_color]['price']
            except KeyError:
                return  # no such variant?
            if variant.get('upc',None):
                vr['upc'] = variant['upc']
            if colors_information[variant_color].get('img_urls', None):
                vr['img_urls'] = colors_information[variant_color]['img_urls']
            if variant.get('type',False):
                vr['type'] = variant['type']
            return vr

    def _variants(self):
            variants = []

            if self.is_bundle:
                image_map_list = re.findall('MACYS.pdp.primaryImages\[(\d+)\] = ({[^;]*});', lxml.html.tostring(self.tree_html))

                image_map = {}
                for item in image_map_list:
                    image_map[item[0]] = json.loads(item[1])

                image_prefix = 'http://slimages.macysassets.com/is/image/MCY/products/'

                products = self.tree_html.xpath('//div[contains(@class,"memberProducts")]')

                for product in products:
                    product_variants = []

                    prod_id = product.xpath('.//img/@id')[0].split('_')[0]
                    product_name = product.xpath('.//div[@id="prodName"]/text()')[0].strip()

                    colorSelection = product.xpath('.//div[@class="colorSelection"]//ul/li')

                    selected_color = product.xpath('.//span[@class="productColor"]/text()')

                    if not colorSelection:
                        if selected_color:
                            colorSelection = [{'title' : selected_color[0]}]
                        else:
                            colorSelection = [{}]

                    price = product.xpath('.//span[@class="colorway-price"]/span/text()')[-1]
                    price = float( price.split(' ')[-1].strip()[1:])

                    for color in colorSelection:
                        v = {
                            'product_name' : product_name,
                            'img_urls' : None,
                            'in_stock' : True,
                            'price' : price,
                            'properties' : {},
                            'selected' : False
                        }

                        if color.get('title'):
                            if color.get('title') in image_map[prod_id]:
                                v['img_urls'] = [image_prefix + image_map[prod_id][color.get('title')]]
                            v['properties']['color'] = color.get('title')
                            if selected_color:
                                v['selected'] = color.get('title') == selected_color[0]

                        if not v['img_urls']:
                            v['img_urls'] = [product.xpath('.//img/@src')[0].split('?')[0]]

                        product_variants.append(v)

                    sizeSelection = product.xpath('.//div[@class="sizeSelection"]//ul/li')

                    selected_size = product.xpath('.//span[@class="productSize"]/text()')

                    new_variants = []

                    for size in sizeSelection:
                        for variant in product_variants:
                            new_variant = copy.deepcopy(variant)
                            new_variant['properties']['size'] = size.get('title')
                            if selected_size:
                                new_variant['selected'] = variant['selected'] and size.get('title') == selected_size[0]
                            else:
                                new_variant['selected'] = False
                            new_variants.append(new_variant)

                    if new_variants:
                        variants.extend(new_variants)
                    else:
                        variants.extend(product_variants)

                return variants

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
                if vr:
                    variation_values_crossed.discard((variant['size'], variant['color']))
                    variants.append(vr)

            # Product not in stock
            for size, color in variation_values_crossed:
                vr = self.__fill_variant({'color': color, 'size':size}, colors_information)
                if vr:
                    variants.append(vr)

            return variants


    def _swatches(self):
        swatch_list = []

        if self.is_bundle:
            image_map_list = re.findall('MACYS.pdp.primaryImages\[(\d+)\] = ({[^;]*});', lxml.html.tostring(self.tree_html))

            image_map = {}
            for item in image_map_list:
                image_map[item[0]] = json.loads(item[1])

            image_prefix = 'http://slimages.macysassets.com/is/image/MCY/products/'

            colors = self.tree_html.xpath('//div[@id="masterColorSelection"]/div[@class="colors"]/ul/li')

            for color in colors:
                hero_image = []

                for color_map in image_map.itervalues():
                    image_frag = color_map.get(color.get('title'))
                    if image_frag and not image_prefix + image_frag in hero_image:
                        hero_image.append( image_prefix + image_frag)

                s = {
                    'color' : color.get('title'),
                    'hero' : 1,
                    'hero_image' : hero_image if hero_image else None,
                    'thumb' : 1,
                    'thumb_image' : [image_prefix + color.get('data-imgurl')],
                }

                swatch_list.append(s)

            if swatch_list:
                return swatch_list
            return None

        product_info_json = self.tree_html.xpath("//script[@id='productMainData' and @type='application/json']/text()")
        product_info_json = json.loads( product_info_json[0] )
        color_list = {}
        for color, url_frag in product_info_json['images']['colorwayPrimaryImages'].iteritems():
            color_list[color] = ["http://slimages.macysassets.com/is/image/MCY/products/" + url_frag]
        for color, url_frags in product_info_json['images']['colorwayAdditionalImages'].iteritems():
            url_frags = url_frags.split(',')
            color_list[color] += map(lambda f: "http://slimages.macysassets.com/is/image/MCY/products/" + f, url_frags)
        for color, url_list in color_list.iteritems():
            swatch = {}
            swatch["swatch_name"] = 'color'
            swatch["color"] = color
            swatch["hero"] = 1
            swatch["hero_image"] = url_list
            thumb_image = "http://slimages.macysassets.com/is/image/MCY/products/" + product_info_json['colorSwatchMap'][color]
            swatch["thumb"] = 1
            swatch["thumb_image"] = [ thumb_image ]
            swatch_list.append( swatch )
        if swatch_list:
            return swatch_list
        return None