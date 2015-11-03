import lxml.html
from itertools import product
import json
import re
from lxml import html, etree
import itertools
import yaml


class DockersVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def _variants(self):
        buy_stack_json = None

        try:
            buy_stack_json_text = self._find_between(" " . join(self.tree_html.xpath("//script[@type='text/javascript']/text()")), "var buyStackJSON = '", "'; var productCodeMaster =").replace("\'", '"').replace('\\\\"', "")
            buy_stack_json = json.loads(buy_stack_json_text)
        except:
            buy_stack_json = None

        if buy_stack_json:
            variant_list = []

            for variant_combination in buy_stack_json["sku"]:
                variant_item = {}
                properties = {}

                if "colorid" in buy_stack_json["sku"][variant_combination]:
                    properties["color"] = buy_stack_json["colorid"][buy_stack_json["sku"][variant_combination]["colorid"]]["finish"]["title"]

                if "length" in buy_stack_json["sku"][variant_combination]:
                    properties["length"] = buy_stack_json["sku"][variant_combination]["length"]

                if "size" in buy_stack_json["sku"][variant_combination]:
                    properties["size"] = buy_stack_json["sku"][variant_combination]["size"]

                if "waist" in buy_stack_json["sku"][variant_combination]:
                    properties["waist"] = buy_stack_json["sku"][variant_combination]["waist"]

                variant_item["properties"] = properties
                variant_item["price"] = None
                for price in buy_stack_json["sku"][variant_combination]["price"]:
                    if price["il8n"] == "now":
                        variant_item["price"] = float(re.findall("\d+.\d+", price["amount"])[0])
                        break
                variant_item["selected"] = False
                variant_item["upc"] = buy_stack_json["sku"][variant_combination]["upc"]
                variant_item["stock"] = buy_stack_json["sku"][variant_combination]["stock"]
                if variant_item["stock"] > 0:
                    variant_item["in_stock"] = True
                else:
                    variant_item["in_stock"] = False

                variant_list.append(variant_item)

            if variant_list:
                return variant_list

        return None