import lxml.html
import json
import re
import itertools


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
            product_url = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]
            attribute_values_list = []
            out_of_stock_combination_list = []

            color_list = []
            color_name_id_map = {}

            for color_id in buy_stack_json["colorid"]:
                color_list.append(buy_stack_json["colorid"][color_id]["finish"]["title"])
                color_name_id_map[buy_stack_json["colorid"][color_id]["finish"]["title"]] = color_id

            if color_list:
                attribute_values_list.append(color_list)

            length_list = buy_stack_json["attrs"]["length"]

            if length_list:
                attribute_values_list.append(length_list)

            size_list = buy_stack_json["attrs"]["size"]

            if size_list:
                attribute_values_list.append(size_list)

            waist_list = buy_stack_json["attrs"]["waist"]

            if waist_list:
                attribute_values_list.append(waist_list)

            out_of_stock_combination_list = list(itertools.product(*attribute_values_list))
            out_of_stock_combination_list = [list(tup) for tup in out_of_stock_combination_list]
            attribute_list = []
            variant_list = []
            registered_value_list = []

            for variant_combination in buy_stack_json["sku"]:
                variant_item = {}
                properties = {}
                value_list = []

                if "colorid" in buy_stack_json["sku"][variant_combination]:
                    if color_list:
                        if buy_stack_json["sku"][variant_combination]["colorid"] not in buy_stack_json["colorid"]:
                            continue
                        variant_item['colorid'] = buy_stack_json["sku"][variant_combination]['colorid']
                        properties["color"] = buy_stack_json["colorid"][buy_stack_json["sku"][variant_combination]["colorid"]]["finish"]["title"]
                        variant_item["url"] = product_url[:product_url.rfind("/") + 1] + buy_stack_json["sku"][variant_combination]["colorid"]
                        value_list.append(properties["color"])
                        if "color" not in attribute_list: attribute_list.append("color")
                    else:
                        continue

                if "length" in buy_stack_json["sku"][variant_combination]:
                    if length_list:
                        properties["length"] = buy_stack_json["sku"][variant_combination]["length"]
                        value_list.append(properties["length"])
                        if "length" not in attribute_list: attribute_list.append("length")
                    else:
                        continue

                if "size" in buy_stack_json["sku"][variant_combination]:
                    if size_list:
                        properties["size"] = buy_stack_json["sku"][variant_combination]["size"]
                        value_list.append(properties["size"])
                        if "size" not in attribute_list: attribute_list.append("size")
                    else:
                        continue

                if "waist" in buy_stack_json["sku"][variant_combination]:
                    if waist_list:
                        properties["waist"] = buy_stack_json["sku"][variant_combination]["waist"]
                        value_list.append(properties["waist"])
                        if "waist" not in attribute_list: attribute_list.append("waist")
                    else:
                        continue

                if value_list in registered_value_list:
                    continue

                registered_value_list.append(value_list)

                if value_list in out_of_stock_combination_list:
                    out_of_stock_combination_list.remove(value_list)

                variant_item["properties"] = properties
                variant_item["price"] = None
                for price in buy_stack_json["sku"][variant_combination]["price"]:
                    if price["il8n"] == "now":
                        variant_item["price"] = float(re.findall(r"\d*\.\d+|\d+", price["amount"].replace(",", ""))[0])
                        break
                variant_item["selected"] = False
                variant_item["upc"] = buy_stack_json["sku"][variant_combination]["upc"]
                variant_item["stock"] = buy_stack_json["sku"][variant_combination]["stock"]
                if variant_item["stock"] > 0:
                    variant_item["in_stock"] = True
                else:
                    variant_item["in_stock"] = False

                variant_list.append(variant_item)

            for out_of_stock_combination in out_of_stock_combination_list:
                properties = {}
                variant_item = {}

                for index, attribute in enumerate(attribute_list):
                    properties[attribute] = out_of_stock_combination[index]

                variant_item["properties"] = properties
                variant_item["price"] = None

                if "color" in properties:
                    for price in buy_stack_json["colorid"][color_name_id_map[properties["color"]]]["price"]:
                        if price["il8n"] == "now":
                            variant_item["price"] = float(re.findall("\d*\.\d+|\d+", price["amount"].replace(",", ""))[0])
                            break

                variant_item["selected"] = False
                variant_item["upc"] = None
                variant_item["stock"] = 0
                variant_item["in_stock"] = False
                variant_item["url"] = None

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
