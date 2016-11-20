import lxml.html
import json
import re
import itertools


class LeviVariants(object):

    local_variants_map = {}  # used to filter unique results (by `properties`)


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

    def _is_unique_variant(self, variant):
        if not 'properties' in variant:
            return
        if not variant['properties']:
            return
        return variant['properties'] in self.local_variants_map

    def _find_variant_with_better_data(self, v1, v2):
        if v1.get('url', None) and not v2.get('url', None):
            return v1
        else:
            return v2

    def _append_variant_or_replace_incomplete_one(self, variant_list, variant):
        """ This will replace the old, existing variant in "variant_list" with "variant"
            if the new "variant" has more data; or will append it if there's no existing variant
            in "variant_list"
            """
        props = variant.get('properties', None)
        if not props:
            variant_list.append(variant)  # just append the variant if properties are not available
            return
        if str(props) not in self.local_variants_map:  # brand-new variant
            self.local_variants_map[str(props)] = variant
            variant_list.append(variant)
            return
        else:  # we have an existing variant
            existing_variant = self.local_variants_map[str(props)]
            if self._find_variant_with_better_data(variant, existing_variant) == existing_variant:
                # the existing, already-added variant has more data - continue
                return
            else:
                # need to replace the old, bad variant with the new one
                self.local_variants_map[str(props)] = variant
                for i, old_var in enumerate(variant_list):
                    if str(old_var.get('properties', None)) == str(props):
                        variant_list[i] = variant

    @staticmethod
    def _strip_ids_from_colors(variants):
        """ Removes the trailing ____XXXXXX code from properties """
        for variant in variants:
            props = variant.get('properties', None)
            if props:
                color = props.get('color', None)
                if color:
                    if '____' in color:
                        color = color.split('____', 1)[0]
                        props['color'] = color

    def _variants(self):
        buy_stack_json = None

        try:
            buy_stack_json_text = self._find_between(" " . join(self.tree_html.xpath("//script[@type='text/javascript']/text()")), "var buyStackJSON = '", "'; var productCodeMaster =").replace("\'", '"').replace('\\\\"', "")
            # print buy_stack_json_text
            buy_stack_json = json.loads(buy_stack_json_text)
        except:
            buy_stack_json = None

        if not buy_stack_json:
            try:
                js_block = self.tree_html.xpath(
                    "//script[@type='text/javascript' and contains(text(), 'buyStackJSON')]/text()")
                js_block = js_block[0] if js_block else ""
                json_regex = r"var\s?buyStackJSON\s?=\s?[\'\"](.+)[\'\"];?\s?"
                json_regex_c = re.compile(json_regex)
                buy_stack_json_text = json_regex_c.search(js_block)
                buy_stack_json_text = buy_stack_json_text.groups()[0] if buy_stack_json_text else ""
                buy_stack_json_text = buy_stack_json_text.replace("\'", '"').replace('\\\\"', "")
                buy_stack_json = json.loads(buy_stack_json_text)
            except Exception as e:
                print "Failed extracting json block with regex: {}".format(e)
                buy_stack_json = None

        if buy_stack_json:
            product_url = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]
            attribute_values_list = []
            out_of_stock_combination_list = []

            color_list = []
            color_name_id_map = {}

            for color_id in buy_stack_json["colorid"]:
                color_list.append(buy_stack_json["colorid"][color_id]["finish"]["title"]
                                  + '____' + str(color_id))
                color_name_id_map[buy_stack_json["colorid"][color_id]["finish"]["title"]
                                  + '____' + str(color_id)] = color_id

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

                        variant_item["colorid"] = buy_stack_json["sku"][variant_combination]["colorid"]
                        properties["color"] = buy_stack_json["colorid"][buy_stack_json["sku"][variant_combination]\
                            ["colorid"]]["finish"]["title"] + '____'\
                            + str(buy_stack_json["colorid"][buy_stack_json["sku"][variant_combination]["colorid"]]['colorid'])
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

                self._append_variant_or_replace_incomplete_one(variant_list, variant_item)
                #variant_list.append(variant_item)

            for out_of_stock_combination in out_of_stock_combination_list:
                properties = {}
                variant_item = {}

                for index, attribute in enumerate(attribute_list):
                    properties[attribute] = out_of_stock_combination[index]

                variant_item["properties"] = properties
                variant_item["price"] = None

                if "color" in properties:
                    variant_item["colorid"] = buy_stack_json["colorid"][color_name_id_map[properties["color"]]]["colorid"]
                    for price in buy_stack_json["colorid"][color_name_id_map[properties["color"]]]["price"]:
                        if price["il8n"] == "now":
                            variant_item["price"] = float(re.findall("\d*\.\d+|\d+", price["amount"].replace(",", ""))[0])
                            break

                variant_item["selected"] = False
                variant_item["upc"] = None
                variant_item["stock"] = 0
                variant_item["in_stock"] = False
                variant_item["url"] = None

                self._append_variant_or_replace_incomplete_one(variant_list, variant_item)
                #variant_list.append(variant_item)

            if variant_list:
                self._strip_ids_from_colors(variant_list)
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
