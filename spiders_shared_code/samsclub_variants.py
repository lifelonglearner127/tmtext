import json

import lxml.html
import re

class SamsclubVariants(object):

    def setupSC(self, response):
        """ Call it from SC spiders """
        self.response = response
        self.tree_html = lxml.html.fromstring(response.body)

    def setupCH(self, tree_html):
        """ Call it from CH spiders """
        self.tree_html = tree_html

    def _clean_text(self, text):
        text = text.replace("<br />"," ").replace("\n"," ").replace("\t"," ").replace("\r"," ")
       	text = re.sub("&nbsp;", " ", text).strip()
        return  re.sub(r'\s+', ' ', text)

    def _swatches(self):
        return None

    def _variants(self):
        variants_json = self.tree_html.xpath("//div[@id='skuVariantDetailsJSON']/text()")

        if variants_json:
            variants_list = []
            variants_json = json.loads(variants_json[0].strip())

            for sku in variants_json:
                variant = {}
                properties = {}
                variant["upc"] = sku
                variant["in_stock"] = True if variants_json[sku]["status"] == "Available" else False

                for key in variants_json[sku]:
                    if key != "status":
                        properties[key] = variants_json[sku][key]

                variant["properties"] = properties
                variants_list.append(variant)

            return variants_list

        return None
