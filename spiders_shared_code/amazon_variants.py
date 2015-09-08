import json

import lxml.html
import itertools
import re


class AmazonVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _variants(self):
        try:
            original_product_canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]
            page_raw_text = lxml.html.tostring(self.tree_html)
            variation_key_values = json.loads(re.search('"variation_values":(.+?),"deviceType', page_raw_text).group(1))
            variation_key_list = list(variation_key_values)

            # reversing variant key list if the site is amazon.in
            if "amazon.in" in original_product_canonical_link:
                variation_key_list = list(reversed(variation_key_list))

            for index, variation_key in enumerate(variation_key_list):
                variation_key_list[index] = variation_key[:variation_key.find("_")]

            variation_values_list = []

            for variation_key in variation_key_list:
                if variation_key == "processor":
                    variation_values_list.append(variation_key_values[variation_key + "_description"])
                else:
                    variation_values_list.append(variation_key_values[variation_key + "_name"])

            variation_combinations_values = list(itertools.product(*variation_values_list))

            variation_combinations_values = map(list, variation_combinations_values)
            instock_variation_combinations_values = json.loads(re.search('"dimensionValuesDisplayData":(.+?),"hidePopover":', page_raw_text).group(1))
            instock_variation_combinations_values = [instock_variation_combinations_values[key] for key in instock_variation_combinations_values]

            outofstock_variation_combinations_values = [variation_combination for variation_combination in variation_combinations_values if variation_combination not in instock_variation_combinations_values]

            selected_variation_combination = json.loads(re.search('"selected_variations":(.+?),"jqupgrade"', page_raw_text).group(1))

            selected_variation_combination = [selected_variation_combination[key] for key in selected_variation_combination]

            # reversing selected variant key list if the site is amazon.in
            if "amazon.in" in original_product_canonical_link:
                selected_variation_combination = list(reversed(selected_variation_combination))

            asin_variation_values = json.loads(re.search('"asin_variation_values":(.+?),"contextMetaData":', page_raw_text).group(1))

            variation_asin_values = {}

            for asin_variation in asin_variation_values:
                del asin_variation_values[asin_variation]['ASIN']

                property_index = 0
                variation_combination_key = ""

                for key in variation_key_list:
                    if key == "processor":
                        variation_combination_key += variation_key_values[key + "_description"][int(asin_variation_values[asin_variation][key+"_description"])]
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
                    properties[variation_key] = variation_combination[index]
                    variation_combination_key += variation_combination[index]
                    if variation_combination[index] != selected_variation_combination[index]:
                        isSelected = False

                stockstatus_for_variants["properties"] = properties
                stockstatus_for_variants["in_stock"] = True
                stockstatus_for_variants["selected"] = isSelected
                stockstatus_for_variants["price"] = None
                stockstatus_for_variants["url"] = original_product_canonical_link[:original_product_canonical_link.rfind("/") + 1] + variation_asin_values[variation_combination_key]

                stockstatus_for_variants_list.append(stockstatus_for_variants)

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except:
            return None
