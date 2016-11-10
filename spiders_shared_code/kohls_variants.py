import re
import json

import lxml.html
import itertools
import json


is_empty = lambda x, y="": x[0] if x else y

class KohlsVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
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

    def swatches(self):
        return None

    def _variants(self):
        try:
            product_info_json = self.tree_html.xpath("//script[contains(text(), 'var productJsonData = {')]/text()")[0].strip()
            start_index = product_info_json.find("var productJsonData = ") + len("var productJsonData = ")
            end_index = product_info_json.rfind(";")
            product_info_json = product_info_json[start_index:end_index].strip()
            product_info_json = json.loads(product_info_json)
        except:
            product_info_json = None

        if product_info_json and product_info_json["productItem"].get("variants", None):
            variants_list = []
            color_value_list = size_value_list = None

            if product_info_json["productItem"]["variants"].get("colorList", None):
                color_value_list = product_info_json["productItem"]["variants"]["colorList"]

                if product_info_json["productItem"]["variants"].get("noInventoryColors", None):
                    color_value_list = list(set(color_value_list) - set(product_info_json["productItem"]["variants"]["noInventoryColors"]))

            if product_info_json["productItem"]["variants"].get("sizeList", None):
                size_value_list = product_info_json["productItem"]["variants"]["sizeList"]

                if product_info_json["productItem"]["variants"].get("noInventorySizes", None):
                    size_value_list = list(set(size_value_list) - set(product_info_json["productItem"]["variants"]["noInventorySizes"]))

            attribute_values_list = []
            attribute_name_list = []

            if color_value_list:
                attribute_values_list.append(color_value_list)
                attribute_name_list.append("color")

            if size_value_list:
                attribute_values_list.append(size_value_list)
                attribute_name_list.append("size")

            if attribute_name_list:
                variant_attribute_combination_list = list(itertools.product(*attribute_values_list))

                for variant_sku in product_info_json["productItem"]["skuDetails"]:
                    price = variant_sku["salePrice"] if variant_sku["salePrice"] else variant_sku["regularPrice"]
                    price = re.findall(r"\d*\.\d+|\d+", price.replace(",", ""))
                    price = float(price[0])
                    property = {}

                    if "color" in attribute_name_list:
                        property["color"] = variant_sku["color"]

                    if "size" in attribute_name_list:
                        property["size"] = variant_sku["size2"]

                    obj = {
                        "skuId": variant_sku["skuId"],
                        "upc": variant_sku["skuUpcCode"],
                        "price": price,
                        "in_stock": variant_sku["inventoryStatus"],
                        "properties": property,
                        "selected": False
                    }

                    variants_list.append(obj)

                    if tuple(property.values()) in variant_attribute_combination_list:
                        variant_attribute_combination_list.remove(tuple(property.values()))

                for variant in variant_attribute_combination_list:
                    property = {}

                    for index, attribute_name in enumerate(attribute_name_list):
                        property[attribute_name] = variant[index]

                    obj = {
                        "skuId": None,
                        "price": None,
                        "in_stock": False,
                        "properties": property,
                        "selected": False,
                    }

                    variants_list.append(obj)

                return variants_list if variants_list else None

        return None
