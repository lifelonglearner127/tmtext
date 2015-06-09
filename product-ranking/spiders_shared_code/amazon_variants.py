import json

import lxml.html


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
