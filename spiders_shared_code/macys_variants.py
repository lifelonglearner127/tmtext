import json

import lxml.html
import itertools
import re


class MacysVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _extract_product_info_json(self):
        try:
            product_info_json = self.tree_html.xpath("//script[@id='pdpMainData' and @type='application/json']/text()")

            if product_info_json:
                product_info_json = json.loads(product_info_json[0])
                return product_info_json
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

    def _get_swatch_colors(self):
        colors = self.tree_html.xpath('//img[@class="colorSwatch"]/@alt')
        if not colors:
            colors = self.tree_html.xpath('//*[contains(@class, "productColor")]/text()')
        if not colors:
            page_raw_text = lxml.html.tostring(self.tree_html)
            pos1 = page_raw_text.find('"colorSwatchMap":')
            pos2 = page_raw_text.find('},', pos1)
            if pos2 > pos1 > 0:
                colors_map = json.loads(page_raw_text[pos1+len('"colorSwatchMap":'):pos2].strip() + '}')
                colors = colors_map.keys()
        return colors

    def _variants(self):
        try:
            colors = self._get_swatch_colors()

            sizes = self.tree_html.xpath('//li[@class=" size"]/@title')
            page_raw_text = lxml.html.tostring(self.tree_html)
            product_id = self._get_prod_id()
            try:
                variants_json = json.loads(re.search('MACYS\.pdp\.upcMap\["' + product_id + '"\] = (.+?);\nMACYS\.pdp', page_raw_text).group(1))
            except (IndexError, AttributeError):
                try:
                    variants_json = json.loads(re.search('MACYS\.pdp\.upcmap\["' + product_id + '"\] = (.+?);\nMACYS\.pdp', page_raw_text).group(1))
                except (IndexError, AttributeError):
                    pos1 = page_raw_text.find('"upcMap": {\n"%s": ' % product_id)
                    pos2 = page_raw_text.find('}\n]\n},', pos1+1)
                    if pos1 > 0 and pos2 > 0:
                        variants_json = json.loads(
                            page_raw_text[pos1+len('"upcMap": {\n"%s": ' % product_id):pos2].strip()+'}]')

            product_info_json = self._extract_product_info_json()

            price_amount = None

            if product_info_json:  # TODO: this one is None?
                sale_price = product_info_json.get("productDetail", {}).get("salePrice", "")
                regular_price = product_info_json.get("productDetail", {}).get("regularPrice", "")

                if sale_price:
                    price_amount = float(sale_price)
                elif regular_price:
                    price_amount = float(regular_price)

            stockstatus_for_variants_list = []
            instock_variation_combinations_values = []

            color_list = []
            size_list = []
            type_list = []

            for variant_item in variants_json:

                stockstatus_for_variants = {}
                properties = {}
                variation_combination = []

                if variant_item["color"] and variant_item["color"] != "No Color":
                    properties["color"] = variant_item["color"]

                    color_list.append(variant_item["color"])
                    variation_combination.append(variant_item["color"])

                if variant_item["size"]:
                    properties["size"] = variant_item["size"]
                    size_list.append(variant_item["size"])
                    variation_combination.append(variant_item["size"])

                if variant_item["type"]:
                    properties["type"] = variant_item["type"]
                    type_list.append(variant_item["type"])
                    variation_combination.append(variant_item["type"])

                if not properties:
                    continue

                color, size = properties['color'] if 'color' in properties else None, properties['size'] if 'size' in properties else None

                if variation_combination in instock_variation_combinations_values:
                    continue

                instock_variation_combinations_values.append(variation_combination)
                stockstatus_for_variants["properties"] = properties

                if len(variants_json) == 1:
                    stockstatus_for_variants["selected"] = True
                else:
                    stockstatus_for_variants["selected"] = False

                stockstatus_for_variants["price"] = price_amount

                if variant_item["isAvailable"] == "true":
                    stockstatus_for_variants["in_stock"] = True
                else:
                    stockstatus_for_variants["in_stock"] = False

                stockstatus_for_variants["upc"] = variant_item["upc"]

                if color in colors:
                    stockstatus_for_variants_list.append(stockstatus_for_variants)

            size_list = list(set(size_list))
            color_list = list(set(color_list))
            type_list = list(set(type_list))

            variation_values_list = []

            key_list = []

            if color_list:
                key_list.append("color")
                variation_values_list.append(color_list)

            if size_list:
                key_list.append("size")
                variation_values_list.append(size_list)

            if type_list:
                key_list.append("type")
                variation_values_list.append(type_list)

            def filter(x):
                color = x[0]
                return color in colors

            if size_list or color_list or type_list:
                variation_combinations_values = list(itertools.ifilter(filter, itertools.product(*variation_values_list)))
            else:
                # only small colors block available?
                colors_imgs = self.tree_html.xpath(
                    '//div[contains(@class, "colors")]'
                    '//li/img[contains(@class, "colorSwatch")][contains(@id, "s")]')
                already_collected_colors = []
                result_variants = []
                for img in colors_imgs:
                    color = img.xpath('./@title')[0].strip()
                    #img_url = img.xpath('./@style')[0].strip()  # TODO: try to find a way to scrape image samples?
                    if color not in already_collected_colors:
                        already_collected_colors.append(color)
                        result_variants.append({
                            'price': None, 'selected': False, 'in_stock': True,
                            #'image_url': src,
                            'properties': {'color': color}
                        })
                return result_variants if result_variants else None

            variation_combinations_values = map(list, variation_combinations_values)
            outofstock_variation_combinations_values = [variation_combination for variation_combination in variation_combinations_values if variation_combination not in instock_variation_combinations_values]

            if outofstock_variation_combinations_values:
                for variation_combination in outofstock_variation_combinations_values:
                    stockstatus_for_variants = {}
                    properties = {}

                    for index, variation in enumerate(variation_combination):
                        properties[key_list[index]] = variation

                    if not properties:
                        continue

                    stockstatus_for_variants["properties"] = properties
                    stockstatus_for_variants["selected"] = False
                    stockstatus_for_variants["price"] = price_amount
                    stockstatus_for_variants["in_stock"] = False

                    stockstatus_for_variants_list.append(stockstatus_for_variants)

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except:
            return None

    def _swatches(self):
        swatch_list = []

        product_id = None

        try:
            product_id = self.tree_html.xpath("//meta[@itemprop='productID']/@content")[0]
        except:
            product_id = self.tree_html.xpath("//input[@id='productId']/@value")[0]

        primary_image_list = re.findall(r"MACYS.pdp.primaryImages\[" + product_id + "\] = {(.*?)}", " ".join(self.tree_html.xpath("//script//text()")), re.DOTALL)
        color_list = primary_image_list[0].split(",")

        additional_image_list = re.findall(r"MACYS.pdp.additionalImages\[" + product_id + "\] = {(.*?)}", " ".join(self.tree_html.xpath("//script//text()")), re.DOTALL)

        try:
            additional_image_list = json.loads("{" + additional_image_list[0] + "}")
        except:
            additional_image_list = {}

        thumbnail_list = self.tree_html.xpath("//ul[@id='colorList{0}']/li".format(product_id))
        thumbnail_image_list = {}

        for thumbnail in thumbnail_list:
            thumbnail_image_list[thumbnail.xpath("./@title")[0]] = "http://slimages.macysassets.com/is/image/MCY/products/" + thumbnail.xpath("./@data-imgurl")[0]

        for swatch in color_list:
            swatch_name = "color"
            color = swatch.split(":")[0].replace('"', '')
            image_path = swatch.split(":")[1].replace('"', '')

            swatch_info = {}
            swatch_info["swatch_name"] = swatch_name
            swatch_info[swatch_name] = color
            swatch_info["hero"] = 1
            swatch_info["hero_image"] = ["http://slimages.macysassets.com/is/image/MCY/products/" + image_path]

            if color in additional_image_list:
                for image_path in additional_image_list[color].split(","):
                    swatch_info["hero_image"].append("http://slimages.macysassets.com/is/image/MCY/products/" + image_path)

            swatch_info["thumb"] = 1
            swatch_info["thumb_image"] = [thumbnail_image_list[color]]

            swatch_list.append(swatch_info)

        if swatch_list:
            return swatch_list

        return None