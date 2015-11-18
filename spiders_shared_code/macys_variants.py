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

    def _variants(self):
        try:
            colors = self.tree_html.xpath('//img[@class="colorSwatch"]/@alt')
            if not colors:
                colors = self.tree_html.xpath('//*[contains(@class, "productColor")]/text()')

            sizes = self.tree_html.xpath('//li[@class=" size"]/@title')
            page_raw_text = lxml.html.tostring(self.tree_html)
            product_id = self.tree_html.xpath("//meta[@itemprop='productID']/@content")[0].strip()
            variants_json = json.loads(re.search('MACYS\.pdp\.upcmap\["' + product_id + '"\] = (.+?);\nMACYS\.pdp', page_raw_text).group(1))

            price = self.tree_html.xpath("//meta[@itemprop='price']/@content")[0].strip()
            price = price.replace(",", "")
            price_amount = float(re.findall(r"[\d\.]+", price)[0])

            stockstatus_for_variants_list = []
            instock_variation_combinations_values = []

            color_list = []
            size_list = []
            type_list = []
            exists_map = {}

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

                color, size = properties['color'], properties['size']
                exists_map[(color, size)] = True

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
                color, size = x
                return color in colors

            variation_combinations_values = list(itertools.ifilter(filter, itertools.product(*variation_values_list)))
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

        for swatch in color_list:
            swatch_name = "color"
            color = swatch.split(":")[0].replace('"', '')
            image_path = swatch.split(":")[1].replace('"', '')

            swatch_info = {}
            swatch_info["swatch_name"] = swatch_name
            swatch_info[swatch_name] = color
            swatch_info["hero"] = 1
            swatch_info["hero_image"] = ["http://slimages.macysassets.com/is/image/MCY/products/" + image_path]

            for image_path in additional_image_list[color].split(","):
                swatch_info["hero_image"].append("http://slimages.macysassets.com/is/image/MCY/products/" + image_path)

            swatch_list.append(swatch_info)

        if swatch_list:
            return swatch_list

        return None