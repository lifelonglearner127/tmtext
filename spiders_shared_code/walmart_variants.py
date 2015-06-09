import json

import lxml.html


class WalmartVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self):
        """ Call it from CH spiders """
        pass

    def _color(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variantTypes":')\
                         + len('"variantTypes":')

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
            startIndex = page_raw_text.find('"variantTypes":')\
                         + len('"variantTypes":')

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
            startIndex = page_raw_text.find('"variantTypes":')\
                         + len('"variantTypes":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"variantProducts":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            json_body = json.loads(json_text)
            color_json_body = json_body[1]["variants"]

            startIndex = page_raw_text.find('"variantTypes":')\
                         + len('"variantTypes":')

            if startIndex == -1:
                return None

            endIndex = page_raw_text.find(',"variantProducts":', startIndex)

            json_text = page_raw_text[startIndex:endIndex]
            json_body = json.loads(json_text)
            size_json_body = json_body[0]["variants"]

            startIndex = page_raw_text.find('"variantProducts":')\
                         + len('"variantProducts":')

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
                    color_size_stockstatus_dictionary[
                        color["name"]][size["name"]] = 0
                    size_id_name_map[size["id"]] = size["name"]

            for item in color_size_stockstatus_json_body:
                variants = item["variants"]

                if item['buyingOptions']['available'] == True:
                    color_size_stockstatus_dictionary[
                        color_id_name_map[variants['actual_color']['id']]
                    ][size_id_name_map[variants['size']['id']]] = 1

            if not color_size_stockstatus_dictionary:
                return None
            else:
                return color_size_stockstatus_dictionary
        except:
            return None

    def _variants(self):
        try:
            page_raw_text = lxml.html.tostring(self.tree_html)
            startIndex = page_raw_text.find('"variantTypes":')\
                         + len('"variantTypes":')

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
            startIndex = page_raw_text.find('"variantTypes":')\
                         + len('"variantTypes":')

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

