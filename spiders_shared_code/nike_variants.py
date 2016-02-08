import lxml.html
from itertools import product
import json
import re
from lxml import html, etree
import itertools
import yaml


class NikeVariants(object):

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
        product_json = None

        try:
            product_json_text = self.tree_html.xpath("//script[@id='product-data']/text()")[0]
            product_json = json.loads(product_json_text)
        except:
            product_json = None


        variant_list = []

        if product_json["inStockColorways"]:
            for swatch in product_json["inStockColorways"]:
                variant_item = {}
                properties = {"color": swatch["colorDescription"]}
                variant_item["properties"] = properties
                variant_item["price"] = float(self.tree_html.xpath("//meta[@property='og:price:amount']/@content")[0])
                variant_item["in_stock"] = True if swatch["status"] == "IN_STOCK" else False
                variant_item["url"] = swatch["url"]
                variant_item["selected"] = True if "pid-" + str(product_json["productId"]) in swatch["url"] else False
                variant_list.append(variant_item)

        if variant_list:
            return variant_list

        return None

    def _swatches(self):
        buy_stack_json = None

        try:
            buy_stack_json_text = self._find_between(" " . join(self.tree_html.xpath("//script[@type='text/javascript']/text()")), "var buyStackJSON = '", "'; var productCodeMaster =").replace("\'", '"').replace('\\\\"', "")
            buy_stack_json = json.loads(buy_stack_json_text)
        except:
            buy_stack_json = None

        if buy_stack_json:
            swatch_list = []

            for swatch in buy_stack_json["colorid"]:
                swatch_info = {}
                swatch_info["swatch_name"] = "color"
                swatch_info["color"] = buy_stack_json["colorid"][swatch]["finish"]["title"]
                swatch_info["hero"] = 1
                swatch_info["thumb"] = 1
                swatch_info["hero_image"] = [buy_stack_json["colorid"][swatch]["imageURL"] + altView for altView in buy_stack_json["colorid"][swatch]["altViewsMain"]]
                swatch_info["thumb_image"] = [buy_stack_json["colorid"][swatch]["swatch"]]
                swatch_list.append(swatch_info)

            if swatch_list:
                return swatch_list

        return None