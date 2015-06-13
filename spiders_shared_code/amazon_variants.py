import json

import lxml.html
import itertools
import re

class AmazonVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _color(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variation_values":') + len('"variation_values":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find("}", startIndex) + 1

            json_text = page_raw_text[startIndex:endIndex]
            json_body =json.loads(json_text)

            return json_body["color_name"]
        except:
            return None

    def _size(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variation_values":') + len('"variation_values":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find("}", startIndex) + 1

            json_text = page_raw_text[startIndex:endIndex]
            json_body =json.loads(json_text)

            return json_body["size_name"]
        except:
            return None

    def _style(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variation_values":') + len('"variation_values":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find("}", startIndex) + 1

            json_text = page_raw_text[startIndex:endIndex]
            json_body =json.loads(json_text)

            return json_body["style_name"]
        except:
            return None

    def _flavor(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variation_values":') + len('"variation_values":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find("}", startIndex) + 1

            json_text = page_raw_text[startIndex:endIndex]
            json_body =json.loads(json_text)

            return json_body["flavor_name"]
        except:
            return None

    def _variants(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variation_values":') + len('"variation_values":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find("}", startIndex) + 1

            json_text = page_raw_text[startIndex:endIndex]
            json_body =json.loads(json_text)

            variants = []

            if "color_name" in json_body:
                variants.append("color")

            if "size_name" in json_body:
                variants.append("size")

            if "style_name" in json_body:
                variants.append("style")

            if "flavor_name" in json_body:
                variants.append("flavor")

            if not variants:
                return None
            else:
                return variants
        except:
            return None

    def _selected_variants(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"selected_variations":') + len('"selected_variations":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find("}", startIndex) + 1

            json_text = page_raw_text[startIndex:endIndex]
            json_body =json.loads(json_text)

            selected_variants = {}

            if "color_name" in json_body:
                selected_variants["color"] = json_body["color_name"]

            if "size_name" in json_body:
                selected_variants["size"] = json_body["size_name"]

            if "style_name" in json_body:
                selected_variants["style"] = json_body["style_name"]

            if "flavor_name" in json_body:
                selected_variants["flavor"] = json_body["flavor_name"]

            if not selected_variants:
                return None
            else:
                return selected_variants
        except:
            return None

    def _color_size_stockstatus(self):
        if not self._color() or not self._size():
            return None

        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"dimensionValuesDisplayData":') + len('"dimensionValuesDisplayData":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find("}", startIndex) + 1
            json_text = page_raw_text[startIndex:endIndex]
            json_body =json.loads(json_text)

            color_size_stockstatus_dictionary = {}
            color_list = self._color()
            size_list = self._size()

            for color in color_list:
                color_size_stockstatus_dictionary[color] = {}

                for size in size_list:
                    color_size_stockstatus_dictionary[color][size] = 0

            for asin in json_body:
                color_size_stockstatus_dictionary[json_body[asin][1]][json_body[asin][0]] = 1

            if not color_size_stockstatus_dictionary:
                return None
            else:
                return color_size_stockstatus_dictionary
        except:
            return None

    def _stockstatus_for_variants(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            variation_key_values = json.loads(re.search('"variation_values":(.+?),"deviceType', page_raw_text).group(1))
            variation_key_list = list(variation_key_values)

            for index, variation_key in enumerate(variation_key_list):
                variation_key_list[index] = variation_key[:variation_key.find("_")]

            variation_values_list = []

            for variation_key in variation_key_values:
                variation_values_list.append(variation_key_values[variation_key])

            variation_combinations_values = list(itertools.product(*variation_values_list))

            variation_combinations_values = map(list, variation_combinations_values)
            instock_variation_combinations_values = json.loads(re.search('"dimensionValuesDisplayData":(.+?),"hidePopover":', page_raw_text).group(1))
            instock_variation_combinations_values = [instock_variation_combinations_values[key] for key in instock_variation_combinations_values]

            outofstock_variation_combinations_values = [variation_combination for variation_combination in variation_combinations_values if variation_combination not in instock_variation_combinations_values]

            selected_variation_combination = json.loads(re.search('"selected_variations":(.+?),"jqupgrade"', page_raw_text).group(1))

            selected_variation_combination = [selected_variation_combination[key] for key in selected_variation_combination]

            stockstatus_for_variants_list = []

            for variation_combination in outofstock_variation_combinations_values:
                stockstatus_for_variants = {}
                properties = {}
                isSelected = True

                for index, variation_key in enumerate(variation_key_list):
                    properties[variation_key] = variation_combination[index]

                    if variation_combination[index] != selected_variation_combination[index]:
                        isSelected = False

                stockstatus_for_variants["properties"] = properties
                stockstatus_for_variants["in_stock"] = False
                stockstatus_for_variants["selected"] = isSelected
                stockstatus_for_variants["price"] = None

                stockstatus_for_variants_list.append(stockstatus_for_variants)

            for variation_combination in instock_variation_combinations_values:
                stockstatus_for_variants = {}
                properties = {}
                isSelected = True

                for index, variation_key in enumerate(variation_key_list):
                    properties[variation_key] = variation_combination[index]

                    if variation_combination[index] != selected_variation_combination[index]:
                        isSelected = False

                stockstatus_for_variants["properties"] = properties
                stockstatus_for_variants["in_stock"] = True
                stockstatus_for_variants["selected"] = isSelected
                stockstatus_for_variants["price"] = None

                stockstatus_for_variants_list.append(stockstatus_for_variants)

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except:
            return None

    def _price_for_variants(self):
        return None