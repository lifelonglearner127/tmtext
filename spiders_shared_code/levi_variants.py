import lxml.html
from itertools import product
import json
import re
from lxml import html, etree
import itertools
import yaml


class LeviVariants(object):

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
        try:
#            buy_stack_json_text = self._find_between(" " . join(self.tree_html.xpath("//script[@type='text/javascript']/text()")), "var buyStackJSON = '", "'; var productCodeMaster =")
            buy_stack_json_text = self._find_between(" " . join(self.tree_html.xpath("//script[@type='text/javascript']/text()")), "var buyStackJSON = '", "'; var productCodeMaster =").replace("\'", '"')
            self.buy_stack_json = json.loads(buy_stack_json_text)
        except:
            self.buy_stack_json = None

        if self.buy_stack_json:
                upc = self.tree_html.xpath("//meta[@property='og:upc']/@content")[0]

                variants_data = re.findall(
                        'wf\.appData\.product_data_%s\s?=\s?({.[^;]+)' % upc,
                        html.tostring(self.tree_html)
                    )[0]

                variants_json = json.loads(variants_data)
                variant_list = []


                variation_values_list = []

                for variation_option in variants_json["option_info"]:
                    variation_values_list.append(variants_json["option_info"][variation_option]["options"])

                variation_combinations_values = list(itertools.product(*variation_values_list))
                price = float(self.tree_html.xpath("//meta[@property='og:price:amount']/@content")[0])

                for variant_combination in variation_combinations_values:
                    variant_item = {}
                    properties = {}
                    stock_status = True
                    delta_price = 0

                    for variant_option in variant_combination:
                        properties[variants_json["option_details"][str(variant_option)]["category"].lower()] = variants_json["option_details"][str(variant_option)]["name"]
                        delta_price = delta_price + float(variants_json["option_details"][str(variant_option)]["price"])

                    for exception_variant in variants_json["option_exceptions"]:
                        if set(exception_variant) == set(variant_combination):
                            stock_status = False
                            break

                    variant_item["properties"] = properties
                    variant_item["in_stock"] = stock_status
                    variant_item["price"] = price + delta_price
                    variant_item["selected"] = False

                    variant_list.append(variant_item)

                if not variant_list:
                    return None

                return variant_list

        return None