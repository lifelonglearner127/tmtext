import json

import lxml.html
import re

class WalmartVariants(object):

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
            startIndex = page_raw_text.find('"variantTypes":') + len('"variantTypes":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"variantProducts":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            json_body = json.loads(json_text)
            color_json_body = None

            for item in json_body:
                if item['name'] == "Actual Color":
                    color_json_body = item["variants"]
                    break

            if not color_json_body:
                return None

            color_list = []

            for color_item in color_json_body:
                color_list.append(color_item["name"])

            if not color_list:
                return None
            else:
                return color_list
        except:
            return None

    def _size(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variantTypes":') + len('"variantTypes":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"variantProducts":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            json_body = json.loads(json_text)
            size_json_body = None

            for item in json_body:
                if item['name'] == "Size":
                    size_json_body = item["variants"]
                    break

            if not size_json_body:
                return None

            size_list = []

            for color_item in size_json_body:
                size_list.append(color_item["name"])

            if not size_list:
                return None
            else:
                return size_list
        except:
            return None

    def _color_size_stockstatus(self):
        if not self._color() or not self._size():
            return None

        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variantTypes":') + len('"variantTypes":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"variantProducts":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            json_body = json.loads(json_text)
            color_json_body = json_body[1]["variants"]

            startIndex = page_raw_text.find('"variantTypes":') + len('"variantTypes":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"variantProducts":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            json_body = json.loads(json_text)
            size_json_body = json_body[0]["variants"]

            startIndex = page_raw_text.find('"variantProducts":') + len('"variantProducts":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"primaryProductId":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            color_size_stockstatus_json_body = json.loads(json_text)

            color_size_stockstatus_dictionary = {}
            color_id_name_map = {}
            size_id_name_map = {}

            for color in color_json_body:
                color_size_stockstatus_dictionary[color["name"]] = {}
                color_id_name_map[color["id"]] = color["name"]

                for size in size_json_body:
                    color_size_stockstatus_dictionary[color["name"]][size["name"]] = 0
                    size_id_name_map[size["id"]] = size["name"]

            for item in color_size_stockstatus_json_body:
                variants = item["variants"]

                if item['buyingOptions']['available'] == True:
                    color_size_stockstatus_dictionary[color_id_name_map[variants['actual_color']['id']]][size_id_name_map[variants['size']['id']]] = 1

            if not color_size_stockstatus_dictionary:
                return None
            else:
                return color_size_stockstatus_dictionary
        except:
            return None

    def _variants(self):

        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variantTypes":') + len('"variantTypes":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"variantProducts":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            json_body = json.loads(json_text)
            variants = []

            for item in json_body:
                if item['name'] == "Size":
                    variants.append("size")
                elif item['name'] == "Actual Color":
                    variants.append("color")

            if not variants:
                return None
            else:
                return variants
        except:
            return None

    def _style(self):
        return None

    def _selected_variants(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variantTypes":') + len('"variantTypes":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"variantProducts":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            json_body = json.loads(json_text)
            selected_variants = {}

            for item in json_body:
                if item['name'] == "Size" and "selectedValue" in item:
                    selected_variants["size"] = item["selectedValue"]
                elif item['name'] == "Actual Color" and "selectedValue" in item:
                    selected_variants["color"] = item["selectedValue"]

            if not selected_variants:
                return None
            else:
                return selected_variants
        except:
            return None

    def _stockstatus_for_variants(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variantTypes":') + len('"variantTypes":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"variantProducts":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            json_body = json.loads(json_text)

            variation_key_values_by_attributes = {}

            for variation_attribute in json_body:
                variation_key_values = {}
                variation_attribute_id = variation_attribute["id"]

                for variation in variation_attribute["variants"]:
                    variation_key_values[variation["id"]] = variation["name"]

                variation_key_values_by_attributes[variation_attribute_id] = variation_key_values

            selected_variants = {}

            for item in json_body:
                selected_variants[item["id"]] = item["selectedValue"]

            startIndex = page_raw_text.find('"variantProducts":') + len('"variantProducts":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"primaryProductId":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]

            color_size_stockstatus_json_body = json.loads(json_text)
            stockstatus_for_variants_list = []

            for item in color_size_stockstatus_json_body:
                variants = item["variants"]
                stockstatus_for_variants = {}
                properties = {}
                isSelected = True

                for key in variants:
                    if key in variation_key_values_by_attributes:
                        if key == "actual_color":
                            properties["color"] = variation_key_values_by_attributes[key][variants[key]["id"]]
                        else:
                            properties[key] = variation_key_values_by_attributes[key][variants[key]["id"]]

                    if selected_variants[key] != variation_key_values_by_attributes[key][variants[key]["id"]]:
                        isSelected = False

                stockstatus_for_variants["properties"] = properties
                stockstatus_for_variants["in_stock"] = item['buyingOptions']['available']
                stockstatus_for_variants["price"] = None
                stockstatus_for_variants["selected"] = isSelected
                stockstatus_for_variants_list.append(stockstatus_for_variants)

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except:
            return None

    def _price_for_variants(self):
        return None
