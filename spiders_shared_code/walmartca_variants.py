import json

import lxml.html


class WalmartCAVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, variant_json, tree_html):
        """ Call it from CH spiders """
        self.variant_json = variant_json
        self.tree_html = tree_html

    def _variants(self):
        if self.variant_json["numberOfVariants"] == 0:
            return None

        try:
            variants_info_list = self.variant_json["variantDataRaw"]
            variants_list = []

            for variant_info in variants_info_list:
                variant_item = {}

                if variant_info["StoreStatus"][0] == "NotSold":
                    variant_item["in_stock"] = False
                else:
                    variant_item["in_stock"] = True

                variant_item["price"] = float(self.tree_html.xpath("//span[@itemprop='price']/text()")[0][1:])
                canonical_link = self.tree_html.xpath("//link[@rel='canonical']/@href")[0]

                '''
                if canonical_link.split('/')[-1] == variant_info["sku_id"][0]:
                    variant_item["selected"] = True
                else:
                    variant_item["selected"] = False
                '''
                variant_item["selected"] = False
#                variant_item["url"] = canonical_link[:canonical_link.rfind("/") + 1] + variant_info["sku_id"][0]
                properties = {}

                for attribute in variant_info:
                    if "variantKey_en_" in attribute:
                        key = attribute[len("variantKey_en_"):]
                        key = key.lower()

                        if key == "colour":
                            key = "color"

                        properties[key] = variant_info[attribute][0]

                variant_item["properties"] = properties
                variants_list.append(variant_item)
        except:
            return None

        if not variants_list:
            return None

        return variants_list