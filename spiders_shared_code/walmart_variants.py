import json

import lxml.html


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
        self.stockstatus_for_variants()

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
        color_list = self._color()
        size_list = self._size()

        if not color_list and not size_list:
            return None

        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variantTypes":') + len('"variantTypes":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"variantProducts":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            json_body = json.loads(json_text)

            color_json_body = None
            size_json_body = None

            if color_list and size_list:
                size_json_body = json_body[0]["variants"]
                color_json_body = json_body[1]["variants"]
            elif color_list and not size_list:
                color_json_body = json_body[0]["variants"]
            elif size_list and not color_list:
                size_json_body = json_body[0]["variants"]

            startIndex = page_raw_text.find('"variantProducts":') + len('"variantProducts":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"primaryProductId":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            color_size_stockstatus_json_body = json.loads(json_text)

            stockstatus_for_variants_list = []
            color_id_name_map = {}
            size_id_name_map = {}

            if color_json_body:
                for color in color_json_body:
                    color_id_name_map[color["id"]] = color["name"]

            if size_json_body:
                for size in size_json_body:
                    size_id_name_map[size["id"]] = size["name"]

            for item in color_size_stockstatus_json_body:
                variants = item["variants"]
                stockstatus_for_variants = {}

                if color_list:
                    stockstatus_for_variants["color"] = color_id_name_map[variants['actual_color']['id']]

                if size_list:
                    stockstatus_for_variants["size"] = size_id_name_map[variants['size']['id']]

                if item['buyingOptions']['available'] == True:
                    stockstatus_for_variants["stockstatus"] = 1
                stockstatus_for_variants_list.append(stockstatus_for_variants)

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except:
            return None

    def _price_for_variants(self):
        return None
