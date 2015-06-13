import json

import lxml.html
import itertools
import re

class TargetVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _color(self):
        try:
            json_body = None

            if self.tree_html.xpath("//div[@id='entitledItem']/text()"):
                json_body = json.loads(self.tree_html.xpath("//div[@id='entitledItem']/text()")[0])
            else:
                return None

            color_list = []

            for item in json_body:
                attributes = item["Attributes"]

                for key in attributes:
                    if key.startswith("color:"):
                        color_list.append(key[6:])

            color_list = list(set(color_list))

            if not color_list:
                return None
            else:
                return color_list
        except:
            return None

    def _size(self):
        try:
            json_body = None

            if self.tree_html.xpath("//div[@id='entitledItem']/text()"):
                json_body = json.loads(self.tree_html.xpath("//div[@id='entitledItem']/text()")[0])
            else:
                return None

            size_list = []

            for item in json_body:
                attributes = item["Attributes"]

                for key in attributes:
                    if key.startswith("size:"):
                        size_list.append(key[5:])

            size_list = list(set(size_list))

            if not size_list:
                return None
            else:
                return size_list
        except:
            return None

    def _style(self):
        return None

    def _color_size_stockstatus(self):
        return None

    def _variants(self):
        variants = []

        if self._color():
            variants.append("color")

        if self._size():
            variants.append("size")

        if self._style():
            variants.append("style")

        if not variants:
            return None
        else:
            return variants

    def _price_for_variants(self):
        if not self._color() and not self._size():
            return None

        try:
            variants_json_body = None
            price_for_variants_json_body = None

            if self.tree_html.xpath("//div[@id='entitledItem']/text()"):
                variants_json_body = json.loads(self.tree_html.xpath("//div[@id='entitledItem']/text()")[0])
            else:
                return None

            if self.tree_html.xpath("//script[@type='text/javascript' and contains(text(), 'Target.globals.refreshItems =')]/text()"):
                price_for_variants_json_body = self.tree_html.xpath("//script[@type='text/javascript' and contains(text(), 'Target.globals.refreshItems =')]/text()")[0]
                start_index = price_for_variants_json_body.find("Target.globals.refreshItems =") + len("Target.globals.refreshItems =")
                price_for_variants_json_body = price_for_variants_json_body[start_index:]
                price_for_variants_json_body = json.loads(price_for_variants_json_body)
            else:
                return None

            hash_price_for_variants_json_item_to_catentry_id = {}

            for variant_item in price_for_variants_json_body:
                hash_price_for_variants_json_item_to_catentry_id[variant_item["catentry_id"]] = variant_item

            price_for_variants_list = []

            for variant_item in variants_json_body:
                attributes = variant_item["Attributes"]
                price_for_vairant = {}

                for key in attributes:
                    if key.startswith("size:"):
                        price_for_vairant["size"] = key[5:]

                    if key.startswith("color:"):
                        price_for_vairant["color"] = key[6:]

                price_for_vairant["price"] = hash_price_for_variants_json_item_to_catentry_id[variant_item["catentry_id"]]["Attributes"]["price"]["formattedOfferPrice"]

                if not price_for_vairant["price"].isdigit():
                    price_for_vairant["price"] = price_for_vairant["price"][1:]

                price_for_vairant["price"] = float(price_for_vairant["price"])

                price_for_variants_list.append(price_for_vairant)

            if not price_for_variants_list:
                return None
            else:
                return price_for_variants_list
        except:
            return None

    def _selected_variants(self):
        return None

    def _stockstatus_for_variants(self):
        try:
            variation_combinations_values = json.loads(self.tree_html.xpath("//div[@id='entitledItem']/text()")[0])

            if self.tree_html.xpath("//script[@type='text/javascript' and contains(text(), 'Target.globals.refreshItems =')]/text()"):
                stockstatus_for_variation_combinations = self.tree_html.xpath("//script[@type='text/javascript' and contains(text(), 'Target.globals.refreshItems =')]/text()")[0]
                start_index = stockstatus_for_variation_combinations.find("Target.globals.refreshItems =") + len("Target.globals.refreshItems =")
                stockstatus_for_variation_combinations = stockstatus_for_variation_combinations[start_index:]
                stockstatus_for_variation_combinations = json.loads(stockstatus_for_variation_combinations)
            else:
                return None

            hash_catentryid_to_stockstatus = {}

            for stockstatus in stockstatus_for_variation_combinations:
                hash_catentryid_to_stockstatus[stockstatus["catentry_id"]] = stockstatus["Attributes"]

            stockstatus_for_variants_list = []

            for variant_item in variation_combinations_values:
                stockstatus_for_variants = {}
                properties = {}

                attributes = variant_item["Attributes"]

                for key in attributes:
                    if key.startswith("size:"):
                        properties["size"] = key[5:]

                    if key.startswith("color:"):
                        properties["color"] = key[6:]

                stockstatus_for_variants["properties"] = properties
                stockstatus_for_variants["selected"] = None
                stockstatus_for_variants["price"] = float(hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["price"]["formattedOfferPrice"][1:])

                if hash_catentryid_to_stockstatus[variant_item["catentry_id"]]["inventory"]["status"] == "in stock":
                    stockstatus_for_variants["in_stock"] = True
                else:
                    stockstatus_for_variants["in_stock"] = False

                stockstatus_for_variants_list.append(stockstatus_for_variants)

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except:
            return None