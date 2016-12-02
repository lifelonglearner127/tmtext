import json
import collections
import ast
import itertools
import re
import lxml.html


class AmazonVariants(object):

    def setupSC(self, response, product_url=None):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)
        self.product_url = product_url

    def setupCH(self, tree_html, product_url=None):
        """ Call it from CH spiders """
        self.tree_html = tree_html
        self.product_url = product_url

    def _find_between(self, s, first, last, offset=0):
        try:
            start = s.index(first, offset) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def _swatches(self):
        swatch_images = []

        try:
            swatch_image_json = json.loads(self._find_between(lxml.html.tostring(self.tree_html), 'data["colorImages"] = ', ';\n'), object_pairs_hook=collections.OrderedDict)
        except:
            swatch_image_json = None

        swatch_list = []

        for swatch in swatch_image_json:
            swatch_info = {}
            swatch_info["swatch_name"] = "color"
            swatch_info["color"] = swatch
            swatch_info["hero"] = len(swatch_image_json[swatch])
            swatch_info["thumb"] = len(swatch_image_json[swatch])
            swatch_info["hero_image"] = [image["large"] for image in swatch_image_json[swatch]]
            swatch_info["thumb_image"] = [image["thumb"] for image in swatch_image_json[swatch]]
            swatch_list.append(swatch_info)

        if swatch_list:
            return swatch_list

        return None

    def _variants(self):
        try:
            site_name = self._find_between(lxml.html.tostring(self.tree_html), "ue_sn='", "',")
            filtering_attribute_list = ["item_package_quantity", "customer_package_type", "special_size_type", "configuration"]
            original_product_canonical_link = None

            if self.tree_html.xpath("//link[@rel='canonical']/@href"):
                original_product_canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

            page_raw_text = lxml.html.tostring(self.tree_html)
            variation_key_values = json.loads(re.search('"variation_values":(.+?),"deviceType', page_raw_text).group(1), object_pairs_hook=collections.OrderedDict)

            if not variation_key_values:
                variation_key_values = json.loads(self._find_between(page_raw_text, '"variation_values":', ',"deviceType"'), object_pairs_hook=collections.OrderedDict)

            variation_key_list = variation_key_values.keys()

            if not variation_key_list:
                raise Exception

            # reversing variant key list if the site is amazon.in
            if "amazon.in" in site_name:
                variation_key_list = list(reversed(variation_key_list))

            for index, variation_key in enumerate(variation_key_list):
                variation_key_list[index] = variation_key[:variation_key.rfind("_name")] if variation_key.rfind("_name") > 0 else variation_key

            variation_values_list = []

            for variation_key in variation_key_list:
                if variation_key == "processor":
                    variation_values_list.append(variation_key_values[variation_key + "_description"])
                elif variation_key in filtering_attribute_list:
                    variation_values_list.append(variation_key_values[variation_key])
                else:
                    variation_values_list.append(variation_key_values[variation_key + "_name"])

            variation_combinations_values = list(itertools.product(*variation_values_list))

            variation_combinations_values = map(list, variation_combinations_values)
            instock_variation_combinations_values = json.loads(re.search('"dimensionValuesDisplayData":(.+?),"hidePopover":', page_raw_text).group(1), object_pairs_hook=collections.OrderedDict)
            instock_variation_combinations_values = [instock_variation_combinations_values[key] for key in instock_variation_combinations_values]
            dimensions = ast.literal_eval(re.search('"dimensions":(.+?),"prioritizeReqPrefetch":', page_raw_text).group(1))
            dimensions_key_index_map = {}

            for index, key in enumerate(dimensions):
                dimensions_key_index_map[key[:key.rfind("_name")] if key.rfind("_name") > 0 else key] = index

            outofstock_variation_combinations_values = [variation_combination for variation_combination in variation_combinations_values if variation_combination not in instock_variation_combinations_values]

            selected_variation_combination = json.loads(re.search('"selected_variations":(.+?),"jqupgrade"', page_raw_text).group(1), object_pairs_hook=collections.OrderedDict)

            selected_variation_combination = [selected_variation_combination[key] for key in selected_variation_combination]

            # reversing selected variant key list if the site is amazon.in
            if "amazon.in" in site_name:
                selected_variation_combination = list(reversed(selected_variation_combination))

            asin_variation_values = json.loads(re.search('"asin_variation_values":(.+?),"contextMetaData":', page_raw_text).group(1), object_pairs_hook=collections.OrderedDict)

            variation_asin_values = {}

            for asin_variation in asin_variation_values:
                del asin_variation_values[asin_variation]['ASIN']

                property_index = 0
                variation_combination_key = ""

                for key in variation_key_list:
                    if key == "processor":
                        variation_combination_key += variation_key_values[key + "_description"][int(asin_variation_values[asin_variation][key+"_description"])]
                    elif key in filtering_attribute_list:
                        variation_combination_key += variation_key_values[key][int(asin_variation_values[asin_variation][key])]
                    else:
                        variation_combination_key += variation_key_values[key + "_name"][int(asin_variation_values[asin_variation][key+"_name"])]
                    property_index = property_index + 1

                variation_asin_values[variation_combination_key] = asin_variation

            stockstatus_for_variants_list = []

            for variation_combination in outofstock_variation_combinations_values:
                stockstatus_for_variants = {}
                properties = {}
                isSelected = True

                for index, variation_key in enumerate(variation_key_list):
                    properties[variation_key] = variation_combination[index]

                    if variation_combination[index] != selected_variation_combination[index]:
                        isSelected = False

                stockstatus_for_variants["properties"] = properties
                stockstatus_for_variants["in_stock"] = False
                stockstatus_for_variants["selected"] = isSelected
                stockstatus_for_variants["price"] = None
                stockstatus_for_variants["url"] = None
                stockstatus_for_variants_list.append(stockstatus_for_variants)

            for variation_combination in instock_variation_combinations_values:
                stockstatus_for_variants = {}
                properties = {}
                isSelected = True
                variation_combination_key = ""

                for index, variation_key in enumerate(variation_key_list):
                    properties[variation_key] = variation_combination[dimensions_key_index_map[variation_key]]
                    variation_combination_key += variation_combination[dimensions_key_index_map[variation_key]]
                    if variation_combination[dimensions_key_index_map[variation_key]] != selected_variation_combination[index]:
                        isSelected = False

                stockstatus_for_variants["properties"] = properties
                stockstatus_for_variants["in_stock"] = True
                stockstatus_for_variants["selected"] = isSelected
                stockstatus_for_variants["price"] = None
                stockstatus_for_variants["asin"] = variation_asin_values[variation_combination_key]

                if original_product_canonical_link:
                    stockstatus_for_variants["url"] = original_product_canonical_link[:original_product_canonical_link.rfind("/") + 1] + variation_asin_values[variation_combination_key]
                else:
                    stockstatus_for_variants["url"] = self.product_url[:self.product_url.rfind("/") + 1] + variation_asin_values[variation_combination_key]

                stockstatus_for_variants_list.append(stockstatus_for_variants)

            # filter variants (exclude variants with duplicated properties)
            vars2remove = []
            for variant in stockstatus_for_variants_list:
                props = variant.get('properties', None)
                if props:
                    for variant2 in stockstatus_for_variants_list:
                        props2 = variant2.get('properties', None)
                        if props == props2:
                            if variant != variant2:
                                if variant.get('url', None):
                                    if variant2 not in vars2remove:
                                        vars2remove.append(variant2)
                                else:
                                    if variant not in vars2remove:
                                        vars2remove.append(variant)

            stockstatus_for_variants_list = [v for v in stockstatus_for_variants_list
                                             if v not in vars2remove]

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except Exception as e:
            print e
            return None
