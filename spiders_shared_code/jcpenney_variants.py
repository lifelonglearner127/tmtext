import json

import lxml.html
import itertools
import re


class JcpenneyVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _variants(self):
        try:
            canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]
            product_id = re.search('prod\.jump\?ppId=(.+?)$', canonical_link).group(1)
            variation_key_list = []
            variation_values_list = []
            stockstatus_list_by_variation = []
            stockstatus_for_variants_list = []

            color_list = self.tree_html.xpath("//ul[@id='" + product_id + "COLOR']//img/@alt")
            color_li_list = self.tree_html.xpath("//ul[@id='" + product_id + "COLOR']//li")
            stockstatus_list = []

            for color_li in color_li_list:
                if "class" in color_li:
                    stockstatus_list.append(color_li.attrib["class"])
                else:
                    stockstatus_list.append("")

            if color_list:
                variation_key_list.append("color")
                variation_values_list.append(color_list)
                stockstatus_list_by_variation.append(dict(zip(color_list, stockstatus_list)))

            size_list = self.tree_html.xpath("//ul[@id='" + product_id + "SIZE']//a/@title")
            size_li_list = self.tree_html.xpath("//ul[@id='" + product_id + "SIZE']//li")
            stockstatus_list = []

            for size_li in size_li_list:
                if "class" in size_li.attrib:
                    stockstatus_list.append(size_li.attrib["class"])
                else:
                    stockstatus_list.append("")

            if size_list:
                variation_key_list.append("size")
                variation_values_list.append(size_list)
                stockstatus_list_by_variation.append(dict(zip(size_list, stockstatus_list)))

            variation_combinations_values = list(itertools.product(*variation_values_list))

            variation_combinations_values = map(list, variation_combinations_values)

            for variation_combination in variation_combinations_values:
                stockstatus_for_variants = {}
                properties = {}
                stockstatus = True

                for index, variation_key in enumerate(variation_key_list):
                    properties[variation_key] = variation_combination[index]

                    if stockstatus is True and stockstatus_list_by_variation[index][variation_combination[index]] in ["sku_not_available", "sku_illegal"]:
                        stockstatus = False

                stockstatus_for_variants["properties"] = properties
                stockstatus_for_variants["in_stock"] = stockstatus

                if len(variation_combinations_values) == 1:
                    stockstatus_for_variants["selected"] = True
                else:
                    stockstatus_for_variants["selected"] = False

                stockstatus_for_variants["price"] = None

                stockstatus_for_variants_list.append(stockstatus_for_variants)

            if not stockstatus_for_variants_list:
                return None
            else:
                return stockstatus_for_variants_list
        except:
            return None
